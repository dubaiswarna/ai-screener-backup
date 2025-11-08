@echo off
cd /d "c:\python\MG AI\AI_Screener_Complete"
echo.
echo ================================================================
echo  AI SCREENER - TRAINING ALL 42 STOCKS
echo ================================================================
echo.
echo This will train models for all Nifty stocks.
echo Estimated time: 15-20 minutes
echo.
python train_all_stocks.py
echo.
pause

