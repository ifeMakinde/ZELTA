import os
import time
import asyncio
from typing import Dict, Any

from google.cloud import aiplatform
from google.cloud.aiplatform.gapic import PredictionServiceClient
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value


class VertexAIOptimizer:
    """
    Direct Vertex AI Endpoint caller for ZELTA.
    No HTTP Brain service anymore — pure managed inference.
    """

    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("VERTEX_LOCATION", "us-central1")
        self.endpoint_id = os.getenv("VERTEX_ENDPOINT_ID")

        # Initialize Vertex AI
        aiplatform.init(
            project=self.project_id,
            location=self.location,
        )

        self.client = PredictionServiceClient()

        self.endpoint_path = self.client.endpoint_path(
            project=self.project_id,
            location=self.location,
            endpoint=self.endpoint_id,
        )

        # config
        self.max_retries = int(os.getenv("MAX_RETRIES", 2))
        self.timeout = float(os.getenv("VERTEX_TIMEOUT", 10.0))

    async def call_brain(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends structured payload directly to Vertex AI model.
        """

        start = time.time()
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                # Convert Python dict → Vertex AI format
                instance = json_format.ParseDict(payload, Value())

                request = {
                    "endpoint": self.endpoint_path,
                    "instances": [instance],
                }

                # Run in thread (Vertex SDK is sync)
                response = await asyncio.to_thread(
                    self.client.predict,
                    request=request,
                )

                prediction = response.predictions[0]
                latency = round(time.time() - start, 3)

                print(
                    f"[VertexAI] Success | "
                    f"Latency: {latency}s | Attempt {attempt + 1}"
                )

                return {
                    "success": True,
                    "latency": latency,
                    "data": prediction,
                }

            except Exception as e:
                last_error = e
                print(f"[VertexAI] Attempt {attempt + 1} failed: {e}")

                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))

        latency = round(time.time() - start, 3)

        return self._fallback(last_error, latency)

    def _fallback(self, error: Exception, latency: float):
        return {
            "success": False,
            "latency": latency,
            "error": str(error),
            "data": {
                "allocation": {
                    "verdict": "HOLD",
                    "invest_ngn": 0,
                    "save_ngn": 0,
                    "hold_ngn": 0,
                    "plain_english": "Vertex AI unavailable. Holding funds safely.",
                },
                "confidence": {
                    "confidence_score_100": 0,
                    "is_actionable": False,
                    "rational_pct": 50,
                    "behavioral_pct": 50,
                },
                "stress": {
                    "score": 50,
                    "level": "UNKNOWN",
                },
                "meta": {
                    "status": "vertex_fallback",
                },
            },
        }

    async def get_stress_only(self) -> Dict[str, Any]:
        """
        Lightweight inference (same model, smaller prompt).
        """
        try:
            payload = {
                "mode": "stress_only"
            }

            instance = json_format.ParseDict(payload, Value())

            response = await asyncio.to_thread(
                self.client.predict,
                request={
                    "endpoint": self.endpoint_path,
                    "instances": [instance],
                },
            )

            data = response.predictions[0]

            return {
                "success": True,
                "stress_score": data.get("stress_score", 50),
                "stress_level": data.get("stress_level", "UNKNOWN"),
            }

        except Exception as e:
            return {
                "success": False,
                "stress_score": 50,
                "stress_level": "UNKNOWN",
                "error": str(e),
            }