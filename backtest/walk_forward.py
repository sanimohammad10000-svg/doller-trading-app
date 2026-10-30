import time
from core.event_bus import EventBus
from core.events import MarketEvent

class WalkForwardEngine:
    def __init__(self, event_bus: EventBus, events: list):
        self.event_bus = event_bus
        self.events = events

    def run(self, num_windows: int = 5):
        print(f"[WFA] Starting Walk-Forward Analysis with {num_windows} windows...")
        
        # Split data into windows
        window_size = len(self.events) // num_windows
        if window_size == 0:
            print("[WFA] Not enough data to split into windows.")
            return

        for i in range(num_windows):
            start_idx = i * window_size
            end_idx = (i + 1) * window_size if i < num_windows - 1 else len(self.events)
            
            window_events = self.events[start_idx:end_idx]
            print(f"\n--- [WFA] Running Window {i+1}/{num_windows} ({len(window_events)} events) ---")
            
            start_time = time.time()
            for event in window_events:
                self.event_bus.publish(event)
            end_time = time.time()
            
            print(f"[WFA] Window {i+1} completed in {end_time - start_time:.4f} seconds.")
