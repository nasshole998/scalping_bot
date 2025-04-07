from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    def __init__(self, symbol):
        self.symbol = symbol

    @abstractmethod
    def generate_signal(self, df):
        """
        Generate a trading signal based on the latest data.
        Args:
            df (pd.DataFrame): DataFrame with all required indicators.
        Returns:
            str: One of "buy", "sell", "hold"
        """
        pass
