@echo off
echo ========================================
echo  1-YEAR BACKTEST - AI SCREENER
echo ========================================
echo.
echo Starting backtest with Rs 15L capital...
echo Period: Nov 2024 - Nov 2025
echo.

cd /d "C:\python\MG AI\AI_Screener_Complete\ai_screener"

echo Launching backtest engine...
"C:\python\MG AI\venv\Scripts\python.exe" -m streamlit run comprehensive_backtest.py --server.port 8506

pause

