@echo off
echo ============================================================
echo LAUNCHING MCX COMMODITY DASHBOARD
echo ============================================================
echo.

cd /d "%~dp0"

echo Starting Streamlit dashboard...
echo Dashboard will open in your browser automatically.
echo.
echo Press Ctrl+C to stop the dashboard.
echo.

"..\venv\Scripts\streamlit.exe" run commodity_dashboard.py

pause

