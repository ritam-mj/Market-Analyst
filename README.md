# Pentagon Ecosystem - Multi-Agent Autonomous Trading System

This repository contains a Python prototype of the Pentagon Ecosystem, a blackboard-based cooperative multi-agent trading system with integrated learning and hyperparameter optimization.

## Components

- `market_state.py`: `MarketState`, `CyclePhase`, and `TradeIntent` dataclasses.
- `blackboard.py`: `Blackboard` conflict-resolution engine with core lock and virtual netting.
- `agents.py`: 6 agent classes with technical indicators (RSI, MACD, EMA, ATR, Sharpe, KMeans).
- `protocol.py`: `RegimeDetector` and `SyntheticHedgeProtocol` for market condition classification.
- `simulator.py`: `DigitalTwin` jump-diffusion environment with `SimulatorLearner` for adaptive param suggestion.
- `execution.py`: `Portfolio` class with position tracking, trade history, and realized PnL calculation.
- `learning.py`: `ShadowTrader` (ensemble backtesting) and `HyperparameterAnalyzer` (sensitivity ranking).
- `main.py`: Orchestration loop with CLI support for different run modes.

## Usage

### 1. Single Epoch Run (Live Trading Simulation)

```bash
python main.py [scenario] [days]
```

- `scenario`: bull, bear, chop, mixed, flash_crash (default: mixed)
- `days`: simulation length (default: 30)

Examples:
```bash
python main.py              # 30-day mixed scenario
python main.py bull 20      # 20-day bull market
python main.py bear 30      # 30-day bear market with volatility
```

Output: Agent intents, executed trades, final NAV, trade history with per-trade PnL.

### 2. Hyperparameter Importance Analysis

```bash
python main.py analyze [--params param1,param2,...] [--days N]
```

Measures sensitivity of strategy performance to simulator hyperparameters across multiple ensemble runs.

Examples:
```bash
python main.py analyze                              # All params, 30 days
python main.py analyze --params lamb,mu_j --days 15  # Jump params, 15 days
```

Output: Importance ranking (0.0-1.0 scale). Higher scores = more critical parameters.

```
Hyperparameter Importance Ranking:
  mu_j: 1.0000        (jump direction bias - most important)
  sigma_j: 0.6943     (jump volatility - second order)
  lamb: 0.4814        (jump frequency - third order)
```

### 3. Ensemble Shadow Trading

```bash
python main.py shadow [--days N]
```

Backward-tests strategy across 4 different market scenarios (bull, bear, chop, flash_crash) to evaluate regime-dependent performance.

Examples:
```bash
python main.py shadow                # 20-day scenarios
python main.py shadow --days 30      # 30-day scenarios
```

Output: Performance table (PnL, NAV, trade count, price change per scenario) + aggregated statistics.

```
Scenario Performance:
Scenario             PnL          NAV   Trades Price Change
------------------------------------------------------------
bull            $    0.00 $1,000,000.00        0       +0.47%
bear            $  -29.99 $  999,970.01       30       +0.63%
chop            $    0.00 $1,000,000.00        0       +0.24%
flash_crash     $  -13.36 $  999,986.64       18      -16.21%

Average PnL: $-10.84
Std Dev PnL: $14.24
Avg Trades/Scenario: 12.0
```

## System Architecture

### Agent Models

- **The Tactician (Model A)**: Quick opportunistic trades on RSI, MACD, EMA crossovers. Cycle-based fallback.
- **The Explorer (Model B)**: Low-confidence probing trades. 50% pass rate for discovery.
- **The Sentinel (Model C)**: Risk management via options (PUT, CALL) for defense/upside capture.
- **The Anchor (Model D)**: Long-term positioning detection via 200-day moving average; locks positions via core lock.
- **The Treasurer (Model E)**: Cash reserve management and capital adequacy checks.
- **The MetaOpt (Model F)**: Meta-optimization placeholder for future adaptive tuning.

### Blackboard Conflict Resolution

- **Virtual Netting**: Aggregates BUY/SELL, SHORT/COVER, PUT/CALL orders per symbol to reduce position fragmentation.
- **Core Lock**: Prevents strategic position de-risking by agents other than the Anchor. Once Anchor declares a BUY, the position is locked against other agents' SHORTs.
- **Hedge Gating**: Synthetic hedging (SHORT, PUT) only available when bear regime is detected (drawdown >7% or volatility >0.6).

### Learning System

#### SimulatorLearner (in simulator.py)
- Tracks historical outcomes per scenario: maps (scenario, params) → (MSE, final_price).
- Suggests adaptive parameters via 30/70 blend: 30% from best-performing historical params, 70% from base.
- Enables "learning-on-simulator": dynamic parameter adjustment across repeated scenario generations.

#### ShadowTrader (in learning.py)
- Replays agents through generated price histories to measure strategy performance.
- Collects metrics: NAV, realized PnL, trade count, price change per scenario.
- Runs on ensemble of 2-5 scenarios to average out variance.

#### HyperparameterAnalyzer (in learning.py)
- Baseline performance: runs strategy N times with default parameters, computes average PnL.
- Perturbation measurement: ±20% perturb each hyperparameter, re-run, measure impact.
- Sensitivity ranking: importance = |perturbed_pnl - baseline_pnl| / max_impact, normalized to [0, 1].

## Requirements

- Python 3.10+
- pandas
- numpy
- scikit-learn (optional, for KMeans fallback)

## Notes

- Designed for extensibility: agents can be replaced with real ML models, indicators can be enhanced.
- Numeric stability: History generation guards against inf/nan via direct return sampling → cumprod.
- Trade accountability: Every trade logged with cash/PnL snapshots for post-epoch analysis.
- Regime-driven: Bear/bull detection triggers hedging availability; cycle phases guide fallback logic.
- Learning-ready: Full framework for adaptive parameter discovery across scenarios.
