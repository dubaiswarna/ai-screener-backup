@echo off
echo ============================================================
echo STARTING FASTAPI BACKEND
echo ============================================================
echo.

cd /d "%~dp0"

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

echo Installing/updating dependencies...
pip install -q fastapi uvicorn python-multipart

echo.
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API docs: http://localhost:8000/docs
echo.
python api_server.py

pause

