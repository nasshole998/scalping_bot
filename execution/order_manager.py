import os
from dotenv import load_dotenv
from alpaca_trade_api.rest import REST
from execution.risk_management import RiskManager

load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"  # Corrected URL

rest_api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL)
risk = RiskManager(rest_api)

class OrderManager:
    def __init__(self, symbol):
        self.symbol = symbol

    def place_bracket_order(self, signal):
        if signal not in ["buy", "sell"]:
            print("No actionable signal.")
            return None

        if not risk.is_trade_allowed(signal, self.symbol):
            print("Trade blocked by risk manager.")
            return None

        try:
            qty = risk.get_position_size(self.symbol)
            price = float(rest_api.get_latest_trade(self.symbol).price)

            take_profit_pct = 0.005  # 0.5% target
            stop_loss_pct = 0.003    # 0.3% SL

            if signal == "buy":
                take_profit_price = round(price * (1 + take_profit_pct), 2)
                stop_loss_price = round(price * (1 - stop_loss_pct), 2)
            else:
                take_profit_price = round(price * (1 - take_profit_pct), 2)
                stop_loss_price = round(price * (1 + stop_loss_pct), 2)

            order = rest_api.submit_order(
                symbol=self.symbol,
                qty=qty,
                side=signal,
                type="market",
                time_in_force="day",
                order_class="bracket",
                take_profit={"limit_price": take_profit_price},
                stop_loss={"stop_price": stop_loss_price}
            )
            print(f"[ORDER] Bracket {signal.upper()} order placed: {order.id}")
            return order
        except Exception as e:
            print(f"[ERROR] Bracket order failed: {e}")
            return None

    def get_open_position(self):
        try:
            positions = rest_api.list_positions()
            for p in positions:
                if p.symbol == self.symbol:
                    return {
                        "qty": float(p.qty),
                        "side": "long" if float(p.qty) > 0 else "short",
                        "avg_entry_price": float(p.avg_entry_price)
                    }
            return None
        except Exception as e:
            print(f"[ERROR] Fetching position failed: {e}")
            return None

    def close_position(self):
        try:
            position = self.get_open_position()
            if position:
                side = "sell" if position["side"] == "long" else "buy"
                rest_api.close_position(self.symbol)
                print(f"[ORDER] Closed {side.upper()} position on {self.symbol}")
                return True
            else:
                print(f"[INFO] No open position to close for {self.symbol}")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to close position: {e}")
            return False