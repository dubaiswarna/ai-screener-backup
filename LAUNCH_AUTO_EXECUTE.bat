@echo off
echo ============================================================
echo ⚡ AI SCREENER - AUTO EXECUTE MODE
echo ============================================================
echo.
echo FULLY AUTOMATED MODE:
echo   ✅ AI generates signals
echo   ✅ Auto-executes high-confidence signals
echo   ✅ Saves to database automatically
echo   ✅ No manual clicking needed!
echo.
echo Perfect for TESTING and AUTOMATION!
echo.

cd /d "%~dp0"
cd ai_screener

echo Initializing database...
python ..\init_sqlite.py >nul 2>&1

echo.
echo ⚡ Launching AUTO-EXECUTE mode...
echo.
echo Access at: http://localhost:8501
echo.

"..\..\venv\Scripts\streamlit.exe" run screener_auto_execute.py --server.port 8501

pause

