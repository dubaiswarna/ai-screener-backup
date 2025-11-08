@echo off
cd /d "c:\python\MG AI\AI_Screener_Complete"
echo.
echo ================================================================
echo  AI STOCK SCREENER - WEB DASHBOARD
echo ================================================================
echo.
echo Starting web server...
echo.
echo The dashboard will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.
echo ================================================================
echo.
streamlit run web_screener.py

