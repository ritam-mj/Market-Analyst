# Real Data Integration - Quick Reference

## 30-Second Start

```python
from simulator import MarketSimulator

# Fetch 100 days of real data
data = MarketSimulator.fetch_real_market_data('SPY', days=100)

# Generate market states from real data
sim = MarketSimulator()
states = sim.generate_from_real_data('SPY', data_df=data)

# Use in your trading strategy
for state in states:
    print(f"Date: {state.timestamp}, Price: ${state.price:.2f}, Vol: {state.volatility*100:.1f}%")
```

## Common Tasks

### Backtest on Real Data
```python
from trader import ShadowTrader
from config import Config

sim = MarketSimulator()
real_states = sim.generate_from_real_data('AAPL', days=100)

trader = ShadowTrader(Config())
for state in real_states:
    signal = trader.compute_signal(state)
    # ... execute trade
```

### Compare Real vs Simulated
```python
real = sim.generate_from_real_data('QQQ', days=100)
bull = sim.generate('QQQ', days=100, scenario='bull')

real_ret = (real[-1].price - real[0].price) / real[0].price
bull_ret = (bull[-1].price - bull[0].price) / bull[0].price

print(f"Real: {real_ret*100:+.2f}% | Bull: {bull_ret*100:+.2f}%")
```

### Get Market Statistics
```python
import numpy as np

data = MarketSimulator.fetch_real_market_data('IEEE', days=252)
prices = data['price'].values
returns = np.diff(prices) / prices[:-1]

print(f"Volatility: {returns.std()*100:.2f}%")
print(f"Return: {returns.mean()*100:.3f}%")
print(f"Sharpe: {returns.mean() / returns.std() * np.sqrt(252):.2f}")
```

## API Cheat Sheet

| Method | Input | Output | Use Case |
|--------|-------|--------|----------|
| `fetch_real_market_data()` | Symbol, days | DataFrame | Get raw OHLCV data |
| `generate_from_real_data()` | Symbol or DataFrame | List[MarketState] | Create trading states |
| `generate_ensemble()` | Symbol, days | Dict[scenario] → List[MarketState] | Multi-scenario testing |
| `generate()` | Symbol, scenario | List[MarketState] | Generate synthetic data |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: yfinance` | `pip install yfinance` |
| `No data for {symbol}` | Check symbol (case-sensitive), try SPY |
| `Empty DataFrame returned` | Symbol may be delisted; try another |
| Slow to run | Use fewer days or cache results to CSV |

## Data Structure

### MarketState Object
```python
state.symbol        # 'SPY'
state.price         # 456.23
state.volatility    # 0.15 (15%)
state.cycle         # CyclePhase.BULL
state.timestamp     # datetime(2024, 1, 31)
```

### DataFrame from fetch_real_market_data()
```
           timestamp   symbol   price    returns  volatility
0   2024-01-01       SPY    450.00  0.000000      0.012000
1   2024-01-02       SPY    451.23  0.002730      0.012500
2   2024-01-03       SPY    449.45 -0.003941      0.012100
```

## Performance Tips

1. **Cache data to disk**
   ```python
   data.to_csv('spy_100d.csv')
   data = pd.read_csv('spy_100d.csv')
   ```

2. **Vectorize operations**
   ```python
   prices = np.array([s.price for s in states])  # Fast
   # Don't: prices = []; for s in states: prices.append(s.price)
   ```

3. **Batch API calls**
   ```python
   # Good: fetch 252 days once
   data = fetch_real_market_data('SPY', days=252)
   
   # Bad: call 252 times for daily data
   for i in range(252): data[i] = fetch_real_market_data(...)
   ```

## Unit Testing

```python
def test_fetch_real_data():
    data = MarketSimulator.fetch_real_market_data('SPY', days=10)
    assert len(data) == 10
    assert 'price' in data.columns
    assert data['price'].iloc[-1] > 0

def test_generate_from_real():
    sim = MarketSimulator()
    states = sim.generate_from_real_data('SPY', days=10)
    assert len(states) == 10
    assert all(s.price > 0 for s in states)
```

## Next: Run Test Suite

```bash
cd c:\Users\ritam\MarketPredictor
python test_real_data.py
```

This will:
1. Fetch real data for 3 symbols
2. Compare real vs simulated statistics
3. Run shadow trading backtest
4. Generate ensemble scenarios

---

**Last Updated**: 2024  
**Maintainer**: MarketPredictor Dev Team
