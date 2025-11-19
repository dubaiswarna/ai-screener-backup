@echo off
echo ============================================================
echo OPENING AI SCREENER FRONTEND
echo ============================================================
echo.

cd /d "%~dp0\frontend"

echo Starting Next.js development server...
echo.
echo Frontend will be available at: http://localhost:3002
echo Make sure the Python backend API is running on port 8000
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev

pause

