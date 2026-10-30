import time
from core.event_bus import EventBus
from core.events import MarketEvent, SignalEvent, OrderEvent, FillEvent
from strategy.sma_crossover import SMACrossoverStrategy
from risk.manager import RiskManager
from execution.order_manager import OrderManager
from data.database import DatabaseManager

# 1. Setup
bus = EventBus()
strategy = SMACrossoverStrategy(bus)
risk_mgr = RiskManager(bus)
exec_mgr = OrderManager(bus)

bus.subscribe(MarketEvent, strategy.on_market_event)
bus.subscribe(SignalEvent, risk_mgr.on_signal)
bus.subscribe(OrderEvent, exec_mgr.on_order)

# 2. Publish some dummy data to trigger signals and trades
print("Generating dummy market data to trigger trades...")
for i in range(50):
    # Create a wave in price to force crossover
    import math
    price = 1.0500 * (1 + math.sin(i * 0.5) * 0.01)
    
    event = MarketEvent(
        symbol="EURUSD", 
        asset_class="FOREX", 
        bid=price-0.0001, 
        ask=price+0.0001, 
        last=price, 
        volume=100, 
        source="test_db"
    )
    bus.publish(event)
    time.sleep(0.01) # Small delay

print("\n--- Checking Database ---")
db = DatabaseManager()
with db._get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders")
    orders_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM fills")
    fills_count = cursor.fetchone()[0]
    
    print(f"Total Orders in DB: {orders_count}")
    print(f"Total Fills in DB: {fills_count}")

print("\nTest Completed. You can check the file 'doller.db' in D:\\doller folder.")
