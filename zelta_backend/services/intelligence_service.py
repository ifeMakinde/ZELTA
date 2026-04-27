"""
ZELTA Intelligence Service

Thin orchestration layer between routes and the AI Brain.

Responsibilities:
  1. Load wallet + profile context from Firestore
  2. Call optimizer.run_brain() (HTTP -> deployed Brain)
  3. Map the normalised dict to Pydantic response models
  4. Expose lightweight helpers (stress only, bayse only, markets)
"""

import logging
from typing import Any, Dict

from google.cloud import firestore

from optimizer import run_brain, fetch_bayse_signal, fetch_stress_signal
from services.wallet_service import get_wallet_summary, get_transaction_patterns
from services.profile_service import get_profile

from schemas.intelligence import (
    BrainResponse,
    BayseSchema,
    NLPSchema,
    ScoredHeadline,
    StressSchema,
    BiasSchema,
    DecisionSchema,
    ConfidenceSchema,
    ConfidenceMetrics,
    AllocationSchema,
    ScoreSchema,
    ScoreComponents,
    ExplanationSchema,
    StressOnlyResponse,
    BayseMarketItem,
    BayseMarketsResponse,
)

logger = logging.getLogger(__name__)


def _first(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]
    return default


# ──────────────────────────────────────────────────────────────────────────────
# FULL INTELLIGENCE PIPELINE
# ──────────────────────────────────────────────────────────────────────────────

async def get_intelligence(db: firestore.Client, uid: str) -> BrainResponse:
    wallet_summary = await get_wallet_summary(db, uid)
    transaction_patterns = await get_transaction_patterns(db, uid)
    profile = await get_profile(db, uid)

    wallet_data = {
        "total_balance": wallet_summary.total_balance,
        "free_cash": wallet_summary.free_cash,
        "locked_total": wallet_summary.locked_total,
        "total_income": wallet_summary.total_income,
        "total_expenses": wallet_summary.total_expenses,
        "weekly_burn_rate": wallet_summary.weekly_burn_rate,
    }

    profile_data = {
        "risk_preference": getattr(profile.financial, "risk_preference", None),
        "capital_range": getattr(profile.financial, "capital_range", None),
        "monthly_income": getattr(profile.financial, "monthly_income", None),
        "primary_goal": getattr(profile.preferences, "primary_goal", None),
        "decision_aggressiveness": getattr(profile.preferences, "decision_aggressiveness", 50),
        "stress_sensitivity": getattr(profile.preferences, "stress_sensitivity", 60),
    }

    brain = await run_brain(
        wallet_data=wallet_data,
        profile_data=profile_data,
        transaction_patterns=transaction_patterns,
    )

    return _map_to_brain_response(brain)


# ──────────────────────────────────────────────────────────────────────────────
# LIGHTWEIGHT HELPERS
# ──────────────────────────────────────────────────────────────────────────────

async def get_stress_only(db: firestore.Client, uid: str) -> StressOnlyResponse:
    stress = await fetch_stress_signal()

    combined = float(
        _first(
            stress,
            "combined_index",
            "stress_score",
            "score",
            default=50.0,
        )
    )

    return StressOnlyResponse(
        stress_index=combined,
        level=str(_first(stress, "level", default="MODERATE")),
        label=str(_first(stress, "label", "plain_english", default="")),
        bayse_primary=float(
            _first(
                stress,
                "bayse_primary",
                default=stress.get("components", {}).get("bayse_stress", 0.0),
            )
        ),
        nlp_secondary=float(
            _first(
                stress,
                "nlp_secondary",
                default=stress.get("components", {}).get("nlp_stress", 0.0),
            )
        ),
        market_probability=float(
            _first(
                stress,
                "market_probability",
                default=stress.get("components", {}).get("market_probability", 0.5),
            )
        ),
    )


