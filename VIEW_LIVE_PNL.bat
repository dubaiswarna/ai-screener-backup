@echo off
echo ============================================================
echo 📈 LIVE P&L TRACKER
echo ============================================================
echo.
echo Track profit/loss for your AI signals in real-time!
echo.

cd /d "%~dp0"
cd ai_screener

echo 🚀 Launching P&L tracker...
echo.
echo Access at: http://localhost:8502
echo.

"..\..\venv\Scripts\streamlit.exe" run live_pnl_tracker.py --server.port 8502

pause

