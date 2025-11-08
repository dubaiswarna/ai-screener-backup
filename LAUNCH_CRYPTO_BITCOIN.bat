@echo off
echo ============================================================
echo   🪙 CRYPTOCURRENCY AI SCREENER - Including BITCOIN
echo ============================================================
echo.
echo Cryptocurrencies Available:
echo   🟠 Bitcoin (BTC)   - 92.73%% Accuracy (BEST!)
echo   🔷 Ethereum (ETH)  - 72.73%% Accuracy
echo   🟡 BNB (BNB)       - 87.27%% Accuracy
echo   🔵 XRP (XRP)       - 74.55%% Accuracy
echo   🟣 Solana (SOL)    - 67.73%% Accuracy
echo   🔴 Cardano (ADA)   - 69.55%% Accuracy
echo   ⚪ Polkadot (DOT)  - 65.00%% Accuracy
echo   🟤 Dogecoin (DOGE) - 61.82%% Accuracy
echo.
echo Dashboard will open at: http://localhost:8504
echo ============================================================
echo.

cd /d "%~dp0"

:: Check if venv exists
if not exist "..\venv\Scripts\streamlit.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

echo Starting Crypto Dashboard (Bitcoin included)...
echo.

"..\venv\Scripts\streamlit.exe" run crypto_dashboard.py --server.port 8504

pause

