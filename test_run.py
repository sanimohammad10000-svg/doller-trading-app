from core.events import MarketEvent
from core.event_bus import EventBus
from datetime import datetime

def my_strategy(event):
    print(f'[STRATEGY] Received Market Data for {event.symbol} at price: {event.last}')

# Create Bus and subscribe
bus = EventBus()
bus.subscribe(MarketEvent, my_strategy)

# Publish a test market event
test_event = MarketEvent(symbol='EURUSD', asset_class='FOREX', bid=1.0500, ask=1.0502, last=1.0501, volume=100, source='test')
bus.publish(test_event)
