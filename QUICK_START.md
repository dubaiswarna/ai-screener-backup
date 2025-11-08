# 🚀 QUICK START GUIDE

## ⚡ FASTEST WAY TO START TRADING

### **Step 1: Launch ALL Dashboards at Once (RECOMMENDED)**

Simply run this batch file:

```bash
LAUNCH_ALL_DASHBOARDS.bat
```

**This will automatically open:**
- 🌟 Master Dashboard (Port 8500)
- 📊 NSE Stocks (Port 8501)
- 💱 Forex Trading (Port 8502)
- 🥇 MCX Commodities (Port 8503)
- 🪙 Crypto/Bitcoin (Port 8504)

### **Step 2: Access Your Dashboards**

Once launched, the Master Dashboard will auto-open in your browser.

**Click these links to open each market:**

- 🌟 [Master Dashboard](http://localhost:8500) ⭐ **Command Center**
- 📊 [NSE Stocks](http://localhost:8501)
- 💱 [Forex Trading](http://localhost:8502)
- 🥇 [MCX Commodities](http://localhost:8503)
- 🪙 [Crypto/Bitcoin](http://localhost:8504)

---

## 📍 ALTERNATIVE: Launch Individual Markets

If you only want specific markets:

### **For NSE Stocks:**
```bash
LAUNCH_PRO_SCREENER.bat
```
Opens at: http://localhost:8501

### **For Forex Trading:**
```bash
LAUNCH_FOREX_SCREENER.bat
```
Opens at: http://localhost:8502

### **For MCX Commodities:**
```bash
launch_dashboard.bat
```
Opens at: http://localhost:8503

### **For Crypto/Bitcoin:**
```bash
LAUNCH_CRYPTO_BITCOIN.bat
```
Opens at: http://localhost:8504

### **For Master Dashboard Only:**
```bash
LAUNCH_MASTER_DASHBOARD.bat
```
Opens at: http://localhost:8500

---

## 💡 IMPORTANT TIPS

### **Using the Master Dashboard Buttons:**

1. The Master Dashboard shows all markets
2. Click any "🚀 OPEN" button
3. You'll see a clickable link (🔗)
4. **BUT:** That market must be running first!

### **Best Workflow:**

**Option A: All Markets (Multi-Screen Trading)**
1. Run `LAUNCH_ALL_DASHBOARDS.bat`
2. Wait 15-20 seconds for all to load
3. Click the links or use the Master Dashboard buttons
4. Arrange windows on multiple monitors

**Option B: Master + Specific Markets**
1. Run `LAUNCH_MASTER_DASHBOARD.bat`
2. Run the specific market launchers you want
3. Use the Master Dashboard to navigate between them

---

## 🎯 FOR BEGINNERS

**Recommended Starting Sequence:**

### **Day 1-3: Single Market**
```bash
LAUNCH_FOREX_SCREENER.bat
```
- Start with USD/INR (96.2% accuracy!)
- Take only 80%+ confidence signals
- Learn the interface

### **Week 2: Add More Markets**
```bash
LAUNCH_ALL_DASHBOARDS.bat
```
- Add NSE stocks
- Add Bitcoin
- Diversify your trading

---

## ⚠️ TROUBLESHOOTING

### **Problem: "Dashboard won't load"**

**Solution:**
1. Make sure virtual environment is activated:
   ```bash
   cd "C:\python\MG AI"
   .\venv\Scripts\activate.bat
   ```

2. Check if port is already in use
3. Close other Streamlit instances
4. Restart the launcher

### **Problem: "Can't click links in Master Dashboard"**

**Solution:**
- The target dashboard must be running first!
- Run `LAUNCH_ALL_DASHBOARDS.bat` to start everything
- Or run individual launchers before using Master Dashboard

### **Problem: "Forex/Crypto not found"**

**Solution:**
- Make sure `Forex_Screener` folder exists
- Check that models are in `Forex_Screener/models/`
- Verify you extracted the complete system

---

## 🎊 YOU'RE READY!

### **RECOMMENDED COMMAND:**

```bash
LAUNCH_ALL_DASHBOARDS.bat
```

This launches everything in one go!

### **Then visit:**

🌐 **http://localhost:8500** (Master Dashboard)

---

**Happy Trading! 📈💰🚀**

