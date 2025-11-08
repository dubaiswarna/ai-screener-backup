@echo off
echo ============================================================
echo 🚀 QUICK START - SETUP DHAN API
echo ============================================================
echo.
echo This will help you setup Dhan API credentials
echo.
echo Prerequisites:
echo   1. Dhan trading account
echo   2. API enabled in Dhan app
echo   3. Client ID and Access Token ready
echo.
echo ============================================================
echo.

cd /d "%~dp0"

REM Activate virtual environment
call ..\venv\Scripts\activate.bat

REM Run setup script
python setup_dhan_credentials.py

echo.
echo ============================================================
pause

