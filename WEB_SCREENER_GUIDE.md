# 🌐 AI Stock Screener - Web Dashboard Guide

## 🎯 What You Get

A **beautiful web dashboard** accessible at **http://localhost:8501** with:

✅ **Live Stock Scanning** - Scan all 42 stocks in real-time  
✅ **Interactive Tables** - Sort, filter, and search  
✅ **Visual Charts** - Pie charts, bar graphs  
✅ **Color-Coded Tiers** - Green (High), Yellow (Medium), Red (Low)  
✅ **Confidence Sliders** - Filter by confidence level  
✅ **Auto-Refresh** - Update with latest data  
✅ **Download CSV** - Export signals for your records  

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies (ONE TIME)

**Option A: Double-click**
```
install_web_dependencies.bat
```

**Option B: Command line**
```bash
pip install streamlit plotly openpyxl
```

This installs:
- **Streamlit** - Web framework
- **Plotly** - Interactive charts
- **Openpyxl** - Excel export

---

### Step 2: Launch Web Dashboard

**Option A: Double-click (EASIEST)**
```
launch_web_screener.bat
```

**Option B: Command line**
```bash
cd "c:\python\MG AI\AI_Screener_Complete"
streamlit run web_screener.py
```

**What happens:**
- Web server starts
- Browser opens automatically
- Dashboard loads at: **http://localhost:8501**

---

### Step 3: Use the Dashboard

**You'll see:**

