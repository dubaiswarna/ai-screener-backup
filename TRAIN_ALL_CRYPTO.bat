@echo off
echo ============================================================
echo TRAIN AI MODELS FOR ALL CRYPTOCURRENCIES
echo ============================================================
echo.
echo This will train AI models for 8 major cryptocurrencies:
echo   1. Bitcoin (BTC)
echo   2. Ethereum (ETH)
echo   3. Binance Coin (BNB)
echo   4. Solana (SOL)
echo   5. Ripple (XRP)
echo   6. Cardano (ADA)
echo   7. Dogecoin (DOGE)
echo   8. Polkadot (DOT)
echo.
echo Estimated time: 5-8 minutes
echo.
echo ============================================================
echo.

cd /d "%~dp0"

"..\venv\Scripts\python.exe" train_all_crypto.py

echo.
echo ============================================================
echo Training Complete!
echo ============================================================
echo.
pause

