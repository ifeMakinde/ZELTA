"""
ZELTA Intelligence Service

Thin orchestration layer between routes and the AI Brain.

Responsibilities:
  1. Load wallet + profile context from Firestore
  2. Call optimizer.run_brain() (HTTP -> deployed Brain)
  3. Map the normalised dict to Pydantic response models
  4. Expose lightweight helpers (stress only, bayse only, markets)

All computation lives in the deployed Brain. This service owns data
loading and model mapping only.
"""

import logging
from google.cloud import firestore

from optimizer import run_brain, fetch_bayse_signal, fetch_stress_signal
from services.wallet_service import get_wallet_summary, get_transaction_patterns
from services.profile_service import get_profile

from schemas.intelligence import (
    BrainResponse,
    BayseSchema, NLPSchema, ScoredHeadline,
    StressSchema, BiasSchema, DecisionSchema,
    ConfidenceSchema, ConfidenceMetrics,
    AllocationSchema, ScoreSchema, ScoreComponents,
    ExplanationSchema,
    StressOnlyResponse, BayseMarketItem, BayseMarketsResponse,
)

logger = logging.getLogger(__name__)


# ─── Full intelligence pipeline ───────────────────────────────────────────────

async def get_intelligence(db: firestore.Client, uid: str) -> BrainResponse:
    """
    Load user context, call the AI Brain, return a typed BrainResponse.
    """
    # 1. Load context
    wallet_summary = await get_wallet_summary(db, uid)
    transaction_patterns = await get_transaction_patterns(db, uid)
    profile = await get_profile(db, uid)

    wallet_data = {
        "total_balance":   wallet_summary.total_balance,
        "free_cash":       wallet_summary.free_cash,
        "locked_amount":   wallet_summary.locked_amount,
        "total_income":    wallet_summary.total_income,
        "total_expenses":  wallet_summary.total_expenses,
        "weekly_burn_rate": wallet_summary.weekly_burn_rate,
    }

    profile_data = {
        "risk_tolerance": (
            profile.financial.risk_tolerance
            if profile.financial else "moderate"
        ),
        "monthly_budget": (
            profile.financial.monthly_budget
            if profile.financial else None
        ),
    }

    # 2. Call AI Brain (returns normalised dict)
    brain = await run_brain(
        wallet_data=wallet_data,
        profile_data=profile_data,
        transaction_patterns=transaction_patterns,
    )

    # 3. Map to typed response
    return _map_to_brain_response(brain)


# ─── Lightweight helpers ──────────────────────────────────────────────────────

async def get_stress_only(db: firestore.Client, uid: str) -> StressOnlyResponse:
    """Return stress index only. Tries the /stress endpoint first."""
    stress = await fetch_stress_signal()
    return StressOnlyResponse(
        stress_index=stress["combined_index"],
        level=stress["level"],
        label=stress["label"],
        bayse_primary=stress["bayse_primary"],
        nlp_secondary=stress["nlp_secondary"],
        market_probability=stress["market_probability"],
    )


async def get_bayse_markets() -> BayseMarketsResponse:
    """Return live Bayse market data for the UI markets screen."""
    bayse = await fetch_bayse_signal()

    items = [
        BayseMarketItem(
            name=bayse.get("market_title") or "Active Bayse Market",
            probability=bayse["naira_weakness_probability"],
            description="Real-money crowd probability on the active Nigerian financial market",
        ),
        BayseMarketItem(
            name="Market Spread Signal",
            probability=round(bayse["spread"] * 100, 2),
            description="Bid-ask spread as market uncertainty indicator",
        ),
        BayseMarketItem(
            name="Order Book Imbalance",
            probability=round(bayse["imbalance"] * 100, 2),
            description="Directional pressure from Bayse order book",
        ),
        BayseMarketItem(
            name="Composite Crowd Stress",
            probability=bayse["raw_crowd_stress"],
            description="Composite behavioral stress signal from Bayse crowd pricing",
        ),
    ]

    return BayseMarketsResponse(
        markets=items,
        composite_stress=bayse["raw_crowd_stress"],
        bayse_available=bayse.get("available", False),
        market_title=bayse.get("market_title", ""),
        verdict=(
            "CALM" if bayse["raw_crowd_stress"] < 30 else
            "MODERATE" if bayse["raw_crowd_stress"] < 60 else
            "HIGH_STRESS" if bayse["raw_crowd_stress"] < 80 else
            "CRISIS"
        ),
    )


# ─── Mapper ───────────────────────────────────────────────────────────────────

