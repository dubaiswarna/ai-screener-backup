@echo off
echo ========================================
echo  JUNE 2025 BACKTEST - AI SCREENER
echo ========================================
echo.
echo Generating signals using data up to June 2025
echo Port: 8502
echo.

cd /d "C:\python\MG AI\AI_Screener_Complete\ai_screener"

echo Launching June 2025 test screener...
"C:\python\MG AI\venv\Scripts\python.exe" -m streamlit run screener_june2025_test.py --server.port 8502

pause

