@echo off
echo ============================================================
echo 📊 DAILY EOD DATA UPDATE - Using Dhan API
echo ============================================================
echo.
echo This will update your master Excel file with today's EOD data
echo Using Dhan API (NO delay - official close prices!)
echo.
echo Run this every evening after market close (after 3:30 PM)
echo.

cd /d "%~dp0"

echo 🔄 Fetching today's EOD data from Dhan...
echo.

venv\Scripts\python.exe UPDATE_EOD_DATA_DHAN.py

echo.
echo ============================================================
pause

