@echo off
echo ============================================================
echo MASTER AI TRADING DASHBOARD
echo ============================================================
echo.
echo Opening unified view of ALL markets:
echo   - NSE Stocks
echo   - MCX Commodities  
echo   - Cryptocurrencies
echo.

cd /d "%~dp0"

"..\venv\Scripts\python.exe" generate_master_dashboard.py

pause

