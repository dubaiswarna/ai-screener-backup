"""
Run Full AI Screening
======================
Runs all 42 AI models and generates signals
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'ai_screener'))

from ai_screener.feature_engineering import FeatureEngineer
from ai_screener.signal_generator_fixed import SignalGeneratorFixed
from ai_screener.live_data_loader import LiveDataLoader
from ai_screener.save_signals_csv import save_signals_to_csv
import pandas as pd
from datetime import datetime

print("="*70)
print("🚀 RUNNING FULL AI SCREENING - ALL 42 MODELS")
print("="*70)
print()

# Load AI models
print("🤖 Loading your 42 trained AI models...")
models_dir = Path('ai_screener/models')
signal_gen = SignalGeneratorFixed(models_dir=str(models_dir))

stocks = []
for model_file in models_dir.glob("xgb_NSE_*.pkl"):
    symbol = model_file.stem.replace("xgb_", "")
    if signal_gen.load_model(symbol):
        stocks.append(symbol)

print(f"✅ Loaded {len(stocks)} AI models")
print()

# Fetch data and engineer features
print("📊 Fetching EOD data and engineering features...")
print()

live_loader = LiveDataLoader()
engineer = FeatureEngineer()
featured_data = {}

for i, symbol in enumerate(stocks, 1):
    print(f"  [{i}/{len(stocks)}] Processing {symbol}...", end=" ")
    
    try:
        df = live_loader.fetch_live_data(symbol, period="3mo")
        if df is not None and not df.empty:
            df_features = engineer.engineer_features(df)
            if df_features is not None and not df_features.empty:
                featured_data[symbol] = df_features
                print("✅")
            else:
                print("⚠️ No features")
        else:
            print("⚠️ No data")
    except Exception as e:
        print(f"❌ {e}")

print()
print(f"✅ Successfully processed {len(featured_data)} stocks")
print()

# Generate signals
print("🤖 Generating AI signals...")
print()

signals_list = signal_gen.generate_signals_batch(
    symbols=list(featured_data.keys()),
    featured_data=featured_data
)

if signals_list:
    df_signals = pd.DataFrame(signals_list)
    
    print("="*70)
    print("📊 AI SCREENING RESULTS")
    print("="*70)
    print()
    
    # Summary
    print(f"Total Signals Generated: {len(df_signals)}")
    print()
    
    buy_count = len(df_signals[df_signals['signal'].str.lower() == 'buy'])
    sell_count = len(df_signals[df_signals['signal'].str.lower() == 'sell'])
    hold_count = len(df_signals[df_signals['signal'].str.lower() == 'hold'])
    
    print(f"  BUY signals:  {buy_count}")
    print(f"  SELL signals: {sell_count}")
    print(f"  HOLD signals: {hold_count}")
    print()
    
    # Confidence stats
    min_conf = df_signals['confidence'].min()
    max_conf = df_signals['confidence'].max()
    avg_conf = df_signals['confidence'].mean()
    
    print(f"Confidence Range: {min_conf:.1%} to {max_conf:.1%}")
    print(f"Average Confidence: {avg_conf:.1%}")
    print()
    
    # Filter high-confidence BUY/SELL signals
    df_actionable = df_signals[df_signals['confidence'] >= 0.70]
    df_actionable = df_actionable[df_actionable['signal'].str.upper().isin(['BUY', 'SELL'])]
    
    print("="*70)
    print(f"🎯 HIGH-CONFIDENCE SIGNALS (>70% confidence, BUY/SELL only)")
    print("="*70)
    print()
    
    if not df_actionable.empty:
        print(f"Total Actionable Signals: {len(df_actionable)}")
        print()
        
        # Show each signal
        for idx, row in df_actionable.iterrows():
            signal_type = str(row['signal']).upper()
            symbol = row['symbol']
            conf = row['confidence']
            price = row.get('current_price', 0)
            
            print(f"{idx+1}. {symbol:20} {signal_type:5} @ ₹{price:8,.2f} | Confidence: {conf:6.1%}")
        
        print()
        print("="*70)
        
        # Save to CSV
        csv_path = save_signals_to_csv(df_actionable)
        print(f"💾 Signals saved to: {csv_path}")
        print()
        
        # Also save full report
        full_csv = f"full_screening_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df_signals.to_csv(full_csv, index=False)
        print(f"📄 Full report saved to: {full_csv}")
        print()
        
        print("="*70)
        print("✅ SCREENING COMPLETE!")
        print("="*70)
        print()
        print("Next steps:")
        print("1. Review signals in CSV file")
        print("2. Open P&L tracker: http://localhost:8505")
        print("3. Plan your trades for tomorrow!")
        
    else:
        print("⚠️ No high-confidence BUY/SELL signals today")
        print("   (All signals are HOLD or low confidence)")
    
else:
    print("❌ Could not generate signals")

print()
input("Press Enter to exit...")

