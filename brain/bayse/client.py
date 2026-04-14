import asyncio
import time
import hmac
import json
import hashlib
import base64
import httpx

from config.settings import settings
from .ws import BayseWebSocket


class BayseClient:
    def __init__(self):
        self.PUBLIC_KEY = settings.BAYSE_PUBLIC_KEY
        self.SECRET_KEY = settings.BAYSE_PRIVATE_KEY
        self.BASE_URL = "https://relay.bayse.markets"

        self.client = httpx.AsyncClient(timeout=10)

        self.last_request_time = 0
        self.min_interval = 0.2

        # ✅ FIXED: WebSocket does NOT need auth
        self.ws = BayseWebSocket()

    # ─────────────────────────────
    # HELPERS
    # ─────────────────────────────

    def _get_timestamp(self):
        return str(int(time.time()))

    def _hash_body(self, body: dict):
        if not body:
            return hashlib.sha256(b"").hexdigest()

        body_str = json.dumps(body, separators=(",", ":"), sort_keys=True)
        return hashlib.sha256(body_str.encode()).hexdigest()

    def _sign_payload(self, method, path, timestamp, body_hash, use_base64=False):
        payload = f"{timestamp}.{method}.{path}.{body_hash}"

        digest = hmac.new(
            self.SECRET_KEY.encode(),
            payload.encode(),
            hashlib.sha256
        ).digest()

        return base64.b64encode(digest).decode() if use_base64 else digest.hex()

    # ─────────────────────────────
    # REQUEST CORE
    # ─────────────────────────────

    async def _request(
        self,
        method: str,
        path: str,
        body: dict = None,
        params=None,
        use_base64_sig=False,
        retries=3,
    ):
        body = body or {}

        for attempt in range(retries):
            try:
                # rate limiting
                now = time.time()
                wait = self.min_interval - (now - self.last_request_time)
                if wait > 0:
                    await asyncio.sleep(wait)
                self.last_request_time = time.time()

                timestamp = self._get_timestamp()
                body_hash = self._hash_body(body)

                signature = self._sign_payload(
                    method,
                    path,
                    timestamp,
                    body_hash,
                    use_base64_sig
                )

                headers = {
                    "X-API-KEY": self.PUBLIC_KEY,
                    "X-TIMESTAMP": timestamp,
                    "X-SIGNATURE": signature,
                    "Content-Type": "application/json",
                }

                response = await self.client.request(
                    method=method,
                    url=self.BASE_URL + path,
                    headers=headers,
                    params=params,
                    json=body if method != "GET" else None,
                )

                response.raise_for_status()
                return response.json()

            except Exception as e:
                if attempt == retries - 1:
                    raise Exception(f"Bayse request failed: {e}")
                await asyncio.sleep(0.5 * (attempt + 1))

    # ─────────────────────────────
    # REST ENDPOINTS
    # ─────────────────────────────

    async def get_events(self):
        return await self._request("GET", "/v1/pm/events")

    async def get_event(self, event_id):
        return await self._request("GET", f"/v1/pm/events/{event_id}")

    async def get_markets(self, event_id):
        data = await self.get_event(event_id)
        return data.get("markets") or data.get("data", {}).get("markets", [])

    async def get_ticker(self, market_id):
        return await self._request(
            "GET",
            f"/v1/pm/markets/{market_id}/ticker",
            params={"currency": "NGN"}
        )

    async def get_order_books(self, outcome_ids):
        return await self._request(
            "GET",
            "/v1/pm/books",
            params=[("outcomeId[]", oid) for oid in outcome_ids]
        )

    async def place_order(self, market_id, event_id, outcome_id, amount, price):
        return await self._request(
            "POST",
            f"/v1/pm/events/{event_id}/markets/{market_id}/orders",
            body={
                "side": "BUY",
                "outcomeId": outcome_id,
                "amount": amount,
                "type": "LIMIT",
                "price": price,
                "currency": "NGN"
            },
            use_base64_sig=True
        )

    # ─────────────────────────────
    # WEBSOCKET SHORTCUTS (FIXED)
    # ─────────────────────────────

    async def connect_ws(self):
        await self.ws.connect()

    async def subscribe_orderbook(self, market_id):
        """
        Subscribe to live orderbook updates (correct Bayse format)
        """
        await self.ws.subscribe_orderbook(market_id)

    async def listen_ws(self):
        async for msg in self.ws.listen():
            yield msg

    async def close(self):
        await self.client.aclose()
        await self.ws.close()