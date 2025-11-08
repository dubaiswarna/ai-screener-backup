"""
BIOCON Backtest with Excel Output
==================================
"""

import yfinance as yf
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

from feature_engineering import FeatureEngineer
from xgboost_trainer import XGBoostTrainer

# Configuration
SYMBOL = "BIOCON.NS"
BACKTEST_START = "2024-10-03"
BACKTEST_END = "2025-10-03"

print("Starting BIOCON Backtest...")
print(f"Period: {BACKTEST_START} to {BACKTEST_END}")

# Load model
print("\n1. Loading AI model...")
trainer = XGBoostTrainer()
trainer.load_model("ai_screener/models/xgb_NSE_BIOCON.pkl")
print("✓ Model loaded")

# Fetch data
print("\n2. Fetching data...")
ticker = yf.Ticker(SYMBOL)
df = ticker.history(start="2024-01-01", end="2025-12-31")
df = df.reset_index()
df.columns = [c.lower() for c in df.columns]
df['vwap'] = ((df['high'] + df['low'] + df['close']) / 3 * df['volume']).cumsum() / df['volume'].cumsum()
df['vwap'] = df['vwap'].fillna(df['close'])
df = df.rename(columns={'date': 'time'})
print(f"✓ Got {len(df)} days of data")

# Engineer features
print("\n3. Engineering features...")
engineer = FeatureEngineer()
df_feat = engineer.engineer_features(df)
print(f"✓ Generated {len(df_feat.columns)} features")

# Filter to backtest period
df_test = df_feat[(df_feat['time'] >= BACKTEST_START) & (df_feat['time'] <= BACKTEST_END)].copy()
print(f"✓ Backtest period: {len(df_test)} days")

# Generate predictions
print("\n4. Generating predictions...")
non_feat = ['time', 'Date', 'open', 'high', 'low', 'close', 'vwap', 'volume']
feat_cols = [c for c in df_test.columns if c not in non_feat][:89]
X = df_test[feat_cols]

preds = trainer.predict(X)
probs = trainer.predict_proba(X)

df_test['prediction'] = preds
df_test['confidence'] = np.max(probs, axis=1)
df_test['signal'] = df_test['prediction'].map({-1: 'SELL', 0: 'HOLD', 1: 'BUY'})
print(f"✓ Predictions complete")

# Simulate trades
print("\n5. Simulating trades...")
trades = []
position = None
entry_price = None
entry_date = None
entry_conf = None

for _, row in df_test.iterrows():
    if position and row['signal'] == 'SELL' and row['confidence'] >= 0.70:
        # Exit
        profit_pct = (row['close'] - entry_price) / entry_price * 100
        trades.append({
            'Entry Date': entry_date.strftime('%Y-%m-%d'),
            'Entry Price': round(entry_price, 2),
            'Entry Confidence': f"{entry_conf*100:.1f}%",
            'Exit Date': row['time'].strftime('%Y-%m-%d'),
            'Exit Price': round(row['close'], 2),
            'Days Held': (row['time'] - entry_date).days,
            'Profit %': round(profit_pct, 2),
            'Profit ₹': round(row['close'] - entry_price, 2),
            'Result': 'WIN' if profit_pct > 0 else 'LOSS'
        })
        position = None
    
    elif not position and row['signal'] == 'BUY' and row['confidence'] >= 0.70:
        # Entry
        position = 'LONG'
        entry_price = row['close']
        entry_date = row['time']
        entry_conf = row['confidence']

# Close final position
if position:
    row = df_test.iloc[-1]
    profit_pct = (row['close'] - entry_price) / entry_price * 100
    trades.append({
        'Entry Date': entry_date.strftime('%Y-%m-%d'),
        'Entry Price': round(entry_price, 2),
        'Entry Confidence': f"{entry_conf*100:.1f}%",
        'Exit Date': row['time'].strftime('%Y-%m-%d'),
        'Exit Price': round(row['close'], 2),
        'Days Held': (row['time'] - entry_date).days,
        'Profit %': round(profit_pct, 2),
        'Profit ₹': round(row['close'] - entry_price, 2),
        'Result': 'WIN' if profit_pct > 0 else 'LOSS'
    })

print(f"✓ Found {len(trades)} trades")

# Create results
if trades:
    df_trades = pd.DataFrame(trades)
    
    # Calculate stats
    wins = len([t for t in trades if t['Profit %'] > 0])
    losses = len(trades) - wins
    win_rate = wins / len(trades) * 100 if trades else 0
    avg_profit = np.mean([t['Profit %'] for t in trades])
    total_profit = sum([t['Profit %'] for t in trades])
    
    # Create summary
    summary = pd.DataFrame([{
        'Metric': 'Total Trades',
        'Value': len(trades)
    }, {
        'Metric': 'Winning Trades',
        'Value': wins
    }, {
        'Metric': 'Losing Trades',
        'Value': losses
    }, {
        'Metric': 'Win Rate %',
        'Value': round(win_rate, 1)
    }, {
        'Metric': 'Average Profit %',
        'Value': round(avg_profit, 2)
    }, {
        'Metric': 'Total Return %',
        'Value': round(total_profit, 2)
    }])
    
    # Capital growth
    capital = 100000
    growth = [{'After Trade': 0, 'Capital': capital}]
    for i, trade in enumerate(trades, 1):
        capital = capital * (1 + trade['Profit %'] / 100)
        growth.append({'After Trade': i, 'Capital': round(capital, 2)})
    df_growth = pd.DataFrame(growth)
    
    # Save to Excel
    output_file = 'BIOCON_BACKTEST_Oct2024_Oct2025.xlsx'
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df_trades.to_excel(writer, sheet_name='Trades', index=False)
        summary.to_excel(writer, sheet_name='Summary', index=False)
        df_growth.to_excel(writer, sheet_name='Capital Growth', index=False)
    
    print(f"\n✅ SUCCESS!")
    print(f"Excel file created: {output_file}")
    print(f"\nQuick Summary:")
    print(f"Total Trades: {len(trades)}")
    print(f"Win Rate: {win_rate:.1f}%")
    print(f"Total Return: {total_profit:.2f}%")
    print(f"Final Capital: ₹{capital:,.0f}")
else:
    print("\n⚠️ No trades generated in this period")

print("\nDone!")