def _map_to_brain_response(b: dict) -> BrainResponse:
    """
    Map the normalised brain dict (from optimizer.normalise_brain_response)
    to the typed BrainResponse Pydantic model.
    """

    # Bayse
    braw = b.get("bayse", {})
    bayse = BayseSchema(
        score=braw.get("score", 50.0),
        status=braw.get("status", "MODERATE"),
        market_title=braw.get("market_title", ""),
        market_id=braw.get("market_id", ""),
        crowd_yes_price=braw.get("crowd_yes_price", 0.5),
        crowd_no_price=braw.get("crowd_no_price", 0.5),
        mid_price=braw.get("mid_price", 0.5),
        best_bid=braw.get("best_bid", 0.0),
        best_ask=braw.get("best_ask", 0.0),
        spread=braw.get("spread", 0.0),
        imbalance=braw.get("imbalance", 0.0),
        volume24h=braw.get("volume24h", 0.0),
        trade_count_24h=braw.get("trade_count_24h", 0),
        available=braw.get("available", True),
        raw_crowd_stress=braw.get("raw_crowd_stress", 50.0),
        naira_weakness_probability=braw.get("naira_weakness_probability", 50.0),
    )

    # NLP
    nlp_raw = b.get("nlp", {})
    headlines = [
        ScoredHeadline(**h) for h in nlp_raw.get("scored_headlines", [])
        if isinstance(h, dict)
    ]
    nlp = NLPSchema(
        scored_headlines=headlines,
        aggregate_sentiment=float(nlp_raw.get("aggregate_sentiment", 0.0)),
    )

    # Stress
    sraw = b.get("stress", {})
    stress = StressSchema(
        combined_index=sraw.get("combined_index", 50.0),
        level=sraw.get("level", "MODERATE"),
        label=sraw.get("label", ""),
        bayse_primary=sraw.get("bayse_primary", 0.0),
        nlp_secondary=sraw.get("nlp_secondary", 0.0),
        market_probability=sraw.get("market_probability", 0.5),
        bayse_weight=sraw.get("bayse_weight", 0.6),
        nlp_weight=sraw.get("nlp_weight", 0.4),
    )

    # Bias
    biraw = b.get("bias", {})
    bias = BiasSchema(
        active_bias=biraw.get("active_bias", "Rational"),
        confidence=biraw.get("confidence", "Low"),
        explanation=biraw.get("explanation", ""),
        inputs=biraw.get("inputs", {}),
    )

    # Decision
    draw = b.get("decision", {})
    decision = DecisionSchema(
        verdict=draw.get("verdict", "HOLD"),
        market_probability=draw.get("market_probability", 0.5),
        rational_probability=draw.get("rational_probability", 0.5),
        edge=draw.get("edge", 0.0),
        confidence=draw.get("confidence", "Low"),
        win_probability=draw.get("win_probability", 0.5),
        bias_applied=draw.get("bias_applied", "Rational"),
        plain_english=draw.get("plain_english", ""),
    )

    # Confidence
    craw = b.get("confidence", {})
    metrics_raw = craw.get("metrics", {})
    conf_metrics = ConfidenceMetrics(
        edge_contribution=float(metrics_raw.get("edge_contribution", 0.0)),
        stress_penalty=float(metrics_raw.get("stress_penalty", 0.0)),
        conviction_contribution=float(metrics_raw.get("conviction_contribution", 0.0)),
    )
    confidence = ConfidenceSchema(
        rational_pct=craw.get("rational_pct", 50.0),
        behavioral_pct=craw.get("behavioral_pct", 50.0),
        gap=craw.get("gap", 0.0),
        confidence_score=craw.get("confidence_score", 50.0),
        confidence_tier=craw.get("confidence_tier", "Low"),
        score_label=craw.get("score_label", "WEAK"),
        intervention_urgency=craw.get("intervention_urgency", "MODERATE"),
        is_actionable=craw.get("is_actionable", False),
        plain_english=craw.get("plain_english", ""),
        metrics=conf_metrics,
    )

    # Allocation
    araw = b.get("allocation", {})
    allocation = AllocationSchema(
        verdict=araw.get("verdict", "HOLD"),
        invest_amount=araw.get("invest_amount", 0.0),
        save_amount=araw.get("save_amount", 0.0),
        hold_amount=araw.get("hold_amount", 0.0),
        allocation_pct=araw.get("allocation_pct", 0.0),
        allocator_notes=araw.get("allocator_notes", ""),
        plain_english=araw.get("plain_english", ""),
    )

    # Score
    scraw = b.get("score", {})
    comp_raw = scraw.get("components", {})
    score = ScoreSchema(
        score=scraw.get("score", 1.0),
        decision_score=scraw.get("decision_score", 1.0),
        rating=scraw.get("rating", "Poor"),
        components=ScoreComponents(
            edge_score=float(comp_raw.get("edge_score", 0.0)),
            confidence_score=float(comp_raw.get("confidence_score", 0.0)),
            verdict_score=float(comp_raw.get("verdict_score", 0.0)),
        ),
    )

    # Explanation
    eraw = b.get("explanation", {})
    explanation = ExplanationSchema(
        summary=eraw.get("summary", ""),
        reasoning=eraw.get("reasoning", ""),
        action=eraw.get("action", ""),
        confidence_note=eraw.get("confidence_note", ""),
        bq_alert=eraw.get("bq_alert", ""),
        context_summary=eraw.get("context_summary", ""),
    )

    return BrainResponse(
        bayse=bayse,
        nlp=nlp,
        stress=stress,
        bias=bias,
        decision=decision,
        confidence=confidence,
        allocation=allocation,
        score=score,
        explanation=explanation,
    )