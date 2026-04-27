import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from brain.bayse.stress_signal import monitor
from brain.nlp.scraper import run_scraper
from brain.nlp.scorer import ZeltaSentimentScorer
from brain.stress.index import run_stress_index
from brain.bias.detector import ZeltaBiasDetector
from brain.bayesian.engine import run_bayesian_engine
from brain.bayesian.confidence import run_confidence_scorer
from brain.kelly.allocator import run_kelly_allocator
from brain.sharpe.scorer import ZeltaDecisionScorer
from brain.copilot.gemini import ZeltaCopilot

logger = logging.getLogger("zelta.pipeline")


class ZeltaPipeline:
    """
    Central AI Brain Orchestrator (QUELO)

    Flow:
    Market → NLP → Stress → Bias → Bayesian → Confidence → Kelly → Sharpe → Copilot
    """

    def __init__(self):
        # IMPORTANT: use the shared singleton monitor
        self.bayse = monitor
        self.nlp = ZeltaSentimentScorer()
        self.bias = ZeltaBiasDetector()
        self.sharpe = ZeltaDecisionScorer()
        self.copilot = ZeltaCopilot()

    async def _load_news_payload(self, bayse_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        payload = bayse_data.get("news_payload") or bayse_data.get("news") or []

        if payload:
            return payload

        try:
            scraped = await run_scraper()
            return scraped or []
        except Exception as exc:
            logger.exception("Scraper failed: %s", exc)
            return []

    def _validate_wallet(self, wallet_data: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """
        Ensure wallet is always valid (comes from USER).
        Supports both locked_total and locked_amount for compatibility.
        """
        if not wallet_data:
            return {
                "free_cash": 10000.0,
                "locked_total": 0.0,
                "total_balance": 10000.0,
            }

        locked_value = wallet_data.get("locked_total", wallet_data.get("locked_amount", 0.0))

        return {
            "free_cash": float(wallet_data.get("free_cash", 0.0)),
            "locked_total": float(locked_value),
            "total_balance": float(wallet_data.get("total_balance", 0.0)),
        }

    async def run_async(
        self,
        wallet_data: Optional[Dict[str, Any]] = None,
        transactions: Optional[List[Dict[str, Any]]] = None,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()

        try:
            wallet_data = self._validate_wallet(wallet_data)
            transactions = transactions or []
            user_context = user_context or {}

            # 1. PRIMARY SIGNAL
            bayse_data = self.bayse.get_signal()

            # 2. NLP
            news_payload = await self._load_news_payload(bayse_data)
            nlp_data = self.nlp.run(news_payload)
            aggregate_sentiment = nlp_data.get("aggregate_sentiment", 0.0)

            # 3. STRESS
            stress_data = run_stress_index(
                bayse_data,
                aggregate_sentiment,
            )

            # 4. BIAS
            bias_data = self.bias.run(
                stress_data,
                aggregate_sentiment,
                wallet_data,
            )

            # 5. BAYESIAN
            bayesian_data = run_bayesian_engine(
                stress_data,
                bias_data,
            )

            # 6. CONFIDENCE
            confidence_data = run_confidence_scorer(
                bayesian_data,
                stress_data,
                bias_data,
            )

            # 7. KELLY
            kelly_data = run_kelly_allocator(
                bayesian_data,
                confidence_data,
                wallet_data,
            )

            # 8. SHARPE
            sharpe_data = self.sharpe.run(bayesian_data)

            # 9. COPILOT
            explanation = await self.copilot.run(
                {
                    "bayse": bayse_data,
                    "nlp": nlp_data,
                    "stress": stress_data,
                    "bias": bias_data,
                    "decision": bayesian_data,
                    "confidence": confidence_data,
                    "allocation": kelly_data,
                    "sharpe": sharpe_data,
                    "score": sharpe_data,  # backward compatibility
                    "transactions": transactions,
                    "user_context": user_context,
                }
            )

            latency = round(time.time() - start_time, 3)

            return {
                "meta": {
                    "latency_sec": latency,
                    "status": "success",
                },
                "bayse": bayse_data,
                "nlp": nlp_data,
                "stress": stress_data,
                "bias": bias_data,
                "decision": bayesian_data,
                "confidence": confidence_data,
                "allocation": kelly_data,
                "score": sharpe_data,
                "explanation": explanation,
            }

        except Exception as exc:
            logger.exception("Pipeline failed: %s", exc)
            return {
                "meta": {
                    "status": "error",
                    "error": str(exc),
                }
            }

    def run(
        self,
        wallet_data: Optional[Dict[str, Any]] = None,
        transactions: Optional[List[Dict[str, Any]]] = None,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper for environments that are not already running an event loop.

        If you're already inside async code (for example, a FastAPI route),
        call `await run_async(...)` instead of this method.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            raise RuntimeError(
                "run() cannot be used inside an active event loop. "
                "Use `await run_async(...)` instead."
            )

        return asyncio.run(self.run_async(wallet_data, transactions, user_context))
