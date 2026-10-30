from strategy.base import StrategyBase
from strategy.indicators import SMA
from core.events import MarketEvent, FillEvent

class SMACrossoverStrategy(StrategyBase):
    def __init__(self, event_bus, strategy_id="SMA_Cross_v1"):
        super().__init__(event_bus, strategy_id)
        # We will track SMAs per symbol
        self.fast_sma = {}
        self.slow_sma = {}
        self.prev_fast = {}
        self.prev_slow = {}

    def on_market_event(self, event: MarketEvent):
        sym = event.symbol
        price = event.last

        # Initialize indicators for a new symbol
        if sym not in self.fast_sma:
            self.fast_sma[sym] = SMA(period=3)   # Fast MA
            self.slow_sma[sym] = SMA(period=7)   # Slow MA
            self.prev_fast[sym] = None
            self.prev_slow[sym] = None

        # Update SMAs
        fast_val = self.fast_sma[sym].update(price)
        slow_val = self.slow_sma[sym].update(price)

        # Check for crossover
        if fast_val is not None and slow_val is not None:
            prev_f, prev_s = self.prev_fast[sym], self.prev_slow[sym]

            # If we have previous values, check for crosses
            if prev_f is not None and prev_s is not None:
                # Bullish Crossover (Fast crosses above Slow) -> BUY
                if prev_f <= prev_s and fast_val > slow_val:
                    print(f"[{self.strategy_id}] BUY SIGNAL for {sym} at {price}")
                    self.publish_signal(sym, "LONG", strength=0.8, target_price=price)

                # Bearish Crossover (Fast crosses below Slow) -> SELL
                elif prev_f >= prev_s and fast_val < slow_val:
                    print(f"[{self.strategy_id}] SELL SIGNAL for {sym} at {price}")
                    self.publish_signal(sym, "SHORT", strength=0.8, target_price=price)

            # Save current as previous for next iteration
            self.prev_fast[sym] = fast_val
            self.prev_slow[sym] = slow_val

    def on_fill(self, event: FillEvent):
        pass # Handle order fills here later
