# Pentagon Ecosystem - Quick Start Guide

## Installation

```bash
# Requires Python 3.10+
pip install pandas numpy
# Optional: pip install scikit-learn  (for KMeans fallback)
```

## Running the System

### Mode 1: Live Trading Simulation

Run one market scenario end-to-end with visible trades:

```bash
# Basic usage
python main.py [scenario] [days]

# Examples:
python main.py                    # Default: mixed market, 30 days
python main.py bull 20            # Bull market, 20 days
python main.py bear 30            # Bear market, 30 days
python main.py chop 15            # Choppy market, 15 days
python main.py flash_crash 10     # Crisis mode, 10 days

# Output: Agent trades + final NAV + trade history
```

---

### Mode 2: Ensemble Shadow Trading

Test strategy across 4 market regimes (bull/bear/chop/flash_crash):

```bash
# Shadow trading usage
python main.py shadow [--days N]

# Examples:
python main.py shadow             # Default: 20-day scenarios
python main.py shadow --days 30   # 30-day scenarios
python main.py shadow --days 10   # 10-day scenarios

# Output: Performance table (PnL, NAV, trades, price change per scenario)
```

---

### Mode 3: Hyperparameter Importance Analysis

Rank simulator parameters by their impact on strategy performance:

```bash
# Analysis usage
python main.py analyze [--params P1,P2,...] [--days N]

# Examples:
python main.py analyze                                    # All params, 30 days
python main.py analyze --params lamb,mu_j                 # Jump params, 30 days
python main.py analyze --params sigma_j --days 15         # Single param, 15 days
python main.py analyze --params lamb,mu_j,sigma_j --days 60  # Full analysis, 60 days

# Output: Importance ranking (normalized 0.0-1.0)
```

---

## Key System Components

### Six Trading Agents

| Agent | Role | Main Indicators |
|-------|------|-----------------|
| Tactician (A) | Quick opportunistic trades | RSI, MACD, EMA |
| Explorer (B) | Low-confidence probing | Random + MACD confirmation |
| Sentinel (C) | Risk management | ATR, Sharpe, options |
| Anchor (D) | Long-term positioning | 200-day MA, core lock |
| Treasurer (E) | Capital adequacy | Cash reserve checks |
| MetaOpt (F) | Meta-optimization | Placeholder for auto-tuning |

### Conflict Resolution

- **Virtual Netting**: Groups BUY/SELL, SHORT/COVER, PUT/CALL orders
- **Core Lock**: Prevents selling Anchor's locked positions
- **Hedge Gating**: Restricts shorts/puts until bear market detected

### Learning Components

- **SimulatorLearner**: Tracks outcomes per scenario, suggests adaptive parameters
- **ShadowTrader**: Replays agents through scenarios, measures performance
- **HyperparameterAnalyzer**: Ranks simulator parameters by importance

---

## Output Examples

### Example 1: Single Epoch Trading

```bash
$ python main.py bear 20

2026-03-26 | Blackboard -> PUT 4.0 SPY @ 99.67
2026-03-27 | Blackboard -> PUT 4.0 SPY @ 99.67
...
Final NAV: $1,000,006.02, Realized PnL: $6.02

Trade history:
001 | PUT 4.0 SPY @ 99.6747 | trade_pnl=-1.9935 | realized_pnl=0.00
...
```

### Example 2: Ensemble Shadow Trading

```bash
$ python main.py shadow --days 15

Scenario Performance:
Scenario             PnL          NAV   Trades Price Change
------------------------------------------------------------
bull            $    0.00 $1,000,000.00        0       +0.47%
bear            $  -29.99 $  999,970.01       30       +0.63%
chop            $    0.00 $1,000,000.00        0       +0.24%
flash_crash     $  -13.36 $  999,986.64       18      -16.21%

Average PnL: $-10.84
Std Dev PnL: $14.24
```

### Example 3: Hyperparameter Analysis

```bash
$ python main.py analyze --params lamb,mu_j,sigma_j --days 20

=== Hyperparameter Importance Analysis ===
Params: ['lamb', 'mu_j', 'sigma_j']
Days per run: 20

Hyperparameter Importance Ranking:
  mu_j: 1.0000        (jump direction - CRITICAL)
  sigma_j: 0.9470     (jump volatility - HIGH)
  lamb: 0.0982        (jump frequency - LOW)
```

---

## Interpretation Guide

### Realized PnL Signals

- **Positive PnL**: Strategy outperformed market (or hedged down-move profitably)
- **Negative PnL**: Strategy underperformed (aggressive hedging costs premium)
- **Zero PnL**: No trades executed (agents uncertain or market too quiet)

### Trade Count Patterns

- **High count in bear**: Sentinel buying defensive options
- **Low count in bull**: Agents cautious of losses
- **Zero in chop**: Uncertain signal, threshold not met

### Parameter Importance

- **1.0**: Change by ±20% causes maximum variance in strategy PnL
- **0.5**: Moderate impact; worth tuning
- **0.1**: Minimal impact; can leave at default

---

## Customization

### Add New Market Scenarios

Edit `simulator.py` `generate()` method to add scenario types:

```python
if scenario == "custom":
    params = {"mu": 0.002, "sigma": 0.015, "lamb": 0.1, ...}
```

### Tune Agent Aggressiveness

Edit `agents.py` class thresholds:

```python
class Sentinel:
    PUT_THRESHOLD = 0.3  # Lower = more frequent hedges
```

### Adjust Learning Blend

Edit `simulator.py` `adaptive_params()` method:

```python
adapted[key] = 0.3 * best[key] + 0.7 * base_params[key]
               # Change 0.3 (learner weight) or 0.7 (base weight)
```

---

## Troubleshooting

### "No trades executed"
- Market may be too quiet or agents too conservative
- Try: `python main.py bear 30` (higher volatility triggers more trading)

### "All PUT trades, negative PnL"
- Hedge cost exceeds benefit in current market regime
- Try: `python main.py shadow` to see regime-specific performance

### "ModuleNotFoundError: pandas"
- Install missing dependency: `pip install pandas numpy`

### "DeprecationWarning: datetime.utcnow()"
- Harmless warning; library update coming in Python 3.13+

---

## Files Overview

- `main.py`: Entry point with CLI and three modes
- `market_state.py`: Data packets (MarketState, TradeIntent, CyclePhase)
- `agents.py`: Six trading agents with indicators
- `blackboard.py`: Conflict resolution engine
- `protocol.py`: Regime detection and hedge gating
- `simulator.py`: Jump-diffusion price generator + learner
- `execution.py`: Portfolio accounting and trade history
- `learning.py`: ShadowTrader and HyperparameterAnalyzer
- `tests/`: Unit test suite (pytest)
- `README.md`: Full documentation
- `LEARNING_SYSTEM.md`: Advanced learning features

---

## Next Steps

1. **Run single epoch**: `python main.py bear 30` → observe agent behavior
2. **Test ensemble**: `python main.py shadow --days 20` → compare regime performance
3. **Analyze parameters**: `python main.py analyze --days 20` → identify tuning priorities
4. **Read LEARNING_SYSTEM.md**: Deep dive into how learning works
5. **Extend agents**: Add real technical indicators or ML models

---

## Support

For issues or questions:
- Check `LEARNING_SYSTEM.md` for advanced concepts
- Review agent logic in `agents.py` for decision rules
- Inspect `execution.py` for trade accounting details
- Run with different `--days` and `--params` to see sensitivity

Happy trading! 📈
