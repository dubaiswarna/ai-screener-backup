"""
Update Local Data with Latest Prices
=====================================
Downloads today's latest close from Yahoo Finance and updates CSV files
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import yfinance as yf

def update_stock_data(symbol: str, data_folder: Path) -> bool:
    """
    Update a single stock's CSV with latest data.
    
    Args:
        symbol: Stock symbol (e.g., 'NSE_RELIANCE')
        data_folder: Path to Nifty200_Data folder
        
    Returns:
        True if successful
    """
    try:
        csv_file = data_folder / f"{symbol}_1D.csv"
        
        if not csv_file.exists():
            return False
        
        # Read existing data
        df_existing = pd.read_csv(csv_file)
        
        # Get latest date in CSV
        df_existing['time'] = pd.to_datetime(df_existing['time'])
        latest_date = df_existing['time'].max()
        
        # Download new data from Yahoo Finance
        yf_symbol = symbol.replace('NSE_', '') + '.NS'
        
        # Get last 5 days to ensure we have latest
        df_new = yf.download(yf_symbol, period='5d', progress=False)
        
        if df_new.empty:
            return False
        
        # Convert to same format as existing
        df_new = df_new.reset_index()
        df_new.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        df_new['vwap'] = (df_new['high'] + df_new['low'] + df_new['close']) / 3
        
        # Only keep rows newer than existing
        df_new['time'] = pd.to_datetime(df_new['time'])
        df_new = df_new[df_new['time'] > latest_date]
        
        if not df_new.empty:
            # Append to existing
            df_updated = pd.concat([df_existing, df_new], ignore_index=True)
            
            # Save back
            df_updated.to_csv(csv_file, index=False)
            return True
        
        return False  # No new data
        
    except Exception as e:
        print(f"Error updating {symbol}: {e}")
        return False

def update_all_signals_data(symbols: list, data_folder: Path) -> dict:
    """
    Update CSV files for all symbols in signal list.
    
    Args:
        symbols: List of symbols to update
        data_folder: Path to data folder
        
    Returns:
        Dict with update stats
    """
    updated = 0
    skipped = 0
    errors = 0
    
    for symbol in symbols:
        try:
            if update_stock_data(symbol, data_folder):
                updated += 1
            else:
                skipped += 1
        except:
            errors += 1
    
    return {
        'updated': updated,
        'skipped': skipped,
        'errors': errors,
        'total': len(symbols)
    }

