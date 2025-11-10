@echo off
title Deploy Updates to Railway
color 0B

echo ============================================================
echo  DEPLOYING UPDATES TO RAILWAY
echo ============================================================
echo.
echo Your Railway App: https://ai-screener-production-7319.up.railway.app/
echo.
echo This will deploy:
echo   - Extended lookback (90/180/365/730 days)
echo   - SMA 200 analysis
echo   - Fibonacci retracements
echo   - All improvements
echo.
echo ============================================================
pause

cd /d "%~dp0"

echo.
echo [1/5] Checking git status...
git status

echo.
echo [2/5] Adding updated files...
git add enhanced_screener.py
git add config/stock_universe.py
git add batch_processor.py
git add fetch_expanded_universe_data.py
git add *.md

echo.
echo [3/5] Committing changes...
git commit -m "Added SMA 200, Fibonacci levels, extended lookback to 730 days, Nifty 500 + Smallcap 250 support"

echo.
echo [4/5] Pushing to Railway...
echo (This will trigger auto-deployment)
git push

echo.
echo [5/5] Deployment triggered!
echo.
echo ============================================================
echo ✅ DEPLOYMENT IN PROGRESS
echo ============================================================
echo.
echo Railway is now building and deploying...
echo.
echo Wait 2-3 minutes, then check:
echo https://ai-screener-production-7319.up.railway.app/
echo.
echo You should see:
echo   - Lookback: [90, 180, 365, 730] days
echo   - New improvements banner
echo   - SMA 200 column in results
echo   - Fibonacci patterns
echo.
echo ============================================================
echo.
echo Press any key to open Railway dashboard...
pause >nul
start https://railway.app/project/YOUR_PROJECT_ID
echo.
echo Check deployment logs in Railway dashboard!
pause



