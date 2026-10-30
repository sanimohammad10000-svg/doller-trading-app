from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class OrderState(Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

@dataclass
class Order:
    client_order_id: str
    symbol: str
    quantity: float
    direction: str 
    order_type: str 
    price: Optional[float] = None
    state: OrderState = OrderState.PENDING
    created_at: datetime = datetime.utcnow()

@dataclass
class Position:
    symbol: str
    quantity: float = 0.0
    average_price: float = 0.0
    
    def update_position(self, fill_qty: float, fill_price: float):
        if self.quantity == 0:
            self.quantity = fill_qty
            self.average_price = fill_price
        else:
            total_value = (self.quantity * self.average_price) + (fill_qty * fill_price)
            self.quantity += fill_qty
            if self.quantity != 0:
                self.average_price = total_value / self.quantity
            else:
                self.average_price = 0.0
