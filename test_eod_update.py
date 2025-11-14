"""Test EOD Update with one stock"""
import yfinance as yf
import pandas as pd
from pathlib import Path

print("Testing EOD Update Fix...")
print("="*50)

# Test with first CSV file
csv_files = list(Path('Nify50_data').glob('*.csv'))
if csv_files:
    test_file = csv_files[0]
    print(f"Testing with: {test_file.name}")
    
    # Read CSV
    df = pd.read_csv(test_file)
    print(f"CSV has {len(df)} rows")
    
    # Check date column
    date_col = 'time' if 'time' in df.columns else 'date'
    print(f"Date column: '{date_col}'")
    print(f"First 3 dates: {df[date_col].head(3).tolist()}")
    print(f"Last 3 dates: {df[date_col].tail(3).tolist()}")
    
    # Try parsing
    try:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        last_date = df[date_col].max()
        print(f"✅ Date parsing SUCCESS!")
        print(f"Last date in CSV: {last_date}")
    except Exception as e:
        print(f"❌ Date parsing FAILED: {e}")
    
    # Test Yahoo Finance fetch
    stock_name = test_file.stem.replace('NSE_', '').replace(', 1D', '')
    symbol = f"{stock_name}.NS"
    print(f"\nFetching data for {symbol}...")
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='5d')
        print(f"✅ Yahoo Finance SUCCESS! Got {len(hist)} days")
        if len(hist) > 0:
            print(f"Latest data date: {hist.index[-1]}")
    except Exception as e:
        print(f"❌ Yahoo Finance FAILED: {e}")

print("="*50)
print("Test complete!")

