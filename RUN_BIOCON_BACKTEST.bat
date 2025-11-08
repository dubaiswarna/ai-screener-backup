@echo off
echo ============================================================
echo   📊 BIOCON AI BACKTEST - Oct 3, 2024 to Oct 3, 2025
echo ============================================================
echo.
echo Using pre-trained AI model - FAST execution!
echo Estimated time: 30 seconds
echo.
echo ============================================================

cd /d "%~dp0"

"..\venv\Scripts\python.exe" backtest_biocon.py

echo.
pause

