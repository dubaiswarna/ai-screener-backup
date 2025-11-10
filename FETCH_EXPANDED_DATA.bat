@echo off
title Fetch Expanded Stock Universe Data (Nifty 500 + Smallcap 250)
color 0A

echo ========================================
echo  FETCH EXPANDED STOCK DATA
echo ========================================
echo.
echo This will download data for up to 750 stocks!
echo.
echo Available Universes:
echo   1. Nifty 50    (50 stocks)
echo   2. Nifty 200   (200 stocks)
echo   3. Nifty 500   (500 stocks)
echo   4. Smallcap 250 (250 stocks)
echo   5. ALL         (750+ stocks)
echo.
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the fetch script
python fetch_expanded_universe_data.py

echo.
echo ========================================
echo Press any key to exit...
pause > nul

