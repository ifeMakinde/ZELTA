import asyncio
from brain.bayse.client import BayseClient


def extract_list(response):
    """
    Safely extract list from API response.
    Handles cases where response is already a list or a dict containing a list.
    """
    if not response:
        return []

    # If the API already returned a list, just return it
    if isinstance(response, list):
        return response

    # If it's a dictionary, look for common data keys
    if isinstance(response, dict):
        return (
                response.get("data")
                or response.get("events")
                or response.get("markets")
                or response.get("items")
                or []
        )

    return []


async def test():
    client = BayseClient()

    try:
        print("\n🚀 Testing Bayse API...\n")

        # ─────────────────────────────
        # 1. EVENTS
        # ─────────────────────────────
        events = await client.get_events()
        event_list = extract_list(events)

        print(f"🔥 Found {len(event_list)} events")

        if not event_list:
            print("⚠️ No events found — check your API keys or connectivity.")
            return

        # Pick the first event
        event = event_list[0]
        event_id = event.get("id")
        # Use .get('title') as seen in the Bayse JSON structure
        print(f"📌 Using event: {event.get('title', 'Unknown Title')} ({event_id})")

        if not event_id:
            print("❌ Event ID missing — cannot continue")
            return

        # ─────────────────────────────
        # 2. MARKETS
        # ─────────────────────────────
        # In your previous client fix, get_markets already extracts the list
        markets = await client.get_markets(event_id)
        market_list = extract_list(markets)

        print(f"📊 Found {len(market_list)} markets")

        if not market_list:
            print("⚠️ No markets found for this event")
            return

        # Pick the first market
        market = market_list[0]
        market_id = market.get("id")

        # Bayse markets typically use 'title' for the specific outcome name
        market_name = market.get("title") or market.get("outcome1Label") or "Unknown Market"
        print(f"🎯 Using market: {market_name} ({market_id})")

        if not market_id:
            print("❌ Market ID missing — cannot continue")
            return

        # ─────────────────────────────
        # 3. TICKER
        # ─────────────────────────────
        try:
            ticker = await client.get_ticker(market_id)
            print("\n⚡ TICKER DATA:")
            print(ticker)
        except Exception as e:
            print(f"\n⚠️ Ticker failed: {e}")

        # ─────────────────────────────
        # 4. ORDER BOOK
        # ─────────────────────────────
        try:
            order_book = await client.get_order_book(market_id)
            print("\n📚 ORDER BOOK:")
            print(order_book)
        except Exception as e:
            print(f"\n⚠️ Order book failed: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(test())