import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="doller.db"):
        self.db_name = db_name
        self._create_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def _create_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Orders Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    client_order_id TEXT PRIMARY KEY,
                    symbol TEXT,
                    direction TEXT,
                    order_type TEXT,
                    quantity REAL,
                    price REAL,
                    status TEXT,
                    created_at TEXT
                )
            ''')
            
            # Fills Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fills (
                    fill_id TEXT PRIMARY KEY,
                    client_order_id TEXT,
                    symbol TEXT,
                    direction TEXT,
                    quantity REAL,
                    fill_price REAL,
                    commission REAL,
                    filled_at TEXT
                )
            ''')
            conn.commit()
        print("[DATABASE] Tables created/verified successfully.")

    def save_order(self, order_event, status="SUBMITTED"):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO orders 
                (client_order_id, symbol, direction, order_type, quantity, price, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_event.client_order_id, 
                order_event.symbol, 
                order_event.direction, 
                order_event.order_type, 
                order_event.quantity, 
                order_event.price, 
                status,
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            print(f"[DATABASE] Order {order_event.client_order_id[:8]} saved to DB.")

    def save_fill(self, fill_event):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO fills 
                (fill_id, client_order_id, symbol, direction, quantity, fill_price, commission, filled_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fill_event.event_id,
                fill_event.client_order_id,
                fill_event.symbol,
                fill_event.direction,
                fill_event.quantity,
                fill_event.fill_cost,
                fill_event.commission,
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            print(f"[DATABASE] Fill for {fill_event.symbol} saved to DB.")
