@echo off
echo ============================================================
echo MCX AUTO-ALERT SCHEDULER
echo ============================================================
echo.
echo This will send Telegram alerts automatically at:
echo   - 09:15 AM (Market Open)
echo   - 12:00 PM (Mid-day)
echo   - 03:30 PM (Market Close)
echo   - Every 2 hours
echo.
echo Keep this window open for automated alerts!
echo Press Ctrl+C to stop
echo.
echo ============================================================
echo.

cd /d "%~dp0"

"..\venv\Scripts\python.exe" auto_mcx_alerts.py

pause

