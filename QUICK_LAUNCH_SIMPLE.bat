@echo off
echo ============================================================
echo SIMPLE LAUNCH - AI SCREENER (No Database Setup Required)
echo ============================================================
echo.
echo This version uses SQLite (no PostgreSQL needed)
echo All features work, signals persist!
echo.

cd /d "%~dp0"

REM Install minimal requirements
echo Installing required packages...
python -m pip install --user streamlit pandas plotly yfinance dhanhq python-dotenv --quiet

echo.
echo ✅ Packages installed!
echo.

REM Set environment to use SQLite
set USE_POSTGRESQL=false

REM Launch Streamlit
echo 🚀 Starting dashboard...
echo.
python -m streamlit run enhanced_screener.py --server.port 8501

pause

