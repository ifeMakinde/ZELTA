import asyncio
from .client import BayseClient
from .ws import BayseWebSocket

# Nigerian financial market keywords QUELO watches
QUELO_KEYWORDS = ["NGN", "naira", "CBN", "inflation", "MPC", "dollar"]


class LiveStressMonitor:
    def __init__(self):
        self.ws = BayseWebSocket()
        self.client = BayseClient()
        self.market_id = None  # Resolved dynamically at startup

        self.current_signal = {
            "score": 50.0,
            "status": "MODERATE",
            "crowd_yes_price": 0.5,
            "crowd_no_price": 0.5,
            "spread": 0.0,
            "imbalance": 0.5,
            "market_title": "Initialising...",
        }

    def calculate_stress(self, orderbook: dict):
        """
        Converts Bayse orderbook data into QUELO Stress Score (0-100).

        Two signals:
        1. Spread stress — wide spread = high uncertainty = fear
        2. Ask imbalance — more sellers than buyers = crowd panic
        """
        try:
            bids = orderbook.get("bids", [])
            asks = orderbook.get("asks", [])

            if not bids or not asks:
                return

            best_bid = bids[0]["price"]
            best_ask = asks[0]["price"]
            spread = best_ask - best_bid

            # 1. Spread stress: spread of 0.10 = 100% stress
            spread_stress = min(spread * 10, 1.0)

            # 2. Ask imbalance: more ask volume = crowd selling = panic
            # Docs confirmed field is 'quantity' not 'amount'
            bid_vol = sum(b["quantity"] for b in bids[:5])
            ask_vol = sum(a["quantity"] for a in asks[:5])
            total_vol = bid_vol + ask_vol
            imbalance = ask_vol / total_vol if total_vol > 0 else 0.5

            # Final score: spread weighted 70%, imbalance 30%
            score = (spread_stress * 0.7 + imbalance * 0.3) * 100

            # Map score to QUELO's 4 stress levels
            if score >= 80:
                status = "EXTREME PANIC"
            elif score >= 60:
                status = "HIGH STRESS"
            elif score >= 30:
                status = "MODERATE"
            else:
                status = "CALM"

            self.current_signal = {
                "score": round(score, 2),
                "status": status,
                "crowd_yes_price": round(best_bid, 4),
                "crowd_no_price": round(best_ask, 4),
                "spread": round(spread, 4),
                "imbalance": round(imbalance, 4),
                "market_title": self.current_signal.get("market_title", ""),
            }

            print(
                f"[QUELO Stress] Score: {score:.1f} | "
                f"Status: {status} | Spread: {spread:.4f}"
            )

        except Exception as e:
            print(f"⚠️ Stress calculation error: {e}")

    async def resolve_market(self):
        """Find the best Nigerian financial market on Bayse at startup"""
        self.market_id = await self.client.find_market_id(QUELO_KEYWORDS)
        if not self.market_id:
            raise Exception("No active Nigerian financial market found on Bayse")
        print(f"✅ QUELO stress monitor locked to market: {self.market_id}")

    async def start(self):
        """
        Background task — keeps stress signal updated in real time.
        Call this once at app startup.
        """
        # Step 1: find the right Bayse market
        await self.resolve_market()

        # Step 2: connect WebSocket
        await self.ws.connect()
        await self.ws.subscribe_orderbook(self.market_id)

        # Step 3: listen and recalculate on every update
        async for orderbook in self.ws.listen():
            self.calculate_stress(orderbook)

    def get_signal(self) -> dict:
        """Called by brain/pipeline.py to get current stress from Bayse"""
        return self.current_signal


# Singleton — shared across the entire brain
monitor = LiveStressMonitor()
