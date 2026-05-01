from __future__ import annotations
import random
from collections import deque
from typing import List, Optional

import numpy as np

from market_state import MarketState, TradeIntent, CyclePhase


class BaseAgent:
    def __init__(self, name: str, history_len: int = 250):
        self.name = name
        self.prices: deque[float] = deque(maxlen=history_len)
        self.vols: deque[float] = deque(maxlen=history_len)

    def update(self, market: MarketState):
        self.prices.append(market.price)
        self.vols.append(market.volatility)

    def decide(self, market: MarketState) -> List[TradeIntent]:
        raise NotImplementedError

    def _sma(self, window: int) -> Optional[float]:
        if len(self.prices) < window:
            return None
        return float(np.mean(list(self.prices)[-window:]))

    def _ema(self, values: List[float], window: int):
        if len(values) < window:
            return None
        weights = np.exp(np.linspace(-1., 0., window))
        weights /= weights.sum()
        return float(np.convolve(values, weights, mode='valid')[-1])

    def _rsi(self, window: int = 14) -> Optional[float]:
        if len(self.prices) < window + 1:
            return None
        deltas = np.diff(np.array(self.prices))
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-window:])
        avg_loss = np.mean(losses[-window:])
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))


class Tactician(BaseAgent):
    def __init__(self):
        super().__init__("The Tactician")

    def decide(self, market: MarketState) -> List[TradeIntent]:
        rsi = self._rsi(14)
        ema12 = self._ema(list(self.prices), 12)
        ema26 = self._ema(list(self.prices), 26)

        if rsi is None or ema12 is None or ema26 is None:
            return []

        macd = ema12 - ema26
        signal = self._ema(list(self.prices)[-9:], 9) if len(self.prices) >= 9 else None
        intents: List[TradeIntent] = []

        if market.cycle_phase == CyclePhase.BEAR:
            intents.append(TradeIntent(self.name, market.symbol, "SHORT", 12, 0.70, "bear momentum"))

        # RSI signals - but NOT in BULL regimes (high RSI is normal in uptrends)
        if market.cycle_phase != CyclePhase.BULL:
            if rsi < 30 and macd > 0:
                intents.append(TradeIntent(self.name, market.symbol, "BUY", 15, 0.85, "RSI oversold + momentum"))
            elif rsi > 70 and macd < 0:
                intents.append(TradeIntent(self.name, market.symbol, "SELL", 14, 0.83, "RSI overbought + momentum"))
        else:
            # In BULL regime: only sell on very extreme RSI reversals
            if rsi > 85 and macd < -0.1:
                intents.append(TradeIntent(self.name, market.symbol, "SELL", 6, 0.60, "extreme overbought reversal"))

        # fallback trades to keep activity alive if no signal yet.
        if not intents:
            if market.cycle_phase == CyclePhase.CHOP:
                intents.append(TradeIntent(self.name, market.symbol, "BUY", 8, 0.40, "CHOP exploration"))
            elif market.cycle_phase == CyclePhase.BULL:
                # Increased Bull bias: higher qty and confidence to capture upside
                intents.append(TradeIntent(self.name, market.symbol, "BUY", 16, 0.65, "BULL momentum aggression"))
            elif market.cycle_phase == CyclePhase.BEAR:
                intents.append(TradeIntent(self.name, market.symbol, "SHORT", 10, 0.55, "BEAR continuation"))

        return intents


