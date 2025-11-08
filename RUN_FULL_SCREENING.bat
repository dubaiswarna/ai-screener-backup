@echo off
echo ============================================================
echo 🚀 RUNNING FULL AI SCREENING - ALL 42 MODELS
echo ============================================================
echo.
echo This will:
echo   1. Load all 42 AI models
echo   2. Fetch 3 months EOD data for each stock
echo   3. Engineer 89 features per stock
echo   4. Generate AI signals
echo   5. Save high-confidence signals to CSV
echo.
echo This may take 2-3 minutes...
echo.

cd /d "%~dp0"

..\venv\Scripts\python.exe run_full_screening.py

echo.
echo ============================================================
pause

