@echo off
cls
echo ================================================================
echo    FEB 2025 EXPERIMENT - SIGNAL GENERATION
echo ================================================================
echo.
echo This will:
echo   1. Extract data till February 2025
echo   2. Generate signals using trained AI models
echo   3. Save results to CSV
echo.
echo Base system will NOT be modified!
echo All work in: Feb2025_Experiment\
echo.
pause

cd /d "%~dp0"

echo.
echo Step 1: Extracting Feb 2025 data...
echo ----------------------------------------------------------------
python extract_feb2025_data.py

if errorlevel 1 (
    echo.
    echo ERROR: Data extraction failed!
    pause
    exit /b 1
)

echo.
echo.
echo Step 2: Generating signals...
echo ----------------------------------------------------------------
python generate_feb2025_signals.py

if errorlevel 1 (
    echo.
    echo ERROR: Signal generation failed!
    pause
    exit /b 1
)

echo.
echo ================================================================
echo  EXPERIMENT COMPLETE!
echo ================================================================
echo.
echo Results saved in: Feb2025_Experiment\
echo Check: signals_feb2025_*.csv
echo.
echo Base system: UNTOUCHED
echo.
pause

