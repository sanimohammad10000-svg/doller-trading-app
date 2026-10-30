import random
import time
import threading
import math
from core.event_bus import EventBus
from core.events import MarketEvent
from data.normalizer import DataNormalizer

class MockDataAdapter:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.is_running = False
        self.start_time = time.time()
        self.symbols = [
            {'symbol': 'EURUSD', 'asset_class': 'FOREX', 'base_price': 1.0500},
            {'symbol': 'BTCUSDT', 'asset_class': 'CRYPTO', 'base_price': 65000.00},
            {'symbol': 'AAPL', 'asset_class': 'STOCK', 'base_price': 175.50}
        ]

    def start(self):
        self.is_running = True
        print("[MOCK ADAPTER] Starting real-time feed simulation...")
        thread = threading.Thread(target=self._stream_loop)
        thread.daemon = True
        thread.start()

    def stop(self):
        self.is_running = False
        print("[MOCK ADAPTER] Stopped.")

    def _stream_loop(self):
        while self.is_running:
            elapsed = time.time() - self.start_time
            for sym in self.symbols:
                # Create a wave motion to guarantee crossovers
                wave = math.sin(elapsed * 2) * 0.002 
                current_price = sym['base_price'] * (1 + wave)
                
                spread = current_price * 0.0002
                raw_data = {
                    'symbol': sym['symbol'],
                    'asset_class': sym['asset_class'],
                    'bid': round(current_price - spread, 5),
                    'ask': round(current_price + spread, 5),
                    'last': round(current_price, 5),
                    'volume': random.randint(10, 1000)
                }

                event = DataNormalizer.normalize(raw_data, source="mock_api")
                self.event_bus.publish(event)
            
            time.sleep(1) # Send data every 1 second
