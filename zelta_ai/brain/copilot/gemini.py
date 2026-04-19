import os
import json
import asyncio
from typing import Dict, Any, Optional

import google.generativeai as genai
from config.settings import settings


class ZeltaCopilot:
    """
    Gemini-powered AI Co-Pilot for ZELTA.

    Converts quantitative outputs into structured plain English
    explanations for Nigerian university students.

    Two entry points:
    - run(data)                    → called by brain/pipeline.py
    - answer_question(q, context)  → called by /api/copilot route
    """

    SYSTEM_PROMPT = """
You are the ZELTA BQ Co-Pilot — a behavioral quantitative financial 
intelligence assistant built for Nigerian university students.

You ONLY answer three types of questions:
1. Explaining a ZELTA signal or recommendation
2. Explaining a quantitative finance concept in simple terms
3. Telling the student what action to take right now

You NEVER give general lifestyle advice.
You NEVER discuss anything outside personal finance and trading signals.
You ALWAYS end with a clear VERDICT: INVEST/SAVE/HOLD + NGN amount.
You keep answers under 120 words.
You use plain English. No jargon on screen.
You sound calm, sharp, and intelligent.
"""

    def __init__(self):
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not set. Add it to your .env file."
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=self.SYSTEM_PROMPT,
        )

    # ── PROMPT BUILDERS ───────────────────────────────────────────────────────

    def _build_pipeline_prompt(self, data: Dict[str, Any]) -> str:
        """
        Build prompt for pipeline run.
        Returns structured JSON explanation of the full BQ report.
        """
        decision   = data.get("decision", {})
        stress     = data.get("stress", {})
        bias       = data.get("bias", {})
        nlp        = data.get("nlp", {})
        confidence = data.get("confidence", {})

        # Kelly data — handle both key names from pipeline
        kelly = data.get("allocation") or data.get("kelly", {})

        sharpe     = data.get("score") or data.get("sharpe", {})

        return f"""
Interpret the following ZELTA quantitative data for a Nigerian student.

BAYSE MARKET DATA (PRIMARY SIGNAL):
Market Probability (Bayse crowd): {decision.get("market_probability")}
Rational Probability (ZELTA model): {decision.get("rational_probability")}
Edge (gap): {decision.get("edge")}
Verdict: {decision.get("verdict")}

STUDENT ENVIRONMENT:
Stress Score: {stress.get("score")}/100
Stress Level: {stress.get("level")}
NLP Sentiment: {nlp.get("aggregate_sentiment")}

BEHAVIORAL ANALYSIS:
Active Bias: {bias.get("bias")}
Bias Explanation: {bias.get("explanation")}
Bias Confidence: {bias.get("confidence")}

DECISION QUALITY:
Confidence Score: {confidence.get("confidence_score_100")}/100
Confidence Tier: {confidence.get("confidence_tier")}
Rational %: {confidence.get("rational_pct")}%
Behavioral Impulse %: {confidence.get("behavioral_pct")}%

KELLY ALLOCATION:
Invest NGN: {kelly.get("invest_ngn")}
Save NGN: {kelly.get("save_ngn")}
Hold NGN: {kelly.get("hold_ngn")}

Decision Score: {sharpe.get("decision_score") or sharpe.get("score")}

Return ONLY valid JSON. No markdown. No extra text. No backticks.

{{
  "summary": "One sentence overview of current market situation",
  "reasoning": "Why ZELTA made this recommendation (data-driven, max 2 sentences)",
  "action": "Specific instruction: INVEST/SAVE/HOLD + exact NGN amount",
  "confidence_note": "How confident this decision is and why",
  "bq_alert": "Short behavioral warning if bias is HIGH confidence, else null",
  "context_summary": "One sentence summary for Co-Pilot context pills"
}}
"""

    def _build_question_prompt(
        self,
        question: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Build prompt for direct student question.
        Uses full pipeline context to give personalised answer.
        """
        stress   = context.get("stress", {})
        bias     = context.get("bias", {})
        kelly    = context.get("allocation") or context.get("kelly", {})
        decision = context.get("decision", {})

        return f"""
A Nigerian university student asked: "{question}"

Their current ZELTA context:
- Stress Index: {stress.get("score")}/100 ({stress.get("level")})
- Active Bias: {bias.get("bias")} ({bias.get("confidence")} confidence)
- ZELTA Verdict: {decision.get("verdict")}
- Invest Amount: ₦{kelly.get("invest_ngn", 0):,.0f}
- Save Amount: ₦{kelly.get("save_ngn", 0):,.0f}
- Hold Amount: ₦{kelly.get("hold_ngn", 0):,.0f}
- Rational Probability: {decision.get("rational_probability")}
- Bayse Crowd Probability: {decision.get("market_probability")}

Answer their question using this context.
Keep answer under 120 words.
Plain English only — no jargon on screen.
End with: VERDICT: [INVEST/SAVE/HOLD] ₦[amount]
"""

    # ── JSON EXTRACTION ───────────────────────────────────────────────────────

    def _safe_json(self, text: str) -> Dict[str, Any]:
        """
        Robust JSON extraction.
        Handles Gemini formatting issues — backticks, extra text, etc.
        """
        # Clean common Gemini formatting issues
        text = text.strip()
        text = text.replace("```json", "").replace("```", "").strip()

        # Direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Find JSON block manually
        start = text.find("{")
        end   = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass

        # Final fallback — return safe defaults
        return {
            "summary":         "Market analysis complete.",
            "reasoning":       text[:200] if text else "Analysis unavailable.",
            "action":          "Review your ZELTA dashboard for recommendations.",
            "confidence_note": "AI explanation temporarily unavailable.",
            "bq_alert":        None,
            "context_summary": "ZELTA analysis running.",
        }

    # ── GEMINI CALLER ─────────────────────────────────────────────────────────

    async def _call_gemini(self, prompt: str) -> str:
        """
        Call Gemini in a thread pool to avoid blocking the event loop.
        Gemini SDK is synchronous — asyncio.to_thread makes it async safe.
        """
        response = await asyncio.to_thread(
            self.model.generate_content,
            prompt,
        )
        return (response.text or "").strip()

    # ── ENTRY POINT 1: PIPELINE ───────────────────────────────────────────────

    async def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called by brain/pipeline.py.
        Takes full pipeline output. Returns structured explanation dict.
        """
        prompt = self._build_pipeline_prompt(data)

        try:
            text   = await self._call_gemini(prompt)
            result = self._safe_json(text)

            print(
                f"[ZELTA Co-Pilot] Action: {result.get('action', 'N/A')[:60]}"
            )
            return result

        except Exception as e:
            print(f"[ZELTA Co-Pilot] Gemini error: {e}")
            return {
                "summary":         "Market analysis complete.",
                "reasoning":       "AI explanation temporarily unavailable.",
                "action":          "Check your ZELTA dashboard.",
                "confidence_note": "Gemini API error.",
                "bq_alert":        None,
                "context_summary": "ZELTA running.",
            }

    # ── ENTRY POINT 2: DIRECT QUESTION ───────────────────────────────────────

    async def answer_question(
        self,
        question: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Called by /api/copilot route.
        Takes student question + full pipeline context.
        Returns plain English answer string.
        """
        prompt = self._build_question_prompt(question, context)

        try:
            answer = await self._call_gemini(prompt)

            # Clean any JSON formatting if Gemini returns it
            answer = answer.replace("```", "").strip()

            print(f"[ZELTA Co-Pilot] Q: {question[:50]}")
            print(f"[ZELTA Co-Pilot] A: {answer[:80]}...")

            return answer

        except Exception as e:
            print(f"[ZELTA Co-Pilot] Question error: {e}")
            return (
                "I could not process your question right now. "
                "Please check your ZELTA dashboard for the latest recommendation."
            )