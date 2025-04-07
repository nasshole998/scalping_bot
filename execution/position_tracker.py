# position_tracker.py

class PositionTracker:
    def __init__(self, symbol, api):
        self.symbol = symbol
        self.api = api
        self.current_position = None
        self.refresh_position()

    def refresh_position(self):
        try:
            position = self.api.get_position(self.symbol)
            self.current_position = {
                "qty": float(position.qty),
                "side": "buy" if float(position.qty) > 0 else "sell",
                "entry_price": float(position.avg_entry_price)
            }
        except Exception:
            self.current_position = None

    def is_in_position(self):
        self.refresh_position()
        return self.current_position is not None

    def get_position_info(self):
        self.refresh_position()
        return self.current_position
