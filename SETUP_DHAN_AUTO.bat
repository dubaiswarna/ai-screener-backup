@echo off
echo ============================================================
echo AUTOMATIC DHAN SETUP
echo ============================================================
echo.
echo Creating .env file with your Dhan credentials...
echo.

cd /d "%~dp0"

REM Create .env file
(
echo DB_HOST=localhost
echo DB_PORT=5432
echo DB_NAME=ai_screener_pro
echo DB_USER=postgres
echo DB_PASSWORD=postgres
echo USE_POSTGRESQL=true
echo.
echo DHAN_CLIENT_ID=1104147457
echo DHAN_ACCESS_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzYyNDkwMDUxLCJpYXQiOjE3NjI0MDM2NTEsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTA0MTQ3NDU3In0.H91FqXQGRmtfJ229QDO8j_u-l6e79oBjascO9kd7vkmRZEuN0IEKYT6M64pYfZlun2iJJ3Ra8YZyrSLRYreqTg
echo.
echo ACTIVE_BROKER=dhan
echo.
echo TOTAL_CAPITAL=1000000
echo MAX_RISK_PER_TRADE=2.0
echo MAX_POSITIONS=10
echo MIN_CONFIDENCE=70.0
) > .env

echo ✅ .env file created successfully!
echo.

REM Verify file was created
if exist .env (
    echo ✅ Verified: .env file exists
    echo.
) else (
    echo ❌ Error: .env file was not created
    echo.
    pause
    exit
)

echo ============================================================
echo INSTALLING DHAN PACKAGE
echo ============================================================
echo.

REM Activate virtual environment
call ..\venv\Scripts\activate.bat

REM Install dhanhq package
echo Installing dhanhq package...
pip install dhanhq

echo.
echo ✅ Dhan package installed!
echo.

echo ============================================================
echo TESTING DHAN CONNECTION
echo ============================================================
echo.

REM Test connection
python broker_integration\dhan_client.py

echo.
echo ============================================================
echo.
echo 🎉 SETUP COMPLETE!
echo.
echo Your Dhan API is now configured and ready to use!
echo.
echo Next step: Double-click LAUNCH_PROFESSIONAL_SYSTEM.bat
echo.
echo ============================================================
pause

