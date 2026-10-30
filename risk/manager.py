import yaml
import uuid
import json
import os
from core.events import SignalEvent, OrderEvent, RejectEvent

class RiskManager:
    def __init__(self, event_bus, config_path="config/risk_limits.yaml"):
        self.event_bus = event_bus
        self.config = self._load_config(config_path)
        self.kill_switch_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kill_switch.json')

    def _load_config(self, path):
        try:
            with open(path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"[RISK] Error loading config: {e}")
            return {}

    def _is_kill_switch_active(self):
        try:
            if os.path.exists(self.kill_switch_path):
                # FIX: using utf-8-sig to ignore BOM
                with open(self.kill_switch_path, 'r', encoding='utf-8-sig') as f:
                    status = json.load(f)
                    return status.get("active", False)
            return False
        except Exception as e:
            print(f"[RISK] Error reading kill switch: {e}")
            return False

    def on_signal(self, event: SignalEvent):
        print(f"[RISK] Evaluating {event.signal_type} signal for {event.symbol}...")
        
        if self._is_kill_switch_active():
            print("[RISK] 🚨 KILL SWITCH IS ACTIVE! Rejecting all orders.")
            self._reject_order(event, "Kill switch is active. Trading halted.")
            return

        max_qty = self.config.get('per_trade', {}).get('max_quantity', 100)
        order_qty = 10 
        
        if order_qty > max_qty:
            reason = f"Order quantity {order_qty} exceeds max limit {max_qty}"
            self._reject_order(event, reason)
            return

        price = event.target_price if event.target_price else 1.0
        order_value = order_qty * price
        max_value = self.config.get('global', {}).get('max_order_value', 50000)

        if order_value > max_value:
            reason = f"Order value {order_value} exceeds max limit {max_value}"
            self._reject_order(event, reason)
            return

        direction = "BUY" if event.signal_type == "LONG" else "SELL"
        client_order_id = str(uuid.uuid4())
        
        order_event = OrderEvent(
            symbol=event.symbol,
            order_type="MKT",
            quantity=order_qty,
            direction=direction,
            price=price,
            client_order_id=client_order_id
        )
        
        print(f"[RISK] APPROVED. Generating OrderEvent for {direction} {order_qty} {event.symbol}.")
        self.event_bus.publish(order_event)

    def _reject_order(self, signal_event: SignalEvent, reason: str):
        print(f"[RISK] REJECTED! Reason: {reason}")
        reject_event = RejectEvent(
            symbol=signal_event.symbol,
            reason=reason,
            original_signal=signal_event
        )
        self.event_bus.publish(reject_event)
