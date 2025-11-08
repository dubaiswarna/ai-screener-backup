@echo off
echo ============================================================
echo   📊 NSE AI SCREENER - Updated Design
echo ============================================================
echo.
echo Starting with yesterday's clean table design...
echo Port: 8501
echo.
echo ============================================================

cd /d "%~dp0\ai_screener"

echo Loading 42 AI models...
echo.

"..\..\venv\Scripts\streamlit.exe" run screener_app.py --server.port 8501

pause

