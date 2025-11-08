@echo off
echo ============================================================
echo MCX ADVANCED ANALYSIS DASHBOARD
echo ============================================================
echo.
echo Features:
echo - Support and Resistance Levels
echo - Entry/Exit Trade Signals
echo - 1-Year Performance Analysis
echo.

cd /d "%~dp0"

"..\venv\Scripts\python.exe" advanced_commodity_analysis.py

pause

