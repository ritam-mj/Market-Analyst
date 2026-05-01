# Documentation Index - MarketPredictor

This file serves as an index for all documentation. **Start with [README.md](README.md) for complete system information.**

---

## Primary Documentation

- **[README.md](README.md)** ⭐ **START HERE** - Comprehensive guide covering:
  - Quick Start
  - System Architecture  
  - Installation & Setup
  - Usage Guide (main.py, backtest.py, dashboard.py)
  - Risk Management
  - State Persistence
  - Live Dashboard
  - Backtesting
  - Testing & Verification
  - Deployment Roadmap
  - API Reference
  - Troubleshooting

---

## Topic-Specific References

### Getting Started
- **Quick Start**: See [README.md - Quick Start](#quick-start)
- **Installation**: See [README.md - Installation & Setup](#installation--setup)
- **Running First Trade**: See [README.md - Usage Guide](#usage-guide)

### Trading & Scenarios
- **Main Trading Script**: See [README.md - Usage Guide / Main Script](#main-script-mainpy)
- **Backtesting**: See [README.md - Backtesting](#backtesting)
- **Market Scenarios**: See [README.md - System Architecture](#market-cycle-detection)
  - Bull, Bear, Chop, Flash Crash, Mixed

### Risk Management
- **Risk Manager Overview**: See [README.md - Risk Management](#risk-management)
- **Risk Limits & Stops**: See [README.md - Risk Management / Risk Manager](#risk-manager-risk_managerpy)
- **Customizing Limits**: See [README.md - Risk Management / Customizing Risk Limits](#customizing-risk-limits)

### Data & Persistence  
- **State Persistence**: See [README.md - State Persistence](#state-persistence)
- **Database Schema**: See [README.md - State Persistence / Database Schema](#database-schema)
- **Querying Database**: See [README.md - State Persistence / Querying Database](#querying-database)

### Monitoring & Dashboard
- **Live Dashboard**: See [README.md - Live Dashboard](#live-dashboard)
- **Dashboard Features**: See [README.md - Live Dashboard / Dashboard Features](#dashboard-features)

### Development & Testing
- **System Verification**: See [README.md - Testing & Verification](#testing--verification)
- **Running Scenarios**: See [README.md - Testing & Verification / Running Scenarios](#running-scenarios)
- **Backtest Verification**: See [README.md - Testing & Verification / Backtest Verification](#backtest-verification)

### Troubleshooting
- **Common Issues**: See [README.md - Troubleshooting](#troubleshooting)
- **Unicode Errors**: See [README.md - Troubleshooting / Unicode Encoding Errors](#issue-unicode-encoding-errors)
- **Data Connection**: See [README.md - Troubleshooting / Yahoo Finance Connection](#issue-yahoo-finance-connection-failed)

### Deployment
- **Roadmap**: See [README.md - Deployment Roadmap](#deployment-roadmap)
- **Next Phase**: See [README.md - Support & Next Steps](#next-phase-broker-integration)

---

## Legacy Documentation (Archived)

The following documents contain information now consolidated in README.md:

| File | Content | Location in README |
|------|---------|-------------------|
| GETTING_STARTED.md | Installation steps | Installation & Setup |
| QUICK_START.md | Quick start examples | Quick Start |
| REAL_DATA_INTEGRATION.md | Real data fetching | Usage Guide |
| REAL_DATA_QUICK_REF.md | Real data commands | Quick Start |
| README_REAL_DATA_ADDON.md | Real data setup | Installation & Setup |
| RISK_AND_PERSISTENCE_SETUP.md | Risk & persistence | Risk Management + State Persistence |
| LEARNING_SYSTEM.md | Agent learning | System Architecture |
| INTEGRATION_POINTS.md | Component integration | System Architecture |
| IMPLEMENTATION_SUMMARY.md | Implementation details | System Architecture |
| IMPLEMENTATION_COMPLETE.md | Completion status | Testing & Verification |
| IMPROVEMENTS_EXECUTED.md | Features added | Deployment Roadmap |
| FINAL_DELIVERY_SUMMARY.md | Delivery status | Deployment Roadmap (Phase 1) |
| NEXT_STEPS_COMPLETE.md | Next phases | Deployment Roadmap (Phase 2+) |
| COMPLETION_CHECKLIST.md | Task checklist | Testing & Verification |
| TROUBLESHOOTING_REAL_DATA.md | Data troubleshooting | Troubleshooting |
| README_INDEX.md | Previous index | (Replaced by this file) |

---

## File Structure

```
MarketPredictor/
├── 📄 README.md                     ⭐ START HERE
├── 📄 DOCUMENTATION_INDEX.md        This file
│
├── 🔧 Core Trading System
│   ├── main.py                      # Trading loop
│   ├── backtest.py                  # Historical testing
│   ├── dashboard.py                 # Live monitoring
│   ├── verify_system.py             # System validation
│   │
│   ├── agents.py                    # 6 agent models
│   ├── blackboard.py                # Conflict resolution
│   ├── market_state.py              # Data classes
│   ├── protocol.py                  # Regime detection
│   ├── simulator.py                 # Market simulation
│   ├── execution.py                 # Portfolio execution
│   ├── learning.py                  # Learning system
│   │
│   ├── risk_manager.py              # Risk limits & stops
│   └── state_persistence.py         # SQLite persistence
│
├── 📊 Database
│   └── portfolio.db                 # Auto-created SQLite database
│
├── 📁 Tests
│   └── tests/
│       └── test_simulator.py        # Simulator unit tests
│   ├── test_real_data.py            # Real data tests
│   └── test_fetch_debug.py          # Debug utilities
│
├── 📚 Configuration
│   └── learner_state.json           # Optimization parameters
│
└── 📖 Documentation (Archived)
    ├── GETTING_STARTED.md           → See README.md
    ├── QUICK_START.md               → See README.md  
    ├── REAL_DATA_INTEGRATION.md     → See README.md
    ├── RISK_AND_PERSISTENCE_SETUP.md → See README.md
    └── [10 more]                    → See table above
```

---

## Quick Commands Reference

| Task | Command |
|------|---------|
| **Verify System** | `python verify_system.py` |
| **Run Bull Scenario** | `python main.py bull 30` |
| **Run Bear Scenario** | `python main.py bear 30` |
| **Backtest 90 Days** | `python backtest.py 90` |
| **Backtest 1 Year** | `python backtest.py 252` |
| **Backtest 5 Years** | `python backtest.py 1260` |
| **Test Symbol** | `python backtest.py --symbol AAPL 90` |
| **Launch Dashboard** | `streamlit run dashboard.py` |
| **Query Trades** | `sqlite3 portfolio.db "SELECT * FROM trades;"` |
| **Get NAV History** | `sqlite3 portfolio.db "SELECT timestamp, nav FROM portfolio_snapshots;"` |

---

## Architecture Overview

```
Agents (6 Models)
    ↓
Blackboard (Conflict Resolution)
    ↓
Execution (Portfolio Management)
    ↓
Risk Manager (Validation & Stops)
    ↓
State Persistence (SQLite Database)
    ↓
Dashboard (Live Monitoring)
```

---

## Key Dates & Status

- **Created**: May 1, 2026
- **Status**: ✅ Production-Ready (Phase 1 Complete)
- **Phase 1**: ✅ Risk Management + State Persistence + Dashboard
- **Phase 2**: ⏭️ Broker Integration (Next)
- **Phase 3**: ⏭️ Cloud Deployment
- **Phase 4**: ⏭️ Advanced Features

---

## System Verification Status

Last verified: May 1, 2026

✅ All modules import correctly  
✅ Core components functional  
✅ All required files present  
✅ Database persistence working  
✅ Risk management system active  
✅ All scenarios tested (bull, bear, chop, flash_crash, mixed)  
✅ Backtesting works (30/90/252/1260 days)  
✅ Dashboard ready for launch  

---

## For More Information

1. **Getting Started**: Go to [README.md - Quick Start](#quick-start)
2. **Understanding Architecture**: Go to [README.md - System Architecture](#system-architecture)
3. **Running Trades**: Go to [README.md - Usage Guide](#usage-guide)
4. **Risk Setup**: Go to [README.md - Risk Management](#risk-management)
5. **Monitoring**: Go to [README.md - Live Dashboard](#live-dashboard)
6. **Historical Testing**: Go to [README.md - Backtesting](#backtesting)
7. **Troubleshooting**: Go to [README.md - Troubleshooting](#troubleshooting)
8. **API Reference**: Go to [README.md - API Reference](#api-reference)

---

**Last Updated**: May 1, 2026  
**Maintained By**: MarketPredictor Development Team  
**License**: Open Source
