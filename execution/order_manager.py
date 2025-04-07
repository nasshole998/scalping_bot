# execution/order_manager.py

from alpaca_trade_api.rest import REST, TimeInForce, OrderSide
import os
from dotenv import load_dotenv
from execution.risk_management import RiskManager

load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"

rest_api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL)
risk = RiskManager(rest_api)

class OrderManager:
    def __init__(self, symbol):
        self.symbol = symbol

    # order_manager.py (replace place_order method)

    def place_order(self, signal):
        if signal not in ["buy", "sell"]:
            print("No actionable signal.")
            return

        if not self.risk_manager.can_trade():
            print("RiskManager: Trade not allowed.")
            return

        qty = self.risk_manager.calculate_position_size()
        side = signal

        # Bracket config (tight for scalping)
        take_profit_pct = 0.003  # +0.3%
        stop_loss_pct = 0.0025   # -0.25%

        market_price = self.get_market_price()
        if market_price is None:
            print("Failed to get market price.")
            return

        take_profit = round(market_price * (1 + take_profit_pct), 2)
        stop_loss = round(market_price * (1 - stop_loss_pct), 2)
        if side == "sell":
            take_profit = round(market_price * (1 - take_profit_pct), 2)
            stop_loss = round(market_price * (1 + stop_loss_pct), 2)

        try:
            order = self.api.submit_order(
                symbol=self.symbol,
                qty=qty,
                side=side,
                type="market",
                time_in_force="gtc",
                order_class="bracket",
                take_profit={"limit_price": take_profit},
                stop_loss={"stop_price": stop_loss}
            )
            print(f"[{side.upper()}] Order placed: {qty} @ {market_price}")
        except Exception as e:
            print(f"Error placing order: {e}")
    
    def get_market_price(self):
        try:
            quote = self.api.get_latest_trade(self.symbol)
            return float(quote.price)
        except Exception as e:
            print(f"Error getting market price: {e}")
            return None
