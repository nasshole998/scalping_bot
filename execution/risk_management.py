# risk_manager.py

from execution.position_tracker import PositionTracker

class RiskManager:
    def __init__(self, symbol, api):
        self.symbol = symbol
        self.api = api
        self.position_tracker = PositionTracker(symbol, api)

    def can_trade(self):
        # For now, only one position at a time
        return not self.position_tracker.is_in_position()

    def calculate_position_size(self):
        try:
            account = self.api.get_account()
            buying_power = float(account.cash)
            risk_fraction = 0.05  # Risk up to 5% of capital
            max_trade_value = buying_power * risk_fraction
            market_price = self.api.get_latest_trade(self.symbol).price
            qty = int(max_trade_value / market_price)
            return max(1, qty)
        except Exception as e:
            print(f"Error calculating position size: {e}")
            return 1
