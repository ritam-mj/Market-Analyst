#!/usr/bin/env python3
"""
Live Trading Dashboard - Real-time portfolio monitoring

A Streamlit web application that displays:
- Portfolio NAV and daily PnL
- Open positions with mark-to-market
- Recent trades and execution history
- Risk metrics and alerts
- Agent activity and decision history
- Historical performance charts

Usage:
    pip install streamlit yfinance
    streamlit run dashboard.py
    
Then open: http://localhost:8501
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from state_persistence import StateManager
from risk_manager import RiskConfig, RiskManager
import json
from pathlib import Path


# Page configuration
st.set_page_config(
    page_title="MarketPredictor Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .positive { color: #00cc00; font-weight: bold; }
    .negative { color: #ff0000; font-weight: bold; }
    .neutral { color: #888888; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_state_manager():
    """Initialize state manager"""
    return StateManager(backend='sqlite', db_path='portfolio.db')


@st.cache_resource
def get_risk_config():
    """Initialize risk config"""
    return RiskConfig()


def load_learner_state():
    """Load learner state from JSON"""
    try:
        with open('learner_state.json', 'r') as f:
            return json.load(f)
    except:
        return {"history": []}


def get_current_prices(symbols: list) -> dict:
    """Fetch current prices for symbols"""
    prices = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if not data.empty:
                prices[symbol] = data['Close'].iloc[-1]
        except:
            prices[symbol] = None
    return prices


def format_currency(value):
    """Format value as currency"""
    if value >= 0:
        return f'<span class="positive">${value:,.2f}</span>'
    else:
        return f'<span class="negative">${value:,.2f}</span>'


def format_pct(value):
    """Format value as percentage"""
    if value >= 0:
        return f'<span class="positive">{value:+.2f}%</span>'
    else:
        return f'<span class="negative">{value:+.2f}%</span>'


# ============================================================================
# PAGE: DASHBOARD
# ============================================================================
def page_dashboard():
    """Main dashboard page"""
    st.title("📊 MarketPredictor Live Dashboard")
    
    # Sidebar configuration
    st.sidebar.header("Settings")
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 10)
    
    # Get data
    state_manager = get_state_manager()
    learner_state = load_learner_state()
    
    # Load latest portfolio state
    portfolio_data = state_manager.load()
    
    if portfolio_data is None:
        st.warning("No portfolio data found. Run main.py first to initialize.")
        return
    
    # Extract data
    nav = portfolio_data.get('nav', 0)
    cash = portfolio_data.get('cash', 0)
    realized_pnl = portfolio_data.get('realized_pnl', 0)
    positions = portfolio_data.get('positions', {})
    timestamp = portfolio_data.get('timestamp', 'Unknown')
    
    # Get current prices for positions
    if positions:
        symbols = list(positions.keys())
        current_prices = get_current_prices(symbols)
    else:
        current_prices = {}
    
    # Calculate metrics
    starting_capital = 1_000_000.0  # Assumption
    total_return = ((nav - starting_capital) / starting_capital) * 100
    
    # Top metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Portfolio NAV", f"${nav:,.0f}", f"{total_return:+.2f}%")
    
    with col2:
        st.metric("Cash", f"${cash:,.0f}", f"{(cash/nav)*100:.1f}%")
    
    with col3:
        st.metric("Realized PnL", f"${realized_pnl:,.0f}")
    
    with col4:
        position_count = len(positions)
        st.metric("Open Positions", position_count)
    
    with col5:
        trade_count = len(state_manager.get_trades(days=1))
        st.metric("Today's Trades", trade_count)
    
    # Divider
    st.divider()
    
    # Positions section
    st.subheader("📈 Open Positions")
    
    if positions:
        pos_data = []
        total_unrealized = 0.0
        
        for symbol, pos_info in positions.items():
            qty = pos_info['quantity']
            avg_price = pos_info['avg_price']
            current_price = current_prices.get(symbol, avg_price)
            
            unrealized = (current_price - avg_price) * qty
            total_unrealized += unrealized
            
            pos_data.append({
                'Symbol': symbol,
                'Quantity': f"{qty:.0f}",
                'Avg Price': f"${avg_price:.2f}",
                'Current Price': f"${current_price:.2f}",
                'Unrealized PnL': f"${unrealized:+,.2f}",
                'Return %': f"{((current_price/avg_price - 1) * 100):+.2f}%"
            })
        
        positions_df = pd.DataFrame(pos_data)
        st.dataframe(positions_df, use_container_width=True)
        
        st.write(f"**Total Unrealized PnL:** ${total_unrealized:+,.2f}")
    else:
        st.info("No open positions")
    
    st.divider()
    
    # Recent trades
    st.subheader("🔄 Recent Trades")
    
    trades = state_manager.get_trades(days=7, limit=20)
    if trades:
        trades_df = pd.DataFrame(trades)
        # Format columns
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        trades_df['price'] = trades_df['price'].apply(lambda x: f"${x:.2f}")
        trades_df['pnl'] = trades_df['pnl'].apply(lambda x: f"${x:+,.2f}")
        
        st.dataframe(trades_df[['timestamp', 'symbol', 'side', 'quantity', 'price', 'pnl']], 
                    use_container_width=True, hide_index=True)
    else:
        st.info("No trades in the last 7 days")
    
    st.divider()
    
    # Risk management status
    st.subheader("⚠️ Risk Management Status")
    
    risk_config = get_risk_config()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Max Position Size", f"{risk_config.max_position_size_pct*100:.0f}%")
    
    with col2:
        st.metric("Daily Loss Limit", f"{risk_config.max_daily_loss_pct*100:.1f}%")
    
    with col3:
        st.metric("Stop Loss Level", f"{-risk_config.stop_loss_pct*100:.1f}%")
    
    with col4:
        st.metric("Trading Halted", "No" if not risk_config.trading_halted else "YES")
    
    st.divider()
    
    # Learner state
    st.subheader("🤖 Learner State")
    
    if learner_state.get('history'):
        history = learner_state['history'][-5:]  # Last 5
        
        learner_data = []
        for entry in history:
            learner_data.append({
                'Scenario': entry.get('scenario', 'unknown').upper(),
                'λ (Jump Freq)': f"{entry.get('params', {}).get('lamb', 0):.4f}",
                'μⱼ (Jump Dir)': f"{entry.get('params', {}).get('mu_j', 0):+.4f}",
                'σⱼ (Jump Vol)': f"{entry.get('params', {}).get('sigma_j', 0):.4f}",
                'MSE': f"{entry.get('mse', 0):.6f}",
            })
        
        learner_df = pd.DataFrame(learner_data)
        st.dataframe(learner_df, use_container_width=True, hide_index=True)
    
    # Last updated
    st.divider()
    st.caption(f"Last updated: {timestamp}")
    st.caption("Refresh this page to get latest data")


# ============================================================================
# PAGE: PERFORMANCE
# ============================================================================
def page_performance():
    """Performance analysis page"""
    st.title("📈 Performance Analysis")
    
    state_manager = get_state_manager()
    
    # Historical data
    st.subheader("Portfolio NAV History")
    
    days = st.slider("Days to display", 1, 90, 30)
    history = state_manager.get_history(days=days, limit=1000)
    
    if history:
        history_df = pd.DataFrame(history)
        history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
        history_df = history_df.sort_values('timestamp')
        
        # Plot NAV over time
        st.line_chart(history_df.set_index('timestamp')[['nav']], use_container_width=True)
        
        # Statistics
        st.subheader("Portfolio Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            starting_nav = history_df['nav'].iloc[0]
            ending_nav = history_df['nav'].iloc[-1]
            total_return = ((ending_nav - starting_nav) / starting_nav) * 100
            st.metric("Total Return", f"{total_return:+.2f}%")
        
        with col2:
            max_nav = history_df['nav'].max()
            max_dd = ((history_df['nav'].min() - max_nav) / max_nav) * 100
            st.metric("Max Drawdown", f"{max_dd:.2f}%")
        
        with col3:
            daily_returns = history_df['nav'].pct_change().dropna()
            sharpe = (daily_returns.mean() / daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0
            st.metric("Sharpe Ratio", f"{sharpe:.3f}")
        
        with col4:
            volatility = daily_returns.std() * np.sqrt(252) * 100
            st.metric("Annualized Vol", f"{volatility:.2f}%")
    else:
        st.info("No historical data available")


# ============================================================================
# PAGE: ALERTS & LOGS
# ============================================================================
def page_alerts():
    """Alerts and logging page"""
    st.title("🚨 Alerts & Events")
    
    state_manager = get_state_manager()
    
    st.subheader("Risk Events (Last 24 Hours)")
    
    # This would require querying the risk_events table
    # For now, show a placeholder
    st.info("Risk event logging available when trading is active")
    
    st.subheader("System Logs")
    
    log_level = st.selectbox("Log Level", ["ALL", "WARNING", "CRITICAL", "ERROR"])
    
    st.info("System logging configured in main.py with timestamps and severity levels")


# ============================================================================
# MAIN APP
# ============================================================================
def main():
    """Main application"""
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", ["Dashboard", "Performance", "Alerts & Logs"])
    
    if page == "Dashboard":
        page_dashboard()
    elif page == "Performance":
        page_performance()
    elif page == "Alerts & Logs":
        page_alerts()
    
    # Auto-refresh
    st.sidebar.divider()
    st.sidebar.write("**Auto-refresh:** Enable browser auto-refresh to update in real-time")


if __name__ == "__main__":
    main()
