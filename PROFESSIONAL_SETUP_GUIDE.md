# 🚀 PROFESSIONAL AI SCREENER v3.0 - COMPLETE SETUP GUIDE

## 📋 **What's New in v3.0?**

### **Major Upgrades:**
1. ✅ **PostgreSQL Database** - Persistent signal storage (no data loss on refresh!)
2. ✅ **Risk Management Engine** - Kelly Criterion, VaR, drawdown tracking
3. ✅ **Broker API Integration** - Real-time data from Dhan/Zerodha/Upstox
4. ✅ **WebSocket Support** - Live price updates with zero delay
5. ✅ **Advanced Backtesting** - Walk-forward validation, Monte Carlo simulation
6. ✅ **Model Monitoring** - Track accuracy, detect drift, auto-retrain
7. ✅ **FastAPI Backend** - RESTful API for web/mobile apps
8. ✅ **Professional Architecture** - Production-ready, institutional-grade

---

## 🎯 **Architecture Overview**

```
┌─────────────────────────────────────────────────────┐
│         PROFESSIONAL AI SCREENER v3.0               │
└─────────────────────────────────────────────────────┘

DATA LAYER
├── Broker APIs (Dhan/Zerodha/Upstox) ──► Real-time data
├── Yahoo Finance ──► Historical data
└── PostgreSQL ──► Persistent storage

MODEL LAYER
├── XGBoost (50 models) ──► Current models
├── LSTM (Future) ──► Time-series patterns
└── Ensemble (Future) ──► Voting mechanism

RISK ENGINE
├── Position Sizing (Kelly Criterion)
├── Value at Risk (VaR 95%)
├── Drawdown Monitoring
└── Correlation Analysis

EXECUTION
├── Paper Trading ──► Current
├── Broker Integration ──► Ready to enable
└── Smart Order Router ──► Future

FRONTEND
├── Streamlit (Current) ──► 4 dashboards
├── FastAPI Backend ──► REST endpoints
└── React (Future) ──► Modern web UI
```

---

## 📥 **INSTALLATION STEPS**

### **Step 1: Install PostgreSQL**

#### **Windows:**
```bash
# Download PostgreSQL
# Visit: https://www.postgresql.org/download/windows/
# Install with default settings
# Remember your postgres password!

# Verify installation
psql --version
```

#### **Create Database:**
```bash
# Open Command Prompt as Administrator
psql -U postgres

# In psql shell:
CREATE DATABASE ai_screener_pro;
\q
```

#### **Initialize Schema:**
```bash
cd "C:\python\MG AI\AI_Screener_Complete"
psql -U postgres -d ai_screener_pro -f database_schema.sql
```

---

### **Step 2: Install Python Dependencies**

```bash
# Navigate to project directory
cd "C:\python\MG AI\AI_Screener_Complete"

# Activate virtual environment (if not already active)
..\venv\Scripts\activate

# Install new dependencies
pip install -r requirements_professional.txt

# Verify installation
python -c "import psycopg2; print('PostgreSQL: OK')"
python -c "import fastapi; print('FastAPI: OK')"
python -c "import websocket; print('WebSocket: OK')"
```

---

### **Step 3: Configure Database Connection**

#### **Option A: Environment Variables (Recommended)**

Create `.env` file in `AI_Screener_Complete/`:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_screener_pro
DB_USER=postgres
DB_PASSWORD=your_postgres_password
USE_POSTGRESQL=true

# Broker Configuration (Choose one)
# For Dhan (RECOMMENDED - FREE!)
DHAN_CLIENT_ID=your_client_id
DHAN_ACCESS_TOKEN=your_access_token

# For Zerodha (₹2000/month)
# ZERODHA_API_KEY=your_api_key
# ZERODHA_API_SECRET=your_api_secret
# ZERODHA_ACCESS_TOKEN=your_access_token

# Risk Management
TOTAL_CAPITAL=1000000  # ₹10 Lakh
MAX_RISK_PER_TRADE=2.0  # 2%
MAX_POSITIONS=10
```

#### **Option B: Direct Configuration**

Edit `config/db_config.py`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ai_screener_pro',
    'user': 'postgres',
    'password': 'your_password_here',  # Change this!
}
```

---

### **Step 4: Test Database Connection**

```bash
# Test database
python -c "from database.db_manager import get_db; db = get_db(); print('✅ Database OK' if db.test_connection() else '❌ Database Failed')"
```

---

## 🔌 **BROKER SETUP (Choose One)**

### **Option 1: Dhan (RECOMMENDED ⭐)**

**Why Dhan?**
- ✅ **FREE** API with trading account
- ✅ **1 YEAR** of historical 1-minute data
- ✅ Easy authentication (no daily token refresh)
- ✅ 500 API calls/minute
- ✅ WebSocket real-time data

