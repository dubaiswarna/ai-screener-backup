# 🧪 JUNE 2025 BACKTEST GUIDE

## 🎯 WHAT IS THIS?

A special screener that generates AI signals using **ONLY data up to June 30, 2025**.

### Purpose:
Test your AI accuracy by comparing predictions with **known outcomes** (July-Nov 2025)!

---

## 🌐 ACCESS THE TEST SCREENER

```
http://localhost:8502
```

**Different from main screener (8501):**
- **8501** = Current/Live screener (uses all data)
- **8502** = June 2025 test (data cutoff: June 30, 2025)

---

## 🚀 HOW TO USE

### Step 1: Open Test Screener
```
http://localhost:8502
```

### Step 2: Configure Settings
**Sidebar Options:**
- Min Confidence: 75% (default)
- Selection: "All Trained Models" (42 stocks)

### Step 3: Generate Signals
Click: **"🧪 GENERATE JUNE 2025 SIGNALS"**

### Step 4: Review Results
You'll see:
- BUY/SELL/HOLD signals
- Confidence levels
- Entry prices (as of June 30, 2025)
- Target & Stop Loss

### Step 5: Download CSV
Click: **"📥 Download June 2025 Signals CSV"**

---

## 📊 WHAT YOU'LL GET

### Example Output:
```
✅ Generated 18 signals from June 2025 data!

BUY Signals: 8
SELL Signals: 10
HOLD Signals: 0
Avg Confidence: 89.2%

⚡ 15 signals above 75% confidence
```

### Signals Table:
| Symbol | Signal | Confidence | Entry Price (June 30) | Target | Stop Loss | Qty |
|--------|--------|------------|----------------------|--------|-----------|-----|
| RELIANCE | BUY | 98.5% | ₹2,450 | ₹2,573 | ₹2,377 | 20 |
| TATASTEEL | SELL | 96.2% | ₹145 | ₹138 | ₹149 | 100 |

---

## 🎯 HOW TO VALIDATE ACCURACY

### Step 1: Get June 2025 Signals
Run the test screener → Get signals → Download CSV

### Step 2: Compare with Actual Outcomes

**For BUY signals:**
- Check: Did price GO UP after June 30?
- Target hit? Stop loss hit?
- What was actual return?

**For SELL signals:**
- Check: Did price GO DOWN after June 30?
- Target hit? Stop loss hit?
- What was actual return?

### Step 3: Calculate Metrics

#### **Accuracy:**
```
Correct Signals / Total Signals × 100
```

**Example:**
- Generated 15 signals
- 12 were correct (price moved as predicted)
- Accuracy = 12/15 = **80%**

#### **Profitability:**
```
Total Profit from Correct Signals - Total Loss from Wrong Signals
```

**Example:**
- 12 correct signals: +₹50,000
- 3 wrong signals: -₹8,000
- Net Profit: **₹42,000**

#### **Win Rate:**
```
Profitable Trades / Total Trades × 100
```

---

## 📈 EXAMPLE VALIDATION

### Signal Generated (June 30, 2025):
```
Symbol: RELIANCE
Signal: BUY
Entry: ₹2,450
Target: ₹2,573
Stop Loss: ₹2,377
Confidence: 98.5%
```

### Actual Outcome (July-Nov 2025):
```
Price on Nov 5: ₹2,650
Result: ✅ CORRECT! (Target exceeded)
Return: +8.2%
```

### Validation:
- ✅ Signal was correct
- ✅ High confidence (98.5%) was justified
- ✅ Target was hit
- ✅ Profitable trade

---

## 🧮 SAMPLE VALIDATION SHEET

Create an Excel sheet to track:

| Symbol | Signal | June Price | Nov Price | Predicted | Actual | Correct? | Return% |
|--------|--------|------------|-----------|-----------|--------|----------|---------|
| RELIANCE | BUY | ₹2,450 | ₹2,650 | UP | UP | ✅ YES | +8.2% |
| TATASTEEL | SELL | ₹145 | ₹142 | DOWN | DOWN | ✅ YES | +2.1% |
| HDFCBANK | BUY | ₹1,650 | ₹1,620 | UP | DOWN | ❌ NO | -1.8% |

