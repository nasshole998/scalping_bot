import pandas as pd
from .base import BaseStrategy

class MACDMomentumStrategy(BaseStrategy):
    def generate_signal(self, df: pd.DataFrame) -> str:
        if len(df) < 2:
            return "hold"

        macd = df['macd'].iloc[-1]
        signal = df['macd_signal'].iloc[-1]
        prev_macd = df['macd'].iloc[-2]
        prev_signal = df['macd_signal'].iloc[-2]

        if prev_macd < prev_signal and macd > signal:
            return "buy"
        elif prev_macd > prev_signal and macd < signal:
            return "sell"
        else:
            return "hold"
