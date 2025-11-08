# BACKTEST DASHBOARD - COMPLETE GUIDE

## 🚀 Launch Dashboard

**Double-click:** `LAUNCH_BACKTEST_DASHBOARD.bat`

**Or run:**
```bash
cd Feb2025_Experiment
streamlit run backtest_dashboard.py
```

**Dashboard opens at:** http://localhost:8502

---

## 📊 Features

### 1. Stock Selection
- Choose from 169 Nifty 200 stocks
- **Quick Select:** Top 5 or Top 10 buttons
- **Manual Select:** Pick any combination
- Default: RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK

### 2. Time Period
- **Start Date:** Any date from 2015-2025
- **End Date:** Any date from 2015-2025
- Default: March 2022 to February 2025 (3 years)

### 3. Portfolio Settings
- **Investment per Stock:** Rs 10,000 to Rs 1 Crore
  - Default: Rs 2,00,000 (2 Lakh)
- **Max Portfolio Size:** 1 to 50 stocks
  - Default: 20 stocks

### 4. Risk Management
- **Target Return:** 5% to 30%
  - Default: 10% (take profit)
- **Stop Loss:** 3% to 15%
  - Default: 7% (protection)
- **Max Holding Days:** 10 to 365 days
  - Default: 60 days

---

## 📈 What You Get

### Performance Summary
- **Total P&L** (Profit/Loss in Rs)
- **Total Trades** (Number of trades executed)
- **Win Rate** (% of profitable trades)
- **Average Return** (% per trade)
- **Average Holding** (Days per trade)

### Portfolio Performance Chart
- **Interactive Line Chart** showing portfolio value over time
- **Initial Capital Line** for reference
- **Zoom & Pan** capabilities
- **Hover for exact values**

### Portfolio Statistics
- **Initial Capital:** Total investment capacity
- **Final Value:** Ending portfolio value
- **Total Return %:** Overall return on capital
- **Total P&L:** Absolute profit/loss

### Trade Statistics
- **Winners:** Number & percentage
- **Losers:** Number & percentage
- **Average Win:** Average winning trade return
- **Average Loss:** Average losing trade return

### Best & Worst Trades
- **Symbol, dates, prices, returns**
- **Quick insight** into extreme outcomes

### Complete Trade History
- **Interactive Table** with all trades
- Columns:
  - Symbol
  - Entry Date & Price
  - Exit Date & Price
  - Exit Reason (TARGET/STOP_LOSS/TIME_EXIT)
  - Investment
  - Exit Value
  - P&L
  - Return %
  - Holding Days
  - Entry Reason (technical signal)
  - Confidence

### Download Option
- **Export to CSV** button
- Contains all trade details
- Use in Excel for further analysis

---

## 🎯 Strategy Used

### Technical Analysis Signals

**1. Golden Cross (85% confidence)**
- SMA 20 crosses above SMA 50
- RSI < 40 (oversold)
- Price above SMA 20

**2. Uptrend Entry (75% confidence)**
- Price above both SMAs
- 30 < RSI < 70 (healthy)
- SMA 20 > SMA 50 (uptrend)

**3. Pullback Entry (70% confidence)**
- Price near SMA 20 (within 2%)
- SMA 20 > SMA 50 (uptrend)
- RSI < 50 (room to grow)

### Exit Rules
- **Target Hit:** Exit at +10% (or your custom %)
- **Stop Loss:** Exit at -7% (or your custom %)
- **Time Exit:** Exit after 60 days (or your custom days)

---

## 💡 Usage Tips

### For Quick Test:
1. Use "Top 5" button
2. Keep default dates (3 years)
3. Click "Run Backtest"

### For Custom Analysis:
1. Select specific stocks
2. Choose bull/bear periods
3. Adjust risk parameters
4. Compare different settings

### For Portfolio Optimization:
1. Try different portfolio sizes
2. Test various target/stop combinations
3. Experiment with holding periods
4. Find best risk/reward ratio

---

## 🔄 Running Multiple Backtests

You can run unlimited backtests with different settings:

1. Run first backtest
2. Change settings in sidebar
3. Click "Run Backtest" again
4. Compare results
5. Download each for analysis

---

## 📥 Exporting Results

1. Scroll to bottom of results
2. Click "Download Full Results (CSV)"
3. File saves automatically
4. Open in Excel for detailed analysis

---

## ⚠️ Important Notes

- **Historical data only:** Tests past performance
- **Not predictive:** Past results ≠ future results
- **Strategy fixed:** Uses technical analysis rules
- **Execution instant:** No slippage modeled
- **Transaction costs:** Not included (add ~0.1-0.2% per trade)

---

## 🎨 Dashboard Layout

```
┌─────────────────────────────────────────────┐
│ Sidebar (Left)                              │
│ ─────────────────                           │
│ Stock Selection                             │
│ Time Period                                 │
│ Portfolio Settings                          │
│ Risk Management                             │
│ [Run Backtest Button]                       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Main Area (Right)                           │
│ ─────────────────                           │
│ Performance Metrics (5 columns)             │
│ Portfolio Performance Chart                 │
│ Portfolio & Trade Statistics (2 columns)    │
│ Best & Worst Trades (2 columns)             │
│ Complete Trade History Table                │
│ [Download CSV Button]                       │
└─────────────────────────────────────────────┘
```

---

## 🚀 Ready to Use!

**Launch:** LAUNCH_BACKTEST_DASHBOARD.bat

**URL:** http://localhost:8502

**Enjoy interactive backtesting!** 📊✨