**Summary:**
- Total Signals: 3
- Correct: 2 (66.7%)
- Wrong: 1 (33.3%)
- Net Return: +8.5%

---

## 💡 WHY THIS IS VALUABLE

### 1. **Validate AI Models:**
- See real accuracy with known outcomes
- Identify which models/stocks work best
- Build confidence in AI predictions

### 2. **Identify Patterns:**
- Which confidence levels are most reliable?
- Which stocks does AI predict best?
- What conditions lead to accurate signals?

### 3. **Improve Strategy:**
- Should you increase/decrease position sizes?
- Should you adjust confidence thresholds?
- Which signals to trust more?

### 4. **Build Confidence:**
- Prove AI works before live trading
- Show evidence to investors/partners
- Validate your investment in AI models

---

## 📊 EXPECTED RESULTS

### Good AI Performance:
- **Accuracy**: 70-85%
- **Win Rate**: 65-80%
- **Profit Factor**: 2.0-3.0
- **Return**: 15-30% over 5 months

### Excellent AI Performance:
- **Accuracy**: 85%+
- **Win Rate**: 80%+
- **Profit Factor**: 3.0+
- **Return**: 30%+ over 5 months

---

## 🎯 WHAT TO DO WITH RESULTS

### If Accuracy is HIGH (80%+):
✅ **Action:** Proceed with live trading!
- Use same confidence thresholds
- Follow AI signals confidently
- Start with smaller positions, scale up

### If Accuracy is MEDIUM (65-80%):
⚠️ **Action:** Optimize settings
- Increase confidence threshold to 85%+
- Focus on best-performing stocks
- Adjust position sizing

### If Accuracy is LOW (<65%):
❌ **Action:** Retrain models
- Models may need fresh data
- Consider different features
- Test different time periods

---

## 📝 QUICK TEST STEPS

### 5-Minute Quick Test:
1. Open: `http://localhost:8502`
2. Click: "🧪 GENERATE JUNE 2025 SIGNALS"
3. Wait: ~30 seconds
4. Download: CSV file
5. Compare: 5 random signals with actual Nov prices
6. Calculate: Quick accuracy check

### Full Validation (1 hour):
1. Generate all June 2025 signals
2. Export to Excel
3. Add actual Nov 2025 prices
4. Calculate all metrics
5. Create performance report
6. Make strategy decisions

---

## 🔧 TECHNICAL DETAILS

### Data Cutoff:
```
Date: June 30, 2025
Time: End of Day (EOD)
```

### What AI Sees:
- Historical data: Up to June 30, 2025
- NO data from July onwards
- Same as if you ran it on July 1, 2025

### What You Compare:
- AI predictions (June 30)
- Actual outcomes (July-November)
- 5 months of known results

---

## 📊 RUNNING BOTH SCREENERS

### Current Screener (8501):
```
http://localhost:8501
Purpose: Live/current trading signals
Data: All data including November 2025
```

### Test Screener (8502):
```
http://localhost:8502
Purpose: Backtest/validation
Data: Only up to June 30, 2025
```

**Both can run simultaneously!**

---

## 🚀 GET STARTED NOW

### Step 1: Open Test Screener
```
http://localhost:8502
```

### Step 2: Generate Signals
Click the big button!

### Step 3: Download Results
Save CSV file

### Step 4: Start Validation
Compare with actual November 2025 prices

---

## 📞 QUICK REFERENCE

**Test Screener URL:** `http://localhost:8502`  
**Data Cutoff:** June 30, 2025  
**Purpose:** Validate AI accuracy  
**Stocks:** 42 trained models  
**Time to run:** 20-30 seconds  

**Output:** CSV with June 2025 predictions  
**Compare with:** Actual prices (July-Nov 2025)  
**Goal:** Prove AI works before live trading!

---

**Created:** November 6, 2025  
**Status:** 🟢 READY FOR TESTING

---

