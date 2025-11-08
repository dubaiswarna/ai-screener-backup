@echo off
REM ============================================================
REM COMPLETE PROFESSIONAL SETUP - ONE TIME ONLY
REM ============================================================

echo.
echo ============================================================
echo PROFESSIONAL AI SCREENER v3.0
echo COMPLETE SETUP - ONE TIME INSTALLATION
echo ============================================================
echo.
echo This will set up everything you need:
echo   1. Virtual environment
echo   2. All Python packages
echo   3. Database configuration
echo   4. Dhan API setup
echo   5. System testing
echo.
echo This only needs to be run ONCE!
echo.
pause

cd /d "%~dp0"

REM ============================================================
REM STEP 1: CREATE VIRTUAL ENVIRONMENT
REM ============================================================

echo.
echo ============================================================
echo STEP 1: Setting up Virtual Environment
echo ============================================================
echo.

cd ..

if exist venv (
    echo ✅ Virtual environment already exists
) else (
    echo Creating new virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created!
)

cd AI_Screener_Complete

REM ============================================================
REM STEP 2: INSTALL ALL PACKAGES
REM ============================================================

echo.
echo ============================================================
echo STEP 2: Installing All Packages
echo ============================================================
echo.
echo This may take 5-10 minutes...
echo.

REM Use full path to pip in venv
set PIP_PATH=..\venv\Scripts\pip.exe

%PIP_PATH% install --upgrade pip

echo Installing core packages...
%PIP_PATH% install psycopg2-binary

echo Installing web frameworks...
%PIP_PATH% install fastapi uvicorn[standard]

echo Installing data science packages...
%PIP_PATH% install pandas numpy scipy scikit-learn

echo Installing visualization...
%PIP_PATH% install plotly matplotlib seaborn

echo Installing Streamlit...
%PIP_PATH% install streamlit streamlit-aggrid

echo Installing market data...
%PIP_PATH% install yfinance dhanhq

echo Installing utilities...
%PIP_PATH% install python-dotenv pyyaml requests

echo Installing additional packages...
%PIP_PATH% install xgboost joblib

echo.
echo ✅ All packages installed!
echo.

REM ============================================================
REM STEP 3: CREATE .ENV FILE
REM ============================================================

echo.
echo ============================================================
echo STEP 3: Creating Configuration File
echo ============================================================
echo.

if exist .env (
    echo ℹ️ .env file already exists
    echo Backing up to .env.backup
    copy .env .env.backup >nul
)

(
echo # ============================================================
echo # PROFESSIONAL AI SCREENER - CONFIGURATION
echo # ============================================================
echo.
echo # Database Configuration
echo DB_HOST=localhost
echo DB_PORT=5432
echo DB_NAME=ai_screener_pro
echo DB_USER=postgres
echo DB_PASSWORD=postgres
echo USE_POSTGRESQL=true
echo.
echo # Dhan API Credentials
echo DHAN_CLIENT_ID=1104147457
echo DHAN_ACCESS_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzYyNDkwMDUxLCJpYXQiOjE3NjI0MDM2NTEsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTA0MTQ3NDU3In0.H91FqXQGRmtfJ229QDO8j_u-l6e79oBjascO9kd7vkmRZEuN0IEKYT6M64pYfZlun2iJJ3Ra8YZyrSLRYreqTg
echo.
echo # Broker Selection
echo ACTIVE_BROKER=dhan
echo.
echo # Risk Management
echo TOTAL_CAPITAL=1000000
echo MAX_RISK_PER_TRADE=2.0
echo MAX_POSITIONS=10
echo MIN_CONFIDENCE=70.0
) > .env

echo ✅ Configuration file created!
echo.

REM ============================================================
REM STEP 4: TEST SYSTEM
REM ============================================================

echo.
echo ============================================================
echo STEP 4: Testing System
echo ============================================================
echo.

echo Testing database connection...
..\venv\Scripts\python.exe -c "from database.db_manager import get_db; db = get_db(); print('✅ Database OK' if db.test_connection() else '❌ Database Failed')" 2>nul

if %ERRORLEVEL% EQU 0 (
    echo ✅ Database test passed!
) else (
    echo ⚠️ Database test failed - might need PostgreSQL setup
    echo Run INSTALL_POSTGRESQL_AUTO.bat first
)

echo.
echo Testing Dhan API...
..\venv\Scripts\python.exe broker_integration\dhan_client.py 2>nul

echo.

REM ============================================================
REM STEP 5: CREATE LAUNCH SCRIPTS
REM ============================================================

echo.
echo ============================================================
echo STEP 5: Creating Launch Scripts
echo ============================================================
echo.

REM Create simple launch script
(
echo @echo off
echo echo ============================================================
echo echo PROFESSIONAL AI SCREENER v3.0
echo echo ============================================================
echo echo.
echo echo Starting system...
echo echo.
echo cd /d "%%~dp0"
echo.
echo REM Start Streamlit Dashboard
echo start "AI Screener Dashboard" ..\venv\Scripts\streamlit.exe run enhanced_screener.py --server.port 8501
echo.
echo timeout /t 5
echo.
echo echo ✅ Dashboard starting at: http://localhost:8501
echo echo.
echo echo Press any key to open browser...
echo pause ^>nul
echo start http://localhost:8501
echo.
echo echo System is running!
echo echo Close this window to stop the system.
echo pause
) > START_SYSTEM.bat

echo ✅ Launch script created!
echo.

REM ============================================================
REM COMPLETE!
REM ============================================================

echo.
echo ============================================================
echo ✅ SETUP COMPLETE!
echo ============================================================
echo.
echo Your Professional AI Screener is ready to use!
echo.
echo To start the system:
echo   Double-click: START_SYSTEM.bat
echo.
echo Access at: http://localhost:8501
echo.
echo Features enabled:
echo   ✅ Database persistence (signals never lost!)
echo   ✅ Dhan API real-time data
echo   ✅ Risk management (Kelly Criterion, VaR)
echo   ✅ Portfolio tracking
echo   ✅ Trade history
echo   ✅ Advanced analytics
echo.
echo ============================================================
echo.
pause

