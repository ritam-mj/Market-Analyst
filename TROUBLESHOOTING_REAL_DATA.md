# Real Data Integration Troubleshooting

## Quick Diagnostics

Run this command to diagnose the issue:

```bash
python diagnostic_real_data.py
```

This will test:
1. ✓ yfinance installation
2. ✓ pandas installation
3. ✓ Network connectivity to Yahoo Finance
4. ✓ DigitalTwin class loading
5. ✓ Real data fetching
6. ✓ Market state generation

---

## Common Issues & Solutions

### Issue 1: "No module named 'yfinance'"

**Error:** `ModuleNotFoundError: No module named 'yfinance'`

**Solution:**
```bash
pip install yfinance
```

**Verify:**
```bash
python -c "import yfinance; print(yfinance.__version__)"
```

---

### Issue 2: "Failed to fetch real data"

**Possible causes:**

#### A) Network connectivity issue
- Check your internet connection
- Try in a different network
- Yahoo Finance might be temporarily down

**Test:**
```python
import yfinance as yf
ticker = yf.Ticker('SPY')
print(ticker.history(period='1d'))
```

#### B) Invalid symbol
- Symbol must be case-sensitive (e.g., 'SPY' not 'spy')
- Symbol must be listed on Yahoo Finance
- Try 'SPY' first to test

**Known working symbols:**
- SPY, QQQ, IWM (major indices)
- AAPL, MSFT, GOOGL (tech stocks)
- TLT, BND (bonds)

#### C) Date range issues
- `days` parameter too large (> 10 years of data)
- `end_date` in the future
- Both `start_date` and `end_date` on weekends/holidays (no trading)

**Test with:**
```python
from simulator import DigitalTwin

# Simple test - fetch 10 days of SPY
data = DigitalTwin.fetch_real_market_data('SPY', days=10)
print(f"Fetched {len(data)} days of data")
```

---

### Issue 3: "Deprecated pandas method"

**Error:** `FutureWarning: fillna(method=...) is deprecated`

**Fix Applied:** ✓ Code updated to use `.bfill()` instead

**Current code:**
```python
df['volatility'] = df['volatility'].bfill().fillna(0.01)
```

---

### Issue 4: Partial data returned

**Problem:** Fewer days returned than requested

**Reason:** Yahoo Finance doesn't have data for weekends/holidays
- If you request 100 days, you might get 70 trading days
- This is normal and expected

**Solution:** Request more days to account for holidays/weekends
```python
# Instead of 100 days
data = DigitalTwin.fetch_real_market_data('SPY', days=100)

# Request with buffer (business days)
# 100 business days ≈ 140 calendar days
data = DigitalTwin.fetch_real_market_data('SPY', days=150)
```

---

### Issue 5: Empty DataFrame returned

**Problem:** `[ERROR] No data for {symbol}`

**Causes:**
1. Symbol doesn't exist on Yahoo Finance
2. Symbol was delisted
3. Symbol requires special format

**Test valid symbols:**
```bash
python diagnostic_real_data.py
```

**Try different symbols:**
```python
for sym in ['SPY', 'QQQ', 'AAPL', 'MSFT']:
    data = DigitalTwin.fetch_real_market_data(sym, days=5)
    print(f"{sym}: {len(data) if data is not None else 0} days")
```

---

## Step-by-Step Debugging

### Step 1: Verify Installation
```bash
python diagnostic_real_data.py
```

### Step 2: Check Network Manually
```python
import yfinance as yf
result = yf.Ticker("SPY").history(period="5d")
print(result)
```

### Step 3: Test DigitalTwin Import
```python
from simulator import DigitalTwin
print("✓ DigitalTwin imported")
print(hasattr(DigitalTwin, 'fetch_real_market_data'))
```

### Step 4: Try Fetching Small Dataset
```python
data = DigitalTwin.fetch_real_market_data('SPY', days=5)
print(f"Got {len(data) if data is not None else 0} days")
if data is not None:
    print(data.head())
```

### Step 5: Test State Generation
```python
sim = DigitalTwin()
states = sim.generate_from_real_data('SPY', days=5, data_df=data)
print(f"Generated {len(states)} states")
```

---

## Advanced Debugging

### Enable Verbose Logging

Edit `simulator.py` and add logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In fetch_real_market_data method, add:
print(f"[DEBUG] Fetching {symbol} from {start_date} to {end_date}")
print(f"[DEBUG] Downloaded {len(df)} rows")
```

### Check Pandas Version
```python
import pandas as pd
print(f"Pandas version: {pd.__version__}")

# Ensure >= 1.3.0 for bfill() support
```

### Check yfinance Version
```python
import yfinance
print(f"yfinance version: {yfinance.__version__}")
```

---

## If All Else Fails

### Option 1: Use cached test data
```python
# Load from CSV instead
import pandas as pd
data = pd.read_csv('spy_test_data.csv')
sim = DigitalTwin()
states = sim.generate_from_real_data('SPY', data_df=data)
```

### Option 2: Use synthetic data only
```python
# Fall back to synthetic data generation
sim = DigitalTwin()
states = sim.generate('SPY', days=100, scenario='bull')
```

### Option 3: Check offline resources
- Verify internet works: `ping google.com`
- Check if Yahoo Finance is up: `https://finance.yahoo.com`
- Try from different network/device

---

## Getting Help

**Minimal reproducible example for debugging:**

Save as `test_minimal.py`:
```python
from simulator import DigitalTwin

print("Fetching SPY...")
data = DigitalTwin.fetch_real_market_data('SPY', days=10)

if data is None:
    print("Failed to fetch SPY")
else:
    print(f"Success! Got {len(data)} days")
    print(data.head())

    sim = DigitalTwin()
    states = sim.generate_from_real_data('SPY', days=10, data_df=data)
    print(f"Generated {len(states)} states")
```

Run and share output:
```bash
python test_minimal.py
```

---

## Success Indicators

✓ You should see:
- `[Loaded real data] SPY: XX days, price range $XXX-$XXX`
- Market states generated with prices and cycle phases
- No error messages

✗ If you see:
- `[ERROR] Failed to fetch SPY:`
- `[WARNING] yfinance not installed`
- `No data for SPY`
- Follow the relevant solution above

---

## Quick Reference

| Error | First Fix |
|-------|-----------|
| `No module named 'yfinance'` | `pip install yfinance` |
| `No data for SPY` | Try different symbol or dates |
| Network error | Check internet connection |
| Empty data | Verify symbol on Yahoo Finance |
| Deprecation warning | ✓ Already fixed in code |

---

Run the diagnostic NOW:
```bash
python diagnostic_real_data.py
```
