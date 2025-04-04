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
    return df

def clean_data(df):
    """Handles missing values and ensures correct formatting."""
    df.dropna(inplace=True)  # Drop rows with missing values
    df.sort_index(inplace=True)  # Sort by timestamp
    return df

def add_technical_indicators(df):
    """Adds VWAP, EMA, RSI, MACD, Bollinger Bands, and Order Flow analysis."""
    
    # VWAP
    df['vwap'] = ta.volume.VolumeWeightedAveragePrice(high=df['high'], 
                                                      low=df['low'], 
                                                      close=df['close'], 
                                                      volume=df['volume']).volume_weighted_average_price()

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
    cols_to_normalize = ['close', 'high', 'low', 'open', 'volume', 
                         'vwap', 'ema_9', 'ema_21', 'rsi', 
                         'macd', 'macd_signal', 'bollinger_h', 'bollinger_l', 'order_flow']
    df[cols_to_normalize] = (df[cols_to_normalize] - df[cols_to_normalize].min()) / (df[cols_to_normalize].max() - df[cols_to_normalize].min())
    return df

def save_processed_data(df, filename):
    """Saves the processed DataFrame as a CSV in the processed folder."""
    file_path = os.path.join(PROCESSED_DATA_PATH, filename)
    df.to_csv(file_path)
    print(f"Processed data saved to {file_path}")

def handle_missing_values(df):
    """Handles NaN values in the processed dataset after saving."""
    missing_threshold = 0.2  # If more than 20% of a row is NaN, drop it
    
    # Drop rows with too many NaN values
    df.dropna(thresh=int((1 - missing_threshold) * len(df.columns)), inplace=True)
    
    # Fill remaining NaN values
    df.ffill(inplace=True)  # Forward fill
    df.bfill(inplace=True)  # Backward fill
    
    # If any NaNs remain, fill with column mean
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df.loc[:, numeric_cols] = df.loc[:, numeric_cols].fillna(df[numeric_cols].mean())
    
    print("Final NaN check and handling completed.")
    return df

def preprocess_data(raw_filename):
    """Runs the full data preprocessing pipeline."""
    try:
        df = load_raw_data(raw_filename)
        df = clean_data(df)
        df = add_technical_indicators(df)
        df = normalize_data(df)
        
        processed_filename = raw_filename.replace("raw", "processed")
        save_processed_data(df, processed_filename)
        
        # Reload the processed file and handle missing values
        processed_file_path = os.path.join(PROCESSED_DATA_PATH, processed_filename)
        df = pd.read_csv(processed_file_path, parse_dates=['timestamp'])
        df.set_index('timestamp', inplace=True)
        df = handle_missing_values(df)
        
        # Save the cleaned version again
        df.to_csv(processed_file_path)
        print(f"Final cleaned data saved to {processed_file_path}")
    except Exception as e:
        print(f"Error processing data: {e}")

# Example usage
if __name__ == "__main__":
    preprocess_data("AAPL_1Min_raw.csv")
