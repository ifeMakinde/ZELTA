"""
ZELTA Intelligence Service

Thin orchestration layer between routes and the AI Brain.

Responsibilities:
  1. Load wallet + profile context from Firestore
  2. Call optimizer.run_brain() (HTTP -> deployed Brain)
  3. Map the normalized dict to Pydantic response models
  4. Expose lightweight helpers (stress only, bayse only, markets)

This version accepts BOTH:
  - nested brain payloads
  - flat intelligence reports
"""

import logging
from typing import Any, Dict, Optional

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


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_bool(value: Any, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _as_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _ensure_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _looks_flat_report(payload: Dict[str, Any]) -> bool:
    """
    Flat report shape:
      stress_index, bayse_score, decision_verdict, invest_ngn, etc.
    Nested shape:
      stress, bayse, decision, confidence, allocation, score, explanation
    """
    if not payload:
        return True

    nested_keys = {"bayse", "nlp", "stress", "bias", "decision", "confidence", "allocation", "score", "explanation"}
    return not any(k in payload for k in nested_keys)


def _normalize_brain_context(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert either flat intelligence output or nested brain output into one
    consistent nested structure that the rest of this service can use.
    """
    raw = raw or {}

    if not _looks_flat_report(raw):
        # Already nested; still normalize sub-objects so missing keys do not break later.
        return {
            "bayse": _ensure_dict(raw.get("bayse")),
            "nlp": _ensure_dict(raw.get("nlp")),
            "stress": _ensure_dict(raw.get("stress")),
            "bias": _ensure_dict(raw.get("bias")),
            "decision": _ensure_dict(raw.get("decision")),
            "confidence": _ensure_dict(raw.get("confidence")),
            "allocation": _ensure_dict(raw.get("allocation")),
            "score": _ensure_dict(raw.get("score")),
            "explanation": _ensure_dict(raw.get("explanation")),
        }

    # Flat report -> nested form
    stress_index = _as_float(raw.get("stress_index", 50.0), 50.0)
    stress_level = _as_str(raw.get("stress_level", "MODERATE"), "MODERATE")
    stress_label = _as_str(raw.get("stress_label", ""), "")

    bayse_score = _as_float(raw.get("bayse_score", 50.0), 50.0)
    bayse_status = _as_str(raw.get("bayse_status", "MODERATE"), "MODERATE")
    bayse_market = _as_str(raw.get("bayse_market", "Unavailable"), "Unavailable")

    crowd_yes = _as_float(raw.get("crowd_yes", 0.5), 0.5)
    crowd_no = _as_float(raw.get("crowd_no", 0.5), 0.5)
    mid_price = _as_float(raw.get("mid_price", 0.5), 0.5)
    spread = _as_float(raw.get("spread", 0.0), 0.0)

    active_bias = _as_str(raw.get("active_bias", "Rational"), "Rational")
    bias_confidence = _as_str(raw.get("bias_confidence", "Low"), "Low")
    bias_explanation = _as_str(raw.get("bias_explanation", ""), "")

    decision_verdict = _as_str(raw.get("decision_verdict", "HOLD"), "HOLD")
    decision_plain = _as_str(raw.get("decision_plain", ""), "")
    edge = _as_float(raw.get("edge", 0.0), 0.0)
    win_probability = _as_float(raw.get("win_probability", 0.5), 0.5)

    rational_pct = _as_float(raw.get("rational_pct", 50.0), 50.0)
    behavioral_pct = _as_float(raw.get("behavioral_pct", 50.0), 50.0)
    confidence_gap = _as_float(raw.get("confidence_gap", 0.0), 0.0)
    confidence_score = _as_float(raw.get("confidence_score", 50.0), 50.0)
    confidence_tier = _as_str(raw.get("confidence_tier", "Low"), "Low")
    score_label = _as_str(raw.get("score_label", "WEAK"), "WEAK")
    intervention_urgency = _as_str(raw.get("intervention_urgency", "LOW"), "LOW")
    confidence_plain = _as_str(raw.get("confidence_plain", ""), "")

    verdict = _as_str(raw.get("verdict", "HOLD"), "HOLD")
    invest_ngn = _as_float(raw.get("invest_ngn", 0.0), 0.0)
    save_ngn = _as_float(raw.get("save_ngn", 0.0), 0.0)
    hold_ngn = _as_float(raw.get("hold_ngn", 0.0), 0.0)
    allocation_pct = _as_float(raw.get("allocation_pct", 0.0), 0.0)
    allocation_plain = _as_str(raw.get("allocation_plain", ""), "")

    decision_score = _as_float(raw.get("decision_score", 1.0), 1.0)
    score_rating = _as_str(raw.get("score_rating", "Poor"), "Poor")

    summary = _as_str(raw.get("summary", ""), "")
    bq_alert = raw.get("bq_alert")
    action = _as_str(raw.get("action", ""), "")
    nlp_sentiment = _as_float(raw.get("nlp_sentiment", 0.0), 0.0)

    return {
        "bayse": {
            "score": bayse_score,
            "status": bayse_status,
            "market_title": bayse_market,
            "market_id": "",
            "crowd_yes_price": crowd_yes,
            "crowd_no_price": crowd_no,
            "mid_price": mid_price,
            "best_bid": 0.0,
            "best_ask": 0.0,
            "spread": spread,
            "imbalance": 0.0,
            "volume24h": 0.0,
            "trade_count_24h": 0,
            "available": True,
            "raw_crowd_stress": stress_index,
            "naira_weakness_probability": crowd_yes,
            "outcome": None,
            "last_price": 0.0,
            "source": "ZELTA Intelligence",
            "updated_at": None,
        },
        "nlp": {
            "scored_headlines": [],
            "aggregate_sentiment": nlp_sentiment,
        },
        "stress": {
            "combined_index": stress_index,
            "level": stress_level,
            "label": stress_label,
            "bayse_primary": _as_float(raw.get("bayse_primary", stress_index), stress_index),
            "nlp_secondary": _as_float(raw.get("nlp_secondary", 50.0), 50.0),
            "market_probability": _as_float(raw.get("market_probability", 0.5), 0.5),
            "bayse_weight": 0.6,
            "nlp_weight": 0.4,
            "plain_english": stress_label,
        },
        "bias": {
            "active_bias": active_bias,
            "confidence": bias_confidence,
            "explanation": bias_explanation,
            "inputs": {
                "stress_score": stress_index,
                "sentiment": nlp_sentiment,
                "market_probability": _as_float(raw.get("market_probability", 0.5), 0.5),
            },
            "bias": active_bias,
        },
        "decision": {
            "verdict": decision_verdict,
            "market_probability": _as_float(raw.get("market_probability", 0.5), 0.5),
            "rational_probability": _as_float(raw.get("market_probability", 0.5), 0.5),
            "edge": edge,
            "confidence": _as_str(raw.get("confidence_tier", "Low"), "Low"),
            "win_probability": win_probability,
            "bias_applied": active_bias,
            "plain_english": decision_plain,
        },
        "confidence": {
            "rational_pct": rational_pct,
            "behavioral_pct": behavioral_pct,
            "gap": confidence_gap,
            "confidence_score": confidence_score,
            "confidence_score_100": confidence_score,
            "confidence_tier": confidence_tier,
            "confidence_label": confidence_tier,
            "score_label": score_label,
            "intervention_urgency": intervention_urgency,
            "is_actionable": confidence_score >= 60 and decision_verdict in {"SAVE", "INVEST"},
            "plain_english": confidence_plain,
            "metrics": {
                "edge_contribution": 0.0,
                "stress_penalty": 0.0,
                "conviction_contribution": 0.0,
            },
        },
        "allocation": {
            "verdict": verdict,
            "invest_ngn": invest_ngn,
            "save_ngn": save_ngn,
            "hold_ngn": hold_ngn,
            "invest_amount": invest_ngn,
            "save_amount": save_ngn,
            "hold_amount": hold_ngn,
            "allocation_pct": allocation_pct,
            "allocator_notes": "",
            "plain_english": allocation_plain,
        },
        "score": {
            "score": decision_score,
            "decision_score": decision_score,
            "rating": score_rating,
            "components": {
                "edge_score": 0.0,
                "confidence_score": confidence_score / 100.0 if confidence_score > 1 else confidence_score,
                "verdict_score": 0.5,
            },
        },
        "explanation": {
            "summary": summary,
            "reasoning": _as_str(raw.get("reasoning", ""), ""),
            "action": action,
            "what_this_means_for_you": _as_str(raw.get("what_this_means_for_you", ""), ""),
            "bias_explanation": bias_explanation,
            "confidence_note": confidence_plain,
            "bq_alert": bq_alert,
            "context_summary": _as_str(raw.get("context_summary", ""), ""),
        },
    }


def _coerce_bayse_payload(bayse: Dict[str, Any]) -> BayseSchema:
    bayse = bayse or {}
    return BayseSchema(
        score=_as_float(_first(bayse, "score", default=50.0), 50.0),
        status=_as_str(_first(bayse, "status", default="MODERATE"), "MODERATE"),
        market_title=_as_str(_first(bayse, "market_title", default=""), ""),
        market_id=_as_str(_first(bayse, "market_id", default=""), ""),
        crowd_yes_price=_as_float(_first(bayse, "crowd_yes_price", default=0.5), 0.5),
        crowd_no_price=_as_float(_first(bayse, "crowd_no_price", default=0.5), 0.5),
        mid_price=_as_float(_first(bayse, "mid_price", default=0.5), 0.5),
        best_bid=_as_float(_first(bayse, "best_bid", default=0.0), 0.0),
        best_ask=_as_float(_first(bayse, "best_ask", default=0.0), 0.0),
        spread=_as_float(_first(bayse, "spread", default=0.0), 0.0),
        imbalance=_as_float(_first(bayse, "imbalance", default=0.0), 0.0),
        volume24h=_as_float(_first(bayse, "volume24h", default=0.0), 0.0),
        trade_count_24h=_as_int(_first(bayse, "trade_count_24h", default=0), 0),
        available=_as_bool(_first(bayse, "available", default=True), True),
        raw_crowd_stress=_as_float(
            _first(bayse, "raw_crowd_stress", default=_first(bayse, "score", default=50.0)),
            50.0,
        ),
        naira_weakness_probability=_as_float(
            _first(bayse, "naira_weakness_probability", default=_first(bayse, "crowd_yes_price", default=0.5)),
            0.5,
        ),
        outcome=_first(bayse, "outcome", default=None),
        last_price=_as_float(_first(bayse, "last_price", default=0.0), 0.0),
        source=_as_str(_first(bayse, "source", default=""), ""),
        updated_at=_first(bayse, "updated_at", default=None),
    )


def _coerce_nlp_payload(nlp_raw: Dict[str, Any]) -> NLPSchema:
    nlp_raw = nlp_raw or {}
    headlines = []
    for item in nlp_raw.get("scored_headlines", []):
        if isinstance(item, dict):
            headlines.append(
                ScoredHeadline(
                    source=_as_str(item.get("source", ""), ""),
                    title=_as_str(item.get("title", ""), ""),
                    url=_as_str(item.get("url", ""), ""),
                    timestamp=item.get("timestamp"),
                    sentiment=_as_int(item.get("sentiment", 0), 0),
                    confidence=_as_float(item.get("confidence", 0.0), 0.0),
                    sentiment_label=_as_str(item.get("sentiment_label", "neutral"), "neutral"),
                    is_campus_relevant=_as_bool(item.get("is_campus_relevant", False), False),
                    weight=_as_float(item.get("weight", 1.0), 1.0),
                )
            )

    return NLPSchema(
        scored_headlines=headlines,
        aggregate_sentiment=_as_float(_first(nlp_raw, "aggregate_sentiment", default=0.0), 0.0),
    )


def _coerce_stress_payload(sraw: Dict[str, Any]) -> StressSchema:
    sraw = sraw or {}
    components = _ensure_dict(sraw.get("components"))

    combined_index = _as_float(_first(sraw, "combined_index", "stress_score", "score", default=50.0), 50.0)

    return StressSchema(
        combined_index=combined_index,
        level=_as_str(_first(sraw, "level", default="MODERATE"), "MODERATE"),
        label=_as_str(_first(sraw, "label", "plain_english", default=""), ""),
        bayse_primary=_as_float(
            _first(sraw, "bayse_primary", default=components.get("bayse_stress", combined_index)),
            combined_index,
        ),
        nlp_secondary=_as_float(
            _first(sraw, "nlp_secondary", default=components.get("nlp_stress", 50.0)),
            50.0,
        ),
        market_probability=_as_float(
            _first(sraw, "market_probability", default=components.get("market_probability", 0.5)),
            0.5,
        ),
        bayse_weight=_as_float(_first(sraw, "bayse_weight", default=0.6), 0.6),
        nlp_weight=_as_float(_first(sraw, "nlp_weight", default=0.4), 0.4),
        plain_english=_as_str(_first(sraw, "plain_english", default=""), ""),
    )


def _coerce_bias_payload(biraw: Dict[str, Any]) -> BiasSchema:
    biraw = biraw or {}
    return BiasSchema(
        active_bias=_as_str(_first(biraw, "active_bias", "bias", default="Rational"), "Rational"),
        confidence=_as_str(_first(biraw, "confidence", default="Low"), "Low"),
        explanation=_as_str(_first(biraw, "explanation", default=""), ""),
        inputs=_ensure_dict(biraw.get("inputs")),
        bias=_first(biraw, "bias", default=None),
    )


def _coerce_decision_payload(draw: Dict[str, Any]) -> DecisionSchema:
    draw = draw or {}
    return DecisionSchema(
        verdict=_as_str(_first(draw, "verdict", default="HOLD"), "HOLD"),
        market_probability=_as_float(_first(draw, "market_probability", default=0.5), 0.5),
        rational_probability=_as_float(_first(draw, "rational_probability", default=0.5), 0.5),
        edge=_as_float(_first(draw, "edge", default=0.0), 0.0),
        confidence=_as_str(_first(draw, "confidence", default="Low"), "Low"),
        win_probability=_as_float(_first(draw, "win_probability", default=0.5), 0.5),
        bias_applied=_as_str(_first(draw, "bias_applied", default="Rational"), "Rational"),
        plain_english=_as_str(_first(draw, "plain_english", default=""), ""),
    )


def _coerce_confidence_payload(craw: Dict[str, Any]) -> ConfidenceSchema:
    craw = craw or {}
    metrics_raw = _ensure_dict(craw.get("metrics"))

    confidence_score = _as_float(
        _first(craw, "confidence_score", "confidence_score_100", default=50.0),
        50.0,
    )
    confidence_tier = _as_str(_first(craw, "confidence_tier", "confidence_label", default="Low"), "Low")

    return ConfidenceSchema(
        rational_pct=_as_float(_first(craw, "rational_pct", default=50.0), 50.0),
        behavioral_pct=_as_float(_first(craw, "behavioral_pct", default=50.0), 50.0),
        gap=_as_float(_first(craw, "gap", default=0.0), 0.0),
        confidence_score=confidence_score,
        confidence_tier=confidence_tier,
        score_label=_as_str(_first(craw, "score_label", default="WEAK"), "WEAK"),
        intervention_urgency=_as_str(_first(craw, "intervention_urgency", default="LOW"), "LOW"),
        is_actionable=_as_bool(_first(craw, "is_actionable", default=False), False),
        plain_english=_as_str(_first(craw, "plain_english", default=""), ""),
        metrics=ConfidenceMetrics(
            edge_contribution=_as_float(_first(metrics_raw, "edge_contribution", default=0.0), 0.0),
            stress_penalty=_as_float(_first(metrics_raw, "stress_penalty", default=0.0), 0.0),
            conviction_contribution=_as_float(
                _first(metrics_raw, "conviction_contribution", default=0.0),
                0.0,
            ),
        ),
    )


def _coerce_allocation_payload(araw: Dict[str, Any]) -> AllocationSchema:
    araw = araw or {}
    invest = _as_float(_first(araw, "invest_ngn", "invest_amount", default=0.0), 0.0)
    save = _as_float(_first(araw, "save_ngn", "save_amount", default=0.0), 0.0)
    hold = _as_float(_first(araw, "hold_ngn", "hold_amount", default=0.0), 0.0)

    return AllocationSchema(
        verdict=_as_str(_first(araw, "verdict", default="HOLD"), "HOLD"),
        invest_ngn=invest,
        save_ngn=save,
        hold_ngn=hold,
        allocation_pct=_as_float(_first(araw, "allocation_pct", default=0.0), 0.0),
        allocator_notes=_as_str(_first(araw, "allocator_notes", default=""), ""),
        plain_english=_as_str(_first(araw, "plain_english", default=""), ""),
    )


def _coerce_score_payload(scraw: Dict[str, Any]) -> ScoreSchema:
    scraw = scraw or {}
    comp_raw = _ensure_dict(scraw.get("components"))
    return ScoreSchema(
        score=_as_float(_first(scraw, "score", default=1.0), 1.0),
        decision_score=_as_float(_first(scraw, "decision_score", default=1.0), 1.0),
        rating=_as_str(_first(scraw, "rating", default="Poor"), "Poor"),
        components=ScoreComponents(
            edge_score=_as_float(_first(comp_raw, "edge_score", default=0.0), 0.0),
            confidence_score=_as_float(_first(comp_raw, "confidence_score", default=0.0), 0.0),
            verdict_score=_as_float(_first(comp_raw, "verdict_score", default=0.0), 0.0),
        ),
    )


def _coerce_explanation_payload(eraw: Dict[str, Any]) -> ExplanationSchema:
    eraw = eraw or {}
    return ExplanationSchema(
        summary=_as_str(_first(eraw, "summary", default=""), ""),
        reasoning=_as_str(_first(eraw, "reasoning", default=""), ""),
        action=_as_str(_first(eraw, "action", default=""), ""),
        what_this_means_for_you=_first(eraw, "what_this_means_for_you", default=None),
        bias_explanation=_first(eraw, "bias_explanation", default=None),
        confidence_note=_first(eraw, "confidence_note", default=None),
        bq_alert=_first(eraw, "bq_alert", default=None),
        context_summary=_first(eraw, "context_summary", default=None),
    )


# ──────────────────────────────────────────────────────────────────────────────
# FULL INTELLIGENCE PIPELINE
# ──────────────────────────────────────────────────────────────────────────────

async def get_intelligence(db: firestore.Client, uid: str) -> BrainResponse:
    """
    Return a fully normalized BrainResponse.

    This uses:
      - wallet summary
      - transaction patterns
      - user profile
      - deployed brain output if available

    If the deployed brain returns a flat report, it is normalized.
    If the deployed brain returns a nested payload, it is preserved.
    """
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

    try:
        brain = await run_brain(
            wallet_data=wallet_data,
            profile_data=profile_data,
            transaction_patterns=transaction_patterns,
        )
    except Exception as e:
        logger.exception("run_brain failed for uid=%s: %s", uid, e)
        brain = _build_fallback_brain(wallet_summary=wallet_summary, profile=profile)

    normalized = _normalize_brain_context(brain)
    return _map_to_brain_response(normalized, wallet_summary=wallet_summary)


def _build_fallback_brain(wallet_summary, profile) -> Dict[str, Any]:
    """
    Safe fallback derived from real wallet state instead of generic neutral defaults.
    """
    free_cash = float(getattr(wallet_summary, "free_cash", 0.0) or 0.0)
    locked_total = float(getattr(wallet_summary, "locked_total", 0.0) or 0.0)
    total_balance = float(getattr(wallet_summary, "total_balance", 0.0) or 0.0)

    hold_amount = max(0.0, free_cash)

    return _normalize_brain_context(
        {
            "stress_index": 50.0,
            "stress_level": "MODERATE",
            "stress_label": "AI Brain temporarily unavailable. Using safe neutral defaults.",
            "bayse_primary": 50.0,
            "nlp_secondary": 50.0,
            "market_probability": 0.5,
            "bayse_score": 50.0,
            "bayse_status": "MODERATE",
            "bayse_market": "Unavailable",
            "crowd_yes": 0.5,
            "crowd_no": 0.5,
            "mid_price": 0.5,
            "spread": 0.0,
            "active_bias": "Rational",
            "bias_confidence": "Low",
            "bias_explanation": "AI Brain unavailable. Defaulting to rational baseline.",
            "decision_verdict": "HOLD",
            "edge": 0.0,
            "win_probability": 0.5,
            "decision_plain": "AI Brain unavailable. HOLD all positions.",
            "rational_pct": 50.0,
            "behavioral_pct": 50.0,
            "confidence_gap": 0.0,
            "confidence_score": 50.0,
            "confidence_tier": "Low",
            "score_label": "WEAK",
            "is_actionable": False,
            "intervention_urgency": "LOW",
            "confidence_plain": "Signal unavailable. No action recommended.",
            "verdict": "HOLD",
            "invest_ngn": 0.0,
            "save_ngn": 0.0,
            "hold_ngn": hold_amount,
            "allocation_pct": 0.0,
            "allocation_plain": f"Hold ₦{hold_amount:,.0f}. AI Brain temporarily offline.",
            "decision_score": 1.0,
            "score_rating": "Poor",
            "summary": "AI Brain unavailable.",
            "bq_alert": "AI Brain offline. Using safe fallback.",
            "action": "Hold current positions.",
            "nlp_sentiment": 0.0,
            "wallet_snapshot": {
                "free_cash": free_cash,
                "locked_total": locked_total,
                "total_balance": total_balance,
            },
            "user_context": {
                "risk_preference": getattr(profile.financial, "risk_preference", None),
                "primary_goal": getattr(profile.preferences, "primary_goal", None),
            },
        }
    )


# ──────────────────────────────────────────────────────────────────────────────
# LIGHTWEIGHT HELPERS
# ──────────────────────────────────────────────────────────────────────────────

async def get_stress_only(db: firestore.Client, uid: str) -> StressOnlyResponse:
    """
    Return stress index only. Uses the deployed signal if available.
    """
    stress = await fetch_stress_signal()
    stress = stress or {}

    combined = _as_float(
        _first(stress, "combined_index", "stress_score", "score", default=50.0),
        50.0,
    )

    components = _ensure_dict(stress.get("components"))

    return StressOnlyResponse(
        stress_index=combined,
        level=_as_str(_first(stress, "level", default="MODERATE"), "MODERATE"),
        label=_as_str(
            _first(stress, "label", "plain_english", default=""),
            "",
        ),
        bayse_primary=_as_float(
            _first(stress, "bayse_primary", default=components.get("bayse_stress", combined)),
            combined,
        ),
        nlp_secondary=_as_float(
            _first(stress, "nlp_secondary", default=components.get("nlp_stress", 50.0)),
            50.0,
        ),
        market_probability=_as_float(
            _first(stress, "market_probability", default=components.get("market_probability", 0.5)),
            0.5,
        ),
    )


async def get_bayse_markets() -> BayseMarketsResponse:
    """
    Return live Bayse market data for the UI markets screen.
    """
    bayse = await fetch_bayse_signal()
    bayse = bayse or {}

    raw_stress = _as_float(_first(bayse, "raw_crowd_stress", "score", default=50.0), 50.0)
    yes_price = _as_float(_first(bayse, "crowd_yes_price", default=0.5), 0.5)

    items = [
        BayseMarketItem(
            name=_as_str(_first(bayse, "market_title", default="Active Bayse Market"), "Active Bayse Market"),
            probability=yes_price,
            description="Real-money crowd probability on the active Nigerian financial market",
        ),
        BayseMarketItem(
            name="Market Spread Signal",
            probability=round(_as_float(_first(bayse, "spread", default=0.0), 0.0) * 100, 2),
            description="Bid-ask spread as market uncertainty indicator",
        ),
        BayseMarketItem(
            name="Order Book Imbalance",
            probability=round(_as_float(_first(bayse, "imbalance", default=0.0), 0.0) * 100, 2),
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
        bayse_available=_as_bool(_first(bayse, "available", default=True), True),
        market_title=_as_str(_first(bayse, "market_title", default=""), ""),
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

def _map_to_brain_response(b: dict, wallet_summary=None) -> BrainResponse:
    """
    Map the normalized brain dict to the typed BrainResponse Pydantic model.
    Works for both:
      - real nested brain output
      - flat intelligence report normalized by _normalize_brain_context
    """
    b = b or {}

    bayse = _coerce_bayse_payload(_ensure_dict(b.get("bayse")))
    nlp = _coerce_nlp_payload(_ensure_dict(b.get("nlp")))
    stress = _coerce_stress_payload(_ensure_dict(b.get("stress")))
    bias = _coerce_bias_payload(_ensure_dict(b.get("bias")))
    decision = _coerce_decision_payload(_ensure_dict(b.get("decision")))
    confidence = _coerce_confidence_payload(_ensure_dict(b.get("confidence")))
    allocation = _coerce_allocation_payload(_ensure_dict(b.get("allocation")))
    score = _coerce_score_payload(_ensure_dict(b.get("score")))
    explanation = _coerce_explanation_payload(_ensure_dict(b.get("explanation")))

    # Improve allocation fallback from actual wallet when available
    if wallet_summary is not None:
        free_cash = _as_float(getattr(wallet_summary, "free_cash", 0.0), 0.0)
        locked_total = _as_float(getattr(wallet_summary, "locked_total", 0.0), 0.0)
        total_balance = _as_float(getattr(wallet_summary, "total_balance", 0.0), 0.0)

        if allocation.hold_ngn <= 0 and allocation.verdict == "HOLD":
            allocation.hold_ngn = free_cash if free_cash > 0 else max(0.0, total_balance - locked_total)

        if not explanation.action:
            explanation.action = "Hold current positions." if allocation.verdict == "HOLD" else explanation.action

        if not explanation.context_summary:
            explanation.context_summary = (
                f"MPC Decision: {bayse.crowd_yes_price * 100:.0f}% YES | "
                f"Market {bayse.status.lower()} | {allocation.verdict} recommended"
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
