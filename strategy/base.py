from abc import ABC, abstractmethod
from core.events import MarketEvent, SignalEvent, FillEvent

class StrategyBase(ABC):
    def __init__(self, event_bus, strategy_id: str):
        self.event_bus = event_bus
        self.strategy_id = strategy_id
        self.symbols = set()

    @abstractmethod
    def on_market_event(self, event: MarketEvent):
        '''Called when new market data arrives.'''
        pass

    @abstractmethod
    def on_fill(self, event: FillEvent):
        '''Called when an order is filled.'''
        pass

    def publish_signal(self, symbol: str, signal_type: str, strength: float, target_price: float = None):
        '''Helper method to publish a signal to the Event Bus.'''
        signal = SignalEvent(
            strategy_id=self.strategy_id,
            symbol=symbol,
            signal_type=signal_type,
            strength=strength,
            target_price=target_price
        )
        self.event_bus.publish(signal)
