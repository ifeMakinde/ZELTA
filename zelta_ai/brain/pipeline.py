# brain/pipeline.py

import asyncio
import time
from typing import Any, Dict, Optional

from bayse.stress_signal import LiveStressMonitor
from nlp.scraper import run_scraper
from nlp.scorer import ZeltaSentimentScorer
from stress.index import run_stress_index
from bias.detector import ZeltaBiasDetector
from bayesian.engine import run_bayesian_engine
from bayesian.confidence import run_confidence_scorer
from kelly.allocator import run_kelly_allocator
from sharpe.scorer import ZeltaDecisionScorer
from copilot.gemini import ZeltaCopilot


class ZeltaPipeline:
    """
    Central AI Brain Orchestrator (QUELO)

    Flow:
    Market → NLP → Stress → Bias → Bayesian → Confidence → Kelly → Sharpe → Copilot
    """

    def __init__(self):
        self.bayse = LiveStressMonitor()
        self.nlp = ZeltaSentimentScorer()
        self.bias = ZeltaBiasDetector()
        self.sharpe = ZeltaDecisionScorer()
        self.copilot = ZeltaCopilot()

    # ─────────────────────────────────────────────

    async def _load_news_payload(self, bayse_data: Dict[str, Any]) -> list:
        payload = bayse_data.get("news_payload") or bayse_data.get("news") or []

        if payload:
            return payload

        try:
            return await run_scraper()
        except Exception as exc:
            print(f"[QUELO Pipeline] Scraper failed: {exc}")
            return []

    # ─────────────────────────────────────────────

    def _validate_wallet(self, wallet_data: Optional[Dict]) -> Dict:
        """
        Ensure wallet is always valid (comes from USER)
        """
        if not wallet_data:
            return {
                "free_cash": 10000.0,
                "locked_total": 0.0,
                "total_balance": 10000.0,
            }

        return {
            "free_cash": float(wallet_data.get("free_cash", 0.0)),
            "locked_total": float(wallet_data.get("locked_total", 0.0)),
            "total_balance": float(wallet_data.get("total_balance", 0.0)),
        }

    # ─────────────────────────────────────────────

    async def run_async(
        self,
        wallet_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:

        start_time = time.time()

        try:
            # ── 0. USER WALLET ───────────────────────────────
            wallet_data = self._validate_wallet(wallet_data)

            # ── 1. PRIMARY SIGNAL ────────────────────────────
            bayse_data = self.bayse.get_signal()

            # ── 2. NLP ──────────────────────────────────────
            news_payload = await self._load_news_payload(bayse_data)
            nlp_data = self.nlp.run(news_payload)

            # ── 3. STRESS ───────────────────────────────────
            stress_data = run_stress_index(
                bayse_data,
                nlp_data["aggregate_sentiment"]
            )

            # ── 4. BIAS ─────────────────────────────────────
            bias_data = self.bias.run(
                stress_data,
                nlp_data["aggregate_sentiment"],
                wallet_data,
            )

            # ── 5. BAYESIAN ────────────────────────────────
            bayesian_data = run_bayesian_engine(
                stress_data,
                bias_data
            )

            # ── 6. CONFIDENCE ──────────────────────────────
            confidence_data = run_confidence_scorer(
                bayesian_data,
                stress_data,
                bias_data,
            )

            # ── 7. KELLY ───────────────────────────────────
            kelly_data = run_kelly_allocator(
                bayesian_data,
                confidence_data,
                wallet_data
            )

            # ── 8. SHARPE ──────────────────────────────────
            sharpe_data = self.sharpe.run(bayesian_data)

            # ── 9. COPILOT (ASYNC SAFE) ────────────────────
            explanation = await self.copilot.run({
                "bayse": bayse_data,
                "nlp": nlp_data,
                "stress": stress_data,
                "bias": bias_data,
                "decision": bayesian_data,
                "confidence": confidence_data,
                "kelly": kelly_data,
                "sharpe": sharpe_data,
            })

            latency = round(time.time() - start_time, 3)

            return {
                "meta": {
                    "latency_sec": latency,
                    "status": "success"
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

        except Exception as e:
            return {
                "meta": {
                    "status": "error",
                    "error": str(e)
                }
            }

    # ─────────────────────────────────────────────

    def run(self, wallet_data: Optional[Dict] = None) -> Dict[str, Any]:
        return asyncio.run(self.run_async(wallet_data))