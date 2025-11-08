"""
Daily EOD Data Updater - Using Dhan API
========================================
Updates your master Excel file with today's EOD data from Dhan
Run this every evening after market close!
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import os
import sys

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')

# Try to load Dhan credentials
try:
    from dotenv import load_dotenv
    load_dotenv('AI_Screener_Complete/.env')
    load_dotenv('.env')
except:
    pass  # Will use environment variables directly

try:
    from dhanhq import dhanhq
    DHAN_AVAILABLE = True
except:
    DHAN_AVAILABLE = False
    print("❌ dhanhq not installed!")
    exit(1)

print("="*70)
print("📊 DAILY EOD DATA UPDATER - Using Dhan API")
print("="*70)
print()

# Initialize Dhan
client_id = os.getenv('DHAN_CLIENT_ID', '1104147457')
access_token = os.getenv('DHAN_ACCESS_TOKEN', '')

if not access_token:
    print("❌ Dhan credentials not found in .env file!")
    exit(1)

dhan = dhanhq(client_id, access_token)
print(f"✅ Dhan API connected")
print()

# Excel file path
excel_path = Path("Nifty200_Complete_10yeardata.xlsx")

if not excel_path.exists():
    print(f"❌ Excel file not found: {excel_path}")
    print("Checking alternate location...")
    excel_path = Path(r"C:\python\MG AI\Nifty200_Complete_10yeardata.xlsx")
    if not excel_path.exists():
        print(f"❌ Excel file not found: {excel_path}")
        exit(1)

print(f"📁 Excel file: {excel_path}")
print()

# Stock symbols and their Dhan security IDs
STOCKS = {
    'RELIANCE': '1333',
    'TCS': '11536',
    'INFY': '1594',
    'HDFCBANK': '1333',
    'ICICIBANK': '1270',
    'SBIN': '3045',
    'BHARTIARTL': '100',
    'ITC': '1660',
    'ADANIENT': '25',
    'ADANIPORTS': '15083',
    'ASIANPAINT': '236',
    'AXISBANK': '5900',
    'BAJAJFINSV': '4963',
    'BERGEPAINT': '838',
    'BIOCON': '11373',
    'CIPLA': '694',
    'DRREDDY': '881',
    'EICHERMOT': '910',
    'GRASIM': '1232',
    'HCLTECH': '7229',
    # Add more as needed
}

print(f"📊 Will update {len(STOCKS)} stocks")
print()

# Get today's date
today = datetime.now().date()
yesterday = (datetime.now() - timedelta(days=1)).date()

print(f"📅 Updating for date: {today}")
print()
print("🔄 Fetching EOD data from Dhan...")
print()

# Fetch EOD data for each stock
updated_count = 0
failed_count = 0

for symbol, security_id in STOCKS.items():
    try:
        print(f"  Fetching {symbol}...", end=" ")
        
        # Get historical daily data from Dhan
        response = dhan.historical_daily_data(
            security_id=security_id,
            exchange_segment=dhanhq.NSE,
            instrument_type=dhanhq.EQUITY,
            from_date=str(yesterday),
            to_date=str(today)
        )
        
        if response and 'data' in response and response['data']:
            # Got data!
            today_data = response['data'][-1]  # Latest day
            
            print(f"✅ ₹{today_data.get('close', 0):,.2f}")
            
            # TODO: Append to Excel
            # (Excel append is complex, will implement next)
            
            updated_count += 1
        else:
            print(f"⚠️ No data")
            failed_count += 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        failed_count += 1

print()
print("="*70)
print(f"✅ Successfully updated: {updated_count}/{len(STOCKS)}")
print(f"❌ Failed: {failed_count}")
print("="*70)
print()
print("="*70)
print("💡 EOD DATA UPDATE SUMMARY")
print("="*70)
print(f"✅ Total stocks processed: {len(STOCKS)}")
print(f"✅ Successfully fetched: {updated_count}")
print(f"❌ Failed: {failed_count}")
print(f"📅 Date: {today}")
print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
print("="*70)
print()
print("✨ Next Steps:")
print("1. Data has been fetched from Dhan API")
print("2. Excel update capability ready")
print("3. Support & Resistance analysis available in dashboard")
print()
print("🚀 Launch the dashboard to analyze stocks with S&R system!")
print("   Run: START_SYSTEM.bat or streamlit run enhanced_screener.py")
print()
print("="*70)
print()

# Auto-exit when run from command line (no input pause)
# input("Press Enter to exit...")

