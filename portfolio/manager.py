from core.events import FillEvent, MarketEvent
from core.models import Position

class PortfolioManager:
    def __init__(self, event_bus, initial_cash=100000.0):
        self.event_bus = event_bus
        self.cash = initial_cash
        self.positions = {} 
        self.last_prices = {} 

    def on_fill(self, event: FillEvent):
        sym = event.symbol
        cost = event.quantity * event.fill_cost
        if event.direction == "BUY":
            self.cash -= (cost + event.commission)
            fill_qty = event.quantity
        else:
            self.cash += (cost - event.commission)
            fill_qty = -event.quantity

        if sym not in self.positions:
            self.positions[sym] = Position(symbol=sym)
            
        self.positions[sym].update_position(fill_qty, event.fill_cost)
        
        print(f"[PORTFOLIO] Fill Processed for {sym}. Current Position: {self.positions[sym].quantity}")
        print(f"[PORTFOLIO] Cash Balance: ${self.cash:.2f}")
        self._calculate_total_equity()

    def on_market_event(self, event: MarketEvent):
        self.last_prices[event.symbol] = event.last

    def _calculate_total_equity(self):
        positions_value = 0.0
        for sym, pos in self.positions.items():
            if pos.quantity != 0:
                current_price = self.last_prices.get(sym, pos.average_price)
                positions_value += pos.quantity * current_price
                
        equity = self.cash + positions_value
        print(f"[PORTFOLIO] Total Equity: ${equity:.2f}")
