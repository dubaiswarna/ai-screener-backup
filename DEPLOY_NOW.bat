@echo off
echo ============================================================
echo DEPLOYING TO RAILWAY
echo ============================================================
echo.
echo This will push all changes to GitHub
echo Railway will auto-deploy from GitHub
echo.
echo Your Railway App: https://ai-screener-production-7319.up.railway.app/
echo.
echo ============================================================
pause

cd /d "%~dp0"

echo.
echo [1/4] Checking git status...
git status

echo.
echo [2/4] Adding all files...
git add .

echo.
echo [3/4] Committing changes...
git commit -m "Configure Railway deployment with MySQL and Next.js frontend"

echo.
echo [4/4] Pushing to GitHub...
echo (This triggers Railway auto-deployment)
git push origin main

echo.
echo ============================================================
echo DEPLOYMENT TRIGGERED!
echo ============================================================
echo.
echo Railway is now building and deploying...
echo.
echo Monitor deployment at:
echo https://railway.app/project
echo.
echo Wait 3-5 minutes for deployment to complete.
echo.
echo Then check:
echo - Backend: https://your-backend.up.railway.app/health
echo - Frontend: https://your-frontend.up.railway.app
echo.
pause

