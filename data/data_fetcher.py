import os
import pandas as pd
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Load API credentials from .env file
load_dotenv()
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets/v2"  # Paper trading mode

# Initialize Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL, api_version='v2')

# Function to fetch historical data
def fetch_historical_data(symbol="AAPL", timeframe="1Min", start="2024-01-01", end="2024-03-01"):
    """Fetches historical market data for a given symbol and timeframe using Alpaca's updated API."""
    try:
        print(f"Fetching {timeframe} data for {symbol} from {start} to {end}...")
        
        # Fetch data using the new get_bars method
        bars = api.get_bars(
            symbol, 
            timeframe, 
            start=start, 
            end=end
        ).df

        # Save to CSV
        raw_data_path = "data/raw/"
        os.makedirs(raw_data_path, exist_ok=True)
        file_path = os.path.join(raw_data_path, f"{symbol}_{timeframe}_raw.csv")
        bars.to_csv(file_path)

        print(f"Data saved to {file_path}")
    except Exception as e:
        print(f"Error fetching data: {e}")

# Example usage
if __name__ == "__main__":
    fetch_historical_data()
