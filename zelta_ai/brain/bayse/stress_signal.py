import asyncio
import time
from typing import Dict, Optional

from brain.bayse.client import BayseClient


class LiveStressMonitor:
    def __init__(self):
        self.client = BayseClient()

        self.current_signal = {
            "score": 50.0,
            "status": "MODERATE",
            "crowd_yes_price": 0.5,
            "crowd_no_price": 0.5,
            "spread": 0.0,
            "imbalance": 0.5,
            "market_title": "Initializing...",
            "market_id": None,
            "outcome": "YES",
            "mid_price": 0.5,
            "best_bid": 0.5,
            "best_ask": 0.5,
            "last_price": 0.5,
            "volume24h": 0,
            "trade_count_24h": 0,
            "source": "Bayse Prediction Markets",
            "updated_at": None,
        }

        # Keeps older code from breaking if it checks ws.connected.
        self.ws = type("WS", (), {"connected": True})()

    # ── CORE LOGIC ─────────────────────────────────────────

    def calculate_stress(self, yes_price: float, no_price: float) -> float:
        """
        Extreme pricing = higher stress.
        This uses the YES/NO crowd imbalance.
        """
        distance = abs(yes_price - 0.5) * 2
        spread = abs(yes_price - no_price)

        stress = (distance * 0.7 + spread * 0.3) * 100
        return round(min(100, max(0, stress)), 2)

    def classify(self, score: float) -> str:
        if score >= 80:
            return "EXTREME PANIC"
        elif score >= 60:
            return "HIGH STRESS"
        elif score >= 30:
            return "MODERATE"
        else:
            return "CALM"

    @staticmethod
    def _extract_yes_price(ticker: Dict) -> float:
        """
        Bayse ticker returns outcome-level stats:
        lastPrice, bestBid, bestAsk, midPrice, spread, etc.
        Use the best available price estimate for YES.
        """
        candidates = (
            ticker.get("midPrice"),
            ticker.get("bestBid"),
            ticker.get("bestAsk"),
            ticker.get("lastPrice"),
        )

        for value in candidates:
            try:
                if value is not None:
                    price = float(value)
                    if price > 0:
                        return price
            except Exception:
                continue

        return 0.5

    # ── FETCH ──────────────────────────────────────────────

    async def fetch_once(self):
        try:
            best = await self.client.find_best_market()

            if not best:
                print("[Bayse] No market found")
                return

            market_id = best["market_id"]
            title = best["event_title"]

            # Bayse ticker is outcome-level, and docs support outcome or outcomeId.
            ticker = await self.client.get_ticker(market_id, outcome="YES")

            yes_price = self._extract_yes_price(ticker)

            # Normalize if anything odd comes back in 0–100 scale.
            if yes_price > 1.0:
                yes_price /= 100.0

            yes_price = min(max(yes_price, 0.0), 1.0)
            no_price = round(1.0 - yes_price, 4)

            score = self.calculate_stress(yes_price, no_price)
            status = self.classify(score)

            self.current_signal = {
                "score": score,
                "status": status,
                "crowd_yes_price": round(yes_price, 4),
                "crowd_no_price": no_price,
                "spread": round(abs(yes_price - no_price), 4),
                "imbalance": round(abs(yes_price - 0.5) * 2, 4),
                "market_title": title,
                "market_id": market_id,
                "outcome": ticker.get("outcome", "YES"),
                "mid_price": ticker.get("midPrice"),
                "best_bid": ticker.get("bestBid"),
                "best_ask": ticker.get("bestAsk"),
                "last_price": ticker.get("lastPrice"),
                "volume24h": ticker.get("volume24h", 0),
                "trade_count_24h": ticker.get("tradeCount24h", 0),
                "source": "Bayse Prediction Markets",
                "updated_at": time.time(),
            }

            print(
                f"[Bayse Monitor] {title[:50]} | "
                f"YES: {yes_price:.3f} NO: {no_price:.3f} | "
                f"Stress: {score:.1f} ({status})"
            )

        except Exception as e:
            print(f"[Bayse Monitor] Fetch error: {e}")

    # ── LOOP ───────────────────────────────────────────────

    async def start(self):
        """
        Poll Bayse every 60 seconds.
        The first fetch happens immediately.
        """
        print("[Bayse Monitor] Starting REST polling...")
        while True:
            await self.fetch_once()
            await asyncio.sleep(60)

    def get_signal(self) -> Dict:
        return self.current_signal


# Singleton shared across app, routes, and pipeline.
monitor = LiveStressMonitor()