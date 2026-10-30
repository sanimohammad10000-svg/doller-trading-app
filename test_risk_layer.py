import time
from core.event_bus import EventBus
from core.events import MarketEvent, SignalEvent, OrderEvent, RejectEvent
from data.mock_adapter import MockDataAdapter
from strategy.sma_crossover import SMACrossoverStrategy
from risk.manager import RiskManager

# 1. Setup Bus
bus = EventBus()

# 2. Setup Strategy
strategy = SMACrossoverStrategy(bus)
bus.subscribe(MarketEvent, strategy.on_market_event)

# 3. Setup Risk Manager
risk_mgr = RiskManager(bus)
bus.subscribe(SignalEvent, risk_mgr.on_signal)

# 4. Create Execution Listener (To see the approved orders)
def order_listener(event: OrderEvent):
    print(f"--> [EXECUTION ENGINE] Received ORDER: {event.direction} {event.quantity} {event.symbol} (ID: {event.client_order_id[:8]})")

def reject_listener(event: RejectEvent):
    print(f"--> [ALERT] Order Rejected for {event.symbol}: {event.reason}")

bus.subscribe(OrderEvent, order_listener)
bus.subscribe(RejectEvent, reject_listener)

# 5. Start Feed
adapter = MockDataAdapter(bus)
adapter.start()

# 6. Run for 20 seconds
print("Running Risk Management Test for 20 seconds...")
try:
    time.sleep(20)
except KeyboardInterrupt:
    pass
finally:
    adapter.stop()
    print("Test Completed.")
