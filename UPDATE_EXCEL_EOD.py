# -*- coding: utf-8 -*-
"""
Update Excel with Latest EOD Data from Dhan API
Updates ALL stocks in the Excel file
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent / 'ai_screener'))

try:
    from dhanhq import dhanhq
except:
    print("[ERROR] dhanhq not installed!")
    sys.exit(1)

print("="*70)
print("UPDATING EXCEL WITH LATEST EOD DATA")
print("="*70)
print()

# Initialize Dhan
client_id = "1104147457"
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzYyNTg4MzAyLCJpYXQiOjE3NjI1MDE5MDIsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTA0MTQ3NDU3In0.8Hh2Rnz-jDv15U4g3tTv6ZTgJXR70WUPjMVAPtZpv-sQ-AxoBji1GnC2H4RA1YQrkWY0Pa2jXJjKdEzTjrmnSA"

try:
    dhan = dhanhq(client_id, access_token)
    print("[OK] Dhan API connected")
except Exception as e:
    print(f"[ERROR] Dhan connection failed: {e}")
    sys.exit(1)

# Excel file
excel_file = Path(r"C:\python\MG AI\Nifty200_Complete_10yeardata.xlsx")

if not excel_file.exists():
    print(f"[ERROR] Excel not found: {excel_file}")
    sys.exit(1)

print(f"[OK] Excel file: {excel_file.name}")
print()

# Load Excel to get all stock symbols
from excel_data_loader import ExcelDataLoader

try:
    loader = ExcelDataLoader(str(excel_file))
    all_stocks = loader.get_all_available_stocks()
    print(f"[OK] Found {len(all_stocks)} stocks in Excel")
except Exception as e:
    print(f"[ERROR] Failed to load Excel: {e}")
    sys.exit(1)

print()
print(f"[*] Fetching latest data for {len(all_stocks)} stocks...")
print()

# Date range (last 5 days to be safe)
to_date = datetime.now().strftime('%Y-%m-%d')
from_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')

print(f"Date range: {from_date} to {to_date}")
print()

# Symbol to Security ID mapping (you'll need to expand this)
# For now, using a subset - can be expanded with full Dhan scrip master
SECURITY_MAP = {
    'RELIANCE': '2885', 'TCS': '11536', 'HDFCBANK': '1333',
    'INFY': '1594', 'ICICIBANK': '4963', 'SBIN': '3045',
    'BHARTIARTL': '3365', 'KOTAKBANK': '1922', 'HINDUNILVR': '1394',
    'AXISBANK': '5900', 'GRASIM': '1232', 'ASIANPAINT': '340',
    'TITAN': '3506', 'SUNPHARMA': '3351', 'TATASTEEL': '3499',
    'TATAMOTORS': '3456', 'BAJAJFINSV': '16675', 'ADANIPORTS': '15083',
    'NTPC': '11630', 'ONGC': '2475', 'POWERGRID': '14977',
    'CIPLA': '694', 'DRREDDY': '1076', 'EICHERMOT': '882',
    'ADANIENT': '25', 'BIOCON': '11373', 'HCLTECH': '7229',
    'ITC': '1660', 'MARUTI': '10999', 'BAJFINANCE': '16675'
}

# Process stocks
updated_stocks = []
failed_stocks = []

for symbol in all_stocks:
    security_id = SECURITY_MAP.get(symbol)
    
    if security_id is None:
        # Skip stocks without security ID mapping
        continue
    
    try:
        print(f"  {symbol}...", end=" ")
        
        # Fetch data from Dhan (use security_id, not symbol)
        response = dhan.historical_daily_data(
            security_id=security_id,       # Use security ID
            exchange_segment=dhan.NSE,     # NSE_EQ
            instrument_type=0,              # 0 = EQUITY (numeric code)
            from_date=from_date,
            to_date=to_date,
            expiry_code=0
        )
        
        if response and response.get('status') == 'success' and 'data' in response:
            data = response['data']
            
            # Dhan returns data as dict with arrays
            if isinstance(data, dict) and 'timestamp' in data:
                # Get all rows
                timestamps = data['timestamp']
                opens = data['open']
                highs = data['high']
                lows = data['low']
                closes = data['close']
                volumes = data['volume']
                
                # Create DataFrame from all new data
                new_data = []
                for i in range(len(timestamps)):
                    new_data.append({
                        'time': pd.to_datetime(timestamps[i], unit='s'),
                        'open': opens[i],
                        'high': highs[i],
                        'low': lows[i],
                        'close': closes[i],
                        'volume': volumes[i]
                    })
                
                new_df = pd.DataFrame(new_data)
                
                # Load existing stock data
                existing_df = loader.get_stock_data(symbol)
                
                if existing_df is not None:
                    # Ensure time columns are datetime and remove timezone for comparison
                    existing_df['time'] = pd.to_datetime(existing_df['time']).dt.tz_localize(None)
                    new_df['time'] = pd.to_datetime(new_df['time']).dt.tz_localize(None)
                    
                    # Find which rows are actually new
                    existing_dates = set(existing_df['time'].dt.date)
                    new_rows = new_df[~new_df['time'].dt.date.isin(existing_dates)]
                    
                    if len(new_rows) > 0:
                        # Append new data
                        updated_df = pd.concat([existing_df, new_rows], ignore_index=True)
                        updated_df = updated_df.sort_values('time').reset_index(drop=True)
                        
                        # Save back to Excel (update the specific sheet)
                        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                            updated_df.to_excel(writer, sheet_name=symbol, index=False)
                        
                        latest_close = closes[-1]
                        print(f"[OK] +{len(new_rows)} days, Latest: ₹{latest_close:.2f}")
                        updated_stocks.append(symbol)
                    else:
                        print(f"[SKIP] Already up-to-date")
                else:
                    print(f"[ERROR] No existing data")
                    failed_stocks.append(symbol)
        else:
            print(f"[ERROR] No data from API")
            failed_stocks.append(symbol)
            
    except Exception as e:
        print(f"[ERROR] {str(e)[:50]}")
        failed_stocks.append(symbol)

print()
print("="*70)
print(f"[OK] Updated: {len(updated_stocks)} stocks")
print(f"[SKIP] Already current or no mapping: {len(all_stocks) - len(updated_stocks) - len(failed_stocks)}")
print(f"[ERROR] Failed: {len(failed_stocks)}")
print("="*70)
print()

if updated_stocks:
    print(f"Updated stocks: {', '.join(updated_stocks[:20])}")
    if len(updated_stocks) > 20:
        print(f"... and {len(updated_stocks)-20} more")

print()
print("[OK] Excel update complete!")
print(f"[OK] File: {excel_file}")
print()

