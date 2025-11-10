"""Simple MCX Data Updater - Gold & Silver"""
import yfinance as yf
import pandas as pd
from pathlib import Path

print("="*70)
print("MCX DATA UPDATER - Gold & Silver")
print("="*70)

commodities = [
    ('GC=F', 'MCX_GOLD, 1D.csv', 'Gold'),
    ('SI=F', 'MCX_SILVER, 1D.csv', 'Silver')
]

mcx_dir = Path('MCX_data')
mcx_dir.mkdir(exist_ok=True)

for symbol, filename, name in commodities:
    print(f"\n{name}...", end=' ')
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='2y')
        
        if len(hist) == 0:
            print("FAIL - No data")
            continue
        
        # Format data
        hist_reset = hist.reset_index()
        hist_reset['time'] = hist_reset['Date'].dt.strftime('%Y-%m-%d')
        hist_reset['VWAP'] = (hist_reset['High'] + hist_reset['Low'] + hist_reset['Close']) / 3
        hist_reset['Upper Band #1'] = hist_reset['VWAP']
        hist_reset['Lower Band #1'] = hist_reset['VWAP']
        
        output = hist_reset[['time', 'Open', 'High', 'Low', 'Close', 'Volume', 'VWAP', 'Upper Band #1', 'Lower Band #1']]
        output.columns = ['time', 'open', 'high', 'low', 'close', 'Volume', 'VWAP', 'Upper Band #1', 'Lower Band #1']
        
        output.to_csv(mcx_dir / filename, index=False)
        print(f"OK - {len(output)} rows")
        
    except Exception as e:
        print(f"FAIL - {str(e)[:40]}")

print("\n" + "="*70)
print("DONE!")
print("="*70)

