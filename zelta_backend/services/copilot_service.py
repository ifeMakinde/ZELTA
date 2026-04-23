"""
ZELTA BQ Co-Pilot Service

Gemini-powered plain-English financial advisor with full BQ context injection.
Answers student questions with Bayse signal, wallet state, and behavioral bias context.
Always ends with a SAVE / INVEST / HOLD verdict in NGN.
"""

import httpx
import json
import logging
from google.cloud import firestore
from schemas.copilot import CopilotRequest, CopilotResponse, CopilotMessage, ContextPill
from config.settings import settings

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

Format your response as JSON with these fields:
{
  "answer": "your plain English response here (max 120 words)",
  "verdict": "SAVE" | "INVEST" | "HOLD",
  "verdict_amount": <number in NGN or null>,
  "confidence": <0-100 float>,
  "sources": ["Bayse Markets", "Wallet Data", "BQ Engine"]
}
"""


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

    # Build context pills for the UI
    stress_index = brain_context.get("stress", {}).get("combined_index", 50.0)
    stress_level = brain_context.get("stress", {}).get("level", "MODERATE")
    active_bias  = brain_context.get("bias", {}).get("active_bias", "Rational")
    free_cash    = wallet_context.get("free_cash", 0.0)
    verdict_amount = brain_context.get("allocation", {}).get("invest_amount", 0.0)

    context_pills = [
        ContextPill(label="Bayse Fear", value=f"{stress_index:.0f}%"),
        ContextPill(label="Bias", value=active_bias.replace("_", " ").title()),
        ContextPill(label="Free Cash", value=f"₦{free_cash:,.0f}"),
        ContextPill(label="Stress Level", value=stress_level),
    ]

    # Pull fields from normalised brain structure
    confidence_gap   = brain_context.get("confidence", {}).get("gap", 0)
    decision_plain   = brain_context.get("decision", {}).get("plain_english", "")
    bq_alert         = brain_context.get("explanation", {}).get("bq_alert", "")
    rational_pct     = brain_context.get("confidence", {}).get("rational_pct", 50)
    bayse_mid        = brain_context.get("bayse", {}).get("mid_price", 0.5)
    market_title     = brain_context.get("bayse", {}).get("market_title", "Active Bayse market")
    score_label      = brain_context.get("score", {}).get("rating", "Poor")

    # Build context string for Gemini
    context_block = f"""
USER FINANCIAL CONTEXT (Real-time from ZELTA AI Brain):
- Stress Index: {stress_index:.0f}/100 ({stress_level})
- Active Behavioral Bias: {active_bias}
- Free Cash: ₦{free_cash:,.0f}
- Total Balance: ₦{wallet_context.get('total_balance', 0):,.0f}
- Locked Savings: ₦{wallet_context.get('locked_amount', 0):,.0f}
- Bayse Market: {market_title} | Mid Price: {bayse_mid:.2f}
- Confidence Gap (rational vs emotional): {confidence_gap:.0f}%
- Rational percentage: {rational_pct:.0f}%
- Current BQ Verdict: {brain_context.get('allocation', {}).get('verdict', 'HOLD')}
- Kelly-Safe Invest Amount: ₦{verdict_amount:,.0f}
- Decision Rating: {score_label}
- Weekly Burn Rate: ₦{wallet_context.get('weekly_burn_rate', 0):,.0f}
- BQ Alert: {bq_alert}
- Brain Decision Plain English: {decision_plain}

USER QUESTION: {request.question}
"""

    # Build conversation history for Gemini
    messages = []
    for msg in (request.conversation_history or [])[-6:]:  # last 6 messages for context
        messages.append({
            "role": "user" if msg.role == "user" else "model",
            "parts": [{"text": msg.content}],
        })

    # Add current question with context
    messages.append({
        "role": "user",
        "parts": [{"text": context_block}],
    })

    try:
        url = GEMINI_API_URL.format(model=settings.gemini_model)
        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": messages,
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 512,
                "responseMimeType": "application/json",
            },
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                url,
                params={"key": settings.gemini_api_key},
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()

        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(raw_text)

        return CopilotResponse(
            answer=parsed.get("answer", "I couldn't generate a response. Please try again."),
            verdict=parsed.get("verdict"),
            verdict_amount=parsed.get("verdict_amount"),
            context_pills=context_pills,
            confidence=float(parsed.get("confidence", 70.0)),
            sources=parsed.get("sources", ["Bayse Markets", "BQ Engine"]),
        )

    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API error {e.response.status_code}: {e.response.text}")
        return _fallback_response(brain_context, wallet_context, context_pills)

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"Gemini response parsing error: {e}")
        return _fallback_response(brain_context, wallet_context, context_pills)

    except Exception as e:
        logger.error(f"Copilot unexpected error: {e}")
        return _fallback_response(brain_context, wallet_context, context_pills)


def _fallback_response(brain_context: dict, wallet_context: dict, context_pills: list) -> CopilotResponse:
    """Fallback when Gemini API is unavailable — use local BQ engine output."""
    allocation = brain_context.get("allocation", {})
    stress = brain_context.get("stress", {})

    verdict = allocation.get("verdict", "HOLD")
    amount = allocation.get("invest_amount", 0)
    plain = allocation.get("plain_english", "The BQ engine recommends HOLD at current stress levels.")

    return CopilotResponse(
        answer=f"{plain} (Note: AI assistant temporarily unavailable — using local BQ engine.)",
        verdict=verdict,
        verdict_amount=amount,
        context_pills=context_pills,
        confidence=65.0,
        sources=["BQ Engine (local)", "Bayse Markets"],
    )