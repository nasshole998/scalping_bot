import os
import pandas as pd
import numpy as np
import asyncio
from collections import deque
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.rest import REST
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"  # Corrected URL
SYMBOL = "AAPL"
TIME_FRAME = "1Min"  # Adjust based on your strategy
DATA_QUEUE_SIZE = 1000

# Initialize directories
os.makedirs("data/processed", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)

# Initialize Alpaca API
rest_api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, BASE_URL)

class TradeBarAggregator:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe
        self.current_bar = None
        self.trades = []
        self.last_finalized_timestamp = None

    def add_trade(self, trade):
        try:
            trade_time = pd.Timestamp(trade.timestamp).tz_convert('UTC')
            current_time = pd.Timestamp.now(tz='UTC').floor(self.timeframe)
            
            if not self.current_bar or current_time > self.current_bar['timestamp']:
                if self.current_bar:
                    self._finalize_current_bar()
                self._create_new_bar(current_time)
                
            self._update_current_bar(trade)
        except Exception as e:
            print(f"Error adding trade: {e}")

    def _create_new_bar(self, timestamp):
        self.current_bar = {
            'timestamp': timestamp,
            'open': None,
            'high': -np.inf,
            'low': np.inf,
            'close': None,
            'volume': 0,
            'vwap': 0,
            'trade_count': 0
        }

    def _update_current_bar(self, trade):
        price = trade.price
        size = trade.size
        
        if self.current_bar['open'] is None:
            self.current_bar['open'] = price
            
        self.current_bar['high'] = max(self.current_bar['high'], price)
        self.current_bar['low'] = min(self.current_bar['low'], price)
        self.current_bar['close'] = price
        self.current_bar['volume'] += size
        
        # Calculate VWAP
        if self.current_bar['trade_count'] > 0:
            self.current_bar['vwap'] = (self.current_bar['vwap'] * self.current_bar['trade_count'] + 
                                       price * size) / (self.current_bar['trade_count'] + 1)
        else:
            self.current_bar['vwap'] = price * size
            
        self.current_bar['trade_count'] += 1

    def _finalize_current_bar(self):
        if self.current_bar and self.current_bar['timestamp'] != self.last_finalized_timestamp:
            df = pd.DataFrame([self.current_bar])
            file_path = f"data/raw/{self.symbol}_raw.csv"
            header = not os.path.exists(file_path)
            df.to_csv(file_path, mode='a', header=header, index=False)
            
            # Pass to processor
            if 'processor' in globals():
                processor.add_raw_data(df)
                
            self.last_finalized_timestamp = self.current_bar['timestamp']

class DataProcessor:
    def __init__(self):
        self.raw_data = deque(maxlen=DATA_QUEUE_SIZE)
        self.processed_data = deque(maxlen=DATA_QUEUE_SIZE)
        self.indicators = {}
        self.last_processed_timestamp = None
        self.historical_data_loaded = False

    def add_raw_data(self, data):
        try:
            if not self.raw_data or data['timestamp'].iloc[0] != self.last_processed_timestamp:
                self.raw_data.append(data)
                self.last_processed_timestamp = data['timestamp'].iloc[0]
                self._process_data()
        except Exception as e:
            print(f"Error adding raw data: {e}")

    def _process_data(self):
        try:
            if len(self.raw_data) < 50:  # Minimum data needed for indicators
                return

            df = pd.concat(self.raw_data).reset_index(drop=True)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate indicators
            df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
            df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
            
            # RSI calculation
            delta = df['close'].diff(1)
            gain = (delta.where(delta > 0, 0)).ewm(com=13, adjust=False).mean()
            loss = (-delta.where(delta < 0, 0)).ewm(com=13, adjust=False).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD calculation
            macd = df['close'].ewm(span=12, adjust=False).mean() - df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = macd
            df['macd_signal'] = macd.ewm(span=9, adjust=False).mean()
            
            # Bollinger Bands
            bollinger = df['close'].rolling(window=20).mean()
            df['bollinger_h'] = bollinger + 2 * df['close'].rolling(window=20).std()
            df['bollinger_l'] = bollinger - 2 * df['close'].rolling(window=20).std()
            
            # Store latest processed data
            self.processed_data = df.tail(100).copy()
            self._save_processed_data()
        except Exception as e:
            print(f"Error processing data: {e}")

    def _save_processed_data(self):
        if not self.processed_data.empty:
            file_path = f"data/processed/{SYMBOL}_processed.csv"
            header = not os.path.exists(file_path)
            latest_data = self.processed_data.iloc[-1].to_frame().T
            latest_data.to_csv(file_path, mode='a', header=header, index=False)

    def load_historical_data(self, file_path):
        try:
            if os.path.exists(file_path) and not self.historical_data_loaded:
                columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'vwap', 'trade_count']
                historical_data = pd.read_csv(file_path, names=columns, header=None)
                historical_data = historical_data.drop_duplicates(subset='timestamp')
                
                for _, row in historical_data.iterrows():
                    bar_data = pd.DataFrame([{
                        'timestamp': row['timestamp'],
                        'open': row['open'],
                        'high': row['high'],
                        'low': row['low'],
                        'close': row['close'],
                        'volume': row['volume'],
                        'vwap': row['vwap'],
                        'trade_count': row['trade_count']
                    }])
                    self.add_raw_data(bar_data)
                
                self.historical_data_loaded = True
                print(f"Loaded {len(historical_data)} historical data points")
        except Exception as e:
            print(f"Error loading historical data: {e}")

async def handle_trade_update(trade):
    global aggregator, processor
    try:
        aggregator.add_trade(trade)
    except Exception as e:
        print(f"Error handling trade: {e}")

async def start_stream():
    global aggregator, processor
    aggregator = TradeBarAggregator(SYMBOL, TIME_FRAME)
    processor = DataProcessor()

    # Load historical data
    historical_file = f"data/raw/{SYMBOL}_raw.csv"
    processor.load_historical_data(historical_file)

    while True:
        try:
            clock = rest_api.get_clock()
            if clock.is_open:
                print("Market is open. Starting Alpaca WebSocket stream...")
                break
            else:
                next_open = clock.next_open.strftime('%Y-%m-%d %H:%M:%S')
                print(f"Market closed. Next open: {next_open} UTC. Checking again in 60s...")
                await asyncio.sleep(60)
        except Exception as e:
            print(f"Error checking market status: {e}")
            await asyncio.sleep(60)

    stream = Stream(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=BASE_URL, data_feed='iex')  # Use 'sip' for premium data
    stream.subscribe_trades(handle_trade_update, SYMBOL)
    
    try:
        await stream._run_forever()
    except Exception as e:
        print(f"Stream error: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(start_stream())
    except KeyboardInterrupt:
        print("Stream stopped by user")
    except Exception as e:
        print(f"Critical error: {e}")