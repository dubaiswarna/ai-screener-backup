@echo off
echo ============================================================
echo CRYPTO AI TRADING DASHBOARD
echo ============================================================
echo.

cd /d "%~dp0"

"..\venv\Scripts\python.exe" crypto_dashboard.py

pause