async def get_bayse_markets() -> BayseMarketsResponse:
    bayse = await fetch_bayse_signal()

    raw_stress = float(_first(bayse, "raw_crowd_stress", "score", default=50.0))

    items = [
        BayseMarketItem(
            name=str(_first(bayse, "market_title", default="Active Bayse Market")),
            probability=float(
                _first(bayse, "naira_weakness_probability", "crowd_yes_price", default=50.0)
            ),
            description="Real-money crowd probability on the active Nigerian financial market",
        ),
        BayseMarketItem(
            name="Market Spread Signal",
            probability=round(float(_first(bayse, "spread", default=0.0)) * 100, 2),
            description="Bid-ask spread as market uncertainty indicator",
        ),
        BayseMarketItem(
            name="Order Book Imbalance",
            probability=round(float(_first(bayse, "imbalance", default=0.0)) * 100, 2),
            description="Directional pressure from Bayse order book",
        ),
        BayseMarketItem(
            name="Composite Crowd Stress",
            probability=raw_stress,
            description="Composite behavioral stress signal from Bayse crowd pricing",
        ),
    ]

    return BayseMarketsResponse(
        markets=items,
        composite_stress=raw_stress,
        bayse_available=bool(_first(bayse, "available", default=True)),
        market_title=str(_first(bayse, "market_title", default="")),
        verdict=(
            "CALM"
            if raw_stress < 30
            else "MODERATE"
            if raw_stress < 60
            else "HIGH_STRESS"
            if raw_stress < 80
            else "CRISIS"
        ),
    )


# ──────────────────────────────────────────────────────────────────────────────
# MAPPER
# ──────────────────────────────────────────────────────────────────────────────