**Setup:**
```bash
# 1. Open Dhan account: https://dhan.co
# 2. Go to Settings → API
# 3. Generate API credentials
# 4. Copy Client ID and Access Token

# 5. Add to .env file:
DHAN_CLIENT_ID=1234567890
DHAN_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# 6. Install Dhan SDK:
pip install dhanhq

# 7. Test connection:
python -c "from broker_integration.broker_client import get_broker_client; client = get_broker_client('dhan'); print('✅ Dhan Connected' if client.is_connected else '❌ Dhan Failed')"
```

---

### **Option 2: Paper Trading (FREE)**

**Perfect for testing without risk!**

```bash
# No setup needed - uses Yahoo Finance data
# Simulates real trading with ₹10 Lakh virtual capital

# Test paper trading:
python -c "from broker_integration.broker_client import get_broker_client; client = get_broker_client('paper'); print(client.get_portfolio_summary())"
```

---

### **Option 3: Zerodha Kite (₹2000/month)**

```bash
# 1. Visit: https://developers.kite.trade/
# 2. Create app, get API key & secret
# 3. Generate access token (daily!)

# Add to .env:
ZERODHA_API_KEY=your_api_key
ZERODHA_API_SECRET=your_api_secret
ZERODHA_ACCESS_TOKEN=your_access_token

# Install:
pip install kiteconnect
```

---

## 🚀 **LAUNCHING THE SYSTEM**

### **Method 1: Launch Everything (Recommended)**

Create `LAUNCH_PROFESSIONAL_SYSTEM.bat`:

```batch
@echo off
echo ============================================================
echo PROFESSIONAL AI SCREENER v3.0
echo ============================================================
echo.
echo Starting all services...
echo.

cd /d "%~dp0"

REM Start PostgreSQL (if not running)
net start postgresql-x64-15

REM Start FastAPI Backend
start "AI Screener API" cmd /k "..\venv\Scripts\python.exe api_server.py"
timeout /t 3

REM Start Streamlit Dashboard
start "AI Screener Dashboard" cmd /k "..\venv\Scripts\streamlit.exe run enhanced_screener.py --server.port 8501"

echo.
echo ✅ System launched!
echo.
echo 📊 Dashboard: http://localhost:8501
echo 🔌 API: http://localhost:8000/docs
echo.
pause
```

---

### **Method 2: Individual Components**

#### **Database Only:**
```bash
# Windows
net start postgresql-x64-15

# Check status
pg_ctl status
```

#### **API Server:**
```bash
cd AI_Screener_Complete
python api_server.py
# Access at: http://localhost:8000/docs
```

#### **Streamlit Dashboard:**
```bash
cd AI_Screener_Complete
streamlit run enhanced_screener.py --server.port 8501
# Access at: http://localhost:8501
```

---

## 🔧 **CONFIGURATION**

### **Risk Parameters**

Edit `user_config` table in database:

```sql
UPDATE user_config SET
    total_capital = 1000000,  -- ₹10 Lakh
    max_risk_per_trade = 2.0,  -- 2% per trade
    max_portfolio_risk = 10.0,  -- 10% total
    max_positions = 10,  -- Max 10 stocks
    min_confidence = 70.0,  -- Min 70% AI confidence
    min_risk_reward = 1.5  -- Min 1.5:1 R:R
WHERE config_id IS NOT NULL;
```

---

## 📊 **USING THE NEW FEATURES**

### **1. Persistent Signals (Solves Your Refresh Issue!)**

```python
from database.db_manager import get_db

db = get_db()

# Generate signal
signal_data = {
    'symbol': 'NSE_RELIANCE',
    'signal_type': 'BUY',
    'confidence': 85.5,
    'entry_price': 2450.00,
    'target_price': 2550.00,
    'stop_loss': 2400.00,
    # ... more fields
}

# Save to database
signal_id = db.save_signal(signal_data)

# Retrieve after refresh
active_signals = db.get_active_signals(min_confidence=75.0)
print(f"Found {len(active_signals)} active signals")
```

**Now when you refresh Streamlit, signals persist!** ✅

---

### **2. Risk Management**

```python
from risk_management.risk_engine import RiskEngine

engine = RiskEngine(total_capital=1000000)

# Calculate optimal position size
position = engine.calculate_position_size(
    entry_price=2450,
    stop_loss=2400,
    confidence=0.85
)

print(f"Quantity: {position['quantity']}")
print(f"Risk: ₹{position['risk_amount']} ({position['risk_pct']}%)")
```

---

### **3. Live Data with WebSocket**

```python
from broker_integration.broker_client import get_broker_client

# Connect to Dhan
client = get_broker_client('dhan')

# Define callback for price updates
def on_price_update(data):
    print(f"RELIANCE: ₹{data['ltp']}")

# Connect WebSocket
symbols = ['RELIANCE', 'TCS', 'INFY']
client.connect_websocket(symbols, on_price_update)

# Prices update in real-time! ✅
```

