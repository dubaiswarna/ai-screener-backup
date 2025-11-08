"""
Fetch Cryptocurrency Data for AI Trading
=========================================
Downloads historical crypto data and formats it for the AI screener.
Uses yfinance to fetch major cryptocurrency data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path

try:
    import yfinance as yf
    print("✓ yfinance imported successfully")
except ImportError:
    print("ERROR: yfinance not installed!")
    print("Run: pip install yfinance")
    exit(1)


def fetch_crypto_data(symbol, ticker, period="2y", output_dir="Crypto_data"):
    """
    Fetch crypto data and save in compatible format.
    
    Args:
        symbol: Symbol name for file (e.g., 'CRYPTO_BTC')
        ticker: Yahoo Finance ticker (e.g., 'BTC-USD')
        period: Data period (default: 2y - cryptos are volatile, 2 years is good)
    """
    print(f"\n{'='*70}")
    print(f"Fetching {symbol} data from Yahoo Finance...")
    print(f"Ticker: {ticker}")
    print(f"{'='*70}")
    
    try:
        # Download data from Yahoo Finance
        data = yf.download(ticker, period=period, progress=False, interval='1d')
        
        if data.empty:
            print(f"❌ No data retrieved for {ticker}")
            return False
        
        # Flatten multi-index columns if needed
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        print(f"✓ Downloaded {len(data)} rows")
        
        # Prepare DataFrame
        df = pd.DataFrame()
        df['time'] = data.index
        df['open'] = data['Open'].values
        df['high'] = data['High'].values
        df['low'] = data['Low'].values
        df['close'] = data['Close'].values
        df['Volume'] = data['Volume'].values
        
        # Calculate VWAP
        df['VWAP'] = ((df['high'] + df['low'] + df['close']) / 3)
        
        # Calculate Bollinger Bands
        rolling_mean = df['close'].rolling(window=20).mean()
        rolling_std = df['close'].rolling(window=20).std()
        df['Upper Band #1'] = rolling_mean + (rolling_std * 2)
        df['Lower Band #1'] = rolling_mean - (rolling_std * 2)
        
        # Fill NaN values
        df['Upper Band #1'].fillna(df['close'], inplace=True)
        df['Lower Band #1'].fillna(df['close'], inplace=True)
        
        # Remove any NaN rows
        df = df.dropna().reset_index(drop=True)
        
        # Convert time to string format
        df['time'] = pd.to_datetime(df['time']).dt.strftime('%Y-%m-%d')
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save to CSV
        filename = f"{symbol}, 1D.csv"
        filepath = output_path / filename
        df.to_csv(filepath, index=False)
        
        print(f"✓ Saved to: {filepath}")
        print(f"  - Rows: {len(df)}")
        print(f"  - Date range: {df['time'].iloc[0]} to {df['time'].iloc[-1]}")
        print(f"  - Price range: ${df['close'].min():.2f} to ${df['close'].max():.2f}")
        print(f"  - Current price: ${df['close'].iloc[-1]:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fetch all major cryptocurrencies"""
    print("\n" + "="*70)
    print("CRYPTOCURRENCY DATA FETCHER FOR AI SCREENER")
    print("="*70)
    
    cryptocurrencies = [
        {
            'symbol': 'CRYPTO_BTC',
            'ticker': 'BTC-USD',
            'name': 'Bitcoin'
        },
        {
            'symbol': 'CRYPTO_ETH',
            'ticker': 'ETH-USD',
            'name': 'Ethereum'
        },
        {
            'symbol': 'CRYPTO_BNB',
            'ticker': 'BNB-USD',
            'name': 'Binance Coin'
        },
        {
            'symbol': 'CRYPTO_SOL',
            'ticker': 'SOL-USD',
            'name': 'Solana'
        },
        {
            'symbol': 'CRYPTO_XRP',
            'ticker': 'XRP-USD',
            'name': 'Ripple'
        },
        {
            'symbol': 'CRYPTO_ADA',
            'ticker': 'ADA-USD',
            'name': 'Cardano'
        },
        {
            'symbol': 'CRYPTO_DOGE',
            'ticker': 'DOGE-USD',
            'name': 'Dogecoin'
        },
        {
            'symbol': 'CRYPTO_DOT',
            'ticker': 'DOT-USD',
            'name': 'Polkadot'
        }
    ]
    
    success_count = 0
    
    for crypto in cryptocurrencies:
        print(f"\n💰 Fetching {crypto['name']}...")
        success = fetch_crypto_data(
            symbol=crypto['symbol'],
            ticker=crypto['ticker'],
            period='2y'  # 2 years for crypto (enough for patterns)
        )
        if success:
            success_count += 1
        time.sleep(0.5)  # Small delay to avoid rate limiting
    
    print("\n" + "="*70)
    print(f"SUMMARY: {success_count}/{len(cryptocurrencies)} cryptocurrencies downloaded")
    print("="*70)
    
    if success_count > 0:
        print("\n✅ Data saved to 'Crypto_data/' folder")
        print("\nNext steps:")
        print("1. Check the data files in Crypto_data/")
        print("2. Train AI models: python quick_train_crypto.py")
        print("3. View dashboard: python crypto_dashboard.py")
        print("4. Send alerts: python send_crypto_alerts.py")
    else:
        print("\n❌ Failed to download data. Please check your internet connection.")
    
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    import time
    main()

