import json
import logging
from typing import Any, Dict, Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)

BRAIN_TIMEOUT = 30.0


def _brain_headers() -> dict:
    return {
        "x-api-key": settings.internal_api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list:
    return value if isinstance(value, list) else []


def _extract_payload(data: Any) -> dict:
    if isinstance(data, dict):
        if isinstance(data.get("data"), dict):
            return data["data"]
        return data
    return {}


async def run_brain(
    wallet_data: Optional[dict] = None,
    profile_data: Optional[dict] = None,
    transaction_patterns: Optional[dict] = None,
) -> dict:
    wallet_data = wallet_data or {}
    profile_data = profile_data or {}
    transaction_patterns = transaction_patterns or {}

    payload = {
        "wallet_data": {
            "free_cash": _safe_float(wallet_data.get("free_cash", 0.0)),
            "locked_total": _safe_float(wallet_data.get("locked_total", wallet_data.get("locked_amount", 0.0))),
            "total_balance": _safe_float(wallet_data.get("total_balance", 0.0)),
        },
        "transactions": _safe_list(transaction_patterns.get("transactions")),
        "user_context": _safe_dict(profile_data),
    }

    try:
        async with httpx.AsyncClient(timeout=BRAIN_TIMEOUT) as client:
            resp = await client.post(
                f"{settings.ai_brain_url}/brain/intelligence",
                headers=_brain_headers(),
                json=payload,
            )

        logger.info("Brain status=%s body=%s", resp.status_code, resp.text)

        if resp.status_code in (401, 403, 422, 404):
            raise RuntimeError(f"Brain rejected request: {resp.status_code} {resp.text}")

        resp.raise_for_status()

        try:
            data = resp.json()
        except json.JSONDecodeError:
            logger.error("Brain returned non-JSON response: %s", resp.text)
            return _fallback_brain_response(payload["wallet_data"]["free_cash"])

        if isinstance(data, str):
            logger.error("Brain returned string response: %s", data)
            return _fallback_brain_response(payload["wallet_data"]["free_cash"])

        return normalise_brain_response(data.get("data", data))

    except Exception as e:
        logger.error("Brain call failed: %s", e)
        return normalise_brain_response(_fallback_brain_response(payload["wallet_data"]["free_cash"]))


def normalise_brain_response(raw_data: dict) -> dict:
    raw_data = raw_data or {}

    # If the Brain returns already-normalized nested data, keep it.
    if any(k in raw_data for k in ("bayse", "stress", "bias", "decision", "confidence", "allocation", "score", "explanation")):
        return {
            "bayse": raw_data.get("bayse", {}),
            "nlp": raw_data.get("nlp", {}),
            "stress": raw_data.get("stress", {}),
            "bias": raw_data.get("bias", {}),
            "decision": raw_data.get("decision", {}),
            "confidence": raw_data.get("confidence", {}),
            "allocation": raw_data.get("allocation", {}),
            "score": raw_data.get("score", {}),
            "explanation": raw_data.get("explanation", {}),
        }

    # Otherwise map your flat intelligence response into the nested structure.
    stress_index = _safe_float(raw_data.get("stress_index", 50.0), 50.0)
    bayse_score = _safe_float(raw_data.get("bayse_score", 50.0), 50.0)
    market_probability = _safe_float(raw_data.get("market_probability", 0.5), 0.5)

    return {
        "bayse": {
            "score": bayse_score,
            "status": raw_data.get("bayse_status", "MODERATE"),
            "market_title": raw_data.get("bayse_market", "Unavailable"),
            "market_id": "",
            "crowd_yes_price": _safe_float(raw_data.get("crowd_yes", 0.5), 0.5),
            "crowd_no_price": _safe_float(raw_data.get("crowd_no", 0.5), 0.5),
            "mid_price": _safe_float(raw_data.get("mid_price", 0.5), 0.5),
            "best_bid": 0.0,
            "best_ask": 0.0,
            "spread": _safe_float(raw_data.get("spread", 0.0), 0.0),
            "imbalance": 0.0,
            "volume24h": 0.0,
            "trade_count_24h": 0,
            "available": True,
            "raw_crowd_stress": stress_index,
            "naira_weakness_probability": _safe_float(raw_data.get("crowd_yes", 0.5), 0.5),
        },
        "nlp": {
            "scored_headlines": raw_data.get("headlines", []),
            "aggregate_sentiment": _safe_float(raw_data.get("nlp_sentiment", 0.0), 0.0),
        },
        "stress": {
            "combined_index": stress_index,
            "level": raw_data.get("stress_level", "MODERATE"),
            "label": raw_data.get("stress_label", ""),
            "bayse_primary": _safe_float(raw_data.get("bayse_primary", stress_index), stress_index),
            "nlp_secondary": _safe_float(raw_data.get("nlp_secondary", 50.0), 50.0),
            "market_probability": market_probability,
            "bayse_weight": 0.6,
            "nlp_weight": 0.4,
        },
        "bias": {
            "active_bias": raw_data.get("active_bias", "Rational"),
            "confidence": raw_data.get("bias_confidence", "Low"),
            "explanation": raw_data.get("bias_explanation", ""),
            "inputs": {
                "stress_score": stress_index,
                "sentiment": _safe_float(raw_data.get("nlp_sentiment", 0.0), 0.0),
                "market_probability": market_probability,
            },
        },
        "decision": {
            "verdict": raw_data.get("decision_verdict", "HOLD"),
            "market_probability": market_probability,
            "rational_probability": market_probability,
            "edge": _safe_float(raw_data.get("edge", 0.0), 0.0),
            "confidence": raw_data.get("confidence_tier", "Low"),
            "win_probability": _safe_float(raw_data.get("win_probability", 0.5), 0.5),
            "bias_applied": raw_data.get("active_bias", "Rational"),
            "plain_english": raw_data.get("decision_plain", ""),
        },
        "confidence": {
            "rational_pct": _safe_float(raw_data.get("rational_pct", 50.0), 50.0),
            "behavioral_pct": _safe_float(raw_data.get("behavioral_pct", 50.0), 50.0),
            "gap": _safe_float(raw_data.get("confidence_gap", 0.0), 0.0),
            "confidence_score": _safe_float(raw_data.get("confidence_score", 50.0), 50.0),
            "confidence_tier": raw_data.get("confidence_tier", "Low"),
            "score_label": raw_data.get("score_label", "WEAK"),
            "intervention_urgency": raw_data.get("intervention_urgency", "LOW"),
            "is_actionable": _safe_float(raw_data.get("confidence_score", 50.0), 50.0) >= 60,
            "plain_english": raw_data.get("confidence_plain", ""),
            "metrics": {},
        },
        "allocation": {
            "verdict": raw_data.get("verdict", "HOLD"),
            "invest_ngn": _safe_float(raw_data.get("invest_ngn", 0.0), 0.0),
            "save_ngn": _safe_float(raw_data.get("save_ngn", 0.0), 0.0),
            "hold_ngn": _safe_float(raw_data.get("hold_ngn", 0.0), 0.0),
            "allocation_pct": _safe_float(raw_data.get("allocation_pct", 0.0), 0.0),
            "allocator_notes": "",
            "plain_english": raw_data.get("allocation_plain", ""),
        },
        "score": {
            "score": _safe_float(raw_data.get("decision_score", 1.0), 1.0),
            "decision_score": _safe_float(raw_data.get("decision_score", 1.0), 1.0),
            "rating": raw_data.get("score_rating", "Poor"),
            "components": {},
        },
        "explanation": {
            "summary": raw_data.get("summary", ""),
            "reasoning": raw_data.get("reasoning", ""),
            "action": raw_data.get("action", ""),
            "what_this_means_for_you": raw_data.get("what_this_means_for_you", ""),
            "bias_explanation": raw_data.get("bias_explanation", ""),
            "confidence_note": raw_data.get("confidence_plain", ""),
            "bq_alert": raw_data.get("bq_alert", ""),
            "context_summary": raw_data.get("context_summary", ""),
        },
    }


def _fallback_brain_response(free_cash: float = 0.0) -> dict:
    return {
        "bayse": {
            "score": 50.0,
            "status": "MODERATE",
            "market_title": "Unavailable",
            "market_id": "",
            "crowd_yes_price": 0.5,
            "crowd_no_price": 0.5,
            "mid_price": 0.5,
            "best_bid": 0.0,
            "best_ask": 0.0,
            "spread": 0.0,
            "imbalance": 0.0,
            "volume24h": 0.0,
            "trade_count_24h": 0,
            "available": False,
            "raw_crowd_stress": 50.0,
            "naira_weakness_probability": 50.0,
        },
        "nlp": {"scored_headlines": [], "aggregate_sentiment": 0.0},
        "stress": {
            "combined_index": 50.0,
            "level": "MODERATE",
            "label": "AI Brain temporarily unavailable. Using safe neutral defaults.",
            "bayse_primary": 50.0,
            "nlp_secondary": 50.0,
            "market_probability": 0.5,
            "bayse_weight": 0.6,
            "nlp_weight": 0.4,
        },
        "bias": {
            "active_bias": "Rational",
            "confidence": "Low",
            "explanation": "AI Brain unavailable. Defaulting to rational baseline.",
            "inputs": {},
        },
        "decision": {
            "verdict": "HOLD",
            "market_probability": 0.5,
            "rational_probability": 0.5,
            "edge": 0.0,
            "confidence": "Low",
            "win_probability": 0.5,
            "bias_applied": "Rational",
            "plain_english": "AI Brain unavailable. HOLD all positions.",
        },
        "confidence": {
            "rational_pct": 50.0,
            "behavioral_pct": 50.0,
            "gap": 0.0,
            "confidence_score": 50.0,
            "confidence_tier": "Low",
            "score_label": "WEAK",
            "intervention_urgency": "LOW",
            "is_actionable": False,
            "plain_english": "Signal unavailable. No action recommended.",
            "metrics": {},
        },
        "allocation": {
            "verdict": "HOLD",
            "invest_ngn": 0.0,
            "save_ngn": 0.0,
            "hold_ngn": free_cash,
            "allocation_pct": 0.0,
            "allocator_notes": "AI Brain unavailable. Capital protected.",
            "plain_english": f"Hold ₦{free_cash:,.0f}. AI Brain temporarily offline.",
        },
        "score": {
            "score": 1.0,
            "decision_score": 1.0,
            "rating": "Poor",
            "components": {},
        },
        "explanation": {
            "summary": "AI Brain unavailable.",
            "reasoning": "",
            "action": "Hold current positions.",
            "what_this_means_for_you": "",
            "bias_explanation": "AI Brain unavailable. Defaulting to rational baseline.",
            "confidence_note": "Signal unavailable. No action recommended.",
            "bq_alert": "AI Brain offline. Using safe fallback.",
            "context_summary": "MPC Decision: 50% YES | Market moderate | HOLD recommended",
        },
    }