---

### **4. Historical 1-Minute Data**

```python
from datetime import datetime, timedelta
from broker_integration.broker_client import get_broker_client

client = get_broker_client('dhan')

# Get 1-minute data for last 30 days
df = client.get_historical_data(
    symbol='RELIANCE',
    from_date=datetime.now() - timedelta(days=30),
    to_date=datetime.now(),
    interval='1'  # 1-minute
)

print(f"Got {len(df)} 1-minute candles!")
# With Dhan: Up to 1 YEAR of 1-min data! 🎉
```

---

## 📱 **API ENDPOINTS (FastAPI)**

Once API server is running, access:

**Documentation:** http://localhost:8000/docs

**Key Endpoints:**
```
GET  /api/v1/signals          - Get active signals
POST /api/v1/signals          - Create new signal
GET  /api/v1/portfolio        - Get portfolio
GET  /api/v1/trades           - Get trade history
GET  /api/v1/risk/report      - Get risk report
POST /api/v1/orders           - Place order
GET  /api/v1/quotes/{symbol}  - Get live quote
```

**Example:**
```bash
# Get active signals
curl http://localhost:8000/api/v1/signals?min_confidence=75

# Place order
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"symbol":"RELIANCE","type":"BUY","quantity":10}'
```

---

## 🧪 **TESTING**

### **Test Database:**
```bash
cd AI_Screener_Complete
python database/db_manager.py
```

### **Test Risk Engine:**
```bash
python risk_management/risk_engine.py
```

### **Test Broker:**
```bash
python broker_integration/broker_client.py
```

### **Full System Test:**
```bash
python test_professional_system.py
```

Expected output:
```
✅ Database: Connected
✅ Risk Engine: Initialized
✅ Broker: Connected (Paper/Dhan)
✅ WebSocket: Ready
✅ API Server: Running
✅ All systems operational!
```

---

## 🐛 **TROUBLESHOOTING**

### **PostgreSQL not starting:**
```bash
# Windows
net start postgresql-x64-15

# Check if port 5432 is in use
netstat -ano | findstr :5432

# Restart service
net stop postgresql-x64-15
net start postgresql-x64-15
```

### **Database connection failed:**
```bash
# Verify credentials
psql -U postgres -d ai_screener_pro

# Test from Python
python -c "import psycopg2; conn = psycopg2.connect('dbname=ai_screener_pro user=postgres password=your_password'); print('OK')"
```

### **Dhan API not working:**
```bash
# Check credentials
python -c "import os; print(os.getenv('DHAN_CLIENT_ID')); print(os.getenv('DHAN_ACCESS_TOKEN'))"

# Test API
python broker_integration/broker_client.py
```

### **Signals not persisting:**
```sql
-- Check if signals table exists
SELECT COUNT(*) FROM signals;

-- Check recent signals
SELECT * FROM signals ORDER BY generated_at DESC LIMIT 10;
```

---

## 📈 **NEXT STEPS**

### **Phase 1: Start Trading**
1. ✅ Launch system
2. ✅ Generate signals
3. ✅ Review risk metrics
4. ✅ Execute trades (Paper or Live)

### **Phase 2: Monitor & Optimize**
1. Track model performance
2. Adjust risk parameters
3. Backtest strategies
4. Refine signals

### **Phase 3: Scale**
1. Add more models
2. Increase capital
3. Automate fully
4. Deploy to cloud

---

## 💡 **PRO TIPS**

1. **Start with Paper Trading** - Test strategies risk-free
2. **Use Dhan API** - Best value (free + 1 year 1-min data)
3. **Check Risk Report Daily** - Monitor VaR, drawdown, correlation
4. **Set Alerts** - Telegram for high-confidence signals
5. **Backtest First** - Validate before live trading
6. **Keep Records** - Database stores everything automatically
7. **Monitor Accuracy** - Track model performance weekly

---

## 🆘 **NEED HELP?**

Run diagnostic:
```bash
python diagnose_system.py
```

This will check:
- ✅ Database connection
- ✅ Broker authentication
- ✅ Model availability
- ✅ Risk engine
- ✅ API server
- ✅ All dependencies

---

## 🎉 **YOU NOW HAVE:**

✅ **Institutional-Grade AI Trading System**
✅ **Persistent Data Storage** (No signal loss!)
✅ **Professional Risk Management**
✅ **Real-Time Market Data**
✅ **Historical 1-Minute Data** (Up to 1 year!)
✅ **WebSocket Live Updates**
✅ **REST API** (For web/mobile apps)
✅ **Paper Trading** (Risk-free testing)
✅ **Production-Ready Architecture**

---

**Ready to trade like a pro!** 🚀💰📈

**Version:** 3.0
**Date:** November 5, 2025
**Status:** ✅ PRODUCTION-READY

