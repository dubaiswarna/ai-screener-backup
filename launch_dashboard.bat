@echo off
cd /d "c:\python\MG AI\AI_Screener_Complete"
echo.
echo ================================================================
echo  AI STOCK SCREENER - INTERACTIVE DASHBOARD
echo ================================================================
echo.
echo Scanning all 42 stocks and generating charts...
echo This will take 1-2 minutes...
echo.
echo The dashboard will automatically open in your browser!
echo Click "View Chart" buttons to see TradingView-style analysis!
echo.
python screener_with_charts.py
echo.
pause

