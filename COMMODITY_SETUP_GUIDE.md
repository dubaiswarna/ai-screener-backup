# MCX Gold & Silver AI Trading Setup Guide

## Quick Start (3 Steps)

### Step 1: Fetch Commodity Data
```bash
python fetch_commodity_data.py
```

This will:
- Download 10 years of Gold futures data (similar to MCX Gold)
- Download 10 years of Silver futures data (similar to MCX Silver)
- Calculate VWAP and Bollinger Bands
- Save to `Commodity_data/MCX_GOLD, 1D.csv` and `MCX_SILVER, 1D.csv`

### Step 2: Train AI Models
```bash
python train_commodity.py
```

This will:
- Train XGBoost models for both Gold and Silver
- Use VWAP ladder strategy (same as stocks)
- Save models to `ai_screener/models/`
- Show accuracy, F1 score, and performance metrics

### Step 3: Test Predictions
```bash
python test_commodity_prediction.py
```

## Data Format

Your commodities will use the same format as NSE stocks:

```csv
time,open,high,low,close,Volume,VWAP,Upper Band #1,Lower Band #1
2014-11-04,1178.4,1179.8,1167.0,1168.3,154023,1171.4,1171.4,1171.4
2014-11-05,1170.0,1179.3,1165.3,1178.1,157241,1174.4,1174.4,1174.4
```

## Using Your Own MCX Data

If you have actual MCX data, just:

1. Format your CSV with these columns:
   - `time` (date), `open`, `high`, `low`, `close`, `Volume`, `VWAP`
   
2. Save as: `Commodity_data/MCX_GOLD, 1D.csv`

3. Run training: `python train_commodity.py`

## Customization

### Train Single Commodity
```bash
python train_commodity.py --commodity MCX_GOLD
python train_commodity.py --commodity MCX_SILVER
```

### Adjust Profit Targets

Edit `train_commodity.py`:
```python
results = trainer.run_full_pipeline(
    profit_target=0.02,      # Change to 0.01 (1%) or 0.03 (3%)
    forward_days=3,          # Change to 5 or 7 days
    use_vwap_strategy=True,
    tune_hyperparameters=True,  # Set True for better accuracy
)
```

### Better Accuracy (Slower Training)

Set `tune_hyperparameters=True` in training script for GridSearch optimization.

## Differences: Commodities vs Stocks

| Feature | Stocks | Commodities |
|---------|--------|-------------|
| Volatility | Moderate | Higher |
| Trading Hours | 9:15-15:30 | Extended hours |
| Profit Target | 2-3% | 1-2% (faster) |
| Position Size | Larger | Smaller (due to leverage) |

## Model Files

After training, you'll find:
- `ai_screener/models/MCX_GOLD_model.pkl` - Gold prediction model
- `ai_screener/models/MCX_SILVER_model.pkl` - Silver prediction model

## Integration with Existing Screener

To use commodities with your existing screener:

1. Copy commodity CSV files to `Nify50_data/` folder
2. Models will automatically be used by screener
3. Or create separate commodity screener

## Notes

- Free data sources use COMEX futures (similar to MCX but US-based)
- For true MCX data, you'll need to provide your own CSV files
- The AI model works the same for commodities and stocks
- Volume data may be estimated if not available

## Troubleshooting

**"No data received"**
- Check internet connection
- yfinance might be temporarily down
- Try again in a few minutes

**"File not found"**
- Run `fetch_commodity_data.py` first
- Check `Commodity_data/` folder exists

**"Training failed"**
- Check if CSV file has enough data (minimum 500 rows)
- Verify CSV format matches expected columns

## Support

For issues, check:
1. Python version: 3.8+
2. Dependencies installed: `pip install -r requirements.txt`
3. Sufficient data: Minimum 2 years recommended

