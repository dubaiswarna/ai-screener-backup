@echo off
echo ========================================
echo AI Screener - Backup Repository Setup
echo ========================================
echo.

echo Step 1: Create a new repository on GitHub
echo -----------------------------------------
echo 1. Go to: https://github.com/new
echo 2. Repository name: ai-screener-backup (or your choice)
echo 3. Description: Complete backup of AI Screener System
echo 4. Make it PRIVATE (recommended)
echo 5. DO NOT initialize with README/.gitignore
echo 6. Click "Create repository"
echo.
echo After creating, copy the repository URL
echo (Example: https://github.com/dubaiswarna/ai-screener-backup.git)
echo.

set /p BACKUP_URL="Enter your new backup repository URL: "

if "%BACKUP_URL%"=="" (
    echo ERROR: No URL provided!
    pause
    exit /b 1
)

echo.
echo Step 2: Adding backup remote...
git remote add backup %BACKUP_URL%

if errorlevel 1 (
    echo.
    echo WARNING: Remote might already exist. Checking...
    git remote remove backup 2>nul
    git remote add backup %BACKUP_URL%
)

echo.
echo Step 3: Pushing to backup repository...
echo This may take a few minutes...
echo.

git push backup main

if errorlevel 1 (
    echo.
    echo ERROR: Failed to push to backup repository!
    echo Please check:
    echo 1. Repository URL is correct
    echo 2. You have access to the repository
    echo 3. Repository exists on GitHub
    pause
    exit /b 1
)

echo.
echo Step 4: Pushing all branches...
git push backup --all

echo.
echo Step 5: Pushing all tags...
git push backup --tags

echo.
echo ========================================
echo Backup Repository Setup Complete!
echo ========================================
echo.
echo Your backup remote is configured.
echo.
echo To push updates to backup in future:
echo   git push backup main
echo.
echo To push to both repos at once:
echo   git push origin main ^&^& git push backup main
echo.
echo Current remotes:
git remote -v
echo.
pause

