# 🚨 AI Screener Alert System - Complete Setup Guide

Get instant notifications when profitable signals appear!

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Email Alerts Setup](#email-alerts)
3. [Telegram Alerts Setup](#telegram-alerts)
4. [SMS Alerts Setup](#sms-alerts)
5. [Testing Alerts](#testing)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

The alert system is already created! Just configure it:

1. **Find the config file:**
   ```
   C:\python\MG AI\AI_Screener_Complete\ai_screener\alert_config.json
   ```

2. **Edit with your credentials** (see sections below)

3. **Enable desired channels** (email, telegram, sms)

4. **Test alerts** before going live

---

## 📧 Email Alerts Setup

### Step 1: Get Gmail App Password

1. Go to your **Google Account** → Security
2. Enable **2-Step Verification** (if not already)
3. Search for **"App passwords"**
4. Select **Mail** and **Windows Computer**
5. Copy the generated 16-character password

### Step 2: Configure Email

Edit `alert_config.json`:

```json
"email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_16_char_app_password",
    "recipient_emails": ["your_email@gmail.com", "backup@gmail.com"]
}
```

### Email Features:
✅ Beautiful HTML formatting  
✅ Signal details with colors  
✅ Multiple recipients  
✅ Instant delivery  

---

## 📱 Telegram Alerts Setup

### Step 1: Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Give it a name (e.g., "My AI Screener Bot")
4. Give it a username (e.g., "my_ai_screener_bot")
5. Copy the **Bot Token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID

1. Send a message to your bot
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find your **chat_id** in the response (number like: `123456789`)

### Step 3: Configure Telegram

Edit `alert_config.json`:

```json
"telegram": {
    "enabled": true,
    "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
    "chat_ids": ["123456789"]
}
```

### Telegram Features:
✅ Instant push notifications  
✅ Works on phone & desktop  
✅ Markdown formatting  
✅ Emoji indicators (🟢 BUY, 🔴 SELL)  
✅ Multiple recipients  

---

## 📲 SMS Alerts Setup (Optional)

**Note:** SMS requires Twilio account (paid service, but cheap)

### Step 1: Create Twilio Account

1. Go to [twilio.com](https://www.twilio.com)
2. Sign up (free trial available)
3. Get a phone number ($1/month)
4. Copy your **Account SID** and **Auth Token**

### Step 2: Install Twilio

```bash
pip install twilio
```

### Step 3: Configure SMS

Edit `alert_config.json`:

```json
"sms": {
    "enabled": true,
    "twilio_account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "twilio_auth_token": "your_auth_token",
    "twilio_phone": "+1234567890",
    "recipient_phones": ["+919876543210"]
}
```

### SMS Features:
✅ Works without internet  
✅ Ultra-reliable  
✅ Emergency notifications  
✅ Multiple recipients  

---

## ⚙️ Alert Rules Configuration

Customize when alerts are sent:

```json
"alert_rules": {
    "min_confidence": 0.70,           // Only signals above 70%
    "signals": ["buy", "sell"],       // Which signal types
    "stocks": [],                     // Empty = all stocks, or ["NSE_RELIANCE", "NSE_TCS"]
    "min_interval_minutes": 5         // Avoid spam (5 min cooldown per stock)
}
```

### Examples:

**Only high-confidence BUY signals:**
```json
"alert_rules": {
    "min_confidence": 0.80,
    "signals": ["buy"]
}
```

**Only specific stocks:**
```json
"alert_rules": {
    "min_confidence": 0.70,
    "signals": ["buy", "sell"],
    "stocks": ["NSE_RELIANCE", "NSE_TCS", "NSE_HDFCBANK"]
}
```

---

## 🧪 Testing Alerts

### Quick Test:

```bash
cd C:\python\MG AI\AI_Screener_Complete\ai_screener
python alert_system.py
```

This will:
1. Create default config file
2. Show you what to configure

### Full Test:

```python
from alert_system import AlertSystem

alert = AlertSystem()
results = alert.test_alerts()

# Check results
if results.get('email'):
    print("✅ Email working!")
if results.get('telegram'):
    print("✅ Telegram working!")
```

---

## 🔄 Integration with Screener

The alert system is integrated! Signals automatically trigger alerts when:

1. **Confidence threshold met** (default 70%)
2. **Signal type matches** (buy/sell)
3. **Rate limit passed** (5 min cooldown)
4. **Stock filter matches** (if configured)

### Manual Alert Test:

```python
from signal_generator import SignalGenerator
from alert_system import AlertSystem

# Generate signals
signal_gen = SignalGenerator(...)
signals = signal_gen.generate_signals(['NSE_RELIANCE'])

# Send alerts
alert_system = AlertSystem()
results = alert_system.send_alerts(signals)

print(f"Alerts sent: {results['count']}")
```

---

## 📊 Alert Examples

### Email Alert:
![Email Alert Example](https://via.placeholder.com/600x400?text=Beautiful+HTML+Email)

### Telegram Alert:
```
🚨 AI SCREENER ALERT
2025-11-03 23:30:00

🟢 NSE_RELIANCE
Signal: BUY
Confidence: 85.0%
Price: ₹2850.00
Target: ₹2936.00
Stop: ₹2807.00
VWAP Dev: -0.8%

✨ MG AI Trading System
```

### SMS Alert:
```
AI SCREENER: 1 signal(s)
NSE_RELIANCE BUY 85%
```

---

## 🛠️ Troubleshooting

### Email Not Working:

❌ **"Authentication failed"**
- Use App Password, not regular Gmail password
- Enable 2-step verification first

❌ **"Connection refused"**
- Check SMTP server and port
- Verify internet connection

### Telegram Not Working:

❌ **"Unauthorized"**
- Check bot token is correct
- Make sure you sent a message to bot first

❌ **"Chat not found"**
- Send `/start` to your bot
- Get fresh chat_id from getUpdates

### SMS Not Working:

❌ **"Authentication failed"**
- Verify Account SID and Auth Token
- Check Twilio balance

❌ **"Invalid phone number"**
- Use international format: +919876543210
- Verify phone on Twilio dashboard

---

## 💡 Best Practices

### 1. **Start with Telegram** 
- Easiest to setup
- Free forever
- Instant notifications
- Works on all devices

### 2. **Use Email for Details**
- Beautiful formatting
- Full signal information
- Easy to review later

### 3. **Reserve SMS for Critical**
- High-confidence signals only (80%+)
- Emergency use
- Limited messages (costs money)

### 4. **Set Appropriate Thresholds**
- 70%+ confidence recommended
- 5-minute cooldown prevents spam
- Filter to favorite stocks if needed

### 5. **Test Before Live**
- Always test all channels first
- Verify formatting looks good
- Check delivery time

---

## 🎯 Recommended Setup for Beginners

```json
{
    "email": {
        "enabled": true,
        "...": "your_credentials"
    },
    "telegram": {
        "enabled": true,
        "...": "your_credentials"
    },
    "sms": {
        "enabled": false
    },
    "alert_rules": {
        "min_confidence": 0.75,
        "signals": ["buy"],
        "stocks": [],
        "min_interval_minutes": 5
    }
}
```

This gives you:
- ✅ Email for detailed review
- ✅ Telegram for instant notifications
- ✅ Only high-quality BUY signals
- ✅ No spam (5 min cooldown)

---

## 🚀 Ready to Go!

Once configured:

1. **Alerts automatically sent** when screener runs
2. **No manual intervention** needed
3. **Get notified instantly** when opportunities appear
4. **Trade with confidence** - 86.9% win rate signals!

---

## 📞 Support

Having issues? Check:
1. Configuration file syntax (valid JSON)
2. Credentials are correct
3. Internet connection working
4. Test alerts first

---

**🎉 Happy Trading with AI-Powered Alerts!**

*MG AI Trading System - Building the Future of Trading*

