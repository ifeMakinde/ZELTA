import asyncio
import time
import hmac
import json
import hashlib
import base64
import httpx
import urllib.parse

from zelta_ai.config.settings import settings
from .ws import BayseWebSocket


class BayseClient:
    def __init__(self):
        self.PUBLIC_KEY = settings.BAYSE_PUBLIC_KEY
        self.SECRET_KEY = settings.BAYSE_PRIVATE_KEY
        self.BASE_URL = "https://relay.bayse.markets"
        self.client = httpx.AsyncClient(timeout=10)
        self.last_request_time = 0
        self.min_interval = 0.2
        self.ws = BayseWebSocket()

    # ── HELPERS ───────────────────────────────────────────────────────────────

    def _get_timestamp(self) -> str:
        # Docs say: Unix timestamp in SECONDS
        return str(int(time.time()))

    def _hash_body(self, body: dict) -> str:
        # Docs say: SHA-256 HEX of body. Empty string if no body.
        if not body:
            return ""
        body_str = json.dumps(body, separators=(",", ":"), sort_keys=True)
        return hashlib.sha256(body_str.encode()).hexdigest()

    def _sign(self, method: str, path: str, timestamp: str, body_hash: str) -> str:
        # Docs say: payload = {timestamp}.{METHOD}.{path}.{bodyHash}
        # Signature = HMAC-SHA256 BASE64-encoded (always base64)
        payload = f"{timestamp}.{method}.{path}.{body_hash}"
        digest = hmac.new(
            self.SECRET_KEY.encode(),
            payload.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(digest).decode()

    # ── REQUEST CORE ──────────────────────────────────────────────────────────

    async def _request(
        self,
        method: str,
        path: str,
        body: dict = None,
        params=None,
        authenticated: bool = False,
        retries: int = 3,
    ):
        """
        authenticated=False → only X-Public-Key (read endpoints)
        authenticated=True  → X-Public-Key + X-Timestamp + X-Signature (write endpoints)
        """
        body = body or {}

        # Build sign path including query string
        sign_path = path
        if params:
            if isinstance(params, list):
                qs = urllib.parse.urlencode(params)
            else:
                qs = urllib.parse.urlencode(params, doseq=True)
            sign_path = f"{path}?{qs}"

        for attempt in range(retries):
            try:
                now = time.time()
                wait = self.min_interval - (now - self.last_request_time)
                if wait > 0:
                    await asyncio.sleep(wait)
                self.last_request_time = time.time()

                # Read auth — just public key
                headers = {
                    "X-Public-Key": self.PUBLIC_KEY,
                    "Content-Type": "application/json",
                }

                # Write auth — add timestamp + signature
                if authenticated:
                    timestamp = self._get_timestamp()
                    body_hash = self._hash_body(body if method != "GET" else {})
                    signature = self._sign(method, sign_path, timestamp, body_hash)
                    headers["X-Timestamp"] = timestamp
                    headers["X-Signature"] = signature

                response = await self.client.request(
                    method=method,
                    url=self.BASE_URL + path,
                    headers=headers,
                    params=params,
                    json=body if method != "GET" else None,
                )

                if response.status_code != 200:
                    print(f"[Bayse Error {response.status_code}]: {response.text}")

                response.raise_for_status()
                return response.json()

            except Exception as e:
                if attempt == retries - 1:
                    raise Exception(f"Bayse request failed after {retries} retries: {e}")
                await asyncio.sleep(0.5 * (attempt + 1))

    # ── PUBLIC ENDPOINTS (read auth only) ────────────────────────────────────

    async def get_events(self) -> dict:
        """All active prediction market events — PRIMARY data source for QUELO"""
        return await self._request("GET", "/v1/pm/events")

    async def get_event(self, event_id: str) -> dict:
        return await self._request("GET", f"/v1/pm/events/{event_id}")

    async def get_markets(self, event_id: str) -> list:
        data = await self.get_event(event_id)
        return data.get("markets") or data.get("data", {}).get("markets", [])

    async def get_ticker(self, market_id: str, outcome: str = "YES") -> dict:
        return await self._request(
            "GET",
            f"/v1/pm/markets/{market_id}/ticker",
            params={"outcome": outcome, "currency": "NGN"},
        )

    async def get_order_books(self, outcome_ids: list) -> dict:
        params = [("outcomeId[]", oid) for oid in outcome_ids]
        params.append(("currency", "NGN"))
        return await self._request("GET", "/v1/pm/books", params=params)

    async def get_portfolio(self) -> dict:
        """Requires read auth — X-Public-Key only"""
        return await self._request(
            "GET", "/v1/pm/portfolio", authenticated=True
        )

    async def find_market_id(
        self, preferences: list = None
    ) -> str | None:
        """
        Finds an active Nigerian financial market on Bayse.
        Searches for QUELO-relevant keywords first.
        """
        preferences = preferences or [
            "NGN", "naira", "CBN", "inflation",
            "MPC", "interest rate", "dollar"
        ]
        events_data = await self.get_events()
        event_list = (
            events_data
            if isinstance(events_data, list)
            else events_data.get("events", [])
        )

        # Strategy 1: keyword match
        for pref in preferences:
            for event in event_list:
                if pref.lower() in event.get("title", "").lower():
                    markets = await self.get_markets(event.get("id"))
                    if markets:
                        market = markets[0]
                        print(
                            f"✅ Found market ({pref}): "
                            f"{market.get('title')} → {market.get('id')}"
                        )
                        return market.get("id")

        # Strategy 2: first available fallback
        for event in event_list[:5]:
            markets = await self.get_markets(event.get("id"))
            if markets:
                market = markets[0]
                print(f"✅ Fallback market: {market.get('title')} → {market.get('id')}")
                return market.get("id")

        return None

    # ── WRITE ENDPOINTS (full auth) ───────────────────────────────────────────

    async def place_order(
        self,
        event_id: str,
        market_id: str,
        outcome_id: str,
        amount: float,
        price: float,
    ) -> dict:
        return await self._request(
            "POST",
            f"/v1/pm/events/{event_id}/markets/{market_id}/orders",
            body={
                "side": "BUY",
                "outcomeId": outcome_id,
                "amount": amount,
                "type": "LIMIT",
                "price": price,
                "currency": "NGN",
            },
            authenticated=True,
        )

    # ── WEBSOCKET SHORTCUTS ───────────────────────────────────────────────────

    async def connect_ws(self):
        await self.ws.connect()

    async def subscribe_orderbook(self, market_id: str):
        await self.ws.subscribe_orderbook(market_id)

    async def listen_ws(self):
        async for msg in self.ws.listen():
            yield msg

    async def close(self):
        await self.client.aclose()
        await self.ws.close()
