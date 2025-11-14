@echo off
echo ========================================
echo Push to Both Repositories
echo ========================================
echo.

echo Pushing to main repository (origin)...
git push origin main

if errorlevel 1 (
    echo ERROR: Failed to push to origin!
    pause
    exit /b 1
)

echo.
echo Pushing to backup repository...
git remote show backup >nul 2>&1

if errorlevel 1 (
    echo WARNING: Backup remote not found!
    echo Run CREATE_BACKUP_REPO.bat first to set up backup.
    pause
    exit /b 1
)

git push backup main

if errorlevel 1 (
    echo WARNING: Failed to push to backup repository!
    echo Continuing anyway...
) else (
    echo.
    echo Successfully pushed to both repositories!
)

echo.
pause

