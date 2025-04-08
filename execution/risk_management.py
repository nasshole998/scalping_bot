class RiskManager:
    def __init__(self, rest_api, max_position_pct=0.05, max_open_trades=1):
        self.rest_api = rest_api
        self.max_position_pct = max_position_pct
        self.max_open_trades = max_open_trades

    def is_trade_allowed(self, signal, symbol):
        try:
            positions = self.rest_api.list_positions()
            if len(positions) >= self.max_open_trades:
                print("[RISK] Too many open positions.")
                return False

            for p in positions:
                if p.symbol == symbol:
                    current_side = "long" if float(p.qty) > 0 else "short"
                    signal_side = "long" if signal == "buy" else "short"
                    if current_side == signal_side:
                        return False

            return True
        except Exception as e:
            print(f"[RISK ERROR] Failed risk check: {e}")
            return False

    def get_position_size(self, symbol):
        try:
            account = self.rest_api.get_account()
            cash = float(account.cash)
            if cash <= 0:
                return 1  # Default to 1 share if no cash
            
            position_value = self.max_position_pct * cash
            latest_price = float(self.rest_api.get_latest_trade(symbol).price)
            return max(1, int(position_value // latest_price))
        except Exception as e:
            print(f"[RISK ERROR] Position sizing failed: {e}")
            return 1