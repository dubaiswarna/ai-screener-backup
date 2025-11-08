@echo off
echo ============================================================
echo MASTER UNIFIED AI TRADING DASHBOARD
echo ============================================================
echo.
echo Opening unified dashboard for ALL markets:
echo   - NSE Stocks (42 models)
echo   - MCX Commodities (Gold, Silver)
echo   - Cryptocurrencies (8 coins)
echo.
echo Dashboard will open at: http://localhost:8500
echo.

cd /d "%~dp0"

"..\venv\Scripts\streamlit.exe" run master_unified_dashboard.py --server.port 8500

pause

