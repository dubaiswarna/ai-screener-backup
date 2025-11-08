@echo off
REM ========================================================
REM MCX Gold/Silver AI Training - Complete Test Pipeline
REM ========================================================

echo.
echo ========================================================
echo MCX GOLD/SILVER AI TRAINING PIPELINE
echo ========================================================
echo.
echo This script will:
echo   1. Fetch Gold and Silver futures data
echo   2. Format data for AI training
echo   3. Train AI models for MCX_GOLD and MCX_SILVER
echo   4. Display results and accuracy metrics
echo.
echo ========================================================
echo.

pause

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Using global Python...
)

echo.
echo ========================================================
echo STEP 1: Fetching MCX Data (Gold and Silver)
echo ========================================================
echo.

python fetch_mcx_data.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to fetch MCX data!
    echo Check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo STEP 2: Training AI Models
echo ========================================================
echo.

python quick_train_mcx.py

if errorlevel 1 (
    echo.
    echo ERROR: Training failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo SUCCESS! MCX AI Training Complete
echo ========================================================
echo.
echo Trained models are saved in: ai_screener\models\
echo   - xgb_MCX_GOLD.pkl
echo   - xgb_MCX_SILVER.pkl
echo.
echo Next Steps:
echo   1. Use these models for predictions
echo   2. Integrate with your trading strategy
echo   3. Monitor performance on live data
echo.
echo ========================================================
echo.

pause

