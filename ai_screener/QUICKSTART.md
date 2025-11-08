# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
pip install pandas numpy scikit-learn xgboost streamlit plotly pyyaml joblib openpyxl
```

**Note**: TensorFlow installation may take time. You can use the screener with just XGBoost if needed:
```bash
pip install tensorflow  # Optional - only for CNN-LSTM
```

### Step 2: Test Data Loading

```bash
cd "C:\python\MG AI"
python ai_screener/data_loader.py
```

Expected output:
```
Found 30 stocks: ...
Loaded NSE_ABCAPITAL: 475 rows
```

### Step 3: Run the Screener

```bash
cd ai_screener
streamlit run screener_app.py
```

The app opens at: `http://localhost:8501`

## 📊 What You'll See

### Dashboard Features:

1. **Stock Selection**: Choose which stocks to screen
2. **Filters**:
   - Min Confidence (0-100%)
   - Signal Types (Buy/Sell/Hold)
   - VWAP Position
   - Volume Ratio
3. **Results Table**: 
   - Symbol, Signal, Confidence
   - Current Price, Target, Stop Loss
   - VWAP Deviation
4. **Charts**: Interactive candlestick + VWAP
5. **Export**: Download results as CSV

## 🔧 Training Models (Optional)

Before generating signals, you need trained models:

```bash
cd ai_screener
python train_models.py
```

This trains XGBoost on all 30+ stocks (XGBoost only, if TensorFlow not installed).

Training time: ~5-10 minutes for 30 stocks

## 🎯 Using the Screener

1. **Open App**: `streamlit run screener_app.py`
2. **Select Stocks**: Choose 5-10 stocks from dropdown
3. **Set Filters**: 
   - Min confidence: 70%
   - Signal types: Buy, Sell
4. **View Results**: Click through the tabs
5. **Export**: Download CSV for analysis

## 📁 File Locations

- **Data**: `supervwap_data/` folder
- **Config**: `ai_screener/config.yaml`
- **Models**: `ai_screener/models/` (created after training)
- **Results**: Downloaded via UI

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
trading:
  profit_target: 0.03      # Change to 0.05 for 5% target
  stop_loss: 0.015        # Change to 0.02 for 2% stop loss
  
models:
  ensemble:
    min_confidence: 0.70   # Change to 0.80 for stricter signals
```

## 🐛 Troubleshooting

### "No module named 'xgboost'"
```bash
pip install xgboost
```

### "No module named 'streamlit'"
```bash
pip install streamlit
```

### "No stocks found"
Check that `Nify50_data` folder exists with CSV files

### "No signals generated"
Train models first: `python train_models.py`

## 💡 Next Steps

1. ✅ Run the screener
2. 📊 Analyze results
3. 🎯 Adjust filters
4. 📈 Train CNN-LSTM (optional)
5. 🔄 Integrate with live feeds

## 📞 Need Help?

See `README.md` for full documentation.