```
┌─────────────────────────────────────────────────────────┐
│  📈 AI Stock Screener Dashboard                         │
│  Live Scan | 2025-11-03 11:30:00                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📊 Today's Scan Summary                                │
│  ┌──────────┬──────────┬──────────┬──────────┐          │
│  │ Scanned  │ BUY      │ Tier 1   │ Avg      │          │
│  │ 42       │ 8        │ 3        │ 72.5%    │          │
│  └──────────┴──────────┴──────────┴──────────┘          │
│                                                          │
│  🌟 TIER 1 - HIGH CONFIDENCE SIGNALS                    │
│  ┌────────────────────────────────────────────┐         │
│  │ 🎯 BAJAJFINSV                              │         │
│  │ Confidence: 85.2% | Price: Rs 1650         │         │
│  └────────────────────────────────────────────┘         │
│  ┌────────────────────────────────────────────┐         │
│  │ 🎯 ICICIBANK                               │         │
│  │ Confidence: 72.1% | Price: Rs 1145         │         │
│  └────────────────────────────────────────────┘         │
│                                                          │
│  Stock      Confidence  Buy Prob   Price                │
│  BAJAJFINSV  85.2%     88.5%      1650.00               │
│  ICICIBANK   72.1%     75.3%      1145.00               │
│                                                          │
│  ✓ TIER 2 - MEDIUM CONFIDENCE SIGNALS                   │
│  HINDALCO    65.3%     68.1%       650.00               │
│  TATASTEEL   62.8%     64.2%       145.00               │
│                                                          │
│  📊 Signal Distribution [Charts]                        │
│  📋 Recommended Action Plan                             │
│  📥 Download BUY Signals (CSV)                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🎮 Dashboard Features

### Left Sidebar (Controls):

**⚙️ Settings:**
- **Minimum Confidence Slider** (0-100%)
  - Move slider to filter signals
  - Default: 50% (shows signals ≥50% confidence)
  
- **Show Tiers** (Checkboxes)
  - Tier 1: HIGH (40-60% accurate)
  - Tier 2: MEDIUM (30-40% accurate)
  - Tier 3: LOW (<20% accurate)

**🔄 Refresh Button:**
- Click to rescan all stocks
- Gets latest data
- Updates predictions

**📊 Model Info:**
- Shows training stats
- 42 models loaded
- Average precision

**🎯 Quick Guide:**
- Explains tier meanings
- Usage recommendations

---

### Main Panel (Results):

**1. Summary Cards (Top)**
- Total stocks scanned
- Total BUY signals
- Tier 1 BUY signals
- Average confidence

**2. Tier 1 Signals (GREEN)**
- Highlighted cards for each stock
- Big, easy to see
- Stock name, confidence, price
- Interactive table below

**3. Tier 2 Signals (YELLOW)**
- Table format
- Sort by confidence
- Filter options

**4. Tier 3 Signals (RED)**
- Collapsed by default
- Click to expand
- Warning: Not recommended

**5. Charts & Visualizations**
- Pie chart: BUY vs HOLD distribution
- Bar chart: Signals by tier
- Interactive (hover for details)

**6. Top 10 List**
- Highest confidence signals
- Color-coded by tier
- Quick overview

**7. Action Plan**
- Step-by-step instructions
- What to do next
- VWAP filter integration tips

**8. Download Button**
- Export to CSV
- Opens in Excel
- Save for records

---

## 🔄 Auto-Refresh Feature

**Method 1: Manual Refresh**
- Click "🔄 Refresh Scan" in sidebar
- Rescans all stocks
- Updates in 30-60 seconds

**Method 2: Browser Refresh**
- Press F5 in browser
- Reloads page
- Scans again

**Method 3: Always Run (Optional)**
- Click menu (top-right ≡)
- Settings → "Rerun on change"
- Auto-updates when data changes

---

## 💡 How to Use Effectively

### Morning Routine (10 minutes):

**09:00 AM - Launch Dashboard**
```
1. Double-click: launch_web_screener.bat
2. Browser opens automatically
3. Wait 30-60 seconds for scan
```

**09:01 AM - Review Signals**
```
4. Look at Tier 1 signals (GREEN)
5. Note 3-5 stock names
6. Check confidence levels
```

**09:05 AM - VWAP Backtest**
```
7. Copy those 3-5 stock CSV files
8. Run RVwapfilter_ssc.py
9. Compare 3%, 6%, 10% targets
```

**09:10 AM - Final Selection**
```
10. Pick best 2-3 stocks
11. Prepare entry orders
12. Ready to trade!
```

---

## 📊 Understanding the Dashboard

### Color Coding:

**🟢 GREEN (Tier 1)** = Trade these!
- 40-60% accurate
- BAJAJFINSV, MAXHEALTH, ICICIBANK, etc.
- Best for VWAP strategy

**🟡 YELLOW (Tier 2)** = Consider these
- 30-40% accurate
- HINDALCO, TATASTEEL, BIOCON, etc.
- Use if Tier 1 limited

**🔴 RED (Tier 3)** = Avoid these
- <20% accurate
- RELIANCE, TCS, HDFCBANK, etc.
- Too stable for VWAP

### Confidence Levels:

- **80-100%** = Very high confidence (rare, trade these!)
- **70-80%** = High confidence (good signals)
- **60-70%** = Medium-high (consider with VWAP)
- **50-60%** = Medium (verify carefully)
- **<50%** = Low (skip)

---

## ⚡ Advanced Features

### Sidebar Controls:

**Confidence Slider:**
```
Move slider right → Show only high-confidence signals
Move slider left → Show more signals (but lower quality)

