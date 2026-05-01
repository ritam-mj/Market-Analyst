# Real Market Data Integration

## Overview

The MarketPredictor system now supports seamless integration with real market data from **Yahoo Finance**. This enables:

- **Backtesting** strategies on historical market conditions
- **Validation** of trading algorithms against real data
- **Calibration** of simulation parameters to match real market behavior
- **Live baseline** for shadow trading comparisons

## Installation

To use real market data features, install the Yahoo Finance library:

```bash
pip install yfinance
```

## Core API Methods

### 1. Fetch Real Market Data

```python
from simulator import MarketSimulator

# Fetch 100 days of data for a symbol
data = MarketSimulator.fetch_real_market_data('SPY', days=100)

# Fetch data up to a specific date
data = MarketSimulator.fetch_real_market_data('AAPL', days=252, end_date='2024-01-31')
```

**Returns**: DataFrame with columns:
- `timestamp`: Date/time of the market state
- `symbol`: Ticker symbol
- `price`: Closing price (adjusted)
- `returns`: Daily log returns
- `volatility`: 20-day rolling volatility

**Returns `None`** if data fetch fails.

### 2. Generate Market States from Real Data

```python
sim = MarketSimulator()

# Get market states for a symbol from real data
real_states = sim.generate_from_real_data('QQQ', days=60)

# Each state includes:
#   - price: Real historical price
#   - volatility: Calculated from real data
#   - cycle: Detected from recent price momentum
#   - timestamp: Real date/time
```

**Key Features**:
- Automatically detects market cycle phase (BULL/BEAR/CHOP) from lookback performance
- Stores outcomes in the learner for parameter calibration
- Returns list of `MarketState` objects ready for trading strategy testing

### 3. Compare Real vs Simulated Data

```python
# Get statistics on real data
real_data = MarketSimulator.fetch_real_market_data('SPY', days=100)
real_states = sim.generate_from_real_data('SPY', data_df=real_data)

# Compare with simulated scenarios
bull_states = sim.generate('SPY', days=100, scenario='bull')
bear_states = sim.generate('SPY', days=100, scenario='bear')

# Extract prices for analysis
real_prices = [s.price for s in real_states]
bull_prices = [s.price for s in bull_states]
bear_prices = [s.price for s in bear_states]
```

## Usage Examples

### Example 1: Simple Backtest

```python
from simulator import MarketSimulator
from trading_engine import TradingEngine
from config import Config

# Load real market data
sim = MarketSimulator()
real_states = sim.generate_from_real_data('SPY', days=252)

# Initialize trading engine
config = Config()
engine = TradingEngine(config)

# Run backtest
for state in real_states:
    signal = engine.compute_signal(state)
    engine.execute_trade(signal, state)

# Analyze performance
results = engine.get_performance_summary()
print(f"Total return: {results['total_return']:.2%}")
print(f"Sharpe ratio: {results['sharpe_ratio']:.2f}")
```

### Example 2: Compare Strategies on Real Data

```python
# Fetch data
real_data = MarketSimulator.fetch_real_market_data('AAPL', days=100)
sim = MarketSimulator()
real_states = sim.generate_from_real_data('AAPL', data_df=real_data)

# Test multiple strategies
from trader import ShadowTrader, MomentumTrader

traders = {
    'Shadow': ShadowTrader(config),
    'Momentum': MomentumTrader(config),
}

for name, trader in traders.items():
    pnl = 0
    for state in real_states:
        signal = trader.compute_signal(state)
        # ... execute logic
    print(f"{name}: {pnl:.2f} profit")
```

### Example 3: Validate Simulation Parameters

```python
# Get real market statistics
real_data = MarketSimulator.fetch_real_market_data('QQQ', days=252)
real_returns = real_data['returns'].dropna()
real_vol = np.std(real_returns)
real_mean = np.mean(real_returns)

# Generate simulated data with similar parameters
sim = MarketSimulator()
sim_states = sim.generate('QQQ', days=252, params={
    'mu': real_mean,
    's': real_vol,
})

# Compare distributions
sim_returns = np.diff([s.price for s in sim_states]) / np.array([s.price for s in sim_states[:-1]])
sim_vol = np.std(sim_returns)
sim_mean = np.mean(sim_returns)

print(f"Real volatility: {real_vol*100:.2f}%  vs  Simulated: {sim_vol*100:.2f}%")
print(f"Real mean: {real_mean*100:.3f}%  vs  Simulated: {sim_mean*100:.3f}%")
```

