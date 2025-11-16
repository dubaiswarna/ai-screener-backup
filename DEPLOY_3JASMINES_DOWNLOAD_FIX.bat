@echo off
title Deploy 3Jasmines Download Fix to Railway
color 0B

echo ============================================================
echo  DEPLOYING 3JASMINES DOWNLOAD FIX TO RAILWAY
echo ============================================================
echo.
echo This will deploy:
echo   - Fixed 3Jasmines CSV download button
echo   - Removed nested button issue
echo   - Properly flattened nested dictionaries for CSV export
echo   - Better error handling
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
echo [2/4] Adding updated files...
git add enhanced_screener.py
git add CHANGELOG_3JASMINES_DOWNLOAD.md

echo.
echo [3/4] Committing changes...
git commit -m "🔧 FIX: 3Jasmines CSV Download Button

FIXED: Download 3Jasmines Results
- Removed nested button wrapper (st.button -> st.download_button doesn't work)
- Now directly renders download button when signals exist
- Properly flattens nested dictionaries (jasmine1_support, jasmine2_rsi, jasmine3_pattern)
- Added comprehensive CSV export with all fields
- Better error handling with try/except
- Clean CSV format ready for Excel

ISSUE: Download button wasn't working due to nested button pattern
SOLUTION: Direct download button rendering + proper data flattening

READY FOR DEPLOYMENT!"

echo.
echo [4/4] Pushing to Railway...
echo (This will trigger auto-deployment)
git push origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARNING] Push failed. Trying alternative remote...
    git push backup main
)

echo.
echo ============================================================
echo ✅ DEPLOYMENT TRIGGERED!
echo ============================================================
echo.
echo Railway is now building and deploying...
echo.
echo Wait 2-3 minutes, then check:
echo https://ai-screener-production-7319.up.railway.app/
echo.
echo Test the fix:
echo   1. Go to '3Jasmines 🌸' page
echo   2. Run a scan
echo   3. When signals appear, the download button should work
echo   4. Click '📥 Download 3Jasmines Signals (CSV)'
echo.
echo ============================================================
echo.
pause