class Explorer(BaseAgent):
    def __init__(self):
        super().__init__("The Explorer")

    def decide(self, market: MarketState) -> List[TradeIntent]:
        if len(self.prices) < 30:
            return []

        returns = np.diff(np.log(np.array(self.prices)))

        rod = float(returns[-1])
        trade = []

        try:
            from sklearn.cluster import KMeans

            n_clusters = min(3, len(returns) // 10)
            if n_clusters < 2:
                return []
            km = KMeans(n_clusters=n_clusters, n_init=5, random_state=42)
            clusters = km.fit_predict(returns.reshape(-1, 1))
            current = clusters[-1]
            mean_cluster = returns[clusters == current].mean() if np.any(clusters == current) else 0

            if mean_cluster > 0.001:
                trade = [TradeIntent(self.name, market.symbol, "BUY", 6, 0.5, "cluster momentum")]
            elif mean_cluster < -0.001:
                trade = [TradeIntent(self.name, market.symbol, "SELL", 5, 0.5, "cluster mean reversal")]
        except Exception:
            if rod > 0:
                trade = [TradeIntent(self.name, market.symbol, "BUY", 5, 0.45, "fallback exploration")]
            else:
                trade = [TradeIntent(self.name, market.symbol, "SELL", 4, 0.40, "fallback exploration")]

        return trade


class Sentinel(BaseAgent):
    def __init__(self):
        super().__init__("The Sentinel")
        self.last_hedge_step = -100  # Frequency limiting

    def decide(self, market: MarketState) -> List[TradeIntent]:
        intents: List[TradeIntent] = []
        
        # Frequency limit: only hedge every 3 steps to avoid over-hedging
        current_step = len(self.prices)
        if current_step - self.last_hedge_step < 3:
            return intents
        
        atr = self._sma(14)
        vol_spike = market.volatility > 1.2  # Raised threshold from 0.9 → 1.2
        if atr and market.volatility > max(0.6, np.std(list(self.vols)) * 2.0):  # Raised from 1.5
            vol_spike = True

        # Reduced PUT size from 4 → 2; lower confidence in non-BEAR regimes
        if vol_spike or market.cycle_phase == market.cycle_phase.BEAR:
            put_qty = 2 if market.cycle_phase != CyclePhase.BEAR else 3
            confidence = 0.72 if market.cycle_phase == CyclePhase.BEAR else 0.65
            intents.append(TradeIntent(self.name, market.symbol, "PUT", put_qty, confidence, "crash protection"))
            self.last_hedge_step = current_step

        return intents


class Anchor(BaseAgent):
    def __init__(self):
        super().__init__("The Anchor")

    def decide(self, market: MarketState) -> List[TradeIntent]:
        intents: List[TradeIntent] = []
        ma200 = self._sma(200)

        if ma200 is None:
            return []

        if market.cycle_phase == market.cycle_phase.BULL and market.price > ma200:
            intents.append(TradeIntent(self.name, market.symbol, "BUY", 20, 0.95, "core winner accumulation"))

        return intents


class Treasurer(BaseAgent):
    def __init__(self):
        super().__init__("The Treasurer")

    def decide(self, market: MarketState) -> List[TradeIntent]:
        if len(self.prices) < 30:
            return []

        returns = np.diff(np.log(np.array(self.prices)))
        sharpe = np.mean(returns) / (np.std(returns) + 1e-8)

        if sharpe > 0.2 and market.cycle_phase == market.cycle_phase.BULL:
            return [TradeIntent(self.name, market.symbol, "BUY", 3, 0.65, "performance reallocation")]
        if sharpe < -0.2 and market.cycle_phase == market.cycle_phase.BEAR:
            return [TradeIntent(self.name, market.symbol, "SELL", 2, 0.60, "risk reduce")]

        return []


class MetaOpt(BaseAgent):
    def __init__(self):
        super().__init__("The Meta-Opt")
        self.last_adjustment_step = 0
        self.adjustment_interval = 50  # Only suggest every 50 steps

    def decide(self, market: MarketState) -> List[TradeIntent]:
        # Meta-optimization: provide tuning recommendations every N steps
        current_step = len(self.prices)
        if current_step - self.last_adjustment_step < self.adjustment_interval:
            return []
        
        self.last_adjustment_step = current_step
        
        # In a real system, this would:
        # 1. Read from simulator.learner.history
        # 2. Identify which scenarios are underperforming
        # 3. Suggest agent threshold adjustments
        # 4. Return tuning signals (not actual trades)
        
        # Placeholder: provide a status message (in real system, would log to learner or metrics)
        # For now, return empty (MetaOpt doesn't execute trades, only suggests meta-tuning)
        return []

