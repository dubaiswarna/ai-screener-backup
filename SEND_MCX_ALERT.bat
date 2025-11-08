@echo off
echo ============================================================
echo MCX COMMODITY TELEGRAM ALERT
echo ============================================================
echo.

cd /d "%~dp0"

echo Sending AI predictions to your Telegram...
echo.

"..\venv\Scripts\python.exe" send_mcx_alerts.py

echo.
pause

