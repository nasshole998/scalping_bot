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
        signals = [strategy.generate_signal(df) for strategy in self.strategies]
        vote_count = {"buy": 0, "sell": 0, "hold": 0}
        for signal in signals:
            vote_count[signal] += 1

        if vote_count["buy"] > vote_count["sell"] and vote_count["buy"] > vote_count["hold"]:
            return "buy"
        elif vote_count["sell"] > vote_count["buy"] and vote_count["sell"] > vote_count["hold"]:
            return "sell"
        else:
            return "hold"
