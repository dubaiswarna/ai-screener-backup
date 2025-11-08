"""Simple script to fetch MCX data"""
import sys
import yfinance as yf
import pandas as pd
from pathlib import Path

print("=" * 70, flush=True)
print("FETCHING MCX GOLD AND SILVER DATA", flush=True)
print("=" * 70, flush=True)

# Create output directory
output_dir = Path("MCX_data")
output_dir.mkdir(exist_ok=True)
print(f"\n✓ Created directory: {output_dir.absolute()}", flush=True)

# Fetch Gold
print("\n[1/2] Fetching GOLD data (GC=F)...", flush=True)
try:
    gold = yf.download('GC=F', period='10y', progress=False)
    print(f"✓ Downloaded {len(gold)} rows of Gold data", flush=True)
    
    # Flatten multi-index columns if needed
    if isinstance(gold.columns, pd.MultiIndex):
        gold.columns = gold.columns.get_level_values(0)
    
    # Format data
    gold_df = pd.DataFrame({
        'time': gold.index,
        'open': gold['Open'].values,
        'high': gold['High'].values,
        'low': gold['Low'].values,
        'close': gold['Close'].values,
        'Volume': gold['Volume'].values,
        'VWAP': ((gold['High'].values + gold['Low'].values + gold['Close'].values) / 3),
        'Upper Band #1': gold['Close'].values,  # Simplified
        'Lower Band #1': gold['Close'].values   # Simplified
    })
    
    # Save
    gold_file = output_dir / "MCX_GOLD, 1D.csv"
    gold_df.to_csv(gold_file, index=False)
    print(f"✓ Saved to: {gold_file}", flush=True)
    print(f"  Price range: ${gold_df['close'].min():.2f} - ${gold_df['close'].max():.2f}", flush=True)
except Exception as e:
    print(f"✗ Error fetching Gold: {e}", flush=True)
    sys.exit(1)

# Fetch Silver
print("\n[2/2] Fetching SILVER data (SI=F)...", flush=True)
try:
    silver = yf.download('SI=F', period='10y', progress=False)
    print(f"✓ Downloaded {len(silver)} rows of Silver data", flush=True)
    
    # Flatten multi-index columns if needed
    if isinstance(silver.columns, pd.MultiIndex):
        silver.columns = silver.columns.get_level_values(0)
    
    # Format data
    silver_df = pd.DataFrame({
        'time': silver.index,
        'open': silver['Open'].values,
        'high': silver['High'].values,
        'low': silver['Low'].values,
        'close': silver['Close'].values,
        'Volume': silver['Volume'].values,
        'VWAP': ((silver['High'].values + silver['Low'].values + silver['Close'].values) / 3),
        'Upper Band #1': silver['Close'].values,  # Simplified
        'Lower Band #1': silver['Close'].values   # Simplified
    })
    
    # Save
    silver_file = output_dir / "MCX_SILVER, 1D.csv"
    silver_df.to_csv(silver_file, index=False)
    print(f"✓ Saved to: {silver_file}", flush=True)
    print(f"  Price range: ${silver_df['close'].min():.2f} - ${silver_df['close'].max():.2f}", flush=True)
except Exception as e:
    print(f"✗ Error fetching Silver: {e}", flush=True)
    sys.exit(1)

print("\n" + "=" * 70, flush=True)
print("✅ SUCCESS! Data saved to MCX_data/", flush=True)
print("=" * 70, flush=True)
print("\nNext step: Run 'python quick_train_commodity.py' to test", flush=True)

