import os
import pandas as pd
import numpy as np
import asyncio
import json
import time
from collections import deque
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.rest import REST
from dotenv import load_dotenv

# Load API credentials from .env file
load_dotenv()
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"  # Paper trading mode

# Stream Settings
SYMBOL = "AAPL"
DATA_QUEUE = deque(maxlen=1000)  # Store latest data for strategy execution

# Initialize Alpaca API
rest_api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL)

# Ensure processed data directory exists
PROCESSED_DATA_PATH = "data/processed/"
if not os.path.exists(PROCESSED_DATA_PATH):
    print(f"Processed data path missing! Creating: {PROCESSED_DATA_PATH}")
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)

# Column names matching processed historical data
COLUMNS = [
    "timestamp", "close", "high", "low", "trade_count", "open", "volume", "vwap",
    "ema_9", "ema_21", "rsi", "macd", "macd_signal", "bollinger_h", "bollinger_l", "order_flow"
]

def preprocess_live_data(df):
    """Ensures live data structure matches processed historical data."""
    nan_threshold = 0.2 * len(df.columns)
    df.dropna(thresh=len(df.columns) - nan_threshold, inplace=True)
    df.ffill(inplace=True)
    df.bfill(inplace=True)
    df.fillna(df.mean(), inplace=True)
    return df

def save_live_data(df):
    """Appends processed live data to a CSV file."""
    file_path = os.path.join(PROCESSED_DATA_PATH, f"{SYMBOL}_live_data.csv")
    try:
        df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)
        print(f"Data saved to {file_path}")
    except Exception as e:
        print(f"Error saving data: {e}")

async def handle_trade_update(trade):
    """Processes incoming trade updates."""
    global DATA_QUEUE
    try:
        print(f"Received trade update: {trade}")

        data = {
            "timestamp": str(trade.timestamp),
            "close": trade.price,
            "high": trade.price,
            "low": trade.price,
            "trade_count": trade.size,
            "open": trade.price,
            "volume": trade.size,
            "vwap": trade.price,
            "ema_9": np.nan,
            "ema_21": np.nan,
            "rsi": np.nan,
            "macd": np.nan,
            "macd_signal": np.nan,
            "bollinger_h": np.nan,
            "bollinger_l": np.nan,
            "order_flow": trade.size * np.sign(trade.price)
        }

        df = pd.DataFrame([data], columns=COLUMNS)
        print(f"Preprocessed DataFrame:\n{df}")
        df = preprocess_live_data(df)

        if not df.empty:
            DATA_QUEUE.append(df)
            print(f"Data queue updated! Current size: {len(DATA_QUEUE)}")
            print(f"DATA_QUEUE Contents: {[d.to_dict(orient='records') for d in DATA_QUEUE]}")
            save_live_data(df)
            print("Saved live data to CSV.")
    except Exception as e:
        print(f"Error processing trade update: {e}")

async def start_stream():
    """Checks market status and starts Alpaca real-time data streaming when open."""
    while True:
        clock = rest_api.get_clock()
        if clock.is_open:
            print("Market is open. Starting Alpaca WebSocket stream...")
            break
        else:
            next_open = clock.next_open.strftime('%Y-%m-%d %H:%M:%S')
            print(f"Market is closed. Next open: {next_open} (utc-4). Checking again in 60 seconds...")
            time.sleep(60)

    stream = Stream(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=BASE_URL, data_feed='iex')
    stream.subscribe_trades(handle_trade_update, SYMBOL)
    
    try:
        await stream._run_forever()
    except asyncio.CancelledError:
        print("WebSocket stream cancelled.")
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(start_stream())
    except KeyboardInterrupt:
        print("Stream interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
