@echo off
echo Killing old processes...
taskkill /F /IM streamlit.exe 2>nul
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul

echo Starting fresh...
cd /d "%~dp0"
start "" streamlit run enhanced_screener.py --server.port 8501
timeout /t 5

start http://localhost:8501
echo Done! Check browser in 5 seconds.



