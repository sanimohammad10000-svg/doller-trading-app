import time
from core.event_bus import EventBus
from core.events import MarketEvent
from data.mock_adapter import MockDataAdapter

# 1. Setup Bus
bus = EventBus()

# 2. Define a handler (Subscriber)
def price_printer(event: MarketEvent):
    print(f"[{event.source.upper()}] {event.asset_class} | {event.symbol} -> Bid: {event.bid} | Ask: {event.ask}")

# 3. Subscribe to MarketEvent
bus.subscribe(MarketEvent, price_printer)

# 4. Start the Mock Feed
adapter = MockDataAdapter(bus)
adapter.start()

# 5. Let it run for 10 seconds, then stop
try:
    time.sleep(10)
except KeyboardInterrupt:
    pass
finally:
    adapter.stop()
    print("Test Completed.")
