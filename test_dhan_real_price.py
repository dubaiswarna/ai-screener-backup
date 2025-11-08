"""Test Dhan API - Fetch Real INFY Price"""
from dhanhq import dhanhq
from dhan_security_ids import get_security_id
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

client_id = os.getenv('DHAN_CLIENT_ID')
access_token = os.getenv('DHAN_ACCESS_TOKEN')

print(f"Client ID: {client_id}")
print(f"Token: {access_token[:50]}...")
print()

dhan = dhanhq(client_id, access_token)
print("✅ Dhan connection initialized")
print()

# Get INFY security ID
security_id = get_security_id('INFY')
print(f"INFY Security ID: {security_id}")
print()

# Fetch data
end_date = datetime.now().date()
start_date = (datetime.now() - timedelta(days=5)).date()

print(f"Fetching data from {start_date} to {end_date}...")
print()

response = dhan.historical_daily_data(
    security_id=security_id,
    exchange_segment='NSE',
    instrument_type='EQUITY',
    from_date=str(start_date),
    to_date=str(end_date)
)

if response and 'data' in response and response['data']:
    print("✅ Data fetched successfully!")
    print()
    latest = response['data'][-1]
    print(f"📊 INFY Latest Data:")
    print(f"   Date: {latest.get('start_Time', 'N/A')}")
    print(f"   Open: ₹{latest.get('open', 0):.2f}")
    print(f"   High: ₹{latest.get('high', 0):.2f}")
    print(f"   Low: ₹{latest.get('low', 0):.2f}")
    print(f"   Close: ₹{latest.get('close', 0):.2f}")
    print(f"   Volume: {latest.get('volume', 0):,}")
    print()
    
    actual_price = latest.get('close', 0)
    expected_price = 1478
    
    if abs(actual_price - expected_price) < 50:
        print(f"✅ CORRECT PRICE! ₹{actual_price:.2f} (Expected: ₹{expected_price})")
    else:
        print(f"⚠️ Price mismatch: ₹{actual_price:.2f} (Expected: ₹{expected_price})")
else:
    print("❌ Failed to fetch data!")
    print(f"Response: {response}")

