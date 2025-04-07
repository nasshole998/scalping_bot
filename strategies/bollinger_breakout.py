import pandas as pd
from .base import BaseStrategy

class BollingerBreakoutStrategy(BaseStrategy):
    def generate_signal(self, df: pd.DataFrame) -> str:
        if len(df) < 1:
            return "hold"

        price = df['close'].iloc[-1]
        upper = df['bollinger_h'].iloc[-1]
        lower = df['bollinger_l'].iloc[-1]

        if price > upper:
            return "buy"
        elif price < lower:
            return "sell"
        else:
            return "hold"
