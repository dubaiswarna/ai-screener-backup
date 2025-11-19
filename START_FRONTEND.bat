@echo off
echo ============================================================
echo STARTING NEXT.JS FRONTEND
echo ============================================================
echo.

cd /d "%~dp0\frontend"

echo Checking if node_modules exists...
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    echo.
)

echo Starting Next.js development server...
echo Frontend will be available at: http://localhost:3000
echo Make sure the Python backend is running on port 8000
echo.
call npm run dev

pause

