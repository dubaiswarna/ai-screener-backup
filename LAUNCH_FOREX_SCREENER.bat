@echo off
echo ============================================================
echo   💱 FOREX AI TRADING SCREENER
echo ============================================================
echo.
echo Currency Pairs Available:
echo   💱 EUR/USD - 73.9%% Accuracy
echo   💱 GBP/USD - 74.6%% Accuracy  
echo   💱 USD/INR - 96.2%% Accuracy (BEST!)
echo.
echo Dashboard will open at: http://localhost:8502
echo ============================================================
echo.

cd /d "%~dp0\..\Forex_Screener"

:: Check if venv exists
if not exist "..\venv\Scripts\streamlit.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

echo Starting Forex Screener...
echo.

"..\venv\Scripts\streamlit.exe" run forex_screener.py --server.port 8502

pause

