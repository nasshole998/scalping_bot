class PositionTracker:
    def __init__(self, symbol, api):
        self.symbol = symbol
        self.api = api
        self.current_position = None
        self.refresh_position()

    def refresh_position(self):
        try:
            positions = self.api.list_positions()
            found = False
            for p in positions:
                if p.symbol == self.symbol:
                    self.current_position = {
                        "qty": float(p.qty),
                        "side": "long" if float(p.qty) > 0 else "short",
                        "entry_price": float(p.avg_entry_price)
                    }
                    found = True
                    break
            if not found:
                self.current_position = None
        except Exception as e:
            print(f"Error refreshing position: {e}")
            self.current_position = None

    def is_in_position(self):
        self.refresh_position()
        return self.current_position is not None

    def get_position_info(self):
        self.refresh_position()
        return self.current_position