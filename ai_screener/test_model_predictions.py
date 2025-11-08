# -*- coding: utf-8 -*-
"""
Quick test to see what models are actually predicting
Use this tomorrow to verify the feature fix!
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_engineering import FeatureEngineer
from signal_generator_fixed import SignalGeneratorFixed
from excel_data_loader import ExcelDataLoader
import pandas as pd

# Load Excel
excel_loader = ExcelDataLoader(r"C:\python\MG AI\Nifty200_Complete_10yeardata.xlsx")

# Load top 5 models
models_dir = Path(__file__).parent / 'models'
signal_gen = SignalGeneratorFixed(models_dir=str(models_dir))

top_5 = ['NSE_RELIANCE', 'NSE_TCS', 'NSE_HDFCBANK', 'NSE_INFY', 'NSE_ICICIBANK']

print("\n" + "="*60)
print("LOADING MODELS")
print("="*60)

for symbol in top_5:
    signal_gen.load_model(symbol)

# Test on February 2025 data
print("\n" + "="*60)
print("TESTING PREDICTIONS FOR FEBRUARY 28, 2025")
print("="*60)

engineer = FeatureEngineer()

for symbol in top_5:
    df = excel_loader.get_stock_data(symbol)
    if df is None:
        print(f"\n{symbol}: No data available")
        continue
    
    # Filter to February 28, 2025
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['date'] <= '2025-02-28']
    
    if len(df) < 50:
        print(f"\n{symbol}: Insufficient data")
        continue
    
    # Ensure columns
    if 'vwap' not in df.columns and 'high' in df.columns:
        df['vwap'] = (df['high'] + df['low'] + df['close']) / 3
    
    if 'volume' not in df.columns:
        df['volume'] = df['close'] * 1000
    
    # Engineer features
    df_features = engineer.engineer_features(df)
    
    if df_features is None or df_features.empty:
        print(f"\n{symbol}: Feature engineering failed")
        continue
    
    print(f"\n{symbol}:")
    print(f"  Features generated: {len(df_features.columns)}")
    
    # Generate signal
    signal = signal_gen.generate_signal(symbol, df_features)
    
    if 'error' in signal:
        print(f"  ❌ ERROR: {signal['error']}")
    else:
        print(f"  ✅ Raw Prediction: {signal.get('prediction', 'N/A')}")
        print(f"  Signal: {signal['signal']}")
        print(f"  Confidence: {signal['confidence']*100:.1f}%")
        if 'current_price' in signal:
            print(f"  Price: ₹{signal['current_price']:.2f}")

print("\n" + "="*60)
print("LEGEND: -1 = SELL, 0 = HOLD, 1 = BUY")
print("="*60)
print("\n✅ If you see actual predictions (-1, 0, 1), feature fix worked!")
print("❌ If you see 'Feature shape mismatch', features still need fixing")
print("="*60)
