# 📱 TELEGRAM ALERTS - QUICK SETUP

## Step 1: Create Bot (2 minutes)

1. Open Telegram
2. Search: `@BotFather`
3. Send: `/newbot`
4. Name: "AI Trading Bot"
5. Username: `my_ai_trading_bot`
6. **COPY TOKEN:** `123456789:ABCdefGHI...`

## Step 2: Get Chat ID (1 minute)

1. Send "Hello" to your bot
2. Open browser:
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
   ```
3. Find: `"chat":{"id":123456789`
4. **COPY CHAT ID:** `123456789`

## Step 3: Configure (2 minutes)

Edit: `C:\python\MG AI\AI_Screener_Complete\ai_screener\alert_config.json`

```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "123456789:ABCdefGHI...",
    "chat_ids": ["123456789"]
  }
}
```

## Step 4: Install Telegram Library

```bash
pip install requests
```

## Step 5: Test

```bash
cd "C:\python\MG AI\AI_Screener_Complete\ai_screener"
python alert_system.py
```

## Done! 🎉

You'll now get instant Telegram notifications when signals appear!

