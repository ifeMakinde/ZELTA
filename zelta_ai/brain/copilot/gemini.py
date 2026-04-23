import os
import json
import re
import logging
from typing import Any, Dict, Optional

from google import genai
from google.genai.types import GenerateContentConfig, HttpOptions
from pydantic import BaseModel, ValidationError

from config.settings import settings


logger = logging.getLogger("zelta.copilot")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


class CopilotResult(BaseModel):
    summary: Optional[str] = None
    reasoning: Optional[str] = None
    action: Optional[str] = None
    confidence_note: Optional[str] = None
    bq_alert: Optional[str] = None
    context_summary: Optional[str] = None


class ZeltaCopilot:
    """
    Vertex AI-backed Co-Pilot for ZELTA.
    Uses the Google Gen AI SDK on Vertex AI.
    """

    SYSTEM_PROMPT = """
You are the ZELTA BQ Co-Pilot — a behavioral quantitative financial
intelligence assistant built for Nigerian university students.

You ONLY answer:
- Explain ZELTA signals
- Explain finance concepts simply
- Tell the user what to do

You NEVER go outside finance.
You ALWAYS end with: VERDICT: INVEST/SAVE/HOLD + NGN amount.
Keep answers under 120 words.
Plain English only.
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
                "confidence_note": {"type": "STRING"},
                "bq_alert": {"type": "STRING", "nullable": True},
                "context_summary": {"type": "STRING", "nullable": True},
            },
            "required": [
                "summary",
                "reasoning",
                "action",
                "confidence_note",
                "bq_alert",
                "context_summary",
            ],
            "propertyOrdering": [
                "summary",
                "reasoning",
                "action",
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
        kelly = data.get("allocation") or {}
        sharpe = data.get("sharpe") or data.get("score", {})

        return f"""
Interpret this ZELTA data:

Market Probability: {decision.get("market_probability")}
Rational Probability: {decision.get("rational_probability")}
Edge: {decision.get("edge")}
Verdict: {decision.get("verdict")}

Stress: {stress.get("score")}/100 ({stress.get("level")})
Sentiment: {nlp.get("aggregate_sentiment")}

Bias: {bias.get("bias")} ({bias.get("confidence")})

Invest: {kelly.get("invest_ngn")}
Save: {kelly.get("save_ngn")}
Hold: {kelly.get("hold_ngn")}

Decision Score: {sharpe.get("decision_score", sharpe.get("score"))}

Return ONLY valid JSON matching this shape:
{{
  "summary": "string",
  "reasoning": "string",
  "action": "string",
  "confidence_note": "string",
  "bq_alert": null,
  "context_summary": null
}}

Important:
- Make action short.
- Do not repeat the whole explanation inside action.
""".strip()

    def _build_question_prompt(self, question: str, context: Dict[str, Any]) -> str:
        decision = context.get("decision", {})
        kelly = context.get("allocation", {})

        return f"""
User question: {question}

Context:
- Verdict: {decision.get("verdict")}
- Invest: ₦{kelly.get("invest_ngn", 0):,.0f}
- Save: ₦{kelly.get("save_ngn", 0):,.0f}
- Hold: ₦{kelly.get("hold_ngn", 0):,.0f}

Answer clearly in plain English.
Keep it under 120 words.
End with:
VERDICT: [INVEST/SAVE/HOLD] ₦[amount]
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
                    return text[start : i + 1]

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

        # Keep the verdict line if present, but trim overly long prose.
        verdict_match = re.search(
            r"(VERDICT:\s*(INVEST|SAVE|HOLD)\s*[₦N]?\s*[\d,]+(?:\.\d+)?)",
            action,
            flags=re.IGNORECASE,
        )
        if verdict_match:
            verdict = verdict_match.group(1).strip()
            prefix = action[: verdict_match.start()].strip()
            if prefix:
                prefix = re.split(r"(?<=[.!?])\s+", prefix)[0].strip()
                return f"{prefix} {verdict}".strip()
            return verdict

        # If no verdict line, keep only the first sentence.
        parts = re.split(r"(?<=[.!?])\s+", action)
        return parts[0].strip() if parts else action

    @staticmethod
    def _normalize_question_answer(answer: str) -> str:
        answer = answer.strip()

        # Standardize any missing currency symbol spacing.
        answer = re.sub(r"VERDICT:\s*(INVEST|SAVE|HOLD)\s*([₦N])?\s*([\d,]+)",
                        r"VERDICT: \1 ₦\3",
                        answer,
                        flags=re.IGNORECASE)

        # If the model forgot the symbol entirely but included an amount.
        answer = re.sub(r"VERDICT:\s*(INVEST|SAVE|HOLD)\s+([\d,]+)",
                        r"VERDICT: \1 ₦\2",
                        answer,
                        flags=re.IGNORECASE)

        return answer

    async def _call_gemini_json(self, prompt: str) -> CopilotResult:
        config = GenerateContentConfig(
            system_instruction=f"{self.SYSTEM_PROMPT}\n\n{self.JSON_SYSTEM_PROMPT}",
            temperature=0.2,
            max_output_tokens=1024,
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
  summary, reasoning, action, confidence_note, bq_alert, context_summary
- Use null for missing values.
- Do not add markdown or explanation.
- Keep action short.

Broken output:
{text}
""".strip()

            repair_config = GenerateContentConfig(
                system_instruction=f"{self.SYSTEM_PROMPT}\n\n{self.JSON_SYSTEM_PROMPT}",
                temperature=0.0,
                max_output_tokens=1024,
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