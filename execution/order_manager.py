import time
from core.events import OrderEvent, FillEvent
from data.database import DatabaseManager
from core.notifier import TelegramNotifier

class OrderManager:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.processed_orders = set() 
        self.db = DatabaseManager()
        self.notifier = TelegramNotifier()

    def on_order(self, event: OrderEvent):
        print(f"[EXECUTION] Received order for {event.direction} {event.quantity} {event.symbol}")
        
        if event.client_order_id in self.processed_orders:
            print(f"[EXECUTION] WARNING: Duplicate order detected. Ignoring.")
            return
        
        self.processed_orders.add(event.client_order_id)
        self.db.save_order(event, status="SUBMITTED")
        
        time.sleep(0.1) 
        
        fill_price = event.price if event.price else 1.0
        
        fill_event = FillEvent(
            client_order_id=event.client_order_id,
            broker_order_id="BROKER-" + str(int(time.time())),
            symbol=event.symbol,
            quantity=event.quantity,
            direction=event.direction,
            fill_cost=fill_price,
            commission=0.5 
        )
        
        self.db.save_fill(fill_event)
        
        # Telegram Alert
        msg = f"🚀 <b>TRADE EXECUTED</b>\nSymbol: {event.symbol}\nAction: {event.direction}\nQty: {event.quantity}\nPrice: {fill_price}"
        self.notifier.send_message(msg)
        
        print(f"[EXECUTION] Order FILLED: {event.symbol} at {fill_price}")
        self.event_bus.publish(fill_event)
