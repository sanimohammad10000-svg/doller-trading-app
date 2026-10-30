from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

@dataclass(frozen=True)
class Event:
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass(frozen=True)
class MarketEvent(Event):
    symbol: str = ""
    asset_class: str = "" 
    bid: float = 0.0
    ask: float = 0.0
    last: float = 0.0
    volume: float = 0.0
    source: str = "" 

@dataclass(frozen=True)
class SignalEvent(Event):
    strategy_id: str = ""
    symbol: str = ""
    signal_type: str = "" 
    strength: float = 0.0 
    target_price: Optional[float] = None

@dataclass(frozen=True)
class OrderEvent(Event):
    symbol: str = ""
    order_type: str = "" 
    quantity: float = 0.0
    direction: str = "" 
    price: Optional[float] = None
    client_order_id: str = "" 

@dataclass(frozen=True)
class FillEvent(Event):
    client_order_id: str = ""
    broker_order_id: str = ""
    symbol: str = ""
    quantity: float = 0.0
    direction: str = ""
    fill_cost: float = 0.0
    commission: float = 0.0

# NEW: Risk Reject Event
@dataclass(frozen=True)
class RejectEvent(Event):
    symbol: str = ""
    reason: str = ""
    original_signal: Optional[SignalEvent] = None
