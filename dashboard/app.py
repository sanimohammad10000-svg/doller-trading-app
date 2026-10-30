import sys
import os
import time
import sqlite3
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.event_bus import EventBus
from core.events import MarketEvent, SignalEvent, OrderEvent, FillEvent
from data.mock_adapter import MockDataAdapter
from strategy.ml_strategy import MLStrategy
from risk.manager import RiskManager
from execution.order_manager import OrderManager
from portfolio.manager import PortfolioManager

@st.cache_resource
def init_system():
    bus = EventBus()
    strategy = MLStrategy(bus)
    risk_mgr = RiskManager(bus)
    exec_mgr = OrderManager(bus)
    portfolio = PortfolioManager(bus, initial_cash=100000.0)
    
    bus.subscribe(MarketEvent, strategy.on_market_event)
    bus.subscribe(MarketEvent, portfolio.on_market_event)
    bus.subscribe(SignalEvent, risk_mgr.on_signal)
    bus.subscribe(OrderEvent, exec_mgr.on_order)
    bus.subscribe(FillEvent, portfolio.on_fill)
    
    adapter = MockDataAdapter(bus)
    adapter.start()
    return portfolio, adapter

def get_recent_trades():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'doller.db'))
    try:
        conn = sqlite3.connect(db_path)
        orders_df = pd.read_sql_query("SELECT symbol, direction, quantity, price, status, created_at FROM orders ORDER BY created_at DESC LIMIT 5", conn)
        fills_df = pd.read_sql_query("SELECT symbol, direction, quantity, fill_price, commission, filled_at FROM fills ORDER BY filled_at DESC LIMIT 5", conn)
        conn.close()
        return orders_df, fills_df
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

def calculate_advanced_analytics(equity_history):
    if len(equity_history) < 2:
        return {"Sharpe": 0, "Sortino": 0, "Max DD": 0}
    equity_history['Returns'] = equity_history['Total Equity'].pct_change()
    returns = equity_history['Returns'].dropna()
    if returns.empty or returns.std() == 0:
        return {"Sharpe": 0, "Sortino": 0, "Max DD": 0}
    sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
    downside_returns = returns[returns < 0]
    sortino = (returns.mean() / downside_returns.std()) * np.sqrt(252) if not downside_returns.empty and downside_returns.std() != 0 else 0.0
    cumulative = (1 + returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_dd = drawdown.min() * 100
    return {"Sharpe": round(sharpe, 2), "Sortino": round(sortino, 2), "Max DD": f"{round(max_dd, 2)}%"}

st.set_page_config(page_title="Doller Trading Engine", layout="wide")

# --- SIDEBAR: KILL SWITCH UI ---
st.sidebar.header("🚨 Emergency Controls")
kill_switch_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'kill_switch.json'))
if not os.path.exists(kill_switch_path):
    with open(kill_switch_path, 'w', encoding='utf-8') as f:
        json.dump({"active": False}, f)
try:
    with open(kill_switch_path, 'r', encoding='utf-8-sig') as f:
        ks_status = json.load(f).get("active", False)
except Exception:
    ks_status = False

if ks_status:
    st.sidebar.error("🚨 KILL SWITCH IS ACTIVE!\nAll trading is halted.")
    if st.sidebar.button("🟢 RESET (Resume Trading)", use_container_width=True):
        with open(kill_switch_path, 'w', encoding='utf-8') as f:
            json.dump({"active": False}, f)
        st.rerun()
else:
    st.sidebar.success("✅ System is Live and Trading.")
    if st.sidebar.button("🔴 ENGAGE KILL SWITCH", type="primary", use_container_width=True):
        with open(kill_switch_path, 'w', encoding='utf-8') as f:
            json.dump({"active": True}, f)
        st.rerun()

# --- MAIN DASHBOARD ---
st.title("📈 Project Doller - Live Dashboard (ML Strategy)")
st.markdown("Live Market Data -> ML Strategy -> Risk -> Execution -> Portfolio")

portfolio, adapter = init_system()

if 'ohlc_data' not in st.session_state or st.session_state.ohlc_data.empty:
    dates = pd.date_range(end=datetime.now(), periods=60, freq='5s')
    close_prices = 1.0500 + np.cumsum(np.random.randn(60) * 0.0002)
    open_prices = close_prices - np.random.randn(60) * 0.0001
    high_prices = np.maximum(open_prices, close_prices) + np.random.rand(60) * 0.0002
    low_prices = np.minimum(open_prices, close_prices) - np.random.rand(60) * 0.0002
    st.session_state.ohlc_data = pd.DataFrame({'Time': dates, 'Open': open_prices, 'High': high_prices, 'Low': low_prices, 'Close': close_prices})

