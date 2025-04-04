import os
import pandas as pd
import numpy as np
import ta

# Paths
RAW_DATA_PATH = "data/raw/"
PROCESSED_DATA_PATH = "data/processed/"
os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)

def load_raw_data(filename):
    """Loads raw CSV data from the raw folder."""
    file_path = os.path.join(RAW_DATA_PATH, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found.")
    
    df = pd.read_csv(file_path, parse_dates=['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    # Verify data structure
    required_columns = ['close', 'high', 'low', 'open', 'volume', 'vwap', 'trade_count']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Missing required columns in {file_path}")
    
    return df

def clean_data(df):
    """Handles missing values and ensures correct formatting."""
    # Drop rows with missing values
    df = df.dropna()
    
    # Sort by timestamp
    df = df.sort_index()
    
    # Ensure correct data types
    df = df.astype({
        'close': np.float64,
        'high': np.float64,
        'low': np.float64,
        'open': np.float64,
        'volume': np.float64,
        'vwap': np.float64,
        'trade_count': np.int64
    })
    
    return df

def add_technical_indicators(df):
    """Adds VWAP, EMA, RSI, MACD, Bollinger Bands, and Order Flow analysis."""
    # Ensure required columns are present
    required_columns = ['close', 'high', 'low', 'volume']
    if not all(col in df.columns for col in required_columns):
        raise ValueError("Missing required columns for indicator calculation")
    
    # VWAP
    df['vwap'] = ta.volume.VolumeWeightedAveragePrice(
        high=df['high'], 
        low=df['low'], 
        close=df['close'], 
        volume=df['volume'],
        window=14
    ).volume_weighted_average_price()
    
    # EMA (Exponential Moving Average)
    df['ema_9'] = ta.trend.EMAIndicator(df['close'], window=9).ema_indicator()
    df['ema_21'] = ta.trend.EMAIndicator(df['close'], window=21).ema_indicator()
    
    # RSI (Relative Strength Index)
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    
    # MACD (Moving Average Convergence Divergence)
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    
    # Bollinger Bands
    bollinger = ta.volatility.BollingerBands(df['close'])
    df['bollinger_h'] = bollinger.bollinger_hband()
    df['bollinger_l'] = bollinger.bollinger_lband()
    
    # Order Flow (Buy/Sell volume estimation)
    df['order_flow'] = df['volume'] * np.sign(df['close'].diff())  # Approximate buy/sell pressure
    
    return df

def normalize_data(df):
    """Normalizes numerical columns to scale data for machine learning models."""
    # Ensure no NaN values before normalization
    if df.isnull().values.any():
        raise ValueError("NaN values present before normalization")
    
    # Define columns to normalize
    cols_to_normalize = ['close', 'high', 'low', 'open', 'volume', 
                         'vwap', 'ema_9', 'ema_21', 'rsi', 
                         'macd', 'macd_signal', 'bollinger_h', 'bollinger_l', 'order_flow']
    
    # Ensure columns exist
    if not all(col in df.columns for col in cols_to_normalize):
        raise ValueError("Missing columns for normalization")
    
    # Use Z-Score normalization for better stability
    numeric_cols = df[cols_to_normalize]
    df[cols_to_normalize] = (numeric_cols - numeric_cols.mean()) / numeric_cols.std()
    
    return df

def save_processed_data(df, filename):
    """Saves the processed DataFrame as a CSV in the processed folder."""
    file_path = os.path.join(PROCESSED_DATA_PATH, filename)
    df.to_csv(file_path)
    print(f"Processed data saved to {file_path}")
    return file_path

def handle_missing_values(df):
    """Handles NaN values in the processed dataset after saving."""
    # Drop rows with too many NaN values
    missing_threshold = 0.2  # If more than 20% of a row is NaN, drop it
    min_non_nan = int(len(df.columns) * (1 - missing_threshold))
    df = df.dropna(thresh=min_non_nan)
    
    # Fill remaining NaN values with forward fill
    df = df.ffill()
    
    # Fill remaining NaN values with backward fill
    df = df.bfill()
    
    # If any NaNs remain, fill with column mean
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    
    return df

def preprocess_data(raw_filename):
    """Runs the full data preprocessing pipeline."""
    try:
        # Load raw data
        df = load_raw_data(raw_filename)
        
        # Clean data
        df = clean_data(df)
        
        # Add technical indicators
        df = add_technical_indicators(df)
        
        # Handle missing values after indicator calculation
        df = handle_missing_values(df)
        
        # Normalize data
        df = normalize_data(df)
        
        # Save processed data
        processed_filename = raw_filename.replace("raw", "processed")
        save_processed_data(df, processed_filename)
        
        # Reload and verify processed data
        processed_file_path = os.path.join(PROCESSED_DATA_PATH, processed_filename)
        df = pd.read_csv(processed_file_path, parse_dates=['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Final check for NaN values
        if df.isnull().values.any():
            print("Warning: NaN values still present in processed data")
            df = handle_missing_values(df)
            df.to_csv(processed_file_path)
        
        print(f"Data preprocessing completed successfully for {raw_filename}")
        
    except Exception as e:
        print(f"Error processing data: {e}")
        raise

# Example usage
if __name__ == "__main__":
    preprocess_data("AAPL_1Min_raw.csv")