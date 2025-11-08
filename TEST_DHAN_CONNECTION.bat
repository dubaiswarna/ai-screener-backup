@echo off
echo ============================================================
echo TESTING DHAN API CONNECTION
echo ============================================================
echo.
echo Testing connection with your credentials...
echo.

cd /d "%~dp0"

REM Activate virtual environment
call ..\venv\Scripts\activate.bat

REM Set environment variables from .env file
for /f "tokens=1,2 delims==" %%a in (.env) do (
    if not "%%a"=="#" (
        if not "%%a"=="" (
            set %%a=%%b
        )
    )
)

REM Test Dhan connection
python broker_integration\dhan_client.py

echo.
echo ============================================================
pause

