@echo off
REM Launch Support & Resistance Analyzer
REM Port: 8503

echo.
echo ============================================================
echo    SUPPORT ^& RESISTANCE ANALYZER
echo ============================================================
echo.
echo Starting on http://localhost:8503
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Activate virtual environment
call "%~dp0..\venv\Scripts\activate.bat"

REM Go to support_resistance folder
cd /d "%~dp0support_resistance"

REM Launch Streamlit
streamlit run sr_viewer.py --server.port 8503

pause

