@echo off
REM ============================================================
REM AUTOMATED POSTGRESQL INSTALLATION & SETUP
REM ============================================================

echo.
echo ============================================================
echo PROFESSIONAL AI SCREENER - PostgreSQL Setup
echo ============================================================
echo.
echo This will install PostgreSQL automatically.
echo.
echo Press Ctrl+C to cancel, or
pause

cd /d "%~dp0"

REM Check if PostgreSQL is already installed
echo.
echo Checking for existing PostgreSQL installation...
echo.

where psql >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ PostgreSQL is already installed!
    goto :DATABASE_SETUP
)

echo ⚠️ PostgreSQL not found. Installing...
echo.
echo Downloading PostgreSQL installer...
echo This may take a few minutes depending on your internet speed.
echo.

REM Download PostgreSQL installer
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://get.enterprisedb.com/postgresql/postgresql-15.3-1-windows-x64.exe' -OutFile 'postgresql_installer.exe'}"

if not exist postgresql_installer.exe (
    echo ❌ Download failed!
    echo.
    echo Please download manually from:
    echo https://www.postgresql.org/download/windows/
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Download complete!
echo.
echo Starting silent installation...
echo Default password will be: postgres
echo.

REM Silent installation
postgresql_installer.exe --mode unattended --superpassword postgres --servicename postgresql-15 --serverport 5432

echo.
echo Waiting for installation to complete...
timeout /t 30

REM Clean up installer
del postgresql_installer.exe

:DATABASE_SETUP

echo.
echo ============================================================
echo SETTING UP DATABASE
echo ============================================================
echo.

REM Add PostgreSQL to PATH if not already
set PATH=%PATH%;C:\Program Files\PostgreSQL\15\bin

REM Wait for PostgreSQL service to start
echo Waiting for PostgreSQL service to start...
timeout /t 5

REM Create database
echo Creating database: ai_screener_pro
echo.

REM Use psql to create database
psql -U postgres -c "CREATE DATABASE ai_screener_pro;" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Database created successfully!
) else (
    echo ℹ️ Database may already exist or requires password
    echo Default password is: postgres
)

echo.
echo Initializing database schema...
echo.

REM Initialize schema
psql -U postgres -d ai_screener_pro -f database_schema.sql

if %ERRORLEVEL% EQU 0 (
    echo ✅ Database schema initialized!
) else (
    echo ⚠️ Schema initialization requires password
    echo Running with password prompt...
    echo Default password: postgres
    echo.
    psql -U postgres -d ai_screener_pro -f database_schema.sql
)

echo.
echo ============================================================
echo ✅ POSTGRESQL SETUP COMPLETE!
echo ============================================================
echo.
echo Database: ai_screener_pro
echo User: postgres
echo Password: postgres
echo Port: 5432
echo.
echo Next step: Run COMPLETE_SETUP.bat
echo.
pause

