@echo off
echo ============================================================
echo CRYPTO AI SYSTEM - COMPLETE SETUP
echo ============================================================
echo.
echo This will:
echo   1. Fetch crypto data (8 cryptocurrencies)
echo   2. Train AI models for all cryptos
echo   3. Open dashboard
echo   4. Send Telegram alert
echo.
echo Total time: 10-15 minutes
echo.
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/4] Fetching crypto data...
echo.
"..\venv\Scripts\python.exe" fetch_crypto_data.py

echo.
echo.
echo [2/4] Training AI models (this takes 5-8 minutes)...
echo.
"..\venv\Scripts\python.exe" train_all_crypto.py

echo.
echo.
echo [3/4] Opening dashboard...
echo.
"..\venv\Scripts\python.exe" crypto_dashboard.py

echo.
echo.
echo [4/4] Sending Telegram alerts...
echo.
"..\venv\Scripts\python.exe" send_crypto_alerts.py

echo.
echo ============================================================
echo CRYPTO AI SYSTEM READY!
echo ============================================================
echo.
pause

