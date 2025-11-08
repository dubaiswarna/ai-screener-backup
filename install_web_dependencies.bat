@echo off
cd /d "c:\python\MG AI\AI_Screener_Complete"
echo.
echo ================================================================
echo  Installing Web Dashboard Dependencies
echo ================================================================
echo.
echo Installing Streamlit and Plotly...
echo.
pip install streamlit plotly openpyxl
echo.
echo ================================================================
echo  Installation Complete!
echo ================================================================
echo.
echo You can now run the web screener:
echo    launch_web_screener.bat
echo.
pause

