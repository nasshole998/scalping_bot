import pandas as pd
from .base import BaseStrategy

class EMACrossoverStrategy(BaseStrategy):
    def generate_signal(self, df: pd.DataFrame) -> str:
        if len(df) < 2:
            return "hold"

        short_ema = df['ema_9'].iloc[-1]
        long_ema = df['ema_21'].iloc[-1]
        prev_short = df['ema_9'].iloc[-2]
        prev_long = df['ema_21'].iloc[-2]

        if prev_short < prev_long and short_ema > long_ema:
            return "buy"
        elif prev_short > prev_long and short_ema < long_ema:
            return "sell"
        else:
            return "hold"