### Example 4: Ensemble with Real Calibration

```python
# Fetch real baseline
base_data = MarketSimulator.fetch_real_market_data('SPY', days=100)
sim = MarketSimulator()

# Generate ensemble scenarios
ensemble = sim.generate_ensemble('SPY', days=100, n_scenarios=5)

# Compare each scenario to real data
real_prices = base_data['price'].values
final_real_price = real_prices[-1]

for scenario_name, states in ensemble.items():
    final_sim_price = states[-1].price
    diff_pct = (final_sim_price - final_real_price) / final_real_price * 100
    print(f"{scenario_name:15}: {diff_pct:+.2f}% vs real")
```

## Data Quality & Limitations

### What Works Well
✓ Liquid symbols (SPY, AAPL, QQQ, etc.)  
✓ Last 10+ years of data  
✓ Daily close prices  
✓ High-volume, standard trading hours  

### Limitations
✗ Insufficient data for symbols < 1 year old  
✗ Delisted/merged companies  
✗ Corporate actions (splits, dividends) may skew returns  
✗ Extended hours trading not included  
✗ Crypto and OTC markets limited  

### Volatility Calculation
- Rolling 20-day window on daily returns
- Uses log-normal formula: `vol = std(ln(P_t / P_{t-1}))`
- Minimum volatility: 1% (to avoid division errors)

## Performance Considerations

1. **Caching**: Store fetched data locally to avoid repeated API calls
   ```python
   data = MarketSimulator.fetch_real_market_data('SPY', days=252)
   data.to_csv('spy_historical.csv')
   
   # Later: load from cache
   data = pd.read_csv('spy_historical.csv', index_col='timestamp')
   ```

2. **Date Range**: Fetching 10 years of data takes ~2-3 seconds

3. **API Rate Limits**: Yahoo Finance has rate limiting; space requests by 1-2 seconds

## Troubleshooting

### "yfinance not installed"
```bash
pip install yfinance
```

### "No data for {symbol}"
- Check symbol spelling (case-sensitive)
- Ensure symbol is listed on a major US exchange
- Try a different symbol to test connectivity

### Gaps in data
- Weekends and holidays have no trading data (normal)
- If a weekday is missing, company may have been delisted

### High volatility estimates
- Check for stock splits or major corporate actions
- Verify data isn't covering a crisis period
- Use longer rolling windows (e.g., 60-day instead of 20-day)

## Integration with MarketPredictor Workflow

```
Real Market Data
    ↓
fetch_real_market_data()
    ↓
generate_from_real_data()
    ↓
MarketState objects
    ↓
ShadowTrader / TradingStrategy
    ↓
Backtesting Results
    ↓
Compare with simulated scenarios
    ↓
Validate & refine parameters
```

## API Reference

### MarketSimulator.fetch_real_market_data()

```python
@staticmethod
def fetch_real_market_data(
    symbol: str,
    days: int = 100,
    end_date: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """
    Fetch real market data from Yahoo Finance.
    
    Args:
        symbol: Ticker symbol (e.g., 'SPY', 'AAPL')
        days: Number of days of history to fetch
        end_date: End date as 'YYYY-MM-DD', defaults to today
    
    Returns:
        DataFrame or None if fetch fails
        
    Raises:
        ImportError: If yfinance is not installed
    """
```

### MarketSimulator.generate_from_real_data()

```python
def generate_from_real_data(
    self,
    symbol: str,
    days: int = 30,
    data_df: Optional[pd.DataFrame] = None
) -> List[MarketState]:
    """
    Generate market states from real historical data.
    
    Args:
        symbol: Ticker symbol
        days: Number of days to use (from end of data)
        data_df: Real market DataFrame. Fetches if None.
    
    Returns:
        List of MarketState objects with real market prices
        and detected cycle phases
    """
```

## Next Steps

1. **Backtesting Infrastructure**: Build systematic backtesting with metrics
2. **Multi-symbol Support**: Trade correlations across symbols
3. **Live Data**: Integrate WebSocket for real-time prices
4. **Machine Learning**: Calibrate prediction models on real data
5. **Risk Management**: Add drawdown monitoring on real backtests

