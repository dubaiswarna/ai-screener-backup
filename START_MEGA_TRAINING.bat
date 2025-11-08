@echo off
echo ========================================
echo   MEGA TRAINING - 33 REMAINING STOCKS
echo ========================================
echo.
echo Starting automated training...
echo This will take 2-3 hours
echo You can minimize this window
echo.
cd /d "%~dp0"
python train_remaining_stocks.py
echo.
echo ========================================
echo   TRAINING COMPLETED!
echo ========================================
pause

