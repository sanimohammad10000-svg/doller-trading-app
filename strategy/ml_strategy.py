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
        
        # Train a simple Logistic Regression model on synthetic data
        print(f"[{self.strategy_id}] Training ML Model on synthetic data...")
        self.model = self._train_model()

    def _train_model(self):
        # Generate synthetic features (RSI, Price - SMA) and target (1=Buy, 0=Sell)
        np.random.seed(42)
        X = np.random.rand(1000, 2) * 100 # RSI (0-100), Diff (e.g., -50 to 50)
        # Logic: If RSI < 30 (oversold) or Diff > 0 (uptrend), Buy
        y = ((X[:, 0] < 30) | (X[:, 1] > 0)).astype(int)
        
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
                # Prepare features for prediction
                price_diff = price - current_sma
                features = np.array([[current_rsi, price_diff]])
                
                # Predict (0 or 1)
                prediction = self.model.predict(features)[0]
                
                # To avoid spamming trades, we only trade when state changes or specific conditions are met
                if prediction == 1 and prev_r < 50: # ML says BUY
                    print(f"[{self.strategy_id}] ML BUY SIGNAL for {sym} at {price} (RSI: {current_rsi:.2f}, Diff: {price_diff:.5f})")
                    self.publish_signal(sym, "LONG", strength=0.9, target_price=price)
                    
                elif prediction == 0 and prev_r > 50: # ML says SELL
                    print(f"[{self.strategy_id}] ML SELL SIGNAL for {sym} at {price} (RSI: {current_rsi:.2f}, Diff: {price_diff:.5f})")
                    self.publish_signal(sym, "SHORT", strength=0.9, target_price=price)

            self.prev_rsi[sym] = current_rsi

    def on_fill(self, event: FillEvent):
        pass
