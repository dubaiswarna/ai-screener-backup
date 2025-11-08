"""
BIOCON AI Model - Backtesting
==============================
Period: Nov 3, 2024 to Nov 3, 2025 (or latest available)
Uses existing trained model - FAST execution!
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add ai_screener to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

from feature_engineering import FeatureEngineer
from xgboost_trainer import XGBoostTrainer

print("=" * 80)
print("📊 BIOCON AI MODEL - COMPLETE BACKTEST")
print("=" * 80)
print()

# Stock details
SYMBOL = "BIOCON.NS"
STOCK_NAME = "Biocon Ltd"
BACKTEST_START = "2024-10-03"
BACKTEST_END = "2025-10-03"

print(f"📈 Stock: {STOCK_NAME} ({SYMBOL})")
print(f"📅 Backtest Period: {BACKTEST_START} to {BACKTEST_END}")
print(f"🤖 Model: Pre-trained XGBoost (xgb_NSE_BIOCON.pkl)")
print()

# Step 1: Load the trained model
print("Step 1: Loading pre-trained AI model...")
print("-" * 80)

model_path = "ai_screener/models/xgb_NSE_BIOCON.pkl"
if not os.path.exists(model_path):
    print(f"❌ ERROR: Model not found at {model_path}")
    sys.exit(1)

trainer = XGBoostTrainer()
trainer.load_model(model_path)
print(f"✅ Model loaded successfully from {model_path}")
print()

# Step 2: Fetch backtest period data
print("Step 2: Fetching data from Yahoo Finance...")
print("-" * 80)

try:
    ticker = yf.Ticker(SYMBOL)
    # Fetch more data for better feature calculation
    df = ticker.history(start="2024-01-01", end="2025-11-30")
    
    if df.empty:
        print(f"❌ ERROR: No data found for {SYMBOL}")
        sys.exit(1)
    
    print(f"✅ Fetched {len(df)} days of data")
    print(f"   Date range: {df.index[0].date()} to {df.index[-1].date()}")
    print()
    
    # Prepare data format
    df = df.reset_index()
    df = df.rename(columns={
        'Date': 'time',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })
    
    # Calculate VWAP
    df['vwap'] = ((df['high'] + df['low'] + df['close']) / 3 * df['volume']).cumsum() / df['volume'].cumsum()
    df['vwap'] = df['vwap'].fillna(df['close'])
    
except Exception as e:
    print(f"❌ ERROR fetching data: {e}")
    sys.exit(1)

# Step 3: Engineer features
print("Step 3: Engineering features...")
print("-" * 80)

try:
    engineer = FeatureEngineer()
    df_features = engineer.engineer_features(df)
    
    if df_features is None or df_features.empty:
        print("❌ ERROR: Feature engineering failed")
        sys.exit(1)
    
    print(f"✅ Generated {len(df_features.columns)} features")
    print()
    
except Exception as e:
    print(f"❌ ERROR in feature engineering: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Filter to backtest period
df_backtest = df_features[
    (df_features['time'] >= BACKTEST_START) & 
    (df_features['time'] <= BACKTEST_END)
].copy()

print(f"✅ Backtest period: {len(df_backtest)} days")
print()

# Step 4: Generate predictions
print("Step 4: Generating AI predictions...")
print("-" * 80)

try:
    # Prepare features - use same columns model was trained on
    non_feature_cols = ['time', 'Date', 'open', 'high', 'low', 'close', 'vwap', 'volume',
                       'OPEN', 'HIGH', 'LOW', 'VOLUME', 'VWAP', 'series', 'CH_TIMESTAMP']
    feature_cols = [col for col in df_backtest.columns if col not in non_feature_cols]
    
    print(f"Using {len(feature_cols)} features for prediction")
    
    X = df_backtest[feature_cols]
    
    # Ensure we have exactly the right number of features
    if len(feature_cols) != 89:
        print(f"⚠️  Warning: Expected 89 features, got {len(feature_cols)}")
        print(f"   Adjusting feature set...")
        # Take first 89 features if we have more
        if len(feature_cols) > 89:
            feature_cols = feature_cols[:89]
            X = df_backtest[feature_cols]
    
    predictions = trainer.predict(X)
    probabilities = trainer.predict_proba(X)
    
    df_backtest['prediction'] = predictions
    df_backtest['confidence'] = np.max(probabilities, axis=1)
    
    # Map predictions to signals
    signal_map = {-1: 'SELL', 0: 'HOLD', 1: 'BUY'}
    df_backtest['signal'] = df_backtest['prediction'].map(signal_map)
    
    print(f"✅ Predictions generated for {len(df_backtest)} days")
    print()
    
except Exception as e:
    print(f"❌ ERROR generating predictions: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Simulate trades
print("Step 5: Simulating trades...")
print("=" * 80)
print()

trades = []
position = None
entry_price = None
entry_date = None
entry_signal = None
entry_confidence = None

PROFIT_TARGET = 0.03  # 3%
STOP_LOSS = 0.015     # 1.5%
MIN_CONFIDENCE = 0.70  # 70%

for idx, row in df_backtest.iterrows():
    current_date = row['time']
    current_price = row['close']
    signal = row['signal']
    confidence = row['confidence']
    
    # Check if we're in a position
    if position is not None:
        # Calculate current return
        if position == 'LONG':
            return_pct = (current_price - entry_price) / entry_price
            days_held = (current_date - entry_date).days
            
            # Exit conditions
            exit_reason = None
            
            if return_pct >= PROFIT_TARGET:
                exit_reason = 'PROFIT TARGET HIT'
            elif return_pct <= -STOP_LOSS:
                exit_reason = 'STOP LOSS HIT'
            elif signal == 'SELL' and confidence >= MIN_CONFIDENCE:
                exit_reason = 'AI SELL SIGNAL'
            elif days_held >= 30:  # Max holding period
                exit_reason = 'MAX HOLDING (30 days)'
            
            if exit_reason:
                profit_pct = return_pct * 100
                profit_amount = current_price - entry_price
                
                trades.append({
                    'Entry Date': entry_date.strftime('%Y-%m-%d'),
                    'Entry Signal': entry_signal,
                    'Entry Price': entry_price,
                    'Exit Date': current_date.strftime('%Y-%m-%d'),
                    'Exit Reason': exit_reason,
                    'Exit Price': current_price,
                    'Days Held': days_held,
                    'Profit %': profit_pct,
                    'Profit ₹': profit_amount,
                    'Result': '✅ WIN' if profit_pct > 0 else '❌ LOSS'
                })
                position = None
    
    # Check for new entry
    if position is None and signal == 'BUY' and confidence >= MIN_CONFIDENCE:
        position = 'LONG'
        entry_price = current_price
        entry_date = current_date
        entry_confidence = confidence
        entry_signal = f"BUY ({confidence*100:.1f}%)"

# Close any open position at end
if position is not None:
    current_price = df_backtest.iloc[-1]['close']
    current_date = df_backtest.iloc[-1]['time']
    profit_pct = (current_price - entry_price) / entry_price * 100
    profit_amount = current_price - entry_price
    
    trades.append({
        'Entry Date': entry_date.strftime('%Y-%m-%d'),
        'Entry Signal': entry_signal,
        'Entry Price': entry_price,
        'Exit Date': current_date.strftime('%Y-%m-%d'),
        'Exit Reason': 'BACKTEST END',
        'Exit Price': current_price,
        'Days Held': (current_date - entry_date).days,
        'Profit %': profit_pct,
        'Profit ₹': profit_amount,
        'Result': '✅ WIN' if profit_pct > 0 else '❌ LOSS'
    })

# Step 6: Display results
print()
print("=" * 80)
print("📊 BIOCON - DETAILED TRADE HISTORY")
print("=" * 80)
print()

if not trades:
    print("⚠️  No trades executed during backtest period")
    print()
    print("Possible reasons:")
    print("  - No BUY signals with confidence >= 70%")
    print("  - Market conditions didn't meet entry criteria")
    print()
else:
    # Display each trade
    for i, trade in enumerate(trades, 1):
        print(f"Trade #{i}:")
        print(f"  Entry:  {trade['Entry Date']} | {trade['Entry Signal']}")
        print(f"          ₹{trade['Entry Price']:.2f}")
        print()
        print(f"  Exit:   {trade['Exit Date']} | {trade['Exit Reason']}")
        print(f"          ₹{trade['Exit Price']:.2f}")
        print()
        print(f"  Result: {trade['Days Held']} days | {trade['Profit %']:+.2f}% | ₹{trade['Profit ₹']:+.2f}")
        print(f"          {trade['Result']}")
        print()
        print("-" * 80)
        print()
    
    # Statistics
    print("=" * 80)
    print("📈 PERFORMANCE STATISTICS")
    print("=" * 80)
    print()
    
    profits = [t['Profit %'] for t in trades]
    winning_trades = [p for p in profits if p > 0]
    losing_trades = [p for p in profits if p < 0]
    
    win_rate = len(winning_trades) / len(trades) * 100
    avg_profit = np.mean(profits)
    total_profit = sum(profits)
    avg_days = np.mean([t['Days Held'] for t in trades])
    
    print(f"Total Trades:          {len(trades)}")
    print(f"Winning Trades:        {len(winning_trades)} ✅")
    print(f"Losing Trades:         {len(losing_trades)} ❌")
    print(f"Win Rate:              {win_rate:.1f}%")
    print()
    print(f"Average Profit/Trade:  {avg_profit:+.2f}%")
    print(f"Best Trade:            +{max(profits):.2f}%")
    print(f"Worst Trade:           {min(profits):.2f}%")
    print(f"Total Cumulative:      {total_profit:+.2f}%")
    print()
    print(f"Average Hold Time:     {avg_days:.1f} days")
    print()
    
    # Capital growth simulation
    initial_capital = 100000
    capital = initial_capital
    
    print("💰 CAPITAL GROWTH (Starting with ₹1,00,000):")
    print()
    for i, profit_pct in enumerate(profits, 1):
        trade_profit = capital * (profit_pct / 100)
        capital += trade_profit
        print(f"  After Trade #{i}: ₹{capital:,.0f} ({trade_profit:+,.0f})")
    
    print()
    total_return = (capital - initial_capital) / initial_capital * 100
    print(f"Initial Capital:       ₹{initial_capital:,.0f}")
    print(f"Final Capital:         ₹{capital:,.0f}")
    print(f"Total Return:          {total_return:+.2f}%")
    print(f"Net Profit/Loss:       ₹{capital - initial_capital:+,.0f}")
    print()
    
    # Save results
    df_trades = pd.DataFrame(trades)
    output_file = "BIOCON_BACKTEST_RESULTS.csv"
    df_trades.to_csv(output_file, index=False)
    print(f"✅ Results saved to: {output_file}")
    print()

print("=" * 80)
print("✅ BIOCON BACKTEST COMPLETE!")
print("=" * 80)

