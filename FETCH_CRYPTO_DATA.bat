@echo off
echo ============================================================
echo CRYPTOCURRENCY DATA FETCHER
echo ============================================================
echo.
echo Downloading 8 major cryptocurrencies:
echo   1. Bitcoin (BTC)
echo   2. Ethereum (ETH)
echo   3. Binance Coin (BNB)
echo   4. Solana (SOL)
echo   5. Ripple (XRP)
echo   6. Cardano (ADA)
echo   7. Dogecoin (DOGE)
echo   8. Polkadot (DOT)
echo.
echo This will take 1-2 minutes...
echo.

cd /d "%~dp0"

"..\venv\Scripts\python.exe" fetch_crypto_data.py

echo.
echo ============================================================
echo Download Complete!
echo ============================================================
echo.
pause

