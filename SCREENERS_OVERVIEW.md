# 📊 AI Screener Project - Complete Screener List

## Overview

This project contains **multiple screeners** for different markets and use cases. Here's a complete breakdown:

---

## 🎯 MAIN AI STOCK SCREENERS (NSE Stocks)

### 1. **Professional Screener** ⭐ (Recommended)
- **File:** `ai_screener/screener_app_pro.py`
- **Launch:** `LAUNCH_PRO_SCREENER.bat`
- **Port:** 8501
- **Features:**
  - 42+ trained AI models
  - Database persistence
  - Portfolio tracking
  - Risk management
  - Alert system
  - Professional UI

### 2. **Enhanced Screener**
- **File:** `enhanced_screener.py`
- **Launch:** `QUICK_LAUNCH_SIMPLE.bat` or `OPEN_DASHBOARD.bat`
- **Port:** 8501
- **Features:**
  - SQLite/PostgreSQL support
  - Signal generation
  - Risk calculations

### 3. **Original Screener**
- **File:** `ai_screener/screener_app.py`
- **Launch:** Manual `streamlit run ai_screener/screener_app.py`
- **Features:**
  - Basic AI screening
  - Model predictions
  - Signal display

### 4. **Enhanced Version**
- **File:** `ai_screener/screener_app_enhanced.py`
- **Features:**
  - Enhanced UI
  - Additional features

### 5. **Final Version**
- **File:** `ai_screener/screener_app_final.py`
- **Features:**
  - Finalized features

### 6. **Auto-Execute Screener**
- **File:** `ai_screener/screener_auto_execute.py`
- **Launch:** `LAUNCH_AUTO_EXECUTE.bat`
- **Features:**
  - Automatic signal execution
  - Auto-trading capabilities

### 7. **Web Screener**
- **File:** `web_screener.py`
- **Launch:** `launch_web_screener.bat`
- **Features:**
  - Web-based interface
  - HTML output

### 8. **Daily Screener**
- **File:** `daily_screener.py`
- **Features:**
  - Daily screening reports
  - Excel export
  - Batch processing

### 9. **Daily Screener HTML**
- **File:** `daily_screener_html.py`
- **Features:**
  - HTML report generation
  - Visual reports

### 10. **Screener with Charts**
- **File:** `screener_with_charts.py`
- **Features:**
  - Chart visualization
  - Technical analysis

### 11. **Three Jasmines Screener**
- **File:** `three_jasmines_screener.py`
- **Features:**
  - Three Jasmines strategy
  - Pattern detection

### 12. **June 2025 Test Screener**
- **File:** `ai_screener/screener_june2025_test.py`
- **Launch:** `RUN_JUNE2025_TEST.bat`
- **Port:** 8502
- **Features:**
  - Testing specific date range
  - Backtest validation

---

## 💱 MARKET-SPECIFIC SCREENERS

### 13. **Forex Screener**
- **Launch:** `LAUNCH_FOREX_SCREENER.bat`
- **Port:** 8502
- **Features:**
  - Forex pair analysis
  - USD/INR focus
  - Currency signals

### 14. **MCX Commodities Screener**
- **File:** `commodity_dashboard.py`
- **Launch:** `LAUNCH_COMMODITY_DASHBOARD.bat` or `launch_dashboard.bat`
- **Port:** 8503
- **Features:**
  - Commodity analysis
  - MCX market data
  - Metal/energy screening

### 15. **Crypto/Bitcoin Screener**
- **File:** `crypto_dashboard.py`
- **Launch:** `LAUNCH_CRYPTO_BITCOIN.bat` or `LAUNCH_CRYPTO_DASHBOARD.bat`
- **Port:** 8504
- **Features:**
  - Cryptocurrency analysis
  - Bitcoin focus
  - Crypto signals

---

## 📊 DASHBOARDS & ANALYZERS

### 16. **Master Dashboard**
- **File:** `master_unified_dashboard.py`
- **Launch:** `LAUNCH_MASTER_DASHBOARD.bat` or `LAUNCH_ALL_DASHBOARDS.bat`
- **Port:** 8500
- **Features:**
  - Central command center
  - Links to all screeners
  - Market overview

### 17. **Support & Resistance Analyzer**
- **File:** `support_resistance/sr_viewer.py`
- **Launch:** `LAUNCH_SR_ANALYZER.bat`
- **Port:** 8503
- **Features:**
  - S/R level detection
  - Chart analysis
  - Level visualization

### 18. **Backtest Dashboard**
- **File:** `backtest_system/backtest_dashboard.py`
- **Launch:** `LAUNCH_BACKTEST_DASHBOARD.bat`
- **Port:** 8502
- **Features:**
  - Historical backtesting
  - Performance analysis
  - Strategy testing

### 19. **Hybrid Backtest Dashboard**
- **File:** `backtest_system/backtest_dashboard_hybrid.py`
- **Launch:** `LAUNCH_HYBRID_DASHBOARD.bat`
- **Port:** 8503
- **Features:**
  - AI + Technical hybrid
  - Combined strategies

### 20. **Multi-Mode Backtest Dashboard**
- **File:** `backtest_system/backtest_dashboard_multimode.py`
- **Launch:** `LAUNCH_MULTIMODE_DASHBOARD.bat`
- **Port:** 8504
- **Features:**
  - Multiple modes
  - Toggle between strategies

### 21. **AI Powered Dashboard**
- **File:** `ai_powered_dashboard.py`
- **Features:**
  - AI predictions
  - Live data

### 22. **Advanced Commodity Analysis**
- **File:** `advanced_commodity_analysis.py`
- **Features:**
  - Advanced commodity features
  - Deep analysis

---

## 🌐 NEXT.JS FRONTEND (NEW)

### 23. **Next.js Frontend** ⭐ (Latest)
- **Location:** `frontend/`
- **Port:** 3002
- **Launch:** `OPEN_FRONTEND.bat` or `npm run dev` in frontend folder
- **Features:**
  - Modern React UI
  - Dashboard page
  - Signals page
  - Portfolio page
  - Trades page
  - Risk Report page
  - Settings page
  - Connects to FastAPI backend

---

## 📈 SUMMARY

### Total Screeners: **23+**

**Breakdown:**
- **Main AI Stock Screeners:** 12
- **Market-Specific Screeners:** 3 (Forex, Commodities, Crypto)
- **Dashboards & Analyzers:** 7
- **Next.js Frontend:** 1

### Recommended Usage:

1. **For NSE Stocks:** `LAUNCH_PRO_SCREENER.bat` (Port 8501)
2. **For All Markets:** `LAUNCH_ALL_DASHBOARDS.bat` (Multiple ports)
3. **For Modern UI:** Next.js Frontend (Port 3002) + Backend API (Port 8000)

### Port Assignments:

- **8500** - Master Dashboard
- **8501** - NSE Stock Screener (Pro)
- **8502** - Forex Screener / Backtest Dashboard
- **8503** - MCX Commodities / S&R Analyzer / Hybrid Backtest
- **8504** - Crypto / Multi-Mode Backtest
- **8000** - FastAPI Backend
- **3002** - Next.js Frontend

---

## 🚀 Quick Access

**Most Used:**
- `LAUNCH_PRO_SCREENER.bat` - Professional NSE screener
- `LAUNCH_ALL_DASHBOARDS.bat` - All markets at once
- `OPEN_BOTH.bat` - Backend + Frontend (Next.js)

**For Development:**
- Next.js Frontend: `cd frontend && npm run dev`
- Backend API: `python api_server.py`

