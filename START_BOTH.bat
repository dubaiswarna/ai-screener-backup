@echo off
echo ============================================================
echo STARTING AI SCREENER - BACKEND + FRONTEND
echo ============================================================
echo.

cd /d "%~dp0"

REM Start backend in new window
start "AI Screener Backend" cmd /k "START_BACKEND.bat"

REM Wait a bit for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in new window
start "AI Screener Frontend" cmd /k "START_FRONTEND.bat"

echo.
echo ============================================================
echo Both servers are starting...
echo ============================================================
echo.
echo Backend API: http://localhost:8000
echo Backend Docs: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
echo Close the windows to stop the servers.
echo.
pause

