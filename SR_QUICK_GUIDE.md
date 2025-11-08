# 🎯 S&R System - Quick Reference Guide

## 🚀 Launch Dashboard

```bash
streamlit run enhanced_screener.py
```

Or double-click: `START_SYSTEM.bat`

**URL:** http://localhost:8501

---

## 📍 Navigation

1. Open dashboard
2. Sidebar → **"S&R Analysis"**
3. Enter stock symbol
4. Click **"🔍 Analyze"**

---

## 🎛️ Settings

| Setting | Range | Default | Purpose |
|---------|-------|---------|---------|
| **Sensitivity** | 3-10 | 5 | Lower = more levels, Higher = fewer strong levels |
| **Min Touches** | 2-5 | 2 | Minimum times price must touch a level |

---

## 📊 What You'll See

### **1. Key Metrics**
- 💰 Current Price
- 🎯 Trading Signal (STRONG BUY, BUY, HOLD, SELL, STRONG SELL)
- 📈 Confidence Score (0-100%)
- ⚡ Signal Strength (VERY HIGH, HIGH, MODERATE, NEUTRAL)

### **2. Support Levels** 🛡️
- Level price
- Distance from current price (%)
- Number of touches
- Strength score (0-100)

### **3. Resistance Levels** 🚧
- Level price
- Distance from current price (%)
- Number of touches
- Strength score (0-100)

### **4. Price Chart** 📈
- Candlestick price action
- Green dashed lines = Support
- Red dashed lines = Resistance
- Blue line = 50 EMA
- Orange line = 200 EMA

### **5. Moving Averages** 📊
- 50 EMA value & distance
- 200 EMA value & distance
- Trend classification
- Golden/Death Cross alerts

### **6. Breakouts** 💥
- Resistance breakouts (bullish)
- Support breakdowns (bearish)
- Volume confirmation
- Strength scoring

### **7. Role Reversals** 🔄
- Support → Resistance
- Resistance → Support
- Confidence levels

---

## 🎯 Trading Signals Explained

| Signal | Meaning | Action |
|--------|---------|--------|
| 🟢 **STRONG BUY** | Near strong support OR bullish breakout | Strong buy opportunity |
| 🟢 **BUY** | Near support OR bullish trend | Buy opportunity |
| 🟡 **HOLD** | Neutral conditions | Wait for better setup |
| 🔴 **SELL** | Near resistance OR bearish trend | Sell opportunity |
| 🔴 **STRONG SELL** | Near strong resistance OR bearish breakdown | Strong sell opportunity |

---

## 💡 Quick Tips

### **For Buyers:**
1. ✅ Look for price near support
2. ✅ Check for BUY signal
3. ✅ Confirm with volume
4. ✅ Set stop below support
5. ✅ Target resistance level

### **For Sellers:**
1. ✅ Look for price near resistance
2. ✅ Check for SELL signal
3. ✅ Confirm with volume
4. ✅ Set stop above resistance
5. ✅ Target support level

### **For Breakout Traders:**
1. ✅ Identify strong level
2. ✅ Wait for breakout signal
3. ✅ Check volume confirmation
4. ✅ Enter on candle close
5. ✅ Old level becomes new S/R

---

## ⚠️ Important Notes

### **Strength Scores:**
- **80-100**: VERY STRONG level (high confidence)
- **60-79**: STRONG level (good confidence)
- **40-59**: MODERATE level (medium confidence)
- **< 40**: WEAK level (low confidence)

### **Distance Matters:**
- **< 1%**: Very close to level (high probability)
- **1-2%**: Close to level (good probability)
- **2-3%**: Near level (moderate probability)
- **> 3%**: Far from level (wait for price to reach)

### **Volume Confirmation:**
- ✅ Breakouts with high volume = more reliable
- ⚠️ Breakouts with low volume = less reliable
- 📊 Look for 1.2x average volume minimum

---

## 🔧 Troubleshooting

### **No data showing?**
- System uses sample data for demonstration
- Connect Dhan API for live data
- Check internet connection

### **Signal seems wrong?**
- Adjust sensitivity (higher = stricter)
- Increase min touches (more validation)
- Check multiple timeframes

### **Chart not loading?**
- Refresh page
- Check if streamlit is running
- Look for errors in terminal

---

## 📚 Learn More

**Full Documentation:** `SR_SYSTEM_INTEGRATION_COMPLETE.md`

**Support & Resistance Calculator:** `support_resistance/sr_calculator.py`

**Dashboard Code:** `enhanced_screener.py`

---

## 🎉 You're Ready!

1. Launch dashboard
2. Go to S&R Analysis
3. Enter stock symbol
4. Analyze!
5. Trade smart! 🚀

---

**Quick Access:** http://localhost:8501

**Status:** ✅ Ready to Use

**Cost:** 💰 FREE Forever

---

# TRADE WITH CONFIDENCE! 🎯

