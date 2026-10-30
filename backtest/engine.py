import time
from data.historical_loader import HistoricalDataLoader

class BacktestEngine:
    def __init__(self, event_bus, data_loader: HistoricalDataLoader):
        self.event_bus = event_bus
        self.data_loader = data_loader

    def run(self):
        print("[BACKTEST] Loading historical data...")
        events = self.data_loader.load_data()
        print(f"[BACKTEST] Loaded {len(events)} events. Starting simulation...")
        
        start_time = time.time()
        for event in events:
            self.event_bus.publish(event)
            
        end_time = time.time()
        print(f"[BACKTEST] Simulation completed in {end_time - start_time:.2f} seconds.")
