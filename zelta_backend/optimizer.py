"""
ZELTA Optimizer — AI Brain HTTP Client

The centralised AI Brain is already deployed at:
  https://zelta-ai-990094999937.us-central1.run.app

This module is the single point of contact between the ZELTA backend
and the AI Brain. It:
  - Calls POST /brain/intelligence with wallet_data + transactions + user_context
  - Returns the raw brain response dict
  - Exposes helper functions used by other services (stress, bayse signal)
  - Handles errors gracefully with structured fallbacks

All intelligence logic lives in the Brain service.
This module owns the HTTP transport layer only.
"""

import logging
from typing import Any, Dict, List, Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)

BRAIN_TIMEOUT = 30.0  # Brain latency can be ~19s per real response


def _brain_headers() -> dict:
    """Auth headers for the internal AI Brain service."""
    return {
        "x-api-key": settings.internal_api_key,  # must match the Brain OpenAPI
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


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _safe_dict(value: Any) -> dict:
    if isinstance(value, dict):
        return value
    return {}


def _safe_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    return []


def _extract_body(data: Any) -> dict:
    """
    Brain may return:
      - {"success": true, "data": {...}}
      - {"data": {...}}
      - {...}
    """
    if isinstance(data, dict):
        if isinstance(data.get("data"), dict):
            return data["data"]
        return data
    return {}


# ─── Main Brain Call ──────────────────────────────────────────────────────────

async def run_brain(
    wallet_data: Optional[dict] = None,
    profile_data: Optional[dict] = None,
    transaction_patterns: Optional[dict] = None,
) -> dict:
    """
    Call the deployed ZELTA AI Brain and return its response dict.

    Expected Brain contract:
      POST /brain/intelligence
      Headers:
        x-api-key: <internal key>

      Body:
      {
        "wallet_data": {...},
        "transactions": [...],
        "user_context": {...}
      }

    Returns:
        Normalised brain dict with keys:
          bayse, nlp, stress, bias, decision, confidence, allocation, score, explanation
    """
    wallet_data = wallet_data or {}
    profile_data = profile_data or {}
    transaction_patterns = transaction_patterns or {}

    free_cash = _safe_float(wallet_data.get("free_cash", 0.0), 0.0)

    # Match deployed OpenAPI schema as closely as possible
    payload = {
        "wallet_data": {
            "free_cash": _safe_float(wallet_data.get("free_cash", 0.0), 0.0),
            "locked_total": _safe_float(
                wallet_data.get("locked_total", wallet_data.get("locked_amount", 0.0)),
                0.0,
            ),
            "total_balance": _safe_float(wallet_data.get("total_balance", 0.0), 0.0),
        },
        # If caller gives a dict of derived signals, keep it under user_context too.
        # If caller gives a transactions list, pass it as-is.
        "transactions": _safe_list(transaction_patterns.get("transactions"))
        if isinstance(transaction_patterns, dict)
        else _safe_list(transaction_patterns),
        "user_context": {
            **_safe_dict(profile_data),
            **(
                _safe_dict(transaction_patterns)
                if isinstance(transaction_patterns, dict) and "transactions" not in transaction_patterns
                else {}
            ),
        },
    }

    try:
        async with httpx.AsyncClient(timeout=BRAIN_TIMEOUT) as client:
            resp = await client.post(
                f"{settings.ai_brain_url}/brain/intelligence",
                headers=_brain_headers(),
                json=payload,
            )

            # Do not silently swallow auth problems
            if resp.status_code in (401, 403):
                logger.error("Brain auth failed %s: %s", resp.status_code, resp.text)
                return normalise_brain_response(_fallback_brain_response(free_cash))

            resp.raise_for_status()
            data = resp.json()

        body = _extract_body(data)

        if isinstance(data, str):
            logger.error("Brain returned a string response: %s", data)
            return normalise_brain_response(_fallback_brain_response(free_cash))

        if isinstance(data, dict) and data.get("success") is False:
            logger.error("Brain returned success=false: %s", data)
            return normalise_brain_response(_fallback_brain_response(free_cash))

        # If the brain returns the flattened intelligence report, normalize it.
        # If it already returns nested blocks, the normalizer will preserve them.
        logger.info(
            "Brain call OK | stress=%s | verdict=%s",
            _safe_float(
                body.get("stress_index", body.get("stress", {}).get("score", 50.0)),
                50.0,
            ),
            _safe_str(
                body.get("decision_verdict", body.get("allocation", {}).get("verdict", "HOLD")),
                "HOLD",
            ),
        )
        return normalise_brain_response(body)

    except httpx.TimeoutException:
        logger.error("Brain request timed out after %ss", BRAIN_TIMEOUT)
        return normalise_brain_response(_fallback_brain_response(free_cash))
    except httpx.HTTPStatusError as e:
        logger.error("Brain HTTP %s: %s", e.response.status_code, e.response.text)
        return normalise_brain_response(_fallback_brain_response(free_cash))
    except Exception as e:
        logger.error("Brain unexpected error: %s", e)
        return normalise_brain_response(_fallback_brain_response(free_cash))


# ─── Convenience wrappers ─────────────────────────────────────────────────────

async def fetch_bayse_signal() -> dict:
    """
    Fetch Bayse signal — tries /bayse endpoint first, falls back to full brain.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{settings.ai_brain_url}/bayse",
                headers=_brain_headers(),
            )

            if resp.status_code in (401, 403):
                logger.error("Bayse auth failed %s: %s", resp.status_code, resp.text)
                return _fallback_bayse()

            resp.raise_for_status()
            data = resp.json()

            raw = data.get("data", {}).get("bayse", data.get("bayse", {}))
            return _normalise_bayse(raw)

    except Exception as e:
        logger.warning("Bayse-only fetch failed: %s", e)
        return _fallback_bayse()


async def fetch_stress_signal() -> dict:
    """
    Fetch stress index — tries /stress endpoint first, falls back to neutral.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{settings.ai_brain_url}/stress",
                headers=_brain_headers(),
            )

            if resp.status_code in (401, 403):
                logger.error("Stress auth failed %s: %s", resp.status_code, resp.text)
                return _fallback_stress()

            resp.raise_for_status()
            data = resp.json()

            raw = data.get("data", {}).get("stress", data.get("stress", {}))
            return _normalise_stress(raw)

    except Exception as e:
        logger.warning("Stress-only fetch failed: %s", e)
        return _fallback_stress()


