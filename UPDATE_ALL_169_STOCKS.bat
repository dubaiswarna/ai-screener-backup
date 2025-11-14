@echo off
echo ============================================================
echo UPDATE ALL 169 STOCKS (Nifty 50 + Nifty 200 + Small Caps)
echo ============================================================
echo.
echo This will update all 169 stocks from Feb 2025 to Nov 2025
echo Estimated time: 10-15 minutes
echo.
pause
echo.
echo Starting update...
echo.

python update_all_169_stocks.py

echo.
echo ============================================================
echo Update complete! Check the summary above.
echo ============================================================
pause

