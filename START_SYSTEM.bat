@echo off
echo ============================================================
echo PROFESSIONAL AI SCREENER v3.0
echo ============================================================
echo.
echo Starting system...
echo.
cd /d "%~dp0"

REM Start Streamlit Dashboard
start "AI Screener Dashboard" ..\venv\Scripts\streamlit.exe run enhanced_screener.py --server.port 8501

timeout /t 5

echo ✅ Dashboard starting at: http://localhost:8501
echo.
echo Press any key to open browser...
pause >nul
start http://localhost:8501

echo System is running!
echo Close this window to stop the system.
pause