# ─── Normalisers ──────────────────────────────────────────────────────────────

def _normalise_bayse(raw: dict) -> dict:
    """
    Map the brain's bayse block to ZELTA internal format.
    """
    raw = raw or {}
    score = _safe_float(raw.get("score", 50.0), 50.0)
    mid_price = _safe_float(raw.get("mid_price", 0.5), 0.5)

    return {
        "score": score,
        "status": _safe_str(raw.get("status", "MODERATE"), "MODERATE"),
        "market_title": _safe_str(raw.get("market_title", ""), ""),
        "market_id": _safe_str(raw.get("market_id", ""), ""),
        "crowd_yes_price": _safe_float(raw.get("crowd_yes_price", 0.5), 0.5),
        "crowd_no_price": _safe_float(raw.get("crowd_no_price", 0.5), 0.5),
        "mid_price": mid_price,
        "best_bid": _safe_float(raw.get("best_bid", 0.0), 0.0),
        "best_ask": _safe_float(raw.get("best_ask", 0.0), 0.0),
        "spread": _safe_float(raw.get("spread", 0.0), 0.0),
        "imbalance": _safe_float(raw.get("imbalance", 0.0), 0.0),
        "volume24h": _safe_float(raw.get("volume24h", 0.0), 0.0),
        "trade_count_24h": _safe_int(raw.get("trade_count_24h", 0), 0),
        "available": _safe_bool(raw.get("available", True), True),
        "raw_crowd_stress": score,
        "naira_weakness_probability": round(mid_price * 100, 2),
        "cbn_rate_fear_index": score,
        "inflation_anxiety_score": score,
        "usd_ngn_threshold_probability": round(mid_price * 100, 2),
    }


