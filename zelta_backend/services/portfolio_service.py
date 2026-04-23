"""
ZELTA Portfolio Service

Decision history, outcome tracking, and behavioral performance metrics.
Every ZELTA recommendation is logged and tracked for learning.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import List
from google.cloud import firestore
from schemas.portfolio import (
    LogDecisionRequest, UpdateOutcomeRequest,
    DecisionRecord, PerformanceMetrics, PortfolioSummary,
    DecisionOutcome,
)

logger = logging.getLogger(__name__)


def _get_decisions_ref(db: firestore.Client, uid: str) -> firestore.CollectionReference:
    return db.collection("portfolio").document(uid).collection("decisions")


def _get_portfolio_ref(db: firestore.Client, uid: str) -> firestore.DocumentReference:
    return db.collection("portfolio").document(uid)


async def log_decision(
    db: firestore.Client, uid: str, request: LogDecisionRequest
) -> DecisionRecord:
    """Log a ZELTA decision recommendation to the portfolio."""

    decision_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    record = {
        "id": decision_id,
        "verdict": request.verdict,
        "amount": request.amount,
        "rationale": request.rationale,
        "stress_index": request.stress_index_at_decision,
        "bayse_fear": request.bayse_fear_at_decision,
        "bias": request.bias_at_decision,
        "decision_score": request.decision_score,
        "category": request.category,
        "notes": request.notes,
        "actual_outcome": None,
        "outcome_label": DecisionOutcome.PENDING,
        "return_amount": None,
        "return_percentage": None,
        "created_at": now,
        "resolved_at": None,
    }

    _get_decisions_ref(db, uid).document(decision_id).set(record)

    # Update portfolio aggregate
    portfolio_ref = _get_portfolio_ref(db, uid)
    portfolio_doc = portfolio_ref.get()
    if portfolio_doc.exists:
        portfolio_ref.update({
            "total_decisions": firestore.Increment(1),
            "total_invested": firestore.Increment(request.amount),
            "updated_at": now,
        })
    else:
        portfolio_ref.set({
            "uid": uid,
            "total_decisions": 1,
            "total_invested": request.amount,
            "total_returned": 0.0,
            "correct_decisions": 0,
            "incorrect_decisions": 0,
            "created_at": now,
            "updated_at": now,
        })

    return DecisionRecord(**record)


async def update_outcome(
    db: firestore.Client, uid: str, request: UpdateOutcomeRequest
) -> DecisionRecord:
    """Update the actual outcome of a previously logged decision."""

    decision_ref = _get_decisions_ref(db, uid).document(request.decision_id)
    doc = decision_ref.get()

    if not doc.exists:
        raise ValueError(f"Decision {request.decision_id} not found.")

    existing = doc.to_dict()
    now = datetime.now(timezone.utc)

    # Compute return
    invested = existing.get("amount", 0.0)
    return_amount = request.actual_outcome - invested
    return_pct = round((return_amount / invested * 100), 2) if invested > 0 else 0.0

    updates = {
        "actual_outcome": request.actual_outcome,
        "outcome_label": request.outcome_label,
        "return_amount": return_amount,
        "return_percentage": return_pct,
        "resolved_at": now,
        "notes": request.notes or existing.get("notes"),
    }

    decision_ref.update(updates)

    # Update portfolio aggregate
    portfolio_ref = _get_portfolio_ref(db, uid)
    portfolio_updates = {
        "total_returned": firestore.Increment(request.actual_outcome),
        "updated_at": now,
    }
    if request.outcome_label == DecisionOutcome.CORRECT:
        portfolio_updates["correct_decisions"] = firestore.Increment(1)
    elif request.outcome_label == DecisionOutcome.INCORRECT:
        portfolio_updates["incorrect_decisions"] = firestore.Increment(1)

    portfolio_ref.update(portfolio_updates)

    return DecisionRecord(**{**existing, **updates})


async def get_portfolio_summary(db: firestore.Client, uid: str) -> PortfolioSummary:
    """Get full portfolio with performance metrics and recent decisions."""

    portfolio_doc = _get_portfolio_ref(db, uid).get()
    agg = portfolio_doc.to_dict() if portfolio_doc.exists else {}

    total_decisions = agg.get("total_decisions", 0)
    correct = agg.get("correct_decisions", 0)
    incorrect = agg.get("incorrect_decisions", 0)
    pending = total_decisions - correct - incorrect
    total_invested = agg.get("total_invested", 0.0)
    total_returned = agg.get("total_returned", 0.0)

    accuracy_rate = round((correct / max(1, correct + incorrect)) * 100, 1)

    # Fetch recent decisions
    decision_docs = (
        _get_decisions_ref(db, uid)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(20)
        .stream()
    )
    decisions_raw = [d.to_dict() for d in decision_docs]
    recent_decisions = [DecisionRecord(**d) for d in decisions_raw]

    avg_decision_score = (
        sum(d.decision_score for d in recent_decisions) / len(recent_decisions)
        if recent_decisions else 0.0
    )
    best_score = max((d.decision_score for d in recent_decisions), default=0.0)

    # Behavioral pattern summary
    bias_counts: dict = {}
    for d in recent_decisions:
        bias_counts[d.bias] = bias_counts.get(d.bias, 0) + 1
    dominant_bias = max(bias_counts, key=bias_counts.get) if bias_counts else "NONE"

    pattern_summary = (
        f"Your most frequent bias is {dominant_bias.replace('_', ' ').title()}. "
        f"Decision accuracy: {accuracy_rate:.0f}% over {correct + incorrect} resolved decisions. "
        f"Average BQ Decision Score: {avg_decision_score:.1f}/5."
    )

    metrics = PerformanceMetrics(
        total_decisions=total_decisions,
        correct_decisions=correct,
        incorrect_decisions=incorrect,
        pending_decisions=pending,
        accuracy_rate=accuracy_rate,
        average_decision_score=round(avg_decision_score, 2),
        total_invested=round(total_invested, 2),
        total_returned=round(total_returned, 2),
        net_pnl=round(total_returned - total_invested, 2),
        best_decision_score=round(best_score, 2),
        average_bayse_accuracy_gap=_compute_bayse_gap(recent_decisions),
    )

    return PortfolioSummary(
        metrics=metrics,
        recent_decisions=recent_decisions[:10],
        behavioral_pattern_summary=pattern_summary,
    )


def _compute_bayse_gap(decisions: List[DecisionRecord]) -> float:
    """Compute average gap between Bayse crowd fear and actual outcomes."""
    resolved = [d for d in decisions if d.outcome_label != DecisionOutcome.PENDING]
    if not resolved:
        return 0.0
    gaps = [abs(d.bayse_fear - d.decision_score * 20) for d in resolved]
    return round(sum(gaps) / len(gaps), 2)