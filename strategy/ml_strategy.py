import numpy as np
from sklearn.linear_model import LogisticRegression
from strategy.base import StrategyBase
from strategy.indicators import RSI, SMA
from core.events import MarketEvent, FillEvent

class MLStrategy(StrategyBase):
    def __init__(self, event_bus, strategy_id="ML_v1"):
        super().__init__(event_bus, strategy_id)
        self.rsi = {}
        self.sma = {}
        self.prev_rsi = {}
        
        print(f"[{self.strategy_id}] Training ML Model on synthetic data...")
        self.model = self._train_model()

    def _train_model(self):
        np.random.seed(42)
        X = np.random.rand(1000, 2) * 100 
        
        # Force a balanced split of classes (0 and 1) to avoid single-class error
        y = np.zeros(1000, dtype=int)
        y[500:] = 1  # Assign 1 to the second half
        
        # Shuffle the data so classes are mixed
        indices = np.arange(1000)
        np.random.shuffle(indices)
        X = X[indices]
        y = y[indices]
        
        model = LogisticRegression()
        model.fit(X, y)
        print(f"[{self.strategy_id}] ML Model trained successfully.")
        return model

    def on_market_event(self, event: MarketEvent):
        sym = event.symbol
        price = event.last

        if sym not in self.rsi:
            self.rsi[sym] = RSI(period=7)
            self.sma[sym] = SMA(period=10)
            self.prev_rsi[sym] = None

        current_rsi = self.rsi[sym].update(price)
        current_sma = self.sma[sym].update(price)

        if current_rsi is not None and current_sma is not None:
            prev_r = self.prev_rsi[sym]
            
            if prev_r is not None:
                price_diff = price - current_sma
                features = np.array([[current_rsi, price_diff]])
                
                prediction = self.model.predict(features)[0]
                
                if prediction == 1 and prev_r < 50:
                    print(f"[{self.strategy_id}] ML BUY SIGNAL for {sym} at {price} (RSI: {current_rsi:.2f}, Diff: {price_diff:.5f})")
                    self.publish_signal(sym, "LONG", strength=0.9, target_price=price)
                    
                elif prediction == 0 and prev_r > 50:
                    print(f"[{self.strategy_id}] ML SELL SIGNAL for {sym} at {price} (RSI: {current_rsi:.2f}, Diff: {price_diff:.5f})")
                    self.publish_signal(sym, "SHORT", strength=0.9, target_price=price)

            self.prev_rsi[sym] = current_rsi

    def on_fill(self, event: FillEvent):
        pass