def _normalise_stress(raw: dict) -> dict:
    """
    Map brain's stress block.
    """
    raw = raw or {}
    score = _safe_float(raw.get("score", raw.get("stress_score", 50.0)), 50.0)
    components = _safe_dict(raw.get("components"))

    return {
        "combined_index": score,
        "level": _safe_str(raw.get("level", "MODERATE"), "MODERATE"),
        "label": _safe_str(raw.get("plain_english", raw.get("label", "")), ""),
        "bayse_primary": _safe_float(components.get("bayse_stress", 0.0), 0.0),
        "nlp_secondary": _safe_float(components.get("nlp_stress", 0.0), 0.0),
        "bayse_weight": _safe_float(components.get("bayse_weight", 0.6), 0.6),
        "nlp_weight": _safe_float(components.get("nlp_weight", 0.4), 0.4),
        "market_probability": _safe_float(components.get("market_probability", 0.5), 0.5),
    }


def _normalise_bias(raw: dict) -> dict:
    raw = raw or {}
    return {
        "active_bias": _safe_str(raw.get("active_bias", raw.get("bias", "Rational")), "Rational"),
        "confidence": _safe_str(raw.get("confidence", "Low"), "Low"),
        "explanation": _safe_str(raw.get("explanation", ""), ""),
        "inputs": _safe_dict(raw.get("inputs")),
    }


def _normalise_decision(raw: dict) -> dict:
    raw = raw or {}
    return {
        "verdict": _safe_str(raw.get("verdict", "HOLD"), "HOLD"),
        "market_probability": _safe_float(raw.get("market_probability", 0.5), 0.5),
        "rational_probability": _safe_float(raw.get("rational_probability", 0.5), 0.5),
        "edge": _safe_float(raw.get("edge", 0.0), 0.0),
        "confidence": _safe_str(raw.get("confidence", "Low"), "Low"),
        "win_probability": _safe_float(raw.get("win_probability", 0.5), 0.5),
        "bias_applied": _safe_str(raw.get("bias_applied", "Rational"), "Rational"),
        "plain_english": _safe_str(raw.get("plain_english", ""), ""),
    }


def _normalise_confidence(raw: dict) -> dict:
    raw = raw or {}
    return {
        "rational_pct": _safe_float(raw.get("rational_pct", 50.0), 50.0),
        "behavioral_pct": _safe_float(raw.get("behavioral_pct", 50.0), 50.0),
        "gap": _safe_float(raw.get("gap", 0.0), 0.0),
        "confidence_score": _safe_float(
            raw.get("confidence_score_100", raw.get("confidence_score", 50.0)),
            50.0,
        ),
        "confidence_tier": _safe_str(raw.get("confidence_tier", raw.get("confidence_label", "Low")), "Low"),
        "score_label": _safe_str(raw.get("score_label", "WEAK"), "WEAK"),
        "intervention_urgency": _safe_str(raw.get("intervention_urgency", "MODERATE"), "MODERATE"),
        "is_actionable": _safe_bool(raw.get("is_actionable", False), False),
        "plain_english": _safe_str(raw.get("plain_english", ""), ""),
        "metrics": _safe_dict(raw.get("metrics")),
    }


def _normalise_allocation(raw: dict) -> dict:
    raw = raw or {}
    return {
        "verdict": _safe_str(raw.get("verdict", "HOLD"), "HOLD"),
        "invest_amount": _safe_float(raw.get("invest_ngn", raw.get("invest_amount", 0.0)), 0.0),
        "save_amount": _safe_float(raw.get("save_ngn", raw.get("save_amount", 0.0)), 0.0),
        "hold_amount": _safe_float(raw.get("hold_ngn", raw.get("hold_amount", 0.0)), 0.0),
        "allocation_pct": _safe_float(raw.get("allocation_pct", 0.0), 0.0),
        "allocator_notes": _safe_str(raw.get("allocator_notes", ""), ""),
        "plain_english": _safe_str(raw.get("plain_english", ""), ""),
    }


def _normalise_score(raw: dict) -> dict:
    raw = raw or {}
    return {
        "score": _safe_float(raw.get("score", raw.get("decision_score", 1.0)), 1.0),
        "decision_score": _safe_float(raw.get("decision_score", raw.get("score", 1.0)), 1.0),
        "rating": _safe_str(raw.get("rating", "Poor"), "Poor"),
        "components": _safe_dict(raw.get("components")),
    }


