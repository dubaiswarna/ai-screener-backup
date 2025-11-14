# 🤖 Auto Signal Monitor Setup Guide

## Overview
Auto Signal Monitor runs **3Jasmines Screener** and **Hybrid Signal Generator** every **5 minutes** and sends new signals to Telegram.

## ⏰ Recommended Interval: **5 Minutes**

**Why 5 minutes?**
- ✅ Less API calls (Yahoo Finance rate limits)
- ✅ More stable (avoids timeouts)
- ✅ Better for EOD data (patterns don't change every minute)
- ✅ Less server load
- ✅ Still catches signals quickly

**1 minute is too frequent:**
- ❌ Too many API calls (risk of rate limiting)
- ❌ Unnecessary (EOD patterns don't change that fast)
- ❌ Higher server load
- ❌ May miss signals due to timeouts

## 📱 Telegram Setup

### Step 1: Create Telegram Bot
1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the **Bot Token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID
1. Search for **@userinfobot** on Telegram
2. Start a conversation
3. It will send your Chat ID (looks like: `123456789`)

### Step 3: Set Environment Variables

**Option A: Windows (PowerShell)**
```powershell
$env:TELEGRAM_BOT_TOKEN="your_bot_token_here"
$env:TELEGRAM_CHAT_ID="your_chat_id_here"
```

**Option B: Create `.env` file**
Create a file named `.env` in `AI_Screener_Complete` folder:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

**Option C: Set in System Environment Variables**
1. Right-click "This PC" → Properties
2. Advanced System Settings → Environment Variables
3. Add:
   - `TELEGRAM_BOT_TOKEN` = your_bot_token
   - `TELEGRAM_CHAT_ID` = your_chat_id

## 🚀 How to Run

### Method 1: Double-Click Batch File
```
START_AUTO_SIGNAL_MONITOR.bat
```

### Method 2: Command Line
```bash
cd "C:\python\MG AI\AI_Screener_Complete"
python auto_signal_monitor.py
```

### Method 3: Run in Background (Windows)
```powershell
Start-Process python -ArgumentList "auto_signal_monitor.py" -WindowStyle Hidden
```

## ⚙️ Configuration

Edit `auto_signal_monitor.py` to change settings:

```python
RUN_INTERVAL_MINUTES = 5  # Change to 1, 5, 10, etc.
STOCK_UNIVERSE = "Nifty 50"  # Options: "Nifty 50", "Nifty 200", "Small Cap 250"
MIN_CONFIDENCE_JASMINES = 70.0
MIN_CONFIDENCE_HYBRID = 75.0
MIN_RR_HYBRID = 1.5
```

## 📊 What It Does

1. **Every 5 minutes:**
   - Runs 3Jasmines Screener on selected universe
   - Runs Hybrid Signal Generator on selected universe
   - Checks for NEW signals (not sent before)
   - Sends new signals to Telegram

2. **Signal Tracking:**
   - Saves sent signals in `sent_signals.json`
   - Prevents duplicate notifications
   - Each signal identified by: `symbol_entry_price`

3. **Rate Limiting:**
   - 0.2 second delay between stocks
   - Limits to 50 stocks per run (configurable)

## 📱 Telegram Message Format

### 3Jasmines Signal:
```
🌸 3JASMINES SIGNAL 🌸

📊 RELIANCE
🎯 Confidence: 85.0%

💰 Trade Setup:
Entry: ₹2,450.00
Target: ₹2,650.00
Stop Loss: ₹2,400.00
R:R Ratio: 1:4.00

📈 Criteria Met:
✅ Near Support: Near support ₹2,445.00 (+0.20% away)
✅ RSI Oversold: RSI VERY OVERSOLD (28.5)
✅ Pattern: Hammer detected

⏰ 2025-11-14 10:30:00
```

### Hybrid Signal:
```
💎 TREASURE SIGNAL 💎

📊 TCS
🎯 Confidence: 78.5%
📊 Signal: BUY

💰 Trade Setup:
Entry: ₹4,250.00
Target: ₹4,450.00
Stop Loss: ₹4,100.00
R:R Ratio: 1:2.67

📈 3-Layer Analysis:
Technical: 75%
S&R: 80%
Pattern: 85%

⏰ 2025-11-14 10:30:00
```

## 🛑 Stop Monitoring

Press `Ctrl+C` in the terminal to stop.

## 📝 Notes

- **EOD Data Only:** Uses completed candles (excludes today's incomplete candle)
- **No Duplicates:** Each signal sent only once
- **Error Handling:** Continues running even if individual stocks fail
- **Logging:** Shows progress in terminal

## 🔧 Troubleshooting

**No signals sent?**
- Check Telegram bot token and chat ID
- Verify stocks are in the selected universe
- Check confidence thresholds (may be too high)

**Too many signals?**
- Increase `MIN_CONFIDENCE_JASMINES` or `MIN_CONFIDENCE_HYBRID`
- Change `STOCK_UNIVERSE` to smaller list (e.g., "Nifty 50")

**Rate limiting errors?**
- Increase `RUN_INTERVAL_MINUTES` to 10 or 15
- Reduce number of stocks per run

## ✅ Recommended Settings

```python
RUN_INTERVAL_MINUTES = 5  # Perfect balance
STOCK_UNIVERSE = "Nifty 50"  # Start small, expand later
MIN_CONFIDENCE_JASMINES = 75.0  # High quality only
MIN_CONFIDENCE_HYBRID = 75.0  # Treasure signals only
```

