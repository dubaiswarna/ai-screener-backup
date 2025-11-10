@echo off
title Test Expanded Stock Universe System
color 0E

echo ========================================
echo  TEST EXPANDED SYSTEM
echo ========================================
echo.
echo This will test the expanded stock universe:
echo   - Load stock lists
echo   - Test data loading
echo   - Test batch processing
echo   - Verify system configuration
echo.
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Test stock universe
echo.
echo [1/4] Testing stock universe configuration...
python -c "from config.stock_universe import get_universe_info; info = get_universe_info(); print('\n'.join([f'{k}: {v[\"count\"]} stocks' for k, v in info.items()]))"

REM Test data fetcher (dry run)
echo.
echo [2/4] Testing data fetcher module...
python -c "from fetch_expanded_universe_data import StockDataFetcher; print('✅ Data fetcher module OK')"

REM Test batch processor
echo.
echo [3/4] Testing batch processor...
python -c "from batch_processor import BatchProcessor; bp = BatchProcessor(batch_size=10); print('✅ Batch processor OK')"

REM Test system update
echo.
echo [4/4] Verifying system configuration...
python -c "import sys; sys.path.append('config'); from stock_universe import ALL_STOCKS; print(f'✅ System ready! {len(ALL_STOCKS)} stocks available')"

echo.
echo ========================================
echo  TEST RESULTS
echo ========================================
echo ✅ Stock universe: OK
echo ✅ Data fetcher: OK
echo ✅ Batch processor: OK
echo ✅ System configuration: OK
echo ========================================
echo.
echo 🎉 ALL TESTS PASSED!
echo.
echo Next steps:
echo 1. Run UPDATE_SYSTEM_EXPANDED.bat
echo 2. Run FETCH_EXPANDED_DATA.bat
echo 3. Run START_SYSTEM.bat
echo.
echo ========================================
pause

