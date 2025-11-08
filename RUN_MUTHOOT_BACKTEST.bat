@echo off
echo ============================================================
echo   📊 MUTHOOT FINANCE AI BACKTEST
echo ============================================================
echo.
echo Period: Nov 3, 2024 to Nov 3, 2025
echo.
echo This will:
echo   1. Fetch 10 years of Muthoot Finance data
echo   2. Train an XGBoost AI model
echo   3. Generate detailed entry/exit signals
echo   4. Calculate profits for each trade
echo.
echo Estimated time: 2-3 minutes
echo ============================================================
echo.

cd /d "%~dp0"

echo Starting backtest...
echo.

"..\venv\Scripts\python.exe" backtest_muthoot_finance.py

echo.
echo ============================================================
echo   ✅ Backtest complete!
echo ============================================================
echo.
echo Results saved to: MUTHOOT_FINANCE_BACKTEST_2024-11-03_to_2025-11-03.csv
echo.
pause

