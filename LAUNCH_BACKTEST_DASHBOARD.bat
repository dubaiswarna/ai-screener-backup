@echo off
echo ========================================
echo Launching Backtest Dashboard (Technical)
echo Port: 8502
echo ========================================
cd backtest_system
streamlit run backtest_dashboard.py --server.port 8502
pause