def _map_to_brain_response(b: dict) -> BrainResponse:
    braw = b.get("bayse", {})
    bayse = BayseSchema(
        score=float(_first(braw, "score", default=50.0)),
        status=str(_first(braw, "status", default="MODERATE")),
        market_title=str(_first(braw, "market_title", default="")),
        market_id=str(_first(braw, "market_id", default="")),
        crowd_yes_price=float(_first(braw, "crowd_yes_price", default=0.5)),
        crowd_no_price=float(_first(braw, "crowd_no_price", default=0.5)),
        mid_price=float(_first(braw, "mid_price", default=0.5)),
        best_bid=float(_first(braw, "best_bid", default=0.0)),
        best_ask=float(_first(braw, "best_ask", default=0.0)),
        spread=float(_first(braw, "spread", default=0.0)),
        imbalance=float(_first(braw, "imbalance", default=0.0)),
        volume24h=float(_first(braw, "volume24h", default=0.0)),
        trade_count_24h=int(_first(braw, "trade_count_24h", default=0)),
        available=bool(_first(braw, "available", default=True)),
        raw_crowd_stress=float(_first(braw, "raw_crowd_stress", default=_first(braw, "score", default=50.0))),
        naira_weakness_probability=float(
            _first(braw, "naira_weakness_probability", default=_first(braw, "crowd_yes_price", default=50.0))
        ),
        outcome=_first(braw, "outcome", default=None),
        last_price=float(_first(braw, "last_price", default=0.0)),
        source=str(_first(braw, "source", default="")),
        updated_at=_first(braw, "updated_at", default=None),
    )

    nlp_raw = b.get("nlp", {})
    headlines = [
        ScoredHeadline(**h)
        for h in nlp_raw.get("scored_headlines", [])
        if isinstance(h, dict)
    ]
    nlp = NLPSchema(
        scored_headlines=headlines,
        aggregate_sentiment=float(_first(nlp_raw, "aggregate_sentiment", default=0.0)),
    )

    sraw = b.get("stress", {})
    stress = StressSchema(
        combined_index=float(_first(sraw, "combined_index", "stress_score", "score", default=50.0)),
        level=str(_first(sraw, "level", default="MODERATE")),
        label=str(_first(sraw, "label", "plain_english", default="")),
        bayse_primary=float(
            _first(sraw, "bayse_primary", default=sraw.get("components", {}).get("bayse_stress", 0.0))
        ),
        nlp_secondary=float(
            _first(sraw, "nlp_secondary", default=sraw.get("components", {}).get("nlp_stress", 0.0))
        ),
        market_probability=float(
            _first(sraw, "market_probability", default=sraw.get("components", {}).get("market_probability", 0.5))
        ),
        bayse_weight=float(_first(sraw, "bayse_weight", default=0.6)),
        nlp_weight=float(_first(sraw, "nlp_weight", default=0.4)),
        plain_english=str(_first(sraw, "plain_english", default="")),
    )

    biraw = b.get("bias", {})
    bias = BiasSchema(
        active_bias=str(_first(biraw, "active_bias", "bias", default="Rational")),
        confidence=str(_first(biraw, "confidence", default="Low")),
        explanation=str(_first(biraw, "explanation", default="")),
        inputs=biraw.get("inputs", {}),
        bias=_first(biraw, "bias", default=None),
    )

    draw = b.get("decision", {})
    decision = DecisionSchema(
        verdict=str(_first(draw, "verdict", default="HOLD")),
        market_probability=float(_first(draw, "market_probability", default=0.5)),
        rational_probability=float(_first(draw, "rational_probability", default=0.5)),
        edge=float(_first(draw, "edge", default=0.0)),
        confidence=str(_first(draw, "confidence", default="Low")),
        win_probability=float(_first(draw, "win_probability", default=0.5)),
        bias_applied=str(_first(draw, "bias_applied", default="Rational")),
        plain_english=str(_first(draw, "plain_english", default="")),
    )

    craw = b.get("confidence", {})
    metrics_raw = craw.get("metrics", {})
    conf_metrics = ConfidenceMetrics(
        edge_contribution=float(_first(metrics_raw, "edge_contribution", default=0.0)),
        stress_penalty=float(_first(metrics_raw, "stress_penalty", default=0.0)),
        conviction_contribution=float(_first(metrics_raw, "conviction_contribution", default=0.0)),
    )
    confidence = ConfidenceSchema(
        rational_pct=float(_first(craw, "rational_pct", default=50.0)),
        behavioral_pct=float(_first(craw, "behavioral_pct", default=50.0)),
        gap=float(_first(craw, "gap", default=0.0)),
        confidence_score=float(_first(craw, "confidence_score", "confidence_score_100", default=50.0)),
        confidence_tier=str(_first(craw, "confidence_tier", "confidence_label", default="Low")),
        score_label=str(_first(craw, "score_label", default="WEAK")),
        intervention_urgency=str(_first(craw, "intervention_urgency", default="MODERATE")),
        is_actionable=bool(_first(craw, "is_actionable", default=False)),
        plain_english=str(_first(craw, "plain_english", default="")),
        metrics=conf_metrics,
    )

    araw = b.get("allocation", {})
    allocation = AllocationSchema(
        verdict=str(_first(araw, "verdict", default="HOLD")),
        invest_ngn=float(_first(araw, "invest_ngn", "invest_amount", default=0.0)),
        save_ngn=float(_first(araw, "save_ngn", "save_amount", default=0.0)),
        hold_ngn=float(_first(araw, "hold_ngn", "hold_amount", default=0.0)),
        allocation_pct=float(_first(araw, "allocation_pct", default=0.0)),
        allocator_notes=str(_first(araw, "allocator_notes", default="")),
        plain_english=str(_first(araw, "plain_english", default="")),
    )

    scraw = b.get("score", {})
    comp_raw = scraw.get("components", {})
    score = ScoreSchema(
        score=float(_first(scraw, "score", default=1.0)),
        decision_score=float(_first(scraw, "decision_score", default=1.0)),
        rating=str(_first(scraw, "rating", default="Poor")),
        components=ScoreComponents(
            edge_score=float(_first(comp_raw, "edge_score", default=0.0)),
            confidence_score=float(_first(comp_raw, "confidence_score", default=0.0)),
            verdict_score=float(_first(comp_raw, "verdict_score", default=0.0)),
        ),
    )

    eraw = b.get("explanation", {})
    explanation = ExplanationSchema(
        summary=str(_first(eraw, "summary", default="")),
        reasoning=str(_first(eraw, "reasoning", default="")),
        action=str(_first(eraw, "action", default="")),
        what_this_means_for_you=_first(eraw, "what_this_means_for_you", default=None),
        bias_explanation=_first(eraw, "bias_explanation", default=None),
        confidence_note=_first(eraw, "confidence_note", default=None),
        bq_alert=_first(eraw, "bq_alert", default=None),
        context_summary=_first(eraw, "context_summary", default=None),
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
