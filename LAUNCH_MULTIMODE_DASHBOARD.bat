@echo off
echo ========================================
echo Launching Multi-Mode Backtest Dashboard
echo Port: 8504
echo ========================================
cd backtest_system
streamlit run backtest_dashboard_multimode.py --server.port 8504
pause

