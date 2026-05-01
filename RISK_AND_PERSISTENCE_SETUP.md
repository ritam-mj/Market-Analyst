# MarketPredictor - Risk Management & Persistence Setup Complete

## ✅ Phase 1: Risk Management & Stops

### Risk Manager Features Added (`risk_manager.py`)
- **Position Size Limits**: Max 10% of portfolio per symbol
- **Daily Loss Limits**: Stop trading if down 2% in a day
- **Leverage Limits**: Max 1.5x leverage (50% borrowing)
- **Cash Buffer**: Keep minimum 5% in cash
- **Stop Loss**: Auto-exit if position down 5%
- **Circuit Breakers**: 
  - Daily trade limit (50/day max)
  - Trading halt on critical violations
  - Master kill switch

### Risk Config Customization
Edit `risk_manager.py` to adjust thresholds:
```python
config = RiskConfig()
config.max_position_size_pct = 0.10        # Change to 5%, 15%, etc.
config.max_daily_loss_pct = 0.02           # Change to 1%, 3%, etc.
config.stop_loss_pct = 0.05                # Change to 3%, 10%, etc.
config.max_leverage = 1.5                  # Change to 1.0, 2.0, etc.
```

### Integration in Trading Loop
The `main.py` now:
1. Validates each trade against risk limits before execution
2. Logs all violations with severity (INFO, WARNING, CRITICAL)
3. Halts trading if critical violation
4. Reports risk metrics at end of epoch

---

## ✅ Phase 2: Persistent State Storage

### State Manager Features (`state_persistence.py`)
- **Two backends**: JSON (simple) or SQLite (production)
- **Auto-saves**: Portfolio snapshots after each trade
- **Crash recovery**: Restore portfolio state on restart
- **Trade history**: Full audit trail with timestamps
- **Risk events**: All violations logged to database
- **Queries**: Get history over configurable periods

### Database Tables (SQLite)
1. **portfolio_snapshots**: Point-in-time portfolio state
2. **trades**: All trade executions with PnL
3. **risk_events**: All risk violations and events

### Usage in main.py
```python
state_manager = StateManager(backend='sqlite')

# After each trade
state_manager.save_trade(symbol, side, quantity, price, pnl, realized_pnl, cash)

# After epoch ends
state_manager.save(portfolio, nav=nav)

# Retrieve history
history = state_manager.get_history(days=7)
trades = state_manager.get_trades(symbol='SPY', days=1)
```

### Crash Recovery
When you restart:
```python
state = state_manager.load()
if state:
    # Restore portfolio state
    portfolio.cash = state['cash']
    portfolio.positions = state['positions']
    portfolio.realized_pnl = state['realized_pnl']
```

---

## ✅ Phase 3: Live Dashboard

### Dashboard Features (`dashboard.py`)
- **Real-time metrics**: Portfolio NAV, daily PnL, open positions
- **Mark-to-market**: Current prices fetched from Yahoo Finance
- **Trade history**: Recent executions with PnL
- **Risk status**: Current risk configuration and trading state
- **Learner state**: Last 5 optimization runs
- **Performance charts**: NAV over time, drawdown, Sharpe ratio
- **Multi-page**: Dashboard, Performance, Alerts & Logs

### Installation & Launch
```bash
# Install Streamlit
pip install streamlit yfinance

# Run dashboard
streamlit run dashboard.py

# Opens at http://localhost:8501
```

### Dashboard Pages
1. **Dashboard**: Live portfolio snapshot, positions, trades
2. **Performance**: Historical NAV, returns, risk metrics
3. **Alerts & Logs**: Risk events and system logs

---

## 🚀 Quick Start Guide

### Step 1: Run with Risk Management & Persistence
```bash
python main.py
```
This now:
- Validates all trades against risk limits
- Saves portfolio state to `portfolio.db`
- Logs all events with timestamps
- Reports risk summary at end

### Step 2: Check Persistent State
```python
from state_persistence import StateManager

state = StateManager(backend='sqlite')
portfolio_data = state.load()
print(f"NAV: ${portfolio_data['nav']:,.2f}")
print(f"Cash: ${portfolio_data['cash']:,.2f}")
print(f"PnL: ${portfolio_data['realized_pnl']:,.2f}")
```

### Step 3: Launch Live Dashboard
```bash
streamlit run dashboard.py
```
Opens in browser at `http://localhost:8501`

