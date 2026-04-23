# bayse/ws.py
import json
import websockets


class BayseWebSocket:
    def __init__(self):
        self.url = "wss://socket.bayse.markets/ws/v1/markets"
        self.ws = None
        self.connected = False

    async def connect(self):
        self.ws = await websockets.connect(self.url)
        self.connected = True

    async def subscribe_orderbook(self, market_id: str):
        msg = {
            "type": "subscribe",
            "channel": "orderbook",
            "marketIds": [market_id],
            "currency": "NGN",
        }
        await self.ws.send(json.dumps(msg))

    async def listen(self):
        while True:
            raw = await self.ws.recv()
            data = json.loads(raw)

            if data.get("type") == "orderbook_update":
                yield data.get("data", {}).get("orderbook", {})

    async def close(self):
        if self.ws:
            await self.ws.close()