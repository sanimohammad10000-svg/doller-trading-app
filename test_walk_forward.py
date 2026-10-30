import sys
import os
import math
import time
from core.event_bus import EventBus
from core.events import MarketEvent, SignalEvent, OrderEvent, FillEvent
from strategy.rsi_strategy import RSIStrategy
from risk.manager import RiskManager
from execution.order_manager import OrderManager
from portfolio.manager import PortfolioManager
from backtest.walk_forward import WalkForwardEngine

def generate_historical_events(num_events=1000):
    events = []
    for i in range(num_events):
        wave = math.sin(i * 0.1) * 0.005
        price = 1.0500 * (1 + wave)
        event = MarketEvent(
            symbol="EURUSD", 
            asset_class="FOREX", 
            bid=price-0.0001, 
            ask=price+0.0001, 
            last=price, 
            volume=100, 
            source="historical_test"
        )
        events.append(event)
    return events

# Setup
bus = EventBus()
strategy = RSIStrategy(bus)
risk_mgr = RiskManager(bus)
exec_mgr = OrderManager(bus)
portfolio = PortfolioManager(bus, initial_cash=100000.0)

bus.subscribe(MarketEvent, strategy.on_market_event)
bus.subscribe(MarketEvent, portfolio.on_market_event)
bus.subscribe(SignalEvent, risk_mgr.on_signal)
bus.subscribe(OrderEvent, exec_mgr.on_order)
bus.subscribe(FillEvent, portfolio.on_fill)

# Generate Data & Run WFA
events = generate_historical_events(1000)
wfa = WalkForwardEngine(bus, events)

print("\n--- Starting Walk-Forward Analysis ---")
wfa.run(num_windows=5)

print("\n--- Final Portfolio Status ---")
print(f"Final Equity: ${portfolio.cash + sum([pos.quantity * portfolio.last_prices.get(sym, pos.average_price) for sym, pos in portfolio.positions.items()]):,.2f}")