---

## 📊 Dashboard Screenshots (Text Description)

### Main Dashboard Tab
```
[Portfolio NAV] [Cash] [Realized PnL] [Open Pos] [Today's Trades]
   $1,234,567      $50,000       +$1,234         5          3

OPEN POSITIONS
Symbol  Qty    Avg Price  Current  Unrealized PnL  Return
SPY     100    $670.50    $713.94     +$4,344       +6.48%
AAPL    50     $190.00    $195.25     +$262.50      +2.76%

RECENT TRADES (Last 7 Days)
2026-04-24 10:30  SPY   BUY   100  $713.94  +$234.56
2026-04-23 14:15  AAPL  SELL  50   $195.25  -$45.00
```

### Performance Tab
```
NAV Chart: [Line chart showing 30-day NAV trend]

Portfolio Statistics:
Total Return: +12.34%
Max Drawdown: -4.53%
Sharpe Ratio: 0.922
Annualized Vol: 18.5%
```

---

## ⚙️ Configuration & Customization

### Risk Manager Settings
Edit `risk_manager.py` line 20-30:
```python
class RiskConfig:
    def __init__(self):
        self.max_position_size_pct = 0.10      # 10% per symbol
        self.max_daily_loss_pct = 0.02         # 2% per day
        self.stop_loss_pct = 0.05              # 5% stop loss
        self.max_leverage = 1.5                # 1.5x max leverage
```

### State Manager Backend
In `main.py`:
```python
# Use SQLite (recommended for production)
state_manager = StateManager(backend='sqlite', db_path='portfolio.db')

# Use JSON (simple, no external deps)
state_manager = StateManager(backend='json', json_path='portfolio_state.json')
```

### Dashboard Settings
In `dashboard.py`, adjust:
- Refresh interval (sidebar slider)
- Historical lookback period
- Risk event filtering

---

## 🔍 Monitoring & Debugging

### View Risk Events
```bash
sqlite3 portfolio.db
SELECT * FROM risk_events WHERE severity = 'CRITICAL';
```

### View Trade History
```bash
sqlite3 portfolio.db
SELECT * FROM trades ORDER BY timestamp DESC LIMIT 20;
```

### Check Portfolio Snapshots
```python
state = StateManager(backend='sqlite')
history = state.get_history(days=7)
for snap in history:
    print(f"{snap['timestamp']}: NAV={snap['nav']:,.0f}")
```

---

## 📝 Example Deployment Flow

### Development (Current)
1. Run `main.py` locally with risk management enabled
2. Check `portfolio.db` for trade/event history
3. Launch dashboard to view metrics
4. Iterate on risk thresholds

### Paper Trading
1. Connect to broker's paper trading API
2. Replace `execute()` with broker API calls
3. Risk manager still validates all trades
4. Dashboard shows real broker data

### Live Trading
1. Enable persistent state backups
2. Set up automated crash recovery
3. Monitor dashboard continuously
4. Alert on risk violations
5. Keep kill switch ready

---

## ✅ Verification Checklist

- [x] Risk manager created with stops & limits
- [x] Position size enforcement (10% per symbol)
- [x] Daily loss circuit breaker (2% limit)
- [x] Stop loss at -5% per position
- [x] State persistence to SQLite
- [x] Trade audit trail with timestamps
- [x] Auto-save portfolio after each trade
- [x] Crash recovery capability
- [x] Live dashboard with real-time metrics
- [x] Multi-page dashboard (Dashboard, Performance, Alerts)
- [x] Integration into main.py

---

## 🔗 File Reference

| File | Purpose |
|------|---------|
| `risk_manager.py` | Risk limits, stops, circuit breakers |
| `state_persistence.py` | Portfolio state saving/loading, history |
| `dashboard.py` | Live monitoring Streamlit app |
| `main.py` | Updated to use both modules |
| `portfolio.db` | SQLite database (auto-created) |

---

## 📞 Next Steps (Phase 4)

When you're ready for the next phase:
1. **Broker Integration**: Connect to real/paper trading broker
2. **Live Data Feed**: Real-time price updates (replace Yahoo Finance)
3. **Email/SMS Alerts**: Notifications on risk violations
4. **Automated Recovery**: Handle broker disconnections gracefully
5. **Performance Reporting**: Daily/weekly automated reports

---

**Setup Complete! You now have production-ready risk management and persistent state storage. 🎉**
