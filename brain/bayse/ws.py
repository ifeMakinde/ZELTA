import asyncio
import json
import websockets


class BayseWebSocket:
    def __init__(self):
        # ✅ Correct WebSocket endpoint
        self.url = "wss://socket.bayse.markets/ws/v1/markets"
        self.ws = None
        self.connected = False

    # ─────────────────────────────
    # CONNECT
    # ─────────────────────────────

    async def connect(self):
        try:
            print("🔌 Connecting to:", self.url)
            self.ws = await websockets.connect(self.url)

            self.connected = True
            print("✅ WebSocket Connected!")

        except Exception as e:
            self.connected = False
            raise Exception(f"WebSocket connection failed: {e}")

    # ─────────────────────────────
    # SUBSCRIBE
    # ─────────────────────────────

    async def subscribe_orderbook(self, market_id, currency="NGN"):
        if not self.connected:
            raise Exception("WebSocket not connected")

        msg = {
            "type": "subscribe",
            "channel": "orderbook",
            "marketIds": [market_id],
            "currency": currency
        }

        await self.ws.send(json.dumps(msg))
        print(f"📡 Subscribed to orderbook → {market_id}")

    # ─────────────────────────────
    # LISTEN (STREAM)
    # ─────────────────────────────

    async def listen(self):
        if not self.connected:
            raise Exception("WebSocket not connected")

        while True:
            try:
                msg = await self.ws.recv()

                # Handle multiple JSON messages in one frame
                messages = msg.split("\n")

                for m in messages:
                    if not m.strip():
                        continue

                    try:
                        data = json.loads(m)

                        # ✅ Main data stream
                        if data.get("type") == "orderbook_update":
                            yield data["data"]["orderbook"]

                        # Optional debug (can remove later)
                        elif data.get("type") in ["subscribed", "info"]:
                            print("ℹ️ WS:", data)

                    except json.JSONDecodeError:
                        print("⚠️ Failed to decode message:", m)

            except websockets.ConnectionClosed:
                print("❌ WebSocket connection closed")
                self.connected = False
                break

            except Exception as e:
                print("⚠️ WebSocket error:", e)
                await asyncio.sleep(1)

    # ─────────────────────────────
    # CLOSE
    # ─────────────────────────────

    async def close(self):
        if self.ws:
            await self.ws.close()
            self.connected = False
            print("🔌 WebSocket closed")