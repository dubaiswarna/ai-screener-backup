@echo off
title AI Screener Dashboard Launcher
color 0A

echo.
echo ============================================================
echo    LAUNCHING AI SCREENER DASHBOARD
echo ============================================================
echo.
echo Please wait while the dashboard starts...
echo.

cd /d "%~dp0"

echo [1/3] Checking Python...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo [2/3] Checking Streamlit...
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Streamlit not installed!
    echo Installing Streamlit...
    pip install streamlit plotly pandas numpy scipy python-dotenv dhanhq
)

echo.
echo [3/3] Starting Dashboard...
echo.
echo ============================================================
echo    Dashboard will open at: http://localhost:8501
echo ============================================================
echo.
echo Press Ctrl+C to stop the server
echo.

python -m streamlit run enhanced_screener.py

echo.
echo ============================================================
echo    Dashboard stopped
echo ============================================================
pause
