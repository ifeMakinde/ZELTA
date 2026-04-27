"""
ZELTA BQ Co-Pilot Service

Gemini-powered plain-English financial advisor with full BQ context injection.
Answers student questions with Bayse signal, wallet state, and behavioral bias context.
Always ends with a SAVE / INVEST / HOLD verdict in NGN.
"""

import json
import logging
import re
from typing import Any, Dict, List

import httpx
from google.cloud import firestore

from config.settings import settings
from schemas.copilot import CopilotRequest, CopilotResponse, ContextPill

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

SYSTEM_PROMPT = """You are ZELTA's BQ Co-Pilot — a behavioral quantitative financial advisor for Nigerian university students.

You have access to the user's real-time financial context below. Your job is to:
1. Answer their question using plain English — no jargon
2. Reference their actual Bayse stress signal, wallet state, and active bias
3. Apply Bayesian reasoning and Kelly criterion logic in your recommendation
4. Always end your response with a clear VERDICT: SAVE ₦X / INVEST ₦X / HOLD

Rules:
- Maximum 120 words in your response
- Never use financial jargon without explaining it
- Always reference the user's actual numbers (free cash, stress index, etc.)
- Be direct, warm, and specific
- If stress is HIGH (60+), caution against large investments
- If CRISIS (80+), recommend HOLD on everything

Return strict JSON only with these fields:
{
  "answer": "plain English response (max 120 words)",
  "verdict": "SAVE" | "INVEST" | "HOLD",
  "verdict_amount": <number in NGN or null>,
  "confidence": <0-100 float>,
  "sources": ["Bayse Markets", "Wallet Data", "BQ Engine"]
}
"""


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _extract_json(text: str) -> Dict[str, Any]:
    """
    Gemini may return plain JSON or JSON wrapped in markdown fences.
    This strips the fences and parses the first JSON object it can find.
    """
    raw = text.strip()

    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw, flags=re.DOTALL | re.IGNORECASE)
    if fence_match:
        raw = fence_match.group(1).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        obj_match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if obj_match:
            return json.loads(obj_match.group(0))
        raise


def _normalize_brain_context(brain_context: dict) -> dict:
    """
    Accept either:
      1) nested brain format:
         brain_context["stress"]["combined_index"]
      2) flat intelligence format:
         brain_context["stress_index"], brain_context["active_bias"], etc.

    Returns the nested shape expected by the Co-Pilot prompt builder.
    """
    brain_context = brain_context or {}

    if "stress" in brain_context or "bias" in brain_context or "allocation" in brain_context:
        return brain_context

    return {
        "stress": {
            "combined_index": brain_context.get("stress_index", 50.0),
            "level": brain_context.get("stress_level", "MODERATE"),
            "label": brain_context.get("stress_label", ""),
        },
        "bias": {
            "active_bias": brain_context.get("active_bias", "Rational"),
            "confidence": brain_context.get("bias_confidence", "Low"),
            "explanation": brain_context.get("bias_explanation", ""),
        },
        "decision": {
            "verdict": brain_context.get("decision_verdict", "HOLD"),
            "plain_english": brain_context.get("decision_plain", ""),
            "edge": brain_context.get("edge", 0.0),
            "win_probability": brain_context.get("win_probability", 0.5),
        },
        "confidence": {
            "gap": brain_context.get("confidence_gap", 0.0),
            "rational_pct": brain_context.get("rational_pct", 50.0),
            "behavioral_pct": brain_context.get("behavioral_pct", 50.0),
            "confidence_score": brain_context.get("confidence_score", 50.0),
            "confidence_tier": brain_context.get("confidence_tier", "Low"),
            "score_label": brain_context.get("score_label", "WEAK"),
            "intervention_urgency": brain_context.get("intervention_urgency", "LOW"),
            "plain_english": brain_context.get("confidence_plain", ""),
        },
        "allocation": {
            "verdict": brain_context.get("verdict", "HOLD"),
            "invest_ngn": brain_context.get("invest_ngn", 0.0),
            "save_ngn": brain_context.get("save_ngn", 0.0),
            "hold_ngn": brain_context.get("hold_ngn", 0.0),
            "allocation_pct": brain_context.get("allocation_pct", 0.0),
            "plain_english": brain_context.get("allocation_plain", ""),
        },
        "score": {
            "score": brain_context.get("decision_score", 1.0),
            "decision_score": brain_context.get("decision_score", 1.0),
            "rating": brain_context.get("score_rating", "Poor"),
        },
        "bayse": {
            "score": brain_context.get("bayse_score", 50.0),
            "status": brain_context.get("bayse_status", "MODERATE"),
            "market_title": brain_context.get("bayse_market", "Unavailable"),
            "market_id": "",
            "crowd_yes_price": brain_context.get("crowd_yes", 0.5),
            "crowd_no_price": brain_context.get("crowd_no", 0.5),
            "mid_price": brain_context.get("mid_price", 0.5),
            "best_bid": 0.0,
            "best_ask": 0.0,
            "spread": brain_context.get("spread", 0.0),
            "imbalance": 0.0,
            "volume24h": 0.0,
            "trade_count_24h": 0,
            "available": True,
            "raw_crowd_stress": brain_context.get("stress_index", 50.0),
            "naira_weakness_probability": brain_context.get("crowd_yes", 0.5),
            "outcome": None,
            "last_price": 0.0,
            "source": "ZELTA Intelligence",
            "updated_at": None,
        },
        "explanation": {
            "summary": brain_context.get("summary", ""),
            "reasoning": "",
            "action": brain_context.get("action", ""),
            "what_this_means_for_you": None,
            "bias_explanation": brain_context.get("bias_explanation", ""),
            "confidence_note": brain_context.get("confidence_plain", ""),
            "bq_alert": brain_context.get("bq_alert", ""),
            "context_summary": brain_context.get("context_summary", ""),
        },
        "nlp": {
            "scored_headlines": [],
            "aggregate_sentiment": brain_context.get("nlp_sentiment", 0.0),
        },
    }


