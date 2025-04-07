import pandas as pd
from .base import BaseStrategy

class RSIReversalStrategy(BaseStrategy):
    def generate_signal(self, df: pd.DataFrame) -> str:
        if len(df) < 1:
            return "hold"

        rsi = df['rsi'].iloc[-1]

        if rsi > 70:
            return "sell"
        elif rsi < 30:
            return "buy"
        else:
            return "hold"
