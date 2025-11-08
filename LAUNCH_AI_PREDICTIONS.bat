@echo off
echo ============================================================
echo AI LIVE PREDICTIONS - MCX GOLD AND SILVER
echo ============================================================
echo.
echo This will show:
echo - AI BUY/HOLD signals with confidence scores
echo - Support/Resistance levels (reference only)
echo - Real-time predictions from trained models
echo.
echo ============================================================

cd /d "%~dp0"

"..\venv\Scripts\python.exe" ai_live_predictions.py

echo.
pause

