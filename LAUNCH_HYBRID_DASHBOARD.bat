@echo off
echo ========================================
echo Launching Hybrid Backtest Dashboard
echo Port: 8503
echo ========================================
cd backtest_system
streamlit run backtest_dashboard_hybrid.py --server.port 8503
pause

