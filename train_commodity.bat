@echo off
echo ==========================================
echo  TRAIN MCX COMMODITY AI MODEL
echo ==========================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo Training commodity model...
python quick_train_commodity.py

echo.
echo Done!
echo.
pause

