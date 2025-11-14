"""
EOD Data Updater - FIXED VERSION
Updates CSV files with latest EOD data from Yahoo Finance
"""

import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime

print("="*70)
print("EOD DATA UPDATER - FIXED VERSION")
print("="*70)
print(f"Current time: {datetime.now()}")
print()

# Get all CSV files
csv_files = sorted(list(Path('Nify50_data').glob('*.csv')))
print(f"Found {len(csv_files)} CSV files to update")
print()

success_count = 0
fail_count = 0
updated_count = 0

for csv_file in csv_files:
    # Extract stock symbol
    stock_name = csv_file.stem.replace('NSE_', '').replace(', 1D', '')
    symbol = f"{stock_name}.NS"
    
    print(f"{stock_name}...", end=' ', flush=True)
    
    try:
        # Fetch last 5 days data from Yahoo Finance
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='5d')
        
        if len(hist) == 0:
            print("SKIP - No data from Yahoo")
            fail_count += 1
            continue
        
        # Read existing CSV
        df_existing = pd.read_csv(csv_file)
        
        # Get date column
        date_col = 'time' if 'time' in df_existing.columns else 'date'
        
        # Parse dates (auto-detect format)
        df_existing[date_col] = pd.to_datetime(df_existing[date_col], errors='coerce')
        last_date = df_existing[date_col].max()
        
        # Remove timezone from Yahoo data
        hist.index = hist.index.tz_localize(None)
        
        # Get only new data (after last_date)
        new_data = hist[hist.index > last_date]
        
        if len(new_data) > 0:
            # Add new rows
            for new_date, row in new_data.iterrows():
                new_row = {
                    date_col: new_date.strftime('%Y-%m-%d %H:%M:%S'),
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
            print(f"✅ UPDATED ({len(new_data)} new rows)")
            success_count += 1
            updated_count += 1
        else:
            print("✅ Up-to-date")
            success_count += 1
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)[:50]}")
        fail_count += 1

print()
print("="*70)
print(f"Success: {success_count}/{len(csv_files)}")
print(f"Updated: {updated_count}/{len(csv_files)}")
print(f"Failed: {fail_count}/{len(csv_files)}")
print("="*70)

