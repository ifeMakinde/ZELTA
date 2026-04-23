import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import httpx

from config.settings import settings


class BayseClient:
    def __init__(self):
        # Public Bayse endpoints do not require auth, but keeping the key
        # available makes it easy to extend later.
        self.PUBLIC_KEY = getattr(settings, "BAYSE_PUBLIC_KEY", None)
        self.BASE_URL = "https://relay.bayse.markets"

        self.client = httpx.AsyncClient(timeout=15)
        self.min_interval = 0.2
        self.last_request_time = 0.0

        print("[BayseClient] Initialized")

    # ───────────────────────── HELPERS ─────────────────────────

    def _rate_limit(self) -> float:
        now = time.time()
        wait = self.min_interval - (now - self.last_request_time)
        self.last_request_time = time.time()
        return max(0.0, wait)

    @staticmethod
    def _normalize_events_payload(data: Any) -> List[Dict[str, Any]]:
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("events") or data.get("data") or []
        return []

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        try:
            if value is None or value == "":
                return default
            return float(value)
        except Exception:
            return default

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Union[Dict[str, Any], List[Tuple[str, Any]]]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Any:
        for attempt in range(1, 4):
            try:
                wait = self._rate_limit()
                if wait > 0:
                    await asyncio.sleep(wait)

                url = self.BASE_URL + path
                print(f"\n[BayseClient] Attempt {attempt}")
                print(f"[BayseClient] {method} {url}")
                print(f"[BayseClient] Params: {params}")

                headers = {}
                if self.PUBLIC_KEY:
                    headers["X-Public-Key"] = self.PUBLIC_KEY

                response = await self.client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_body,
                )

                print(f"[BayseClient] Status: {response.status_code}")

                if response.status_code != 200:
                    print(f"[BayseClient] ERROR: {response.text}")

                response.raise_for_status()
                data = response.json()

                print("[BayseClient] RAW RESPONSE:")
                try:
                    print(json.dumps(data, indent=2)[:1000])
                except Exception:
                    print(str(data)[:1000])

                return data

            except Exception as e:
                print(f"[BayseClient] Attempt {attempt} failed: {e}")
                await asyncio.sleep(0.5 * attempt)

        raise Exception("Bayse request failed after 3 retries")

    # ───────────────────────── PUBLIC ENDPOINTS ─────────────────────────

    async def get_events(self) -> List[Dict[str, Any]]:
        data = await self._request("GET", "/v1/pm/events")
        events = self._normalize_events_payload(data)
        print(f"[BayseClient] Events found: {len(events)}")
        return events

    async def get_event(self, event_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/v1/pm/events/{event_id}")

    def _score_event(self, event: Dict[str, Any]) -> float:
        """
        Simple deterministic ranking to choose a useful market.
        """
        keywords = [
            "ngn",
            "naira",
            "inflation",
            "dollar",
            "cbn",
            "interest rate",
            "mpc",
            "economy",
            "exchange rate",
            "fx",
            "usd",
        ]

        title = (event.get("title") or event.get("name") or "").lower()
        description = (event.get("description") or "").lower()
        category = (event.get("category") or "").lower()
        text = f"{title} {description} {category}"

        score = 0.0

        for k in keywords:
            if k in text:
                score += 2.5

        if category in {"economics", "finance", "politics", "business"}:
            score += 1.0

        liquidity = self._safe_float(event.get("liquidity"), 0.0)
        score += min(liquidity / 1_000_000, 3.0)

        if event.get("markets"):
            score += 0.5

        return score

    async def find_best_market(self) -> Optional[Dict[str, Any]]:
        """
        Returns a small dict with the best event + market candidate.
        """
        events = await self.get_events()

        if not events:
            print("[BayseClient] ❌ No events returned")
            return None

        best: Optional[Dict[str, Any]] = None
        best_score = -1.0

        for event in events:
            markets = event.get("markets", [])
            if not markets:
                continue

            market = markets[0]
            market_id = market.get("id")
            if not market_id:
                continue

            score = self._score_event(event)
            if score > best_score:
                best_score = score
                best = {
                    "event_id": event.get("id"),
                    "event_title": event.get("title") or event.get("name") or event.get("description") or "Unknown",
                    "market_id": market_id,
                    "liquidity": event.get("liquidity", 0),
                    "score": best_score,
                    "market": market,
                    "event": event,
                }

        if best:
            print(
                f"[BayseClient] ✅ Best market: {best['market_id']} "
                f"({best['event_title'][:70]})"
            )
            return best

        print("[BayseClient] ❌ No markets found anywhere")
        return None

    async def find_market_id(self) -> Optional[str]:
        best = await self.find_best_market()
        return best["market_id"] if best else None

    async def get_ticker(
        self,
        market_id: str,
        outcome: str = "YES",
        outcome_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Bayse ticker is outcome-level.
        Use `outcome="YES"` or `outcome="NO"` for the public ticker endpoint.
        """
        if not market_id:
            raise ValueError("market_id is required")

        params: Dict[str, Any] = {}
        if outcome_id:
            params["outcomeId"] = outcome_id
        else:
            params["outcome"] = outcome

        return await self._request(
            "GET",
            f"/v1/pm/markets/{market_id}/ticker",
            params=params,
        )

    async def get_order_books(
        self,
        outcome_ids: Sequence[str],
        depth: int = 10,
        currency: str = "NGN",
    ) -> Any:
        if not outcome_ids:
            raise ValueError("outcome_ids is required")

        params: List[Tuple[str, Any]] = [("outcomeId[]", oid) for oid in outcome_ids]
        params.append(("depth", depth))
        params.append(("currency", currency))

        return await self._request("GET", "/v1/pm/books", params=params)

    async def get_trades(
        self,
        market_id: Optional[str] = None,
        limit: int = 50,
        trade_id: Optional[str] = None,
    ) -> Any:
        params: Dict[str, Any] = {"limit": limit}
        if market_id:
            params["marketId"] = market_id
        if trade_id:
            params["id"] = trade_id

        return await self._request("GET", "/v1/pm/trades", params=params)

    async def close(self):
        await self.client.aclose()
        print("[BayseClient] Closed connection")


# ── LOCAL TEST RUNNER ─────────────────────────────────────────────

async def _test():
    print("\n🚀 BAYSE CLIENT TEST START\n")

    client = BayseClient()

    try:
        events = await client.get_events()
        print(f"\n📦 EVENTS COUNT: {len(events)}")

        if events:
            print("\n🧪 Sample Event:")
            try:
                print(json.dumps(events[0], indent=2)[:800])
            except Exception:
                print(str(events[0])[:800])

        best = await client.find_best_market()
        market_id = best["market_id"] if best else None
        print(f"\n🎯 Market ID Found: {market_id}")

        if market_id:
            ticker_yes = await client.get_ticker(market_id, outcome="YES")
            print("\n📊 TICKER (YES):")
            try:
                print(json.dumps(ticker_yes, indent=2)[:800])
            except Exception:
                print(str(ticker_yes)[:800])

            ticker_no = await client.get_ticker(market_id, outcome="NO")
            print("\n📊 TICKER (NO):")
            try:
                print(json.dumps(ticker_no, indent=2)[:800])
            except Exception:
                print(str(ticker_no)[:800])

    finally:
        await client.close()

    print("\n✅ BAYSE TEST COMPLETE\n")


if __name__ == "__main__":
    asyncio.run(_test())