def _build_context_pills(brain_context: dict, wallet_context: dict) -> List[ContextPill]:
    brain_context = _normalize_brain_context(brain_context)

    stress_index = _safe_float(brain_context.get("stress", {}).get("combined_index", 50.0), 50.0)
    stress_level = _safe_str(brain_context.get("stress", {}).get("level", "MODERATE"), "MODERATE")
    active_bias = _safe_str(brain_context.get("bias", {}).get("active_bias", "Rational"), "Rational")
    free_cash = _safe_float(wallet_context.get("free_cash", 0.0), 0.0)
    verdict_amount = _safe_float(brain_context.get("allocation", {}).get("invest_ngn", 0.0), 0.0)

    return [
        ContextPill(label="Bayse Fear", value=f"{stress_index:.0f}%"),
        ContextPill(label="Bias", value=active_bias.replace("_", " ").title()),
        ContextPill(label="Free Cash", value=f"₦{free_cash:,.0f}"),
        ContextPill(label="Stress Level", value=stress_level),
        ContextPill(label="Kelly Amount", value=f"₦{verdict_amount:,.0f}"),
    ]


def _build_context_block(
    request: CopilotRequest,
    brain_context: dict,
    wallet_context: dict,
) -> str:
    brain_context = _normalize_brain_context(brain_context)

    stress_index = _safe_float(brain_context.get("stress", {}).get("combined_index", 50.0), 50.0)
    stress_level = _safe_str(brain_context.get("stress", {}).get("level", "MODERATE"), "MODERATE")
    active_bias = _safe_str(brain_context.get("bias", {}).get("active_bias", "Rational"), "Rational")

    free_cash = _safe_float(wallet_context.get("free_cash", 0.0), 0.0)
    total_balance = _safe_float(wallet_context.get("total_balance", 0.0), 0.0)
    locked_total = _safe_float(
        wallet_context.get("locked_total", wallet_context.get("locked_amount", 0.0)),
        0.0,
    )
    weekly_burn_rate = _safe_float(wallet_context.get("weekly_burn_rate", 0.0), 0.0)

    confidence_gap = _safe_float(brain_context.get("confidence", {}).get("gap", 0.0), 0.0)
    rational_pct = _safe_float(brain_context.get("confidence", {}).get("rational_pct", 50.0), 50.0)
    bayse_mid = _safe_float(brain_context.get("bayse", {}).get("mid_price", 0.5), 0.5)
    market_title = _safe_str(brain_context.get("bayse", {}).get("market_title", "Active Bayse market"))
    score_label = _safe_str(brain_context.get("score", {}).get("rating", "Poor"), "Poor")
    bq_alert = _safe_str(brain_context.get("explanation", {}).get("bq_alert", ""), "")
    decision_plain = _safe_str(brain_context.get("decision", {}).get("plain_english", ""), "")
    allocation_verdict = _safe_str(brain_context.get("allocation", {}).get("verdict", "HOLD"), "HOLD")
    invest_amount = _safe_float(brain_context.get("allocation", {}).get("invest_ngn", 0.0), 0.0)

    return f"""
USER FINANCIAL CONTEXT (Real-time from ZELTA AI Brain):
- Stress Index: {stress_index:.0f}/100 ({stress_level})
- Active Behavioral Bias: {active_bias}
- Free Cash: ₦{free_cash:,.0f}
- Total Balance: ₦{total_balance:,.0f}
- Locked Savings: ₦{locked_total:,.0f}
- Bayse Market: {market_title} | Mid Price: {bayse_mid:.2f}
- Confidence Gap (rational vs emotional): {confidence_gap:.0f}%
- Rational percentage: {rational_pct:.0f}%
- Current BQ Verdict: {allocation_verdict}
- Kelly-Safe Invest Amount: ₦{invest_amount:,.0f}
- Decision Rating: {score_label}
- Weekly Burn Rate: ₦{weekly_burn_rate:,.0f}
- BQ Alert: {bq_alert}
- Brain Decision Plain English: {decision_plain}

USER QUESTION:
{request.question}
""".strip()


