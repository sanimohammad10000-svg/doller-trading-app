import os
import sqlite3
from datetime import datetime
import streamlit as st
import pandas as pd

class DatabaseManager:
    def __init__(self, db_name="doller.db"):
        self.db_name = db_name
        self.db_url = None
        try:
            self.db_url = st.secrets["DATABASE_URL"]
            # SSL বাধ্যতামূলক করা হচ্ছে
            if self.db_url and "sslmode=require" not in self.db_url:
                if "?" in self.db_url:
                    self.db_url += "&sslmode=require"
                else:
                    self.db_url += "?sslmode=require"
        except Exception:
            pass
        self._create_tables()

    def _get_connection(self):
        if self.db_url:
            import psycopg2
            return psycopg2.connect(self.db_url)
        else:
            return sqlite3.connect(self.db_name)

    def _create_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
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

    def save_order(self, order_event, status="SUBMITTED"):
        is_pg = self.db_url is not None
        ph = "%s" if is_pg else "?"
        conflict = "ON CONFLICT (client_order_id) DO NOTHING" if is_pg else "OR REPLACE"
        insert = "INSERT INTO" if is_pg else "INSERT OR REPLACE INTO"
        
        query = f'''
            {insert} orders 
            (client_order_id, symbol, direction, order_type, quantity, price, status, created_at)
            VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
            {conflict}
        '''
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                order_event.client_order_id, order_event.symbol, 
                order_event.direction, order_event.order_type, 
                order_event.quantity, order_event.price, status,
                datetime.utcnow().isoformat()
            ))
            conn.commit()

    def save_fill(self, fill_event):
        is_pg = self.db_url is not None
        ph = "%s" if is_pg else "?"
        
        query = f'''
            INSERT INTO fills 
            (fill_id, client_order_id, symbol, direction, quantity, fill_price, commission, filled_at)
            VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
        '''
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                fill_event.event_id, fill_event.client_order_id, 
                fill_event.symbol, fill_event.direction, 
                fill_event.quantity, fill_event.fill_cost, 
                fill_event.commission, datetime.utcnow().isoformat()
            ))
            conn.commit()

    def get_recent_trades(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT symbol, direction, quantity, price, status, created_at FROM orders ORDER BY created_at DESC LIMIT 5")
            orders = cursor.fetchall()
            cursor.execute("SELECT symbol, direction, quantity, fill_price, commission, filled_at FROM fills ORDER BY filled_at DESC LIMIT 5")
            fills = cursor.fetchall()
            
            orders_df = pd.DataFrame(orders, columns=["Symbol", "Direction", "Quantity", "Price", "Status", "Date"])
            fills_df = pd.DataFrame(fills, columns=["Symbol", "Direction", "Quantity", "Fill Price", "Commission", "Date"])
            return orders_df, fills_df
