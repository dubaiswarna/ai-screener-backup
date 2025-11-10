@echo off
title Update System for Expanded Universe
color 0B

echo ========================================
echo  UPDATE SYSTEM FOR EXPANDED UNIVERSE
echo ========================================
echo.
echo This will update your system to support:
echo   - Nifty 500 (500 stocks)
echo   - Smallcap 250 (250 stocks)
echo   - Total: 750+ unique stocks!
echo.
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the update script
python update_system_for_expanded_universe.py

echo.
echo ========================================
echo Press any key to exit...
pause > nul

