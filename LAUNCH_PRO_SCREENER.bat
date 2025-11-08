@echo off
cls
echo ========================================
echo   AI STOCK SCREENER - PROFESSIONAL
echo ========================================
echo.
echo   Features:
echo   - Real-time Alerts
echo   - Portfolio Tracking
echo   - Risk Management
echo   - Auto-refresh
echo   - Mobile-friendly
echo.
echo   86.9%% Proven Win Rate
echo.
echo ========================================
echo.
echo Starting enhanced screener...
echo.
cd /d "%~dp0"
cd ai_screener
streamlit run screener_app_pro.py
pause

