"""
Persistent State Management - Save and restore portfolio state to/from storage

Supports:
- JSON file-based storage (development)
- SQLite database (production-ready)
- Automatic crash recovery
- Portfolio snapshots and history
"""

import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import os

logger = logging.getLogger(__name__)


class PortfolioSnapshot:
    """Represents a point-in-time portfolio state"""
    
    def __init__(self, timestamp: datetime, nav: float, cash: float, 
                 positions: Dict, realized_pnl: float, trade_count: int):
        self.timestamp = timestamp
        self.nav = nav
        self.cash = cash
        self.positions = positions
        self.realized_pnl = realized_pnl
        self.trade_count = trade_count
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'nav': self.nav,
            'cash': self.cash,
            'positions': self.positions,
            'realized_pnl': self.realized_pnl,
            'trade_count': self.trade_count,
        }


class StateManager:
    """
    Manages persistent storage of portfolio state.
    
    Supports both JSON (simple) and SQLite (production) backends.
    
    Usage:
        # JSON backend (simple)
        state = StateManager(backend='json')
        state.save(portfolio)
        restored_portfolio = state.load()
        
        # SQLite backend (production)
        state = StateManager(backend='sqlite')
        state.save(portfolio)
        history = state.get_history(days=7)
    """
    
    def __init__(self, backend: str = 'sqlite', db_path: str = 'portfolio.db', json_path: str = 'portfolio_state.json'):
        self.backend = backend
        self.db_path = db_path
        self.json_path = json_path
        
        if backend == 'sqlite':
            self.db_path = db_path
            self._init_sqlite()
        elif backend == 'json':
            self.json_path = json_path
        else:
            raise ValueError(f"Unknown backend: {backend}")
        
        logger.info(f"StateManager initialized with {backend} backend")
    
    def _init_sqlite(self):
        """Initialize SQLite database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Portfolio snapshots table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                nav REAL NOT NULL,
                cash REAL NOT NULL,
                realized_pnl REAL NOT NULL,
                positions_json TEXT NOT NULL,
                trade_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Trades table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                pnl REAL,
                realized_pnl REAL,
                cash REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Risk events table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                rule TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT,
                action TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON portfolio_snapshots(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)")
            
            conn.commit()
            conn.close()
            logger.info(f"SQLite database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite: {e}")
            raise
    
    def save(self, portfolio, nav: float = None) -> bool:
        """Save portfolio state to persistent storage"""
        try:
            # Build positions dict
            positions_dict = {
                symbol: {
                    'quantity': pos.quantity,
                    'avg_price': pos.avg_price,
                    'symbol': pos.symbol,
                }
                for symbol, pos in portfolio.positions.items()
            }
            
            timestamp = datetime.now()
            if nav is None:
                nav = portfolio.net_asset_value({})
            
            if self.backend == 'json':
                return self._save_json(timestamp, nav, portfolio.cash, 
                                      positions_dict, portfolio.realized_pnl)
            elif self.backend == 'sqlite':
                return self._save_sqlite(timestamp, nav, portfolio.cash,
                                        positions_dict, portfolio.realized_pnl,
                                        len(portfolio.trade_history))
        except Exception as e:
            logger.error(f"Failed to save portfolio state: {e}")
            return False
    
    def _save_json(self, timestamp: datetime, nav: float, cash: float,
                   positions: Dict, realized_pnl: float) -> bool:
        """Save to JSON file"""
        try:
            data = {
                'timestamp': timestamp.isoformat(),
                'nav': nav,
                'cash': cash,
                'positions': positions,
                'realized_pnl': realized_pnl,
                'backup_timestamp': datetime.now().isoformat(),
            }
            
            # Write with backup
            if Path(self.json_path).exists():
                backup_path = f"{self.json_path}.bak"
                Path(self.json_path).rename(backup_path)
            
            with open(self.json_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Portfolio saved to {self.json_path}")
            return True
        except Exception as e:
            logger.error(f"JSON save failed: {e}")
            return False
    
    def _save_sqlite(self, timestamp: datetime, nav: float, cash: float,
                     positions: Dict, realized_pnl: float, trade_count: int) -> bool:
        """Save to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            positions_json = json.dumps(positions)
            
            cursor.execute("""
            INSERT INTO portfolio_snapshots 
            (timestamp, nav, cash, realized_pnl, positions_json, trade_count)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp.isoformat(), nav, cash, realized_pnl, positions_json, trade_count))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Portfolio snapshot saved to SQLite (NAV: ${nav:,.2f})")
            return True
        except Exception as e:
            logger.error(f"SQLite save failed: {e}")
            return False
    
    def load(self) -> Optional[Dict]:
        """Load latest portfolio state from persistent storage"""
        try:
            if self.backend == 'json':
                return self._load_json()
            elif self.backend == 'sqlite':
                return self._load_sqlite()
        except Exception as e:
            logger.error(f"Failed to load portfolio state: {e}")
            return None
    
    def _load_json(self) -> Optional[Dict]:
        """Load from JSON file"""
        try:
            if not Path(self.json_path).exists():
                logger.info(f"No existing state file at {self.json_path}")
                return None
            
            with open(self.json_path, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Portfolio loaded from {self.json_path} (NAV: ${data['nav']:,.2f})")
            return data
        except Exception as e:
            logger.error(f"JSON load failed: {e}")
            return None
    
    def _load_sqlite(self) -> Optional[Dict]:
        """Load latest snapshot from SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT timestamp, nav, cash, realized_pnl, positions_json, trade_count
            FROM portfolio_snapshots
            ORDER BY timestamp DESC
            LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                logger.info("No portfolio snapshots found in database")
                return None
            
            timestamp, nav, cash, realized_pnl, positions_json, trade_count = row
            positions = json.loads(positions_json)
            
            logger.info(f"Portfolio loaded from SQLite (NAV: ${nav:,.2f}, Trades: {trade_count})")
            
            return {
                'timestamp': timestamp,
                'nav': nav,
                'cash': cash,
                'positions': positions,
                'realized_pnl': realized_pnl,
                'trade_count': trade_count,
            }
        except Exception as e:
            logger.error(f"SQLite load failed: {e}")
            return None
    
    def save_trade(self, symbol: str, side: str, quantity: float, price: float,
                   pnl: float, realized_pnl: float, cash: float):
        """Record a trade execution"""
        if self.backend != 'sqlite':
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO trades (timestamp, symbol, side, quantity, price, pnl, realized_pnl, cash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), symbol, side, quantity, price, pnl, realized_pnl, cash))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Trade recorded: {side} {quantity} {symbol} @ ${price:.2f}")
        except Exception as e:
            logger.error(f"Failed to save trade: {e}")
    
    def save_risk_event(self, rule: str, severity: str, message: str, action: str):
        """Record a risk management event"""
        if self.backend != 'sqlite':
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO risk_events (timestamp, rule, severity, message, action)
            VALUES (?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), rule, severity, message, action))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Risk event recorded: [{severity}] {rule}")
        except Exception as e:
            logger.error(f"Failed to save risk event: {e}")
    
    def get_history(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """Get portfolio history from the last N days"""
        if self.backend != 'sqlite':
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get snapshots from last N days
            cursor.execute("""
            SELECT timestamp, nav, cash, realized_pnl, positions_json, trade_count
            FROM portfolio_snapshots
            WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp DESC
            LIMIT ?
            """, (days, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    'timestamp': row[0],
                    'nav': row[1],
                    'cash': row[2],
                    'realized_pnl': row[3],
                    'positions': json.loads(row[4]),
                    'trade_count': row[5],
                })
            
            logger.info(f"Retrieved {len(history)} snapshots from last {days} days")
            return history
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []
    
    def get_trades(self, symbol: str = None, days: int = 1) -> List[Dict]:
        """Get trade history"""
        if self.backend != 'sqlite':
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if symbol:
                cursor.execute("""
                SELECT timestamp, symbol, side, quantity, price, pnl
                FROM trades
                WHERE symbol = ? AND datetime(timestamp) >= datetime('now', '-' || ? || ' days')
                ORDER BY timestamp DESC
                """, (symbol, days))
            else:
                cursor.execute("""
                SELECT timestamp, symbol, side, quantity, price, pnl
                FROM trades
                WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' days')
                ORDER BY timestamp DESC
                """, (days,))
            
            rows = cursor.fetchall()
            conn.close()
            
            trades = [dict(row) for row in rows]
            logger.info(f"Retrieved {len(trades)} trades")
            return trades
        except Exception as e:
            logger.error(f"Failed to get trades: {e}")
            return []
    
    def cleanup_old_data(self, days: int = 90):
        """Delete snapshots older than N days to keep database lean"""
        if self.backend != 'sqlite':
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            DELETE FROM portfolio_snapshots
            WHERE datetime(timestamp) < datetime('now', '-' || ? || ' days')
            """, (days,))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted} old snapshots (older than {days} days)")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