def normalise_brain_response(raw_data: dict) -> dict:
    """
    Normalise the full brain response dict into ZELTA's internal structure.
    All services consume this normalised format.
    """
    raw_data = raw_data or {}

    # If the brain already returned the flat intelligence report, normalize it first.
    if any(
        key in raw_data
        for key in (
            "stress_index",
            "stress_level",
            "bayse_score",
            "bayse_market",
            "decision_verdict",
            "confidence_score",
            "allocation_plain",
            "score_rating",
        )
    ) and not any(
        key in raw_data
        for key in ("bayse", "stress", "bias", "decision", "confidence", "allocation", "score", "explanation")
    ):
        # Convert the flat report into the nested structure expected internally.
        return {
            "bayse": _normalise_bayse(
                {
                    "score": raw_data.get("bayse_score", 50.0),
                    "status": raw_data.get("bayse_status", "MODERATE"),
                    "market_title": raw_data.get("bayse_market", "Unavailable"),
                    "crowd_yes_price": raw_data.get("crowd_yes", 0.5),
                    "crowd_no_price": raw_data.get("crowd_no", 0.5),
                    "mid_price": raw_data.get("mid_price", 0.5),
                    "spread": raw_data.get("spread", 0.0),
                    "available": True,
                }
            ),
            "nlp": {
                "scored_headlines": raw_data.get("headlines", []),
                "aggregate_sentiment": raw_data.get("nlp_sentiment", 0.0),
            },
            "stress": _normalise_stress(
                {
                    "score": raw_data.get("stress_index", 50.0),
                    "level": raw_data.get("stress_level", "MODERATE"),
                    "plain_english": raw_data.get("stress_label", ""),
                    "components": {
                        "bayse_stress": raw_data.get("bayse_primary", 50.0),
                        "nlp_stress": raw_data.get("nlp_secondary", 50.0),
                        "market_probability": raw_data.get("market_probability", 0.5),
                    },
                }
            ),
            "bias": _normalise_bias(
                {
                    "active_bias": raw_data.get("active_bias", "Rational"),
                    "confidence": raw_data.get("bias_confidence", "Low"),
                    "explanation": raw_data.get("bias_explanation", ""),
                }
            ),
            "decision": _normalise_decision(
                {
                    "verdict": raw_data.get("decision_verdict", "HOLD"),
                    "market_probability": raw_data.get("market_probability", 0.5),
                    "rational_probability": raw_data.get("market_probability", 0.5),
                    "edge": raw_data.get("edge", 0.0),
                    "confidence": raw_data.get("confidence_tier", "Low"),
                    "win_probability": raw_data.get("win_probability", 0.5),
                    "bias_applied": raw_data.get("active_bias", "Rational"),
                    "plain_english": raw_data.get("decision_plain", ""),
                }
            ),
            "confidence": _normalise_confidence(
                {
                    "rational_pct": raw_data.get("rational_pct", 50.0),
                    "behavioral_pct": raw_data.get("behavioral_pct", 50.0),
                    "gap": raw_data.get("confidence_gap", 0.0),
                    "confidence_score": raw_data.get("confidence_score", 50.0),
                    "confidence_tier": raw_data.get("confidence_tier", "Low"),
                    "score_label": raw_data.get("score_label", "WEAK"),
                    "intervention_urgency": raw_data.get("intervention_urgency", "LOW"),
                    "is_actionable": raw_data.get("is_actionable", False),
                    "plain_english": raw_data.get("confidence_plain", ""),
                }
            ),
            "allocation": _normalise_allocation(
                {
                    "verdict": raw_data.get("verdict", "HOLD"),
                    "invest_amount": raw_data.get("invest_ngn", 0.0),
                    "save_amount": raw_data.get("save_ngn", 0.0),
                    "hold_amount": raw_data.get("hold_ngn", 0.0),
                    "allocation_pct": raw_data.get("allocation_pct", 0.0),
                    "plain_english": raw_data.get("allocation_plain", ""),
                }
            ),
            "score": _normalise_score(
                {
                    "score": raw_data.get("decision_score", 1.0),
                    "decision_score": raw_data.get("decision_score", 1.0),
                    "rating": raw_data.get("score_rating", "Poor"),
                }
            ),
            "explanation": _safe_dict(
                {
                    "summary": raw_data.get("summary", ""),
                    "reasoning": "",
                    "action": raw_data.get("action", ""),
                    "what_this_means_for_you": raw_data.get("what_this_means_for_you", ""),
                    "bias_explanation": raw_data.get("bias_explanation", ""),
                    "confidence_note": raw_data.get("confidence_plain", ""),
                    "bq_alert": raw_data.get("bq_alert", ""),
                    "context_summary": raw_data.get("context_summary", ""),
                }
            ),
        }

    return {
        "bayse": _normalise_bayse(raw_data.get("bayse", {})),
        "nlp": raw_data.get("nlp", {}),
        "stress": _normalise_stress(raw_data.get("stress", {})),
        "bias": _normalise_bias(raw_data.get("bias", {})),
        "decision": _normalise_decision(raw_data.get("decision", {})),
        "confidence": _normalise_confidence(raw_data.get("confidence", {})),
        "allocation": _normalise_allocation(raw_data.get("allocation", {})),
        "score": _normalise_score(raw_data.get("score", {})),
        "explanation": _safe_dict(raw_data.get("explanation", {})),
    }


