import os
import json
import re
import logging
from typing import Any, Dict, Optional

from google import genai
from google.genai.types import GenerateContentConfig, HttpOptions
from pydantic import BaseModel

from config.settings import settings


logger = logging.getLogger("zelta.copilot")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


class CopilotResult(BaseModel):
    summary: Optional[str] = None
    reasoning: Optional[str] = None
    action: Optional[str] = None
    what_this_means_for_you: Optional[str] = None
    bias_explanation: Optional[str] = None
    confidence_note: Optional[str] = None
    bq_alert: Optional[str] = None
    context_summary: Optional[str] = None


class ZeltaCopilot:
    """
    Vertex AI-backed Co-Pilot for ZELTA.
    Uses the Google Gen AI SDK on Vertex AI.
    """

    SYSTEM_PROMPT = """
You are ZELTA, a friendly money guide for Nigerian university students.

Your job is to explain ZELTA results in simple, calm, everyday English.
Pretend you are talking to a student who has little or no finance knowledge.

You should:
- explain what the market is doing
- explain what it means for the student
- explain what action to take
- use real Naira amounts
- use student life examples when helpful

You must NEVER:
- sound like a textbook
- use heavy finance jargon
- be vague
- be dramatic

Keep answers short, clear, and practical.
Always end with a clear verdict and Naira amount when relevant.

If you are returning JSON, return ONLY valid JSON.
If you are answering a question, keep the answer under 120 words.
""".strip()

    JSON_SYSTEM_PROMPT = """
You are a strict JSON generator.

Rules:
- Return ONLY valid JSON.
- Do NOT wrap in markdown fences.
- Do NOT add commentary before or after JSON.
- Do NOT truncate output.
- Use double quotes for all strings.
- If a field is unknown, use null.
- Keep the action field short and direct.
- Keep the wording simple enough for a student to understand.
""".strip()

    def __init__(self):
        project_id = (
            getattr(settings, "GOOGLE_CLOUD_PROJECT", None)
            or os.getenv("GOOGLE_CLOUD_PROJECT")
        )
        location = (
            getattr(settings, "GOOGLE_CLOUD_LOCATION", None)
            or os.getenv("GOOGLE_CLOUD_LOCATION", "global")
        )

        if not project_id:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT not set. Add it to your environment or settings."
            )

        self.client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
            http_options=HttpOptions(api_version="v1"),
        )

        self.model = os.getenv(
            "VERTEX_GEMINI_MODEL",
            os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        )

    @staticmethod
    def _response_schema() -> Dict[str, Any]:
        return {
            "type": "OBJECT",
            "properties": {
                "summary": {"type": "STRING"},
                "reasoning": {"type": "STRING"},
                "action": {"type": "STRING"},
                "what_this_means_for_you": {"type": "STRING"},
                "bias_explanation": {"type": "STRING"},
                "confidence_note": {"type": "STRING"},
                "bq_alert": {"type": "STRING", "nullable": True},
                "context_summary": {"type": "STRING", "nullable": True},
            },
            "required": [
                "summary",
                "reasoning",
                "action",
                "what_this_means_for_you",
                "bias_explanation",
                "confidence_note",
                "bq_alert",
                "context_summary",
            ],
            "propertyOrdering": [
                "summary",
                "reasoning",
                "action",
                "what_this_means_for_you",
                "bias_explanation",
                "confidence_note",
                "bq_alert",
                "context_summary",
            ],
        }

    def _build_pipeline_prompt(self, data: Dict[str, Any]) -> str:
        decision = data.get("decision", {})
        stress = data.get("stress", {})
        bias = data.get("bias", {})
        nlp = data.get("nlp", {})
        kelly = data.get("allocation") or data.get("kelly", {})
        sharpe = data.get("sharpe") or data.get("score", {})

        headlines = nlp.get("scored_headlines", [])[:3]
        headline_text = "\n".join(
            f"- {h.get('title', 'Untitled')} ({h.get('sentiment_label', 'neutral')})"
            for h in headlines
        ) if headlines else "No headlines available"

        verdict = decision.get("verdict", "HOLD")
        invest_ngn = kelly.get("invest_ngn", 0)
        save_ngn = kelly.get("save_ngn", 0)
        hold_ngn = kelly.get("hold_ngn", 0)
        stress_score = stress.get("score", 50)
        stress_level = stress.get("level", "MODERATE")
        bias_name = bias.get("bias", "Rational")
        market_prob = round((decision.get("market_probability", 0.5) or 0) * 100)
        rational_prob = round((decision.get("rational_probability", 0.5) or 0) * 100)
        market_title = data.get("bayse", {}).get("market_title", "Nigerian financial market")
        decision_score = sharpe.get("decision_score", sharpe.get("score", 0))

        return f"""
You are ZELTA, a money guide for Nigerian university students.

Explain this result like you are talking to a student friend who does not understand finance.
The student cares about:
- hostel fees
- food money
- transport
- data
- side hustle money
- savings
- avoiding panic

HERE IS THE SITUATION:
- Market stress: {stress_score}/100 ({stress_level})
- Market event: "{market_title}"
- Crowd view: {market_prob}% are leaning YES
- ZELTA view: {rational_prob}% are leaning YES
- Difference between crowd and ZELTA: {abs(market_prob - rational_prob)}%
- Active money habit: {bias_name}
- What that means: {bias.get("explanation", "")}
- ZELTA recommendation: {verdict}
- Safe amount to invest: ₦{invest_ngn:,.0f}
- Amount to save: ₦{save_ngn:,.0f}
- Amount to keep as buffer: ₦{hold_ngn:,.0f}
- Decision quality score: {decision_score}

TOP NIGERIAN NEWS HEADLINES:
{headline_text}

HOW TO RESPOND:
- Use very simple English
- Talk like a calm, smart friend
- Connect the advice to student life
- Mention the actual Naira amounts
- Explain the "why" in a way anyone can understand
- Do not sound like a finance lecturer
- Do not use technical terms
- Keep each field short and clear

RETURN ONLY VALID JSON.
No markdown.
No backticks.
No extra text outside JSON.

{{
  "summary": "1 short sentence: what is happening in the market today in simple words.",

  "reasoning": "2 short sentences: why ZELTA made this recommendation, using the crowd view, ZELTA view, the news, and the student's money situation.",

  "action": "1 short sentence: what the student should do with their money right now, with actual NGN amounts.",

  "what_this_means_for_you": "1-2 short sentences: explain how this affects the student's real life, savings, fees, or daily spending.",

  "bias_explanation": "1 short sentence: explain the active bias in simple language the student will understand.",

  "bq_alert": "Short warning if there is stress spending, panic, or risky behavior. Use student-friendly language. Set to null if no alert is needed.",

  "context_summary": "1 short line for the UI pills, such as: 'Bayse: 44% YES | Market calm | HOLD recommended'"
}}
""".strip()

    def _build_question_prompt(self, question: str, context: Dict[str, Any]) -> str:
        stress = context.get("stress", {})
        bias = context.get("bias", {})
        kelly = context.get("allocation") or context.get("kelly", {})
        decision = context.get("decision", {})
        bayse = context.get("bayse", {})

        invest_ngn = kelly.get("invest_ngn", 0)
        save_ngn = kelly.get("save_ngn", 0)
        hold_ngn = kelly.get("hold_ngn", 0)

        return f"""
You are ZELTA, a money assistant for Nigerian university students.

A student just asked you a question.
Reply like a calm smart friend who explains money in simple words.
Assume the student does NOT know finance terms.

The student asked:
"{question}"

Here is their current situation:
- Market stress: {stress.get("score", 50)}/100 ({stress.get("level", "MODERATE")})
- Market event: "{bayse.get("market_title", "Nigerian financial market")}"
- Crowd view: {round((decision.get("market_probability", 0.5) or 0) * 100)}% YES
- ZELTA view: {round((decision.get("rational_probability", 0.5) or 0) * 100)}% YES
- ZELTA recommendation: {decision.get("verdict", "HOLD")}
- Safe amount to invest: ₦{invest_ngn:,.0f}
- Safe amount to save: ₦{save_ngn:,.0f}
- Amount to hold as buffer: ₦{hold_ngn:,.0f}
- Active money habit: {bias.get("bias", "Rational")}
- What that means: {bias.get("explanation", "")}

How to answer:
- Answer the question directly
- Use simple English only
- Mention the actual Naira amounts
- Make it useful for student life, like hostel fees, food, data, transport, or side hustle money
- Keep it short, clear, and practical
- Do not sound like a lecturer or a finance textbook

Return ONLY valid JSON. No markdown. No backticks. No extra text.

{{
  "answer": "A short direct answer in simple language.",
  "why": "1-2 short sentences explaining why this is the best move right now.",
  "what_it_means": "1 short sentence connecting the advice to the student’s real life.",
  "action": "A clear action statement using real Naira amounts.",
  "verdict": "INVEST / SAVE / HOLD",
  "amount": "₦[amount]",
  "follow_up_tip": "A short practical tip the student can use next."
}}
""".strip()

    @staticmethod
    def _extract_text(response) -> str:
        text = getattr(response, "text", None)
        if text:
            return text.strip()

        try:
            return response.candidates[0].content.parts[0].text.strip()
        except Exception:
            return ""

    @staticmethod
    def _fallback_result() -> Dict[str, Any]:
        return {
            "summary": None,
            "reasoning": None,
            "action": None,
            "what_this_means_for_you": None,
            "bias_explanation": None,
            "confidence_note": "AI explanation temporarily unavailable.",
            "bq_alert": None,
            "context_summary": None,
        }

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)
        return text.strip()

    @staticmethod
    def _extract_first_json_object(text: str) -> str:
        text = ZeltaCopilot._strip_code_fences(text)

        start = text.find("{")
        if start == -1:
            return ""

        depth = 0
        in_string = False
        escape = False

        for i in range(start, len(text)):
            ch = text[i]

            if escape:
                escape = False
                continue

            if ch == "\\":
                escape = True
                continue

            if ch == '"':
                in_string = not in_string
                continue

            if in_string:
                continue

            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]

        return ""

    @staticmethod
    def _parse_json_to_result(text: str) -> CopilotResult:
        json_text = ZeltaCopilot._extract_first_json_object(text)
        if not json_text:
            raise ValueError("No complete JSON object found in model output.")

        data = json.loads(json_text)
        return CopilotResult.model_validate(data)

    @staticmethod
    def _shorten_action(action: Optional[str]) -> Optional[str]:
        if not action:
            return action

        action = action.strip()

        verdict_match = re.search(
            r"(VERDICT:\s*(INVEST|SAVE|HOLD)\s*[₦N]?\s*[\d,]+(?:\.\d+)?)",
            action,
            flags=re.IGNORECASE,
        )
        if verdict_match:
            verdict = verdict_match.group(1).strip()
            prefix = action[:verdict_match.start()].strip()
            if prefix:
                prefix = re.split(r"(?<=[.!?])\s+", prefix)[0].strip()
                return f"{prefix} {verdict}".strip()
            return verdict

        parts = re.split(r"(?<=[.!?])\s+", action)
        return parts[0].strip() if parts else action

    @staticmethod
    def _normalize_question_answer(answer: str) -> str:
        answer = answer.strip()

        answer = re.sub(
            r"VERDICT:\s*(INVEST|SAVE|HOLD)\s*([₦N])?\s*([\d,]+)",
            r"VERDICT: \1 ₦\3",
            answer,
            flags=re.IGNORECASE,
        )

        answer = re.sub(
            r"VERDICT:\s*(INVEST|SAVE|HOLD)\s+([\d,]+)",
            r"VERDICT: \1 ₦\2",
            answer,
            flags=re.IGNORECASE,
        )

        return answer

    async def _call_gemini_json(self, prompt: str) -> CopilotResult:
        config = GenerateContentConfig(
            system_instruction=f"{self.SYSTEM_PROMPT}\n\n{self.JSON_SYSTEM_PROMPT}",
            temperature=0.2,
            max_output_tokens=2048,
            response_mime_type="application/json",
            response_schema=self._response_schema(),
        )

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )

        text = self._extract_text(response)

        logger.info("[Vertex Gemini RAW | JSON=True] %s", text[:300] if text else "EMPTY")

        if not text:
            return CopilotResult(
                confidence_note="AI explanation temporarily unavailable."
            )

        try:
            result = self._parse_json_to_result(text)
            result.action = self._shorten_action(result.action)
            return result
        except Exception as e:
            logger.warning("[ZELTA Co-Pilot] JSON parse error: %s", e)

            repair_prompt = f"""
Fix this into valid JSON only.

Rules:
- Output ONLY valid JSON.
- Keep the same keys:
  summary, reasoning, action, what_this_means_for_you, bias_explanation,
  confidence_note, bq_alert, context_summary
- Use null for missing values.
- Do not add markdown or explanation.
- Keep action short.
- Make the language easy for a student to understand.

Broken output:
{text}
""".strip()

            repair_config = GenerateContentConfig(
                system_instruction=f"{self.SYSTEM_PROMPT}\n\n{self.JSON_SYSTEM_PROMPT}",
                temperature=0.0,
                max_output_tokens=2048,
                response_mime_type="application/json",
                response_schema=self._response_schema(),
            )

            try:
                repair_response = await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=repair_prompt,
                    config=repair_config,
                )
                repair_text = self._extract_text(repair_response)

                logger.info(
                    "[Vertex Gemini RAW | JSON-REPAIR] %s",
                    repair_text[:300] if repair_text else "EMPTY",
                )

                if repair_text:
                    repaired = self._parse_json_to_result(repair_text)
                    repaired.action = self._shorten_action(repaired.action)
                    return repaired
            except Exception as repair_error:
                logger.error("[ZELTA Co-Pilot] JSON repair failed: %s", repair_error)

            return CopilotResult(
                confidence_note="AI explanation temporarily unavailable."
            )

    async def _call_gemini_text(self, prompt: str) -> str:
        config = GenerateContentConfig(
            system_instruction=self.SYSTEM_PROMPT,
            temperature=0.3,
            max_output_tokens=240,
        )

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )

        text = self._extract_text(response)

        logger.info("[Vertex Gemini RAW | JSON=False] %s", text[:300] if text else "EMPTY")

        return self._normalize_question_answer(text)

    async def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._build_pipeline_prompt(data)

        try:
            result = await self._call_gemini_json(prompt)
            payload = result.model_dump(exclude_none=False)
            logger.info("[ZELTA Co-Pilot] Action: %s", payload.get("action"))
            return payload

        except Exception as e:
            logger.error("[ZELTA Co-Pilot] Error: %s", e)
            return self._fallback_result()

    async def answer_question(self, question: str, context: Dict[str, Any]) -> str:
        prompt = self._build_question_prompt(question, context)

        try:
            answer = await self._call_gemini_text(prompt)
            if not answer:
                return "Unable to answer right now. Check dashboard."

            logger.info("[ZELTA Co-Pilot] Q: %s", question[:50])
            return answer

        except Exception as e:
            logger.error("[ZELTA Co-Pilot] Question error: %s", e)
            return "Unable to answer right now. Check dashboard."


if __name__ == "__main__":
    import asyncio

    async def _test():
        copilot = ZeltaCopilot()

        sample_data = {
            "decision": {
                "market_probability": 0.50,
                "rational_probability": 0.50,
                "edge": 0.00,
                "verdict": "HOLD",
            },
            "stress": {
                "score": 23,
                "level": "CALM",
            },
            "bias": {
                "bias": "Rational",
                "confidence": "Low",
            },
            "nlp": {
                "aggregate_sentiment": -0.13,
            },
            "allocation": {
                "invest_ngn": 0,
                "save_ngn": 0,
                "hold_ngn": 26500,
            },
            "sharpe": {
                "decision_score": 1,
            },
        }

        print("\n================ PIPELINE TEST ================\n")
        result = await copilot.run(sample_data)
        print(json.dumps(result, indent=2))

        print("\n================ QUESTION TEST ================\n")
        answer = await copilot.answer_question(
            "Should I invest now or hold?",
            sample_data,
        )
        print(answer)

    asyncio.run(_test())
