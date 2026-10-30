from strategy.base import StrategyBase
from strategy.indicators import RSI
from core.events import MarketEvent, FillEvent

class RSIStrategy(StrategyBase):
    def __init__(self, event_bus, strategy_id="RSI_v1"):
        super().__init__(event_bus, strategy_id)
        self.rsi_indicators = {}
        self.prev_rsi = {}

    def on_market_event(self, event: MarketEvent):
        sym = event.symbol
        price = event.last

        # Initialize RSI for new symbol
        if sym not in self.rsi_indicators:
            # Using period 7 for faster signals in mock environment
            self.rsi_indicators[sym] = RSI(period=7) 
            self.prev_rsi[sym] = None

        # Update RSI
        current_rsi = self.rsi_indicators[sym].update(price)

        if current_rsi is not None:
            prev_r = self.prev_rsi[sym]

            # Check for oversold/overbought conditions
            if prev_r is not None:
                # Oversold (Crosses above 30 from below) -> BUY
                if prev_r <= 30 and current_rsi > 30:
                    print(f"[{self.strategy_id}] BUY SIGNAL for {sym} at {price} (RSI: {current_rsi:.2f})")
                    self.publish_signal(sym, "LONG", strength=0.8, target_price=price)

                # Overbought (Crosses below 70 from above) -> SELL
                elif prev_r >= 70 and current_rsi < 70:
                    print(f"[{self.strategy_id}] SELL SIGNAL for {sym} at {price} (RSI: {current_rsi:.2f})")
                    self.publish_signal(sym, "SHORT", strength=0.8, target_price=price)

            # Save current as previous for next iteration
            self.prev_rsi[sym] = current_rsi

    def on_fill(self, event: FillEvent):
        pass