# ─── Fallbacks ────────────────────────────────────────────────────────────────

def _fallback_bayse() -> dict:
    return {
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
        "raw_crowd_stress": 50.0,
        "naira_weakness_probability": 50.0,
        "cbn_rate_fear_index": 50.0,
        "inflation_anxiety_score": 50.0,
        "usd_ngn_threshold_probability": 50.0,
        "available": False,
    }


def _fallback_stress() -> dict:
    return {
        "combined_index": 50.0,
        "level": "MODERATE",
        "label": "Unable to reach AI Brain. Using neutral defaults.",
        "bayse_primary": 50.0,
        "nlp_secondary": 50.0,
        "bayse_weight": 0.6,
        "nlp_weight": 0.4,
        "market_probability": 0.5,
    }


def _fallback_brain_response(free_cash: float = 0.0) -> dict:
    """
    Safe neutral response when the AI Brain is unreachable.
    Returns HOLD on everything, moderate stress.
    """
    return {
        "bayse": {
            "score": 50.0,
            "status": "MODERATE",
            "crowd_yes_price": 0.5,
            "crowd_no_price": 0.5,
            "mid_price": 0.5,
            "spread": 0.0,
            "imbalance": 0.0,
            "volume24h": 0.0,
            "trade_count_24h": 0,
            "market_title": "Unavailable",
            "market_id": "",
        },
        "nlp": {"scored_headlines": [], "aggregate_sentiment": 0.0},
        "stress": {
            "score": 50,
            "stress_score": 50,
            "level": "MODERATE",
            "plain_english": "AI Brain temporarily unavailable. Using safe neutral defaults.",
            "components": {
                "bayse_stress": 0.5,
                "nlp_stress": 0.5,
                "market_probability": 0.5,
                "bayse_weight": 0.6,
                "nlp_weight": 0.4,
            },
            "raw": {},
        },
        "bias": {
            "bias": "Rational",
            "active_bias": "Rational",
            "confidence": "Low",
            "explanation": "AI Brain unavailable. Defaulting to rational baseline.",
            "inputs": {},
        },
        "decision": {
            "market_probability": 0.5,
            "rational_probability": 0.5,
            "edge": 0.0,
            "confidence": "Low",
            "verdict": "HOLD",
            "plain_english": "AI Brain unavailable. HOLD all positions.",
            "win_probability": 0.5,
            "bias_applied": "Rational",
            "stress_score": 50,
        },
        "confidence": {
            "rational_pct": 50,
            "behavioral_pct": 50,
            "gap": 0,
            "confidence_score_100": 50,
            "confidence_score": 50,
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
            "components": {
                "edge_score": 0.0,
                "confidence_score": 0.0,
                "verdict_score": 0.5,
            },
        },
        "explanation": {
            "summary": "AI Brain unavailable.",
            "reasoning": "Could not reach the centralised AI Brain. All positions held.",
            "action": "Hold current positions.",
            "confidence_note": "No signal available.",
            "bq_alert": "AI Brain offline. Using safe fallback.",
            "context_summary": "",
        },
    }
