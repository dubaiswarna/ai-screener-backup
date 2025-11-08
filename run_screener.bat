@echo off
cd /d "c:\python\MG AI\AI_Screener_Complete"
echo.
echo ================================================================
echo  AI STOCK SCREENER - DAILY SCAN
echo ================================================================
echo.
echo Running AI screener on 42 Nifty stocks...
echo This will take 10-20 seconds...
echo.
python daily_screener.py
echo.
echo ================================================================
echo  Scan complete! Check the Excel file for results.
echo ================================================================
echo.
pause

