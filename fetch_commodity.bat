@echo off
echo ==========================================
echo  FETCH MCX GOLD/SILVER COMMODITY DATA
echo ==========================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo Fetching commodity data...
python fetch_commodity_data.py

echo.
echo Done! Check the Commodity_data folder.
echo.
pause

