"""
Fetch Gold & Silver Data for MCX Trading
=========================================

Downloads historical commodity data and formats it for the AI screener.
Uses yfinance to fetch Gold and Silver futures data.
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


def calculate_vwap(df):
    """Calculate VWAP (Volume Weighted Average Price)"""
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
    return vwap


def calculate_bollinger_bands(df, window=20, num_std=2):
    """Calculate Bollinger Bands"""
    rolling_mean = df['close'].rolling(window=window).mean()
    rolling_std = df['close'].rolling(window=window).std()
    
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    
    return upper_band, lower_band


def fetch_commodity_data(symbol, ticker, period="10y", output_dir="MCX_data"):
    """
    Fetch commodity data and save in NSE-compatible format.
    
    Args:
        symbol: Symbol name for file (e.g., 'MCX_GOLD')
        ticker: Yahoo Finance ticker (e.g., 'GC=F')
        period: Data period (default: 10y)
        output_dir: Directory to save data
    """
    print(f"\n{'='*70}")
    print(f"Fetching {symbol} data from Yahoo Finance...")
    print(f"Ticker: {ticker}")
    print(f"{'='*70}")
    
    try:
        # Download data from Yahoo Finance
        data = yf.download(ticker, period=period, progress=False)
        
        if data.empty:
            print(f"❌ No data retrieved for {ticker}")
            return False
        
        print(f"✓ Downloaded {len(data)} rows")
        
        # Prepare DataFrame in NSE format
        df = pd.DataFrame()
        df['time'] = data.index
        df['open'] = data['Open'].values
        df['high'] = data['High'].values
        df['low'] = data['Low'].values
        df['close'] = data['Close'].values
        df['Volume'] = data['Volume'].values
        
        # Calculate VWAP
        print("Calculating VWAP...")
        df['VWAP'] = calculate_vwap(df)
        
        # Calculate Bollinger Bands
        print("Calculating Bollinger Bands...")
        df['Upper Band #1'], df['Lower Band #1'] = calculate_bollinger_bands(df)
        
        # Remove NaN values (from rolling calculations)
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
        print(f"  - Price range: {df['close'].min():.2f} to {df['close'].max():.2f}")
        
        # Show sample data
        print(f"\nSample data (first 3 rows):")
        print(df.head(3).to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return False


def main():
    """Fetch both Gold and Silver data"""
    print("\n" + "="*70)
    print("COMMODITY DATA FETCHER FOR AI SCREENER")
    print("="*70)
    
    commodities = [
        {
            'symbol': 'MCX_GOLD',
            'ticker': 'GC=F',  # Gold Futures
            'name': 'Gold Futures'
        },
        {
            'symbol': 'MCX_SILVER',
            'ticker': 'SI=F',  # Silver Futures
            'name': 'Silver Futures'
        }
    ]
    
    success_count = 0
    
    for commodity in commodities:
        print(f"\n📊 Fetching {commodity['name']}...")
        success = fetch_commodity_data(
            symbol=commodity['symbol'],
            ticker=commodity['ticker'],
            period='10y'
        )
        if success:
            success_count += 1
    
    print("\n" + "="*70)
    print(f"SUMMARY: {success_count}/{len(commodities)} commodities downloaded successfully")
    print("="*70)
    
    if success_count > 0:
        print("\n✓ Data saved to 'MCX_data/' folder")
        print("\nNext steps:")
        print("1. Check the data files in MCX_data/")
        print("2. Train models using: python quick_train_commodity.py")
        print("\nIf you have actual MCX data, replace these files with your CSV files")
        print("in the same format (time,open,high,low,close,Volume,VWAP,Upper Band #1,Lower Band #1)")
    else:
        print("\n❌ Failed to download data. Please check your internet connection.")


if __name__ == '__main__':
    main()