if 'equity_history' not in st.session_state:
    st.session_state.equity_history = pd.DataFrame(columns=["Time", "Total Equity"])

equity = portfolio.cash
for sym, pos in portfolio.positions.items():
    if pos.quantity != 0:
        equity += pos.quantity * portfolio.last_prices.get(sym, pos.average_price)

pnl = equity - 100000.0
now = datetime.now()

current_price = portfolio.last_prices.get("EURUSD", 0)
if current_price > 0:
    new_candle = pd.DataFrame({'Time': [now], 'Open': [current_price], 'High': [current_price], 'Low': [current_price], 'Close': [current_price]})
    st.session_state.ohlc_data = pd.concat([st.session_state.ohlc_data, new_candle], ignore_index=True).tail(100)

new_equity_row = pd.DataFrame({"Time": [now], "Total Equity": [equity]})
st.session_state.equity_history = pd.concat([st.session_state.equity_history, new_equity_row], ignore_index=True).tail(100)

col1, col2, col3 = st.columns(3)
col1.metric("Cash Balance", f"${portfolio.cash:,.2f}")
col2.metric("Total Equity", f"${equity:,.2f}")
col3.metric("Total P&L", f"${pnl:,.2f}", delta=f"{pnl:,.2f}")

st.divider()

analytics = calculate_advanced_analytics(st.session_state.equity_history)
st.subheader("📊 Advanced Performance Metrics")
acol1, acol2, acol3 = st.columns(3)
acol1.metric("Sharpe Ratio", analytics["Sharpe"], help="Risk-adjusted return (Higher is better, >1 is good)")
acol2.metric("Sortino Ratio", analytics["Sortino"], help="Risk-adjusted return focusing only on downside risk")
acol3.metric("Max Drawdown", analytics["Max DD"], help="Maximum observed loss from a peak to a trough")

st.divider()

chart_col1, chart_col2 = st.columns([2, 1])

with chart_col1:
    st.subheader("📊 EURUSD - Live Candlestick Chart")
    df_chart = st.session_state.ohlc_data.copy()
    df_chart['SMA'] = df_chart['Close'].rolling(window=15).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df_chart['Time'], open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'], increasing_line_color='#00FF00', decreasing_line_color='#FF0000', name='EURUSD'))
    fig.add_trace(go.Scatter(x=df_chart['Time'], y=df_chart['SMA'], mode='lines', line=dict(color='#FFD700', width=2), name='SMA (15)'))

    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', type='date', tickformat="%H:%M:%S"),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', side='right'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, width='stretch', key="candle_chart")

with chart_col2:
    st.subheader("💰 Total Equity")
    fig_eq = go.Figure(data=[go.Scatter(x=st.session_state.equity_history['Time'], y=st.session_state.equity_history['Total Equity'], mode='lines', line=dict(color='#00BFFF', width=2), fill='tozeroy', fillcolor='rgba(0, 191, 255, 0.1)')])
    fig_eq.update_layout(template="plotly_dark", height=450, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', type='date', tickformat="%H:%M:%S"),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', side='right', zeroline=False))
    st.plotly_chart(fig_eq, width='stretch', key="equity_chart")

st.divider()

col_pos, col_prices = st.columns(2)

with col_pos:
    st.subheader("Open Positions")
    pos_data = []
    for sym, pos in portfolio.positions.items():
        if pos.quantity != 0:
            current_price = portfolio.last_prices.get(sym, pos.average_price)
            pos_data.append({"Symbol": sym, "Quantity": pos.quantity, "Avg Price": round(pos.average_price, 5), "Current Price": round(current_price, 5), "Unrealized P&L": round((current_price - pos.average_price) * pos.quantity, 2)})
    if pos_data:
        st.dataframe(pos_data, width='stretch')
    else:
        st.info("No open positions right now. Waiting for ML signal...")
        
with col_prices:
    st.subheader("Live Market Prices")
    price_data = [{"Symbol": sym, "Last Price": round(price, 5)} for sym, price in portfolio.last_prices.items()]
    if price_data:
        st.dataframe(price_data, width='stretch')

st.divider()

st.subheader("📜 Recent Trade History (From Database)")
orders_df, fills_df = get_recent_trades()
tab1, tab2 = st.tabs(["Recent Orders", "Recent Fills"])
with tab1:
    if not orders_df.empty:
        st.dataframe(orders_df, width='stretch', hide_index=True)
    else:
        st.info("No orders found in database yet.")
with tab2:
    if not fills_df.empty:
        st.dataframe(fills_df, width='stretch', hide_index=True)
    else:
        st.info("No fills found in database yet.")

time.sleep(1)
st.rerun()
