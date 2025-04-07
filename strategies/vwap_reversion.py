import pandas as pd
from .base import BaseStrategy

class VWAPReversionStrategy(BaseStrategy):
    def generate_signal(self, df: pd.DataFrame) -> str:
        if len(df) < 1:
            return "hold"

        price = df['close'].iloc[-1]
        vwap = df['vwap'].iloc[-1]

        deviation = (price - vwap) / vwap
        threshold = 0.002  # 0.2%

        if deviation > threshold:
            return "sell"
        elif deviation < -threshold:
            return "buy"
        else:
            return "hold"
