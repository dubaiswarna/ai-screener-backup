@echo off
echo ========================================
echo Verify Backup Repository Setup
echo ========================================
echo.

echo Checking remotes...
echo.
git remote -v

echo.
echo Checking if backup remote exists...
git remote show backup >nul 2>&1

if errorlevel 1 (
    echo.
    echo ❌ ERROR: Backup remote not found!
    echo.
    echo Please run CREATE_BACKUP_REPO.bat first.
    pause
    exit /b 1
)

echo.
echo ✅ Backup remote found!
echo.
echo Testing connection to backup repository...
git ls-remote backup main >nul 2>&1

if errorlevel 1 (
    echo.
    echo ⚠️ WARNING: Cannot connect to backup repository
    echo Please check:
    echo 1. Repository exists on GitHub
    echo 2. You have access to the repository
    echo 3. Internet connection is working
) else (
    echo.
    echo ✅ Successfully connected to backup repository!
    echo.
    echo Current setup:
    echo   - Working repo (origin): ai-screener
    echo   - Backup repo (backup): ai-screener-backup
    echo.
    echo ✅ Backup is ready!
)

echo.
pause

