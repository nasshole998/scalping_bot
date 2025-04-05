# Scalping Bot

A high-frequency, modular, and tested algorithmic **scalping bot for stocks**, built using Python and the Alpaca API. This project is designed for paper trading (initially), real-time data handling, ML-powered strategies, and seamless transition to live trading.


## Project Structure

```bash
scalping_bot/
│
├── config/                   # Configuration settings
│   └── config.json
│
├── data/
│   ├── raw/                  # Raw historical data
│   ├── processed/            # Preprocessed data (including live data)
│   ├── data_fetcher.py
│   └── data_preprocessor.py
│
├── models/
│   ├── trained_models/       # Saved ML models
│   └── training_scripts/     # Scripts for training AI strategies
│
├── indicators/               # Technical indicators
│   ├── ema.py
│   ├── rsi.py
│   ├── macd.py
│   ├── vwap.py
│   └── bollinger_bands.py
│
├── strategies/               # Trading logic modules
│   ├── momentum.py
│   ├── mean_reversion.py
│   └── stat_arb.py
│
├── execution/
│   ├── order_manager.py      # Trade execution logic
│   └── risk_management.py    # Stop loss / take profit
│
├── backtesting/
│   ├── backtester.py         # Historical testing
│   └── performance_metrics.py
│
├── data_streaming/
│   └── alpaca_stream.py      # Real-time data stream from Alpaca
│
├── logging/
│   ├── trade_logger.py
│   └── error_handler.py
│
├── main.py                   # Main entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```


## Features

- Real-time data streaming from Alpaca (via WebSockets)
- Data preprocessing and storage in CSV format
- Indicators: EMA, RSI, MACD, VWAP, Bollinger Bands
- ML-ready architecture (plug-and-play models)
- Modular strategy integration (momentum, stat arb, etc.)
- Backtesting framework with performance evaluation
- Risk management (stop-loss/take-profit)
- Paper trading mode with live data feed


## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/nasshole998/scalping_bot.git
cd scalping_bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up Environment Variables

Create a `.env` file in the root directory:

```bash
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
```

### 4. Run the Bot
```bash
python data_streaming/alpaca_stream.py
```

## Project Goals

- Build a production-grade scalping bot
- test and optimize trading strategies
- Monetize via live trading
- Extend modularity for other assets (crypto, forex, etc.)

## Notes

- Paper trading only by default. To go live, change the `BASE_URL` to Alpaca’s live URL.
- This bot uses the free `iex` feed from Alpaca but you can change to the subscription version.
- Data gets saved to `data/processed/AAPL_live_data.csv`


## License

This project is licensed under the **GNU General Public License v3.0**.

You may copy, distribute, and modify the software as long as you track changes/dates in source files and disclose your source. Derivatives must also be open-source and licensed under GPL-3.0.

See [`LICENSE`](https://www.gnu.org/licenses/gpl-3.0.en.html) for full details.


## Author

Developed by **Nick** — student, tech nerd, and future quant
