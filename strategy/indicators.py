from collections import deque
import numpy as np

class SMA:
    def __init__(self, period: int):
        self.period = period
        self.prices = deque(maxlen=period)

    def update(self, price: float) -> float | None:
        self.prices.append(price)
        if len(self.prices) == self.period:
            return sum(self.prices) / self.period
        return None

class RSI:
    def __init__(self, period: int = 14):
        self.period = period
        self.prices = deque(maxlen=period + 1)

    def update(self, price: float) -> float | None:
        self.prices.append(price)
        if len(self.prices) < self.period + 1:
            return None
        
        deltas = np.diff(self.prices)
        seed = deltas[:self.period]
        up = seed[seed >= 0].sum() / self.period
        down = -seed[seed < 0].sum() / self.period
        
        if down == 0:
            return 100.0
        
        rs = up / down
        return 100.0 - (100.0 / (1.0 + rs))
