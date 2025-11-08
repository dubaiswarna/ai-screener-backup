@echo off
echo ========================================
echo  COMPREHENSIVE MONTHLY BACKTEST
echo ========================================
echo.
echo Generating signals for:
echo - May 31, 2025
echo - June 30, 2025
echo - July 31, 2025
echo - Aug 31, 2025
echo - Sept 30, 2025
echo - Oct 31, 2025
echo.
echo Tracking performance up to Nov 5, 2025
echo.
echo This will take 5-10 minutes...
echo.

cd /d "C:\python\MG AI\AI_Screener_Complete\ai_screener"

"C:\python\MG AI\venv\Scripts\python.exe" -u generate_monthly_backtest.py

echo.
echo ========================================
echo  BACKTEST COMPLETE!
echo ========================================
echo.
echo Results saved to:
echo C:\python\MG AI\AI_Backtest_Results.xlsx
echo.

