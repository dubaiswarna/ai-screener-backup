@echo off
echo ============================================================
echo 💰 P&L TRACKER - Using YOUR Local Historical Data
echo ============================================================
echo.
echo Using your 169 CSV files with 30 years of data!
echo Works ANYTIME - No internet needed!
echo.

cd /d "%~dp0"
cd ai_screener

echo 🚀 Launching P&L tracker...
echo.
echo Access at: http://localhost:8505
echo.

"..\..\venv\Scripts\python.exe" -m streamlit run pnl_tracker_local_data.py --server.port 8505

pause

