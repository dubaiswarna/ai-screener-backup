@echo off
echo ============================================================
echo 🚀 PROFESSIONAL AI SCREENER v3.0
echo ============================================================
echo.
echo Starting Professional AI Trading System...
echo.

cd /d "%~dp0"

REM Check if PostgreSQL is running
echo 📊 Checking PostgreSQL...
net start | find "postgresql" >nul
if %errorlevel% == 0 (
    echo ✅ PostgreSQL is running
) else (
    echo ⚠️ PostgreSQL not running, attempting to start...
    net start postgresql-x64-15 2>nul
    if %errorlevel% == 0 (
        echo ✅ PostgreSQL started successfully
    ) else (
        echo ⚠️ Could not start PostgreSQL automatically
        echo    Please start it manually or use Paper Trading mode
        timeout /t 3
    )
)

echo.
echo ============================================================
echo 🔌 LAUNCHING SERVICES
echo ============================================================
echo.

REM Start FastAPI Backend
echo 📡 Starting API Server (Port 8000)...
start "AI Screener API" cmd /k "cd /d "%~dp0" && ..\venv\Scripts\python.exe api_server.py"
timeout /t 3

REM Start Enhanced Streamlit Dashboard
echo 📊 Starting Enhanced Dashboard (Port 8501)...
start "AI Screener Dashboard" cmd /k "cd /d "%~dp0" && ..\venv\Scripts\streamlit.exe run enhanced_screener.py --server.port 8501"
timeout /t 5

echo.
echo ============================================================
echo ✅ SYSTEM LAUNCHED SUCCESSFULLY!
echo ============================================================
echo.
echo 📊 Enhanced Dashboard: http://localhost:8501
echo 📡 API Documentation: http://localhost:8000/docs
echo 💚 Health Check: http://localhost:8000/health
echo.
echo ⚡ Features Available:
echo   ✅ Database Persistence (No signal loss!)
echo   ✅ Real-time Broker Data
echo   ✅ Risk Management Engine
echo   ✅ Portfolio Tracking
echo   ✅ Trade History
echo   ✅ REST API
echo.
echo Press any key to open dashboard in browser...
pause >nul

REM Open browser
start http://localhost:8501

echo.
echo System is running! Close this window to stop.
echo ============================================================
pause

