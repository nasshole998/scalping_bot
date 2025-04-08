# strategies/composite_strategy.py

import pandas as pd
from .base import BaseStrategy
from .ema_crossover import EMACrossoverStrategy
from .vwap_reversion import VWAPReversionStrategy
from .rsi_reversal import RSIReversalStrategy
from .macd_momentum import MACDMomentumStrategy
from .bollinger_breakout import BollingerBreakoutStrategy

class CompositeStrategy(BaseStrategy):
    def __init__(self, symbol):
        super().__init__(symbol)
        self.strategies = [
            EMACrossoverStrategy(symbol),
            VWAPReversionStrategy(symbol),
            RSIReversalStrategy(symbol),
            MACDMomentumStrategy(symbol),
            BollingerBreakoutStrategy(symbol)
        ]

    def generate_signal(self, df: pd.DataFrame) -> str:
        if df.empty or not isinstance(df, pd.DataFrame):
            return "hold"

        row = df.iloc[-1]
        signals = [s.generate_signal(df) for s in self.strategies]
        votes = {"buy": 0, "sell": 0, "hold": 0}

        for s in signals:
            votes[s] += 1

        if votes["buy"] > votes["sell"] and votes["buy"] > votes["hold"]:
            return "buy"
        elif votes["sell"] > votes["buy"] and votes["sell"] > votes["hold"]:
            return "sell"
        return "hold"
