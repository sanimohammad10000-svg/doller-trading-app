import csv
import math
import time
from core.event_bus import EventBus
from core.events import MarketEvent, SignalEvent, OrderEvent, FillEvent
from strategy.sma_crossover import SMACrossoverStrategy
from risk.manager import RiskManager
from execution.order_manager import OrderManager
from portfolio.manager import PortfolioManager
from data.historical_loader import HistoricalDataLoader
from backtest.engine import BacktestEngine

# 1. Generate Dummy Historical Data (CSV)
def generate_dummy_data(filename="historical_data.csv"):
    print("Generating dummy historical data...")
    with open(filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['symbol', 'asset_class', 'bid', 'ask', 'last', 'volume'])
        for i in range(500): # 500 ticks
            wave = math.sin(i * 0.1) * 0.005 # Smooth wave
            price = 1.0500 * (1 + wave)
            writer.writerow(['EURUSD', 'FOREX', round(price - 0.0001, 5), round(price + 0.0001, 5), round(price, 5), 100])

# 2. Setup System
bus = EventBus()
strategy = SMACrossoverStrategy(bus)
risk_mgr = RiskManager(bus)
exec_mgr = OrderManager(bus)
portfolio = PortfolioManager(bus, initial_cash=100000.0)

# 3. Wire up
bus.subscribe(MarketEvent, strategy.on_market_event)
bus.subscribe(MarketEvent, portfolio.on_market_event)
bus.subscribe(SignalEvent, risk_mgr.on_signal)
bus.subscribe(OrderEvent, exec_mgr.on_order)
bus.subscribe(FillEvent, portfolio.on_fill)

# 4. Run Backtest
generate_dummy_data()
loader = HistoricalDataLoader("historical_data.csv")
engine = BacktestEngine(bus, loader)

print("\n--- Starting BACKTEST ---")
engine.run()

print("\n--- Final Portfolio Status ---")
print(f"Final Cash: ${portfolio.cash:.2f}")
equity = portfolio.cash
for sym, pos in portfolio.positions.items():
    if pos.quantity != 0:
         equity += pos.quantity * portfolio.last_prices.get(sym, pos.average_price)
print(f"Final Equity: ${equity:.2f}")
