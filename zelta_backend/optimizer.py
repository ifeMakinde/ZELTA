"""
ZELTA Optimizer — AI Brain HTTP Client

The centralised AI Brain is already deployed at:
  https://zelta-ai-990094999937.us-central1.run.app

This module is the single point of contact between the ZELTA backend
and the AI Brain. It:
  - Calls POST /brain with wallet + free_cash context
  - Returns the raw brain response dict
  - Exposes helper functions used by other services (stress, bayse signal)
  - Handles errors gracefully with structured fallbacks

All intelligence logic lives in the Brain service.
This module owns the HTTP transport layer only.
"""

import httpx
import logging
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)

BRAIN_TIMEOUT = 30.0  # Brain latency can be ~19s per real response


def _brain_headers() -> dict:
    """Auth headers for the internal AI Brain service."""
    return {
        "X-API-Key": settings.internal_api_key,
        "Content-Type": "application/json",
    }


# ─── Main Brain Call ──────────────────────────────────────────────────────────

async def run_brain(
    wallet_data: Optional[dict] = None,
    profile_data: Optional[dict] = None,
    transaction_patterns: Optional[dict] = None,
) -> dict:
    """
    Call the deployed ZELTA AI Brain and return its normalised response dict.

    The brain runs the complete pipeline:
      Bayse API -> NLP Stress -> Bias Detector -> Bayesian Engine -> Kelly Allocator

    Args:
        wallet_data:          Current wallet state. Must include `free_cash` (NGN float).
        profile_data:         User profile context (risk_tolerance, obligations, etc.)
        transaction_patterns: Derived spending pattern signals.

    Returns:
        Normalised brain dict with keys:
          bayse, nlp, stress, bias, decision, confidence, allocation, score, explanation
    """
    wallet_data = wallet_data or {}
    profile_data = profile_data or {}

    free_cash = wallet_data.get("free_cash", 0.0)

    payload = {
        "free_cash": free_cash,
        "wallet": wallet_data,
        "profile": profile_data,
        "transaction_patterns": transaction_patterns or {},
    }

    try:
        async with httpx.AsyncClient(timeout=BRAIN_TIMEOUT) as client:
            resp = await client.post(
                f"{settings.ai_brain_url}/brain",
                headers=_brain_headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        if not data.get("success"):
            logger.error("Brain returned success=false: %s", data)
            return normalise_brain_response(_fallback_brain_response(free_cash))

        logger.info(
            "Brain call OK | latency=%.2fs | stress=%s | verdict=%s",
            data.get("latency_sec", 0),
            data["data"]["stress"]["score"],
            data["data"]["allocation"]["verdict"],
        )
        return normalise_brain_response(data["data"])

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
    Fetch Bayse signal — tries /bayse endpoint first, falls back to full /brain.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{settings.ai_brain_url}/bayse",
                headers=_brain_headers(),
            )
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

    Brain fields:
      score, status, crowd_yes_price, crowd_no_price, spread, imbalance,
      market_title, market_id, outcome, mid_price, best_bid, best_ask,
      last_price, volume24h, trade_count_24h, source, updated_at
    """
    score = float(raw.get("score", 50.0))
    mid_price = float(raw.get("mid_price", 0.5))
    return {
        "score": score,
        "status": raw.get("status", "MODERATE"),
        "market_title": raw.get("market_title", ""),
        "market_id": raw.get("market_id", ""),
        "crowd_yes_price": float(raw.get("crowd_yes_price", 0.5)),
        "crowd_no_price": float(raw.get("crowd_no_price", 0.5)),
        "mid_price": mid_price,
        "best_bid": float(raw.get("best_bid", 0.0)),
        "best_ask": float(raw.get("best_ask", 0.0)),
        "spread": float(raw.get("spread", 0.0)),
        "imbalance": float(raw.get("imbalance", 0.0)),
        "volume24h": float(raw.get("volume24h", 0.0)),
        "trade_count_24h": int(raw.get("trade_count_24h", 0)),
        # Aliased for backward-compat with other services
        "raw_crowd_stress": score,
        "naira_weakness_probability": round(mid_price * 100, 2),
        "cbn_rate_fear_index": score,
        "inflation_anxiety_score": score,
        "usd_ngn_threshold_probability": round(mid_price * 100, 2),
        "available": True,
    }


def _normalise_stress(raw: dict) -> dict:
    """
    Map brain's stress block.

    Brain fields:
      score, stress_score, level, plain_english, components{bayse_stress,
      nlp_stress, market_probability, bayse_weight, nlp_weight}, raw
    """
    score = float(raw.get("score", raw.get("stress_score", 50.0)))
    components = raw.get("components", {})
    return {
        "combined_index": score,
        "level": raw.get("level", "MODERATE"),
        "label": raw.get("plain_english", ""),
        "bayse_primary": round(float(components.get("bayse_stress", 0.0)) * 100, 2),
        "nlp_secondary": round(float(components.get("nlp_stress", 0.0)) * 100, 2),
        "bayse_weight": float(components.get("bayse_weight", 0.6)),
        "nlp_weight": float(components.get("nlp_weight", 0.4)),
        "market_probability": float(components.get("market_probability", 0.5)),
    }


def _normalise_bias(raw: dict) -> dict:
    """
    Map brain's bias block.

    Brain fields: bias, active_bias, confidence, explanation, inputs
    """
    return {
        "active_bias": raw.get("active_bias", raw.get("bias", "Rational")),
        "confidence": raw.get("confidence", "Low"),
        "explanation": raw.get("explanation", ""),
        "inputs": raw.get("inputs", {}),
    }


def _normalise_decision(raw: dict) -> dict:
    """
    Map brain's decision block.

    Brain fields:
      market_probability, rational_probability, edge, confidence,
      verdict, plain_english, win_probability, bias_applied, stress_score
    """
    return {
        "verdict": raw.get("verdict", "HOLD"),
        "market_probability": float(raw.get("market_probability", 0.5)),
        "rational_probability": float(raw.get("rational_probability", 0.5)),
        "edge": float(raw.get("edge", 0.0)),
        "confidence": raw.get("confidence", "Low"),
        "win_probability": float(raw.get("win_probability", 0.5)),
        "bias_applied": raw.get("bias_applied", "Rational"),
        "plain_english": raw.get("plain_english", ""),
    }


def _normalise_confidence(raw: dict) -> dict:
    """
    Map brain's confidence block.

    Brain fields:
      rational_pct, behavioral_pct, gap, confidence_score_100,
      confidence_tier, score_label, intervention_urgency, is_actionable,
      plain_english, metrics
    """
    return {
        "rational_pct": float(raw.get("rational_pct", 50.0)),
        "behavioral_pct": float(raw.get("behavioral_pct", 50.0)),
        "gap": float(raw.get("gap", 0.0)),
        "confidence_score": float(
            raw.get("confidence_score_100", raw.get("confidence_score", 50.0))
        ),
        "confidence_tier": raw.get("confidence_tier", "Low"),
        "score_label": raw.get("score_label", "WEAK"),
        "intervention_urgency": raw.get("intervention_urgency", "MODERATE"),
        "is_actionable": bool(raw.get("is_actionable", False)),
        "plain_english": raw.get("plain_english", ""),
        "metrics": raw.get("metrics", {}),
    }


def _normalise_allocation(raw: dict) -> dict:
    """
    Map brain's allocation block.

    Brain fields:
      verdict, invest_ngn, save_ngn, hold_ngn,
      allocation_pct, allocator_notes, plain_english
    """
    return {
        "verdict": raw.get("verdict", "HOLD"),
        "invest_amount": float(raw.get("invest_ngn", 0.0)),
        "save_amount": float(raw.get("save_ngn", 0.0)),
        "hold_amount": float(raw.get("hold_ngn", 0.0)),
        "allocation_pct": float(raw.get("allocation_pct", 0.0)),
        "allocator_notes": raw.get("allocator_notes", ""),
        "plain_english": raw.get("plain_english", ""),
    }


def _normalise_score(raw: dict) -> dict:
    """
    Map brain's score block.

    Brain fields: score, decision_score, rating, components
    """
    return {
        "score": float(raw.get("score", raw.get("decision_score", 1.0))),
        "decision_score": float(raw.get("decision_score", raw.get("score", 1.0))),
        "rating": raw.get("rating", "Poor"),
        "components": raw.get("components", {}),
    }


def normalise_brain_response(raw_data: dict) -> dict:
    """
    Normalise the full brain response dict into ZELTA's internal structure.
    All services consume this normalised format.
    """
    return {
        "bayse":       _normalise_bayse(raw_data.get("bayse", {})),
        "nlp":         raw_data.get("nlp", {}),
        "stress":      _normalise_stress(raw_data.get("stress", {})),
        "bias":        _normalise_bias(raw_data.get("bias", {})),
        "decision":    _normalise_decision(raw_data.get("decision", {})),
        "confidence":  _normalise_confidence(raw_data.get("confidence", {})),
        "allocation":  _normalise_allocation(raw_data.get("allocation", {})),
        "score":       _normalise_score(raw_data.get("score", {})),
        "explanation": raw_data.get("explanation", {}),
    }


# ─── Fallbacks ────────────────────────────────────────────────────────────────

def _fallback_bayse() -> dict:
    return {
        "score": 50.0, "status": "MODERATE",
        "market_title": "Unavailable", "market_id": "",
        "crowd_yes_price": 0.5, "crowd_no_price": 0.5,
        "mid_price": 0.5, "best_bid": 0.0, "best_ask": 0.0,
        "spread": 0.0, "imbalance": 0.0, "volume24h": 0.0,
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
        "combined_index": 50.0, "level": "MODERATE",
        "label": "Unable to reach AI Brain. Using neutral defaults.",
        "bayse_primary": 50.0, "nlp_secondary": 50.0,
        "bayse_weight": 0.6, "nlp_weight": 0.4,
        "market_probability": 0.5,
    }


def _fallback_brain_response(free_cash: float = 0.0) -> dict:
    """
    Safe neutral response when the AI Brain is unreachable.
    Returns HOLD on everything, moderate stress.
    """
    return {
        "bayse": {
            "score": 50.0, "status": "MODERATE",
            "crowd_yes_price": 0.5, "crowd_no_price": 0.5,
            "mid_price": 0.5, "spread": 0.0, "imbalance": 0.0,
            "volume24h": 0.0, "trade_count_24h": 0,
            "market_title": "Unavailable", "market_id": "",
        },
        "nlp": {"scored_headlines": [], "aggregate_sentiment": 0.0},
        "stress": {
            "score": 50, "stress_score": 50, "level": "MODERATE",
            "plain_english": "AI Brain temporarily unavailable. Using safe neutral defaults.",
            "components": {
                "bayse_stress": 0.5, "nlp_stress": 0.5,
                "market_probability": 0.5,
                "bayse_weight": 0.6, "nlp_weight": 0.4,
            },
            "raw": {},
        },
        "bias": {
            "bias": "Rational", "active_bias": "Rational",
            "confidence": "Low",
            "explanation": "AI Brain unavailable. Defaulting to rational baseline.",
            "inputs": {},
        },
        "decision": {
            "market_probability": 0.5, "rational_probability": 0.5,
            "edge": 0.0, "confidence": "Low", "verdict": "HOLD",
            "plain_english": "AI Brain unavailable. HOLD all positions.",
            "win_probability": 0.5, "bias_applied": "Rational", "stress_score": 50,
        },
        "confidence": {
            "rational_pct": 50, "behavioral_pct": 50, "gap": 0,
            "confidence_score_100": 50, "confidence_score": 50,
            "confidence_tier": "Low", "score_label": "WEAK",
            "intervention_urgency": "LOW", "is_actionable": False,
            "plain_english": "Signal unavailable. No action recommended.",
            "metrics": {},
        },
        "allocation": {
            "verdict": "HOLD",
            "invest_ngn": 0.0, "save_ngn": 0.0,
            "hold_ngn": free_cash,
            "allocation_pct": 0.0,
            "allocator_notes": "AI Brain unavailable. Capital protected.",
            "plain_english": f"Hold \u20a6{free_cash:,.0f}. AI Brain temporarily offline.",
        },
        "score": {
            "score": 1.0, "decision_score": 1.0, "rating": "Poor",
            "components": {"edge_score": 0.0, "confidence_score": 0.0, "verdict_score": 0.5},
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