def _coerce_verdict_amount(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if not text:
        return None

    # remove common currency symbols and commas
    text = re.sub(r"[₦,$\s]", "", text)
    try:
        return float(text)
    except ValueError:
        return None


def _safe_sources(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(v) for v in value if v is not None]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return ["Bayse Markets", "Wallet Data", "BQ Engine"]


async def answer_question(
    db: firestore.Client,
    uid: str,
    request: CopilotRequest,
    brain_context: dict,
    wallet_context: dict,
) -> CopilotResponse:
    """
    Send user question to Gemini with full BQ context and return structured answer.
    """
    _ = (db, uid)  # reserved for future chat history persistence

    brain_context = _normalize_brain_context(brain_context)
    context_pills = _build_context_pills(brain_context, wallet_context)
    context_block = _build_context_block(request, brain_context, wallet_context)

    messages = []
    for msg in (request.conversation_history or [])[-6:]:
        messages.append(
            {
                "role": "user" if msg.role == "user" else "model",
                "parts": [{"text": msg.content}],
            }
        )

    messages.append(
        {
            "role": "user",
            "parts": [{"text": context_block}],
        }
    )

    try:
        if not settings.gemini_api_key:
            raise RuntimeError("Missing GEMINI_API_KEY")

        url = GEMINI_API_URL.format(model=settings.gemini_model)
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": messages,
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 256,
                "responseMimeType": "application/json",
            },
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                url,
                params={"key": settings.gemini_api_key},
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()

        raw_text = ""
        if isinstance(data, dict) and data.get("candidates"):
            try:
                raw_text = data["candidates"][0]["content"]["parts"][0].get("text", "")
            except (KeyError, IndexError, TypeError):
                raw_text = ""

        parsed = _extract_json(raw_text)

        verdict = _safe_str(parsed.get("verdict"), "HOLD").upper()
        if verdict not in {"SAVE", "INVEST", "HOLD"}:
            verdict = "HOLD"

        verdict_amount = _coerce_verdict_amount(parsed.get("verdict_amount"))

        return CopilotResponse(
            answer=_safe_str(
                parsed.get("answer"),
                "I could not generate a response just now. Please try again.",
            ),
            verdict=verdict,
            verdict_amount=verdict_amount if verdict != "HOLD" else 0.0,
            context_pills=context_pills,
            confidence=max(0.0, min(100.0, _safe_float(parsed.get("confidence", 70.0), 70.0))),
            sources=_safe_sources(parsed.get("sources")),
        )

    except httpx.HTTPStatusError as e:
        logger.error("Gemini API error %s: %s", e.response.status_code, e.response.text)
        return _fallback_response(brain_context, wallet_context, context_pills)

    except (json.JSONDecodeError, KeyError, IndexError, ValueError, RuntimeError) as e:
        logger.error("Copilot parsing/config error: %s", e)
        return _fallback_response(brain_context, wallet_context, context_pills)

    except Exception as e:
        logger.error("Copilot unexpected error: %s", e)
        return _fallback_response(brain_context, wallet_context, context_pills)


def _fallback_response(
    brain_context: dict,
    wallet_context: dict,
    context_pills: list,
) -> CopilotResponse:
    """Fallback when Gemini API is unavailable — use local BQ engine output."""
    brain_context = _normalize_brain_context(brain_context)
    allocation = brain_context.get("allocation", {})

    verdict = _safe_str(allocation.get("verdict", "HOLD"), "HOLD").upper()
    if verdict not in {"SAVE", "INVEST", "HOLD"}:
        verdict = "HOLD"

    amount = _safe_float(allocation.get("invest_ngn", allocation.get("invest_amount", 0.0)), 0.0)
    plain = _safe_str(
        allocation.get("plain_english"),
        "The BQ engine recommends HOLD at current stress levels.",
    )

    return CopilotResponse(
        answer=f"{plain} (Note: AI assistant temporarily unavailable — using local BQ engine.)",
        verdict=verdict,
        verdict_amount=amount if verdict != "HOLD" else 0.0,
        context_pills=context_pills,
        confidence=65.0,
        sources=["BQ Engine (local)", "Bayse Markets"],
    )
