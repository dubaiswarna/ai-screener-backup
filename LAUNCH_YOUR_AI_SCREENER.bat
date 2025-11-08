@echo off
echo ============================================================
echo YOUR AI STOCK SCREENER + PROFESSIONAL FEATURES
echo ============================================================
echo.
echo Starting your AI screener with:
echo   ✅ YOUR 50+ trained AI models
echo   ✅ Database persistence (signals never lost!)
echo   ✅ Risk management (Kelly Criterion, VaR)
echo   ✅ Dhan API integration (ready)
echo.

cd /d "%~dp0"
cd ai_screener

REM Initialize SQLite database
echo Initializing database...
python ..\init_sqlite.py

echo.
echo 🚀 Launching AI screener...
echo.

REM Launch with venv streamlit
"..\..\venv\Scripts\streamlit.exe" run screener_app_enhanced.py --server.port 8501

pause