Example:
- Slider at 70%: Shows only very confident signals (3-5 stocks)
- Slider at 50%: Shows moderate signals (8-12 stocks)
- Slider at 30%: Shows many signals (15-20 stocks, some weak)
```

**Tier Selection:**
```
Check only Tier 1 → See best signals only
Check Tier 1+2 → Balanced view (recommended)
Check all → See everything (not recommended)
```

---

## 📱 Dashboard Sections Explained

### 1. Summary Metrics (Top)
```
┌──────────────────────────────────────────────┐
│ Total Scanned: 42 │ BUY: 8 │ Tier 1: 3     │
└──────────────────────────────────────────────┘
```
Quick overview of today's scan

### 2. Signal Cards (Main)
```
┌─────────────────────────────────┐
│ 🎯 BAJAJFINSV                   │ ← Big, easy to read
│ Confidence: 85.2%               │ ← How sure AI is
│ Price: Rs 1650                  │ ← Current price
│ Buy Probability: 88.5%          │ ← Raw AI score
└─────────────────────────────────┘
```

### 3. Interactive Tables
- Click headers to sort
- Scroll for more
- Copy/paste friendly

### 4. Charts
- Visual representation
- Hover for details
- Interactive legends

### 5. Download Section
- CSV export
- Open in Excel
- Archive for records

---

## 🔧 Troubleshooting

### "streamlit: command not found"
**Solution:**
```bash
pip install streamlit plotly
```
Or run: `install_web_dependencies.bat`

### Dashboard won't load
**Check:**
1. Models trained? (42 .pkl files in ai_screener/models/)
2. Data available? (42 CSV files in Nify50_data/)
3. Python working? (Try: `python --version`)

### "No signals found"
**Reasons:**
- Market very bearish (normal)
- Data not updated
- Confidence slider too high
**Solution:** Lower confidence slider or skip trading today

### Browser doesn't open
**Manual access:**
- Open browser
- Go to: `http://localhost:8501`
- Bookmark for daily use

### Need to stop server
**Press:** `Ctrl + C` in command window
**Or:** Close the command window

---

## 🎯 Best Practices

### Daily Usage:
1. ✅ Run every morning before market
2. ✅ Focus on Tier 1 signals
3. ✅ Verify with VWAP filter
4. ✅ Trade only when confident

### Don't:
1. ❌ Trade all signals blindly
2. ❌ Ignore tier classifications
3. ❌ Skip VWAP verification
4. ❌ Overtrade (stick to 2-3 stocks)

### Track Results:
- Note which signals worked
- Learn patterns over time
- Adjust confidence threshold
- Build your own experience

---

## 📈 Expected Performance

**Realistic Expectations:**

**Daily:**
- Scan: 42 stocks in 30 seconds
- Signals: 8-15 BUY signals
- Tier 1: 2-5 signals (focus here)
- Final picks: 2-3 stocks

**Monthly (20 trading days):**
- Trades: 40-60 (2-3 per day)
- Win rate: 50-60%
- Profitable: 24-36 trades
- Losing: 16-24 trades

**Key:** Win more than you lose, small losses, big wins!

---

## 🆚 Command Line vs Web Dashboard

### Command Line (`daily_screener.py`):
- ✓ Fast
- ✓ Simple
- ✓ Text output
- ✗ Less visual

### Web Dashboard (`web_screener.py`):
- ✓ Beautiful UI
- ✓ Interactive
- ✓ Charts & graphs
- ✓ Easy to use
- ✓ Better visualization

**Recommendation:** Use **Web Dashboard** for daily scanning!

---

## 📞 Quick Commands

**Launch Web Dashboard:**
```bash
streamlit run web_screener.py
```

**Or double-click:**
```
launch_web_screener.bat
```

**Access in browser:**
```
http://localhost:8501
```

**Stop server:**
```
Ctrl + C
```

---

## 🎊 You're All Set!

**Your complete system:**

```
Morning (Before Market):
1. Launch web dashboard      ← Beautiful UI in browser
2. See BUY signals instantly ← Green/Yellow/Red coded
3. Pick 5-8 stocks           ← Tier 1 + good Tier 2
4. Run VWAP backtest         ← Verify profit potential
5. Trade best 2-3            ← Execute strategy

Total time: 10 minutes
Success rate: 50-60%
```

---

## 🎯 Tomorrow Morning:

1. **Double-click:** `launch_web_screener.bat`
2. **Browser opens** with live dashboard
3. **Review signals** (30 seconds)
4. **Run VWAP filter** on selected stocks
5. **Trade!**

---

**Enjoy your professional AI trading system!** 🚀📈


