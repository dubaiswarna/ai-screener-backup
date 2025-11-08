# 📊 Support & Resistance Analyzer - User Guide

**Created:** November 7, 2025  
**Strategy Based On:** [Unlocking the Market's Hidden Fortress: Mastering Support & Resistance](https://youtu.be/17tR6S9tqeM)

---

## 🎯 What It Does

Automatically identifies **Support & Resistance levels** for any stock using:

✅ **Swing High/Low Detection** - Finds peaks and troughs  
✅ **Volume Confirmation** - Validates levels with volume spikes  
✅ **Zone-Based Levels** - Treats levels as zones (not exact lines)  
✅ **Strength Scoring** - Ranks levels by number of touches & volume  
✅ **Multi-Timeframe** - Daily or Weekly analysis  
✅ **Visual Charts** - See S&R zones on price charts  

---

## 🚀 How to Launch

### **Option 1: Double-click Batch File**
```
C:\python\MG AI\AI_Screener_Complete\LAUNCH_SR_ANALYZER.bat
```

### **Option 2: Manual Launch**
```bash
cd "C:\python\MG AI\AI_Screener_Complete\support_resistance"
streamlit run sr_viewer.py --server.port 8503
```

**Access at:** http://localhost:8503

---

## 📖 How to Use

### **Step 1: Enter Stock Symbol**
- Type any NSE stock symbol (e.g., RELIANCE, TCS, INFY)
- Works with all NSE stocks (currently top 10 pre-mapped)

### **Step 2: Select Timeframe**
- **1D** = Daily candles (short-term levels)
- **1W** = Weekly candles (long-term levels)

### **Step 3: Adjust Settings** (Optional)
- **Sensitivity (3-10):** 
  - Lower = More levels detected
  - Higher = Fewer, stronger levels
  - Default: 5 (recommended)

- **Minimum Touches (2-5):**
  - How many times price must touch a level
  - Default: 2 (recommended)

### **Step 4: Click ANALYZE**
- Wait 2-3 seconds for analysis
- Results appear below!

---

## 📊 Understanding the Results

### **1. Metrics at Top**
- **Current Price:** Latest closing price
- **Support Levels:** Number of support zones found
- **Resistance Levels:** Number of resistance zones found

### **2. Price Chart**
- **Green zones** = Support (buy zones)
- **Red zones** = Resistance (sell zones)
- **Blue line** = Current price
- **Dashed lines** = Exact S&R levels
- **Shaded areas** = Price zones (±1.5% tolerance)

### **3. Support Levels Table** (Green)
| Column | Meaning |
|--------|---------|
| **Level (₹)** | Support price level |
| **Distance %** | How far below current price |
| **Touches** | Times price tested this level |
| **Volume Factor** | Volume spike at level (>1 = strong) |
| **Strength %** | Overall level strength (0-100) |

### **4. Resistance Levels Table** (Red)
| Column | Meaning |
|--------|---------|
| **Level (₹)** | Resistance price level |
| **Distance %** | How far above current price |
| **Touches** | Times price tested this level |
| **Volume Factor** | Volume spike at level (>1 = strong) |
| **Strength %** | Overall level strength (0-100) |

### **5. Nearest Key Levels**
- Shows the CLOSEST support and resistance to current price
- Most important levels for immediate trading decisions

---

## 🎓 Trading Strategy (From Video)

### **Key Concepts:**

1. **Support = Price Floor**
   - Where buyers step in
   - Price bounces UP from support
   - **Action:** Consider buying near support

2. **Resistance = Price Ceiling**
   - Where sellers step in
   - Price bounces DOWN from resistance
   - **Action:** Consider selling near resistance

3. **Zone Trading**
   - Don't treat levels as exact prices
   - Look for zones (±1.5% around level)
   - Price might not hit exact level

4. **Volume Confirmation**
   - Strong levels have high volume
   - Look for **Volume Factor > 1.5**
   - Higher volume = more reliable level

5. **Strength Matters**
   - **80-100%** = Very strong (high confidence)
   - **60-79%** = Strong (good confidence)
   - **40-59%** = Moderate (use with caution)
   - **<40%** = Weak (risky)

6. **Role Reversals**
   - Broken support becomes new resistance
   - Broken resistance becomes new support
   - Watch for these changes!

---

## ✅ Best Practices

### **1. Use Multiple Timeframes**
- Check both **Daily** (short-term) and **Weekly** (long-term)
- Levels that align on both = STRONGEST

### **2. Focus on Strong Levels**
- Strength > 70%
- Touches ≥ 3
- Volume Factor > 1.5

### **3. Watch the Nearest Levels**
- These are most likely to affect price SOON
- Trade bounces off these levels

### **4. Confirm with Volume**
- When price approaches a level, watch volume
- Volume spike = level is ACTIVE
- Low volume = level might break

### **5. Don't Trade Every Level**
- Too many levels = analysis paralysis
- Focus on the TOP 3 supports and TOP 3 resistances

---

## 🔧 Troubleshooting

### **"Could not fetch data"**
- Check if stock symbol is correct (NSE symbols only)
- Try a different stock (e.g., RELIANCE, TCS)
- Check internet connection

### **"No significant S&R levels found"**
- Reduce **Sensitivity** (try 3-4)
- Reduce **Minimum Touches** (try 2)
- Stock might be in a strong trend (fewer bounces)

### **Levels look wrong**
- Increase **Sensitivity** (try 7-8) for fewer, stronger levels
- Try a different **Timeframe** (Weekly for clearer long-term levels)

### **Too many levels**
- Increase **Sensitivity** (try 7-10)
- Increase **Minimum Touches** (try 3-4)

---

## 📈 Example Interpretation

**Stock:** RELIANCE  
**Current Price:** ₹2,850

**Nearest Support:** ₹2,780 (2.5% below, 80% strength)  
→ **Action:** If price drops to ₹2,780-₹2,800 zone, consider BUYING

**Nearest Resistance:** ₹2,920 (2.5% above, 75% strength)  
→ **Action:** If price rises to ₹2,900-₹2,920 zone, consider SELLING

**Volume Factor at Support:** 1.8  
→ Strong buyer interest at this level

**Strategy:**  
- BUY near ₹2,780-₹2,800 (support zone)
- Target: ₹2,900-₹2,920 (resistance zone)
- Stop-loss: Below ₹2,750 (if support breaks)

---

## 🎯 What's Next?

### **Phase 1 (DONE):** ✅
- S&R level detection
- Visual analysis
- Zone-based approach

### **Phase 2 (Coming Next):**
- 169 trained models integration
- Automatic signal generation
- BUY/SELL recommendations
- Trade entry/exit points
- Risk management

---

## 📝 Key Files

| File | Purpose |
|------|---------|
| `sr_calculator.py` | Core S&R calculation logic |
| `sr_viewer.py` | Streamlit UI interface |
| `LAUNCH_SR_ANALYZER.bat` | Quick launch script |
| `SR_ANALYZER_GUIDE.md` | This guide |

---

## 💡 Tips for Success

1. **Start Simple:** Use default settings (Sensitivity: 5, Touches: 2)
2. **Practice First:** Analyze 5-10 different stocks to get familiar
3. **Compare Timeframes:** Always check both Daily and Weekly
4. **Record Levels:** Note down key levels and watch them over time
5. **Combine with Trends:** S&R works best with trend analysis
6. **Be Patient:** Wait for price to reach your levels
7. **Use Zones:** Don't wait for exact prices

---

## 📞 Support

If you need help:
1. Check this guide first
2. Try adjusting settings
3. Test with a known stock (RELIANCE, TCS)
4. Review the [original video](https://youtu.be/17tR6S9tqeM)

---

## 🎉 Happy Trading!

**Remember:**  
- S&R levels are probabilities, not guarantees
- Always use stop-losses
- Never risk more than you can afford to lose
- Practice makes perfect!

---

**Version:** 1.0  
**Last Updated:** November 7, 2025  
**Port:** 8503  
**Status:** Ready to use! 🚀

