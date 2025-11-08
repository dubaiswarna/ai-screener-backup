@echo off
echo ============================================================
echo MCX COMMODITY AI SCREENER - PERFORMANCE TEST
echo ============================================================
echo.

cd /d "%~dp0"

echo Running comprehensive test on Gold and Silver...
echo This will take approximately 2-3 minutes.
echo.

"..\venv\Scripts\python.exe" test_commodity_performance.py

echo.
echo ============================================================
echo Test Complete!
echo ============================================================
echo.
pause

