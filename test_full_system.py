import time
from core.event_bus import EventBus
from core.events import MarketEvent, SignalEvent, OrderEvent, FillEvent
from data.mock_adapter import MockDataAdapter
from strategy.sma_crossover import SMACrossoverStrategy
from risk.manager import RiskManager
from execution.order_manager import OrderManager
from portfolio.manager import PortfolioManager

# 1. Setup Bus
bus = EventBus()

# 2. Setup Components
strategy = SMACrossoverStrategy(bus)
risk_mgr = RiskManager(bus)
exec_mgr = OrderManager(bus)
portfolio = PortfolioManager(bus, initial_cash=100000.0)

# 3. Wire them up
bus.subscribe(MarketEvent, strategy.on_market_event)
bus.subscribe(MarketEvent, portfolio.on_market_event)
bus.subscribe(SignalEvent, risk_mgr.on_signal)
bus.subscribe(OrderEvent, exec_mgr.on_order)
bus.subscribe(FillEvent, portfolio.on_fill)

# Optional: A simple listener to see live prices
def price_printer(event: MarketEvent):
    # Print price only for EURUSD to keep the output clean
    if event.symbol == "EURUSD":
        print(f"[LIVE PRICE] {event.symbol}: {event.last}")

bus.subscribe(MarketEvent, price_printer)

# 4. Start Feed
adapter = MockDataAdapter(bus)
adapter.start()

print("\n--- Running FULL SYSTEM Test for 20 seconds ---")
print("Watch the flow: Data -> Strategy -> Risk -> Execution -> Portfolio\n")

try:
    time.sleep(20)
except KeyboardInterrupt:
    pass
finally:
    adapter.stop()
    print("\nTest Completed.")
