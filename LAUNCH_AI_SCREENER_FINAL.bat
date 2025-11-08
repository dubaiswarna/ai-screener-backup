@echo off
echo ============================================================
echo AI STOCK SCREENER - YOUR 42 AI MODELS
echo ============================================================
echo.
echo Starting your professional AI screener...
echo.
echo Features:
echo   ✅ YOUR 42 trained AI models
echo   ✅ Database persistence (signals saved forever!)
echo   ✅ Risk management (auto position sizing)
echo   ✅ Clean, simple interface
echo.

cd /d "%~dp0"
cd ai_screener

echo Initializing database...
python ..\init_sqlite.py >nul 2>&1

echo.
echo 🚀 Launching AI Screener at http://localhost:8501
echo.

"..\..\venv\Scripts\streamlit.exe" run screener_app_final.py --server.port 8501

pause

