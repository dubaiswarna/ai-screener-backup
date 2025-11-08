# AI Screener - Single Stock Training Guide

## Quick Start - Train RELIANCE Stock

### Option 1: Run the batch file (Easiest)
```
Double-click: test_train.bat
```

### Option 2: Run from command line
```bash
cd "c:\python\MG AI\AI_Screener_Complete"
python quick_train.py
```

### Option 3: Interactive training
```bash
cd "c:\python\MG AI\AI_Screener_Complete"
python train_single_stock.py
```

---

## What to Expect

The training will show:

1. **DATA LOADING**
   - Number of days loaded
   - Date range
   - Columns available

2. **FEATURE ENGINEERING**
   - Number of features created
   - List of engineered features

3. **LABEL CREATION**
   - Strategy used (VWAP Ladder)
   - Label distribution (Buy/Hold/Sell)

4. **DATA SPLITTING**
   - Train set size and date range
   - Test set size and date range

5. **MODEL TRAINING**
   - Training progress
   - Parameters used

6. **EVALUATION RESULTS**
   - **Accuracy** (most important!)
   - **F1 Score**
   - Per-class performance (Sell/Hold/Buy)
   - Confusion matrix

7. **FEATURE IMPORTANCE**
   - Top 20 most important features
   - Shows which indicators matter most

8. **MODEL SAVED**
   - Location: `ai_screener/models/xgb_NSE_RELIANCE.pkl`

---

## Interpreting Results

### Good Results ✓
- **Accuracy > 60%**: Excellent for stock prediction!
- **F1 Score > 0.50**: Model is balanced
- **Buy Precision > 0.60**: When it says "buy", it's usually right

### Need Improvement ✗
- **Accuracy < 50%**: Worse than random, adjust parameters
- **F1 Score < 0.40**: Model is too imbalanced
- **All predictions same class**: Label distribution problem

---

## Configuration Options

Edit `quick_train.py` to change these:

```python
profit_target=0.03,      # 3% profit target (try: 0.02, 0.05, 0.10)
forward_days=5,          # Look 5 days ahead (try: 3, 7, 10)
use_vwap_strategy=True,  # Use VWAP ladder (try: False for simple strategy)
tune_hyperparameters=False,  # Quick (try: True for better accuracy, slower)
train_ratio=0.7,         # 70% train (try: 0.8 for more training data)
```

---

## Next Steps After Training

### If Accuracy is GOOD (> 60%)
1. ✓ Model is ready!
2. Train all stocks with same settings
3. Use in screener app

### If Accuracy is OK (50-60%)
1. Try `tune_hyperparameters=True` (slower but better)
2. Adjust `profit_target` (try 2%, 5%, 10%)
3. Change `forward_days` (try 3, 7, 10)

### If Accuracy is POOR (< 50%)
1. Check label distribution (should not be all one class)
2. Try `use_vwap_strategy=False`
3. Increase training data
4. Add more features

---

## Training All Stocks

Once you're satisfied with RELIANCE results:

```bash
cd "c:\python\MG AI\AI_Screener_Complete\ai_screener"
python train_models.py
```

This will train models for all 42 stocks with the same settings!

---

## Troubleshooting

### Import Errors
```bash
pip install -r ai_screener/requirements.txt
```

### Data Not Found
- Check: `Nify50_data` folder exists
- Check: CSV files are present
- Stock format: `NSE_STOCKNAME, 1D.csv`

### Model Not Saving
- Check: `ai_screener/models` folder exists
- Run as administrator if needed

---

## What the Model Learns

The XGBoost model learns from:
- Technical indicators (RSI, MACD, Bollinger Bands)
- Price patterns (Moving averages, momentum)
- Volume indicators
- VWAP relationships
- Support/Resistance levels

And predicts:
- **BUY** = Entry signal (profitable in next 5 days)
- **HOLD** = Wait
- **SELL** = No entry signal

---

## Files Created

After training:
```
ai_screener/models/
  └─ xgb_NSE_RELIANCE.pkl  ← Your trained model!
```

Use this model in the screener app to get buy/sell signals!

