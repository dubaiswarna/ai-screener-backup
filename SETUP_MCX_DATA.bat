@echo off
echo ============================================================
echo MCX GOLD AND SILVER DATA SETUP
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/2] Installing yfinance...
"..\venv\Scripts\pip.exe" install yfinance --quiet
if errorlevel 1 (
    echo ERROR: Failed to install yfinance
    pause
    exit /b 1
)
echo Done!
echo.

echo [2/2] Fetching Gold and Silver data...
"..\venv\Scripts\python.exe" fetch_commodity_data.py
if errorlevel 1 (
    echo ERROR: Failed to fetch data
    pause
    exit /b 1
)

echo.
echo ============================================================
echo SUCCESS! MCX data downloaded
echo ============================================================
echo.
echo Next step: Run "python quick_train_commodity.py" to train models
echo.
pause

