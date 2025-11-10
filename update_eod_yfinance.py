"""
Quick EOD Data Updater - Using Yahoo Finance
===========================================
Updates all CSV files with today's EOD data
"""

import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

print("="*70)
print("EOD DATA UPDATER - Using Yahoo Finance")
print("="*70)
print()

# Get all CSV files
csv_files = list(Path('Nify50_data').glob('*.csv'))
print(f"Found {len(csv_files)} CSV files to update")
print()

success_count = 0
fail_count = 0

for csv_file in csv_files:
    # Extract stock symbol
    stock_name = csv_file.stem.replace('NSE_', '').replace(', 1D', '')
    symbol = f"{stock_name}.NS"
    
    print(f"  {stock_name}...", end=' ', flush=True)
    
    try:
        # Fetch last 5 days data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='5d')
        
        if len(hist) == 0:
            print("FAIL - No data")
            fail_count += 1
            continue
        
        # Read existing CSV
        df_existing = pd.read_csv(csv_file)
        
        # Get latest date in CSV (column is 'time' not 'date')
        date_col = 'time' if 'time' in df_existing.columns else 'date'
        df_existing[date_col] = pd.to_datetime(df_existing[date_col], dayfirst=True)
        last_date = df_existing[date_col].max()
        
        # Get new data (only dates after last_date)
        hist.index = hist.index.tz_localize(None)  # Remove timezone
        new_data = hist[hist.index > last_date]
        
        if len(new_data) > 0:
            # Format new data to match CSV structure
            for new_date, row in new_data.iterrows():
                new_row = {
                    date_col: new_date.strftime('%Y-%m-%d'),
                    'open': round(row['Open'], 2),
                    'high': round(row['High'], 2),
                    'low': round(row['Low'], 2),
                    'close': round(row['Close'], 2),
                    'Volume': int(row['Volume']),
                    'VWAP': round((row['High'] + row['Low'] + row['Close']) / 3, 2),
                    'Upper Band #1': round((row['High'] + row['Low'] + row['Close']) / 3, 2),
                    'Lower Band #1': round((row['High'] + row['Low'] + row['Close']) / 3, 2)
                }
                df_existing = pd.concat([df_existing, pd.DataFrame([new_row])], ignore_index=True)
            
            # Save updated CSV
            df_existing.to_csv(csv_file, index=False)
            print(f"OK - Added {len(new_data)} rows")
            success_count += 1
        else:
            print("OK - Up-to-date")
            success_count += 1
            
    except Exception as e:
        print(f"FAIL - {str(e)[:40]}")
        fail_count += 1

print()
print("="*70)
print(f"Success: {success_count}/{len(csv_files)}")
print(f"Failed: {fail_count}/{len(csv_files)}")
print("="*70)

