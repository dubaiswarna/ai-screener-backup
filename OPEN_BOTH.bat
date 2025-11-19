@echo off
echo ============================================================
echo STARTING AI SCREENER - BACKEND + FRONTEND
echo ============================================================
echo.

cd /d "%~dp0"

REM Start backend in new window
echo Starting Backend API...
start "AI Screener Backend" cmd /k "python api_server.py"

REM Wait for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in new window
echo Starting Frontend...
start "AI Screener Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ============================================================
echo Both servers are starting...
echo ============================================================
echo.
echo Backend API: http://localhost:8000
echo Backend Docs: http://localhost:8000/docs
echo Frontend: http://localhost:3002
echo.
echo Close the windows to stop the servers.
echo.
timeout /t 3

REM Open browser
start http://localhost:3002

pause

