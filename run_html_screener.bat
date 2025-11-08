@echo off
cd /d "c:\python\MG AI\AI_Screener_Complete"
echo.
echo ================================================================
echo  AI STOCK SCREENER - HTML DASHBOARD
echo ================================================================
echo.
echo Scanning all stocks and generating HTML report...
echo This will automatically open in your browser!
echo.
python daily_screener_html.py
echo.
pause

