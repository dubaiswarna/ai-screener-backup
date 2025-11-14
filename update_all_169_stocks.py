"""
Update All 169 Stocks (Nifty 50 + Nifty 200 + Small Caps)
============================================================
Updates from Feb 2025 → Nov 2025 (9 months!)
"""

import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

print("="*80)
print("EOD DATA UPDATER - ALL 169 STOCKS (Nifty 50 + Nifty 200 + Small Caps)")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Get all CSV files from backtest folder
csv_files = sorted(list(Path('backtest_system/data_till_feb2025').glob('*.csv')))
print(f"Found {len(csv_files)} stock files to update")
print(f"This will take ~10-15 minutes (Yahoo Finance rate limits)")
print()

success_count = 0
fail_count = 0
updated_count = 0
total_new_rows = 0

for idx, csv_file in enumerate(csv_files, 1):
    # Extract stock symbol
    stock_name = csv_file.stem.replace('NSE_', '').replace('_1D', '')
    symbol = f"{stock_name}.NS"
    
    print(f"[{idx}/{len(csv_files)}] {stock_name:15s} ... ", end='', flush=True)
    
    try:
        # Fetch data from Yahoo Finance (from Mar 2025 onwards)
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start='2025-03-01', end=None)  # From March 1 to today
        
        if len(hist) == 0:
            print("ERROR: No data")
            fail_count += 1
            continue
        
        # Read existing CSV
        df_existing = pd.read_csv(csv_file)
        
        # Parse dates and get last date from existing data
        df_existing['time'] = pd.to_datetime(df_existing['time'], errors='coerce')
        last_date_str = df_existing['time'].max()
        # Convert to naive datetime (remove timezone if present)
        if pd.notna(last_date_str):
            last_date = pd.Timestamp(last_date_str)
            if last_date.tz is not None:
                last_date = last_date.tz_localize(None)
        else:
            last_date = pd.Timestamp('2025-02-28')  # Fallback to Feb 28
        
        # Remove timezone from Yahoo data
        hist.index = hist.index.tz_localize(None) if hist.index.tz is not None else hist.index
        
        # Get only new data (after last_date) - convert index to datetime for comparison
        hist_index_dt = pd.to_datetime(hist.index)
        new_data = hist[hist_index_dt > last_date]
        
        if len(new_data) > 0:
            # Add new rows
            for new_date, row in new_data.iterrows():
                # Calculate VWAP as (H + L + C) / 3
                vwap = (row['High'] + row['Low'] + row['Close']) / 3
                
                new_row = {
                    'time': new_date.strftime('%Y-%m-%d %H:%M:%S+05:30'),
                    'open': round(row['Open'], 2),
                    'high': round(row['High'], 2),
                    'low': round(row['Low'], 2),
                    'close': round(row['Close'], 2),
                    'volume': int(row['Volume']),
                    'vwap': round(vwap, 2)
                }
                df_existing = pd.concat([df_existing, pd.DataFrame([new_row])], ignore_index=True)
            
            # Save updated CSV
            df_existing.to_csv(csv_file, index=False)
            print(f"OK +{len(new_data)} rows")
            success_count += 1
            updated_count += 1
            total_new_rows += len(new_data)
        else:
            print("OK Up-to-date")
            success_count += 1
        
        # Rate limiting: pause every 10 stocks
        if idx % 10 == 0:
            time.sleep(2)  # 2 second pause
            
    except Exception as e:
        error_msg = str(e).replace('\n', ' ')[:60]
        print(f"ERROR: {error_msg}")
        fail_count += 1

print()
print("="*80)
print("UPDATE COMPLETE!")
print("="*80)
print(f"Total stocks: {len(csv_files)}")
print(f"Success: {success_count}")
print(f"Updated: {updated_count} stocks")
print(f"Failed: {fail_count}")
print(f"Total new rows added: {total_new_rows:,}")
print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

