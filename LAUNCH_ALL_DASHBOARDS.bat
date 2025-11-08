@echo off
echo ============================================================
echo   🌟 COMPLETE AI TRADING SYSTEM - ALL MARKETS LAUNCHER
echo ============================================================
echo.
echo Starting ALL trading dashboards simultaneously:
echo.
echo   📊 NSE STOCKS        - Port 8501
echo   🥇 MCX COMMODITIES   - Port 8503  
echo   🪙 CRYPTOCURRENCIES  - Port 8504
echo   💱 FOREX TRADING     - Port 8502
echo   🌟 MASTER DASHBOARD  - Port 8500
echo.
echo ============================================================
echo.

cd /d "%~dp0"

:: Check if venv exists
if not exist "..\venv\Scripts\streamlit.exe" (
    echo ERROR: Virtual environment not found!
    echo Please ensure venv is created at: ..\venv
    pause
    exit /b 1
)

echo [1/5] Starting NSE Stock Screener on port 8501...
start "NSE Stocks Dashboard" cmd /k "cd /d "%~dp0" && "..\venv\Scripts\streamlit.exe" run ai_screener\screener_app_pro.py --server.port 8501"
timeout /t 3 /nobreak >nul

echo [2/5] Starting MCX Commodities Dashboard on port 8503...
start "MCX Commodities Dashboard" cmd /k "cd /d "%~dp0" && "..\venv\Scripts\streamlit.exe" run ai_powered_dashboard.py --server.port 8503"
timeout /t 3 /nobreak >nul

echo [3/5] Starting Cryptocurrency Dashboard on port 8504...
start "Crypto Dashboard" cmd /k "cd /d "%~dp0" && "..\venv\Scripts\streamlit.exe" run crypto_dashboard.py --server.port 8504"
timeout /t 3 /nobreak >nul

echo [4/5] Starting Forex Screener on port 8502...
start "Forex Trading Dashboard" cmd /k "cd /d "%~dp0\..\Forex_Screener" && "..\venv\Scripts\streamlit.exe" run forex_screener.py --server.port 8502"
timeout /t 3 /nobreak >nul

echo [5/5] Starting Master Unified Dashboard on port 8500...
start "Master Dashboard" cmd /k "cd /d "%~dp0" && "..\venv\Scripts\streamlit.exe" run master_unified_dashboard.py --server.port 8500"

echo.
echo ============================================================
echo   ✅ ALL DASHBOARDS LAUNCHED SUCCESSFULLY!
echo ============================================================
echo.
echo Access your dashboards at:
echo.
echo   🌟 MASTER DASHBOARD:  http://localhost:8500  [START HERE]
echo   📊 NSE Stocks:        http://localhost:8501
echo   💱 Forex Trading:     http://localhost:8502
echo   🥇 MCX Commodities:   http://localhost:8503
echo   🪙 Cryptocurrencies:  http://localhost:8504
echo.
echo ============================================================
echo.
echo 💡 TIP: Open Master Dashboard (Port 8500) first!
echo    It provides a unified view and links to all markets.
echo.
echo Press any key to open Master Dashboard in your browser...
pause >nul

:: Open master dashboard in default browser
start http://localhost:8500

echo.
echo All dashboards are running in separate windows.
echo Close the individual windows to stop each dashboard.
echo.
pause

