@echo off
echo ============================================================
echo ⚡ REAL-TIME P&L TRACKER
echo ============================================================
echo.
echo Track your AI signals with LIVE tick data from Dhan!
echo.
echo Features:
echo   ⚡ Live prices (^< 1 second delay)
echo   🔄 Auto-updates every 5 seconds
echo   💾 Saves P&L history automatically
echo   📊 All stocks visible in one table
echo   📈 Visual P&L chart
echo.

cd /d "%~dp0"
cd ai_screener

echo 🚀 Launching real-time P&L tracker...
echo.
echo Access at: http://localhost:8504
echo.

"..\..\venv\Scripts\python.exe" -m streamlit run realtime_pnl_tracker.py --server.port 8504

pause

