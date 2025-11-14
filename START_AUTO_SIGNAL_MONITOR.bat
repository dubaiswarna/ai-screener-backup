@echo off
echo ========================================
echo AUTO SIGNAL MONITOR - Starting...
echo ========================================
echo.
echo This will run 3Jasmines and Hybrid Signal Generator
echo every 5 minutes and send new signals to Telegram
echo.
echo Press Ctrl+C to stop
echo.
pause

cd /d "%~dp0"
python auto_signal_monitor.py

pause

