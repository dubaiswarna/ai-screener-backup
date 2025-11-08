@echo off
echo ============================================================
echo 💰 LIVE P&L TRACKER
echo ============================================================
echo.
echo Track your AI-generated calls anytime!
echo.
echo Features:
echo   ✅ Shows all your signals
echo   ✅ Live price updates
echo   ✅ Real-time P&L calculation
echo   ✅ Saves P&L history
echo   ✅ Accessible anytime!
echo.

cd /d "%~dp0"
cd ai_screener

echo 🚀 Launching P&L tracker...
echo.

"..\..\venv\Scripts\python.exe" -m streamlit run simple_pnl_tracker.py --server.port 8503

pause

