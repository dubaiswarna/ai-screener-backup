@echo off
title Restart System with Updates
color 0C

echo ============================================================
echo  RESTARTING SYSTEM WITH UPDATES
echo ============================================================
echo.
echo This will:
echo 1. Kill any running Streamlit processes
echo 2. Clear Streamlit cache
echo 3. Restart the system with NEW changes
echo.
echo ============================================================
pause

cd /d "%~dp0"

echo.
echo [1/4] Stopping any running Streamlit...
taskkill /F /IM streamlit.exe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *Streamlit*" 2>nul
timeout /t 2 >nul

echo.
echo [2/4] Clearing Streamlit cache...
if exist "%USERPROFILE%\.streamlit" (
    rmdir /s /q "%USERPROFILE%\.streamlit\cache" 2>nul
    echo Cache cleared!
) else (
    echo No cache found (okay)
)

if exist ".streamlit\cache" (
    rmdir /s /q ".streamlit\cache" 2>nul
)

echo.
echo [3/4] Verifying enhanced_screener.py has updates...
python -c "with open('enhanced_screener.py', 'r', encoding='utf-8') as f: content = f.read(); print('✅ File has [90, 180, 365, 730]' if '[90, 180, 365, 730]' in content else '❌ File still has old values')"

echo.
echo [4/4] Starting system with fresh cache...
echo.

REM Activate venv if exists
if exist "..\venv\Scripts\activate.bat" (
    call ..\venv\Scripts\activate.bat
)

REM Start Streamlit with cache cleared
start "AI Screener Dashboard - UPDATED" streamlit run enhanced_screener.py --server.port 8501 --server.headless true

timeout /t 8

echo.
echo ============================================================
echo ✅ System restarted with updates!
echo ============================================================
echo.
echo Opening browser in 3 seconds...
timeout /t 3 >nul
start http://localhost:8501

echo.
echo You should now see:
echo - Lookback: [90, 180, 365, 730] days
echo - Default: 365 days selected
echo - New banner about improvements
echo.
echo If you still see [30, 60, 90], press Ctrl+R in browser!
echo.
pause

