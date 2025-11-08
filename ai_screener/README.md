# AI Stock Screener

**Advanced ML-powered stock screening system using CNN-LSTM and XGBoost ensemble models**

## Overview

This is a production-ready AI stock screener that analyzes 30+ NSE stocks to identify high-probability trading opportunities based on:

- **Candlestick Pattern Recognition**: CNN-LSTM hybrid deep learning model
- **Technical Indicators**: XGBoost with 89 engineered features
- **Ensemble Strategy**: 70% CNN-LSTM + 30% XGBoost weighted predictions
- **VWAP Integration**: Volume-weighted average price analysis

## Features

### Core Components

1. **Data Loader** (`data_loader.py`)
   - Automatically loads CSV files from Nify50_data folder
   - Handles 42 Nifty50 stocks with 10 years of OHLCV + VWAP data
   - Data validation and cleaning

2. **Feature Engineering** (`feature_engineering.py`)
   - 89 technical indicators:
     - Price features (returns, gaps, ranges)
     - Candlestick patterns (doji, hammer, engulfing, etc.)
     - Trend indicators (SMA, EMA, Aroon, ADX)
     - Momentum (RSI, MACD, Stochastic, CCI)
     - Volatility (ATR, Bollinger, Keltner)
     - Volume analysis (OBV, volume spikes)
     - VWAP features
     - Multi-timeframe analysis

3. **CNN-LSTM Model** (`cnn_lstm_model.py`)
   - Convolutional layers for local pattern detection
   - Bidirectional LSTM for temporal sequence modeling
   - 20-candle lookback window
   - 3-class output (buy/hold/sell)

4. **XGBoost Trainer** (`xgboost_trainer.py`)
   - Gradient boosting classifier
   - Hyperparameter tuning with GridSearchCV
   - Feature importance analysis
   - Time-series cross-validation

5. **Signal Generator** (`signal_generator.py`)
   - Ensemble predictions with 70/30 weighting
   - Confidence-based filtering
   - Automatic target and stop-loss calculation

6. **Streamlit UI** (`screener_app.py`)
   - Interactive dashboard
   - Multi-stock screening
   - Real-time signal generation
   - Interactive candlestick charts
   - Results export to CSV

## Installation

### 1. Clone/Download the Module

```bash
cd "C:\python\MG AI"
# The ai_screener folder should already be present
```

### 2. Install Dependencies

```bash
pip install -r ai_screener/requirements.txt
```

**Required packages:**
- pandas, numpy
- scikit-learn
- xgboost
- tensorflow, keras
- streamlit
- plotly
- pyyaml
- joblib

### 3. Verify Data Directory

Ensure your stock data is in the `Nify50_data` folder with CSV files (10 years of Nifty50 data):
- `NSE_RELIANCE, 1D.csv`
- `NSE_TCS, 1D.csv`
- `NSE_HDFCBANK, 1D.csv`
- etc. (42 stocks available)

## Usage

### Step 1: Train Models

Train XGBoost and CNN-LSTM models on your data:

```bash
cd ai_screener
python train_models.py
```

This will:
- Load all 42 Nifty50 stocks from Nify50_data
- Engineer 89 features for each stock
- Create buy/sell/hold labels (3% profit, 1.5% stop loss)
- Train models with 70/15/15 train/val/test split
- Save trained models to `models/` folder

### Step 2: Run Screener UI

Launch the interactive Streamlit dashboard:

```bash
streamlit run screener_app.py
```

The app will open in your browser with:
- Stock selection filters
- Confidence thresholds
- Signal type filters (buy/sell)
- VWAP position filters
- Results table with sortable columns
- Interactive candlestick charts
- CSV export functionality

### Step 3: Generate Signals

Use the signal generator programmatically:

```python
from signal_generator import SignalGenerator
import yaml

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize generator
signal_gen = SignalGenerator(config)

# Generate signals
symbols = ['NSE_RELIANCE', 'NSE_TCS', 'NSE_HDFCBANK']
signals = signal_gen.generate_signals_for_stocks(symbols, X_data)

print(signals)
```

## Configuration

Edit `config.yaml` to customize:

```yaml
trading:
  profit_target: 0.03      # 3% profit target
  stop_loss: 0.015         # 1.5% stop loss
  
models:
  ensemble:
    cnn_lstm_weight: 0.7   # 70% weight for CNN-LSTM
    xgboost_weight: 0.3    # 30% weight for XGBoost
    min_confidence: 0.70   # Minimum confidence threshold
```

## File Structure

```
ai_screener/
├── __init__.py
├── requirements.txt
├── config.yaml
├── README.md
├── data_loader.py          # Load CSV data
├── feature_engineering.py  # 89 technical indicators
├── cnn_lstm_model.py       # Deep learning model
├── xgboost_trainer.py      # Gradient boosting
├── signal_generator.py     # Ensemble predictions
├── train_models.py         # Training pipeline
├── screener_app.py         # Streamlit UI
└── models/                 # Saved models (created after training)
    ├── xgb_NSE_RELIANCE.pkl
    ├── xgb_NSE_TCS.pkl
    └── ...
```

## Model Performance

Expected results after training:

- **Accuracy**: >60% on test set
- **F1 Score**: >0.55 macro-averaged
- **Sharpe Ratio**: >1.5 in backtesting
- **Max Drawdown**: <10%

## Label Generation Logic

Labels are created based on forward returns:

- **Buy (1)**: Future price increases by ≥ profit_target (3%)
- **Sell (-1)**: Future price decreases by ≥ stop_loss (1.5%)
- **Hold (0)**: Price stays within profit_target/stop_loss range

## Feature Categories

### Price Features (10)
Returns, gaps, price position in range

### Candlestick Patterns (16)
Body/wick ratios, doji, hammer, shooting star, engulfing patterns

### Trend Features (17)
SMAs, EMAs, slopes, crossovers, Aroon indicators

### Momentum (12)
RSI, MACD, Stochastic, Williams %R, CCI, ROC

### Volatility (14)
ATR, Bollinger Bands, Keltner Channels

### Volume (8)
Volume ratios, OBV, accumulation/distribution

### VWAP Features (4)
VWAP deviation, slope, position

### Statistical Features (4)
Skewness, kurtosis, Z-score, ADX

### Multi-timeframe (5)
Weekly aggregates, daily vs weekly momentum

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'xgboost'`
- **Solution**: Run `pip install xgboost`

**Issue**: `ModuleNotFoundError: No module named 'tensorflow'`
- **Solution**: Run `pip install tensorflow`

**Issue**: `No such file or directory: Nify50_data`
- **Solution**: Ensure Nify50_data folder exists with CSV files, or update config.yaml

**Issue**: Empty results in screener
- **Solution**: Train models first using `train_models.py`

## Next Steps

1. Train models on your data
2. Run backtesting to validate performance
3. Tune hyperparameters in config.yaml
4. Add more stocks to Nify50_data
5. Integrate with live data feeds
6. Deploy to cloud for production use

## License

Open source - modify and use as needed for your trading system.

## Contact

Part of the MG AI Trading System project.

