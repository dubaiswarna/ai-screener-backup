"""
Muthoot Finance AI Model - Training & Backtesting
=================================================
Period: Nov 3, 2024 to Nov 3, 2025
Generates detailed entry/exit signals with profits
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add ai_screener to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

from feature_engineering import FeatureEngineer
from xgboost_trainer import XGBoostTrainer

print("=" * 80)
print("📊 MUTHOOT FINANCE AI MODEL - COMPLETE BACKTEST")
print("=" * 80)
print()

# Stock details
SYMBOL = "MUTHOOTFIN.NS"  # Yahoo Finance symbol
STOCK_NAME = "Muthoot Finance"
BACKTEST_START = "2024-11-03"
BACKTEST_END = "2025-11-03"
TRAINING_PERIOD = "10y"  # Train on 10 years of data

print(f"📈 Stock: {STOCK_NAME} ({SYMBOL})")
print(f"📅 Backtest Period: {BACKTEST_START} to {BACKTEST_END}")
print()

# Step 1: Fetch historical data
print("Step 1: Fetching historical data from Yahoo Finance...")
print("-" * 80)

try:
    # Fetch training data (10 years)
    ticker = yf.Ticker(SYMBOL)
    df_full = ticker.history(period=TRAINING_PERIOD)
    
    if df_full.empty:
        print(f"❌ ERROR: No data found for {SYMBOL}")
        print("Please check if the stock symbol is correct.")
        sys.exit(1)
    
    print(f"✅ Fetched {len(df_full)} days of historical data")
    print(f"   Date range: {df_full.index[0].date()} to {df_full.index[-1].date()}")
    print()
    
    # Prepare data format
    df_full = df_full.reset_index()
    df_full = df_full.rename(columns={
        'Date': 'time',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })
    
    # Calculate VWAP
    df_full['vwap'] = ((df_full['high'] + df_full['low'] + df_full['close']) / 3 * df_full['volume']).cumsum() / df_full['volume'].cumsum()
    df_full['vwap'] = df_full['vwap'].fillna(df_full['close'])
    
except Exception as e:
    print(f"❌ ERROR fetching data: {e}")
    sys.exit(1)

# Step 2: Engineer features
print("Step 2: Engineering 89 technical features...")
print("-" * 80)

try:
    engineer = FeatureEngineer()
    df_features = engineer.engineer_features(df_full)
    
    if df_features is None or df_features.empty:
        print("❌ ERROR: Feature engineering failed")
        sys.exit(1)
    
    print(f"✅ Generated {len(df_features.columns)} features")
    print(f"   Features include: SMA, EMA, RSI, MACD, Bollinger Bands, etc.")
    print()
    
except Exception as e:
    print(f"❌ ERROR in feature engineering: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Prepare training data
print("Step 3: Preparing training data...")
print("-" * 80)

# Create target variable (1 = price up next day, -1 = price down, 0 = hold)
df_features['future_return'] = df_features['close'].shift(-1) / df_features['close'] - 1
df_features['target'] = 0  # hold
df_features.loc[df_features['future_return'] > 0.015, 'target'] = 1  # buy (>1.5% gain)
df_features.loc[df_features['future_return'] < -0.01, 'target'] = -1  # sell (>1% loss)

# Remove rows with NaN
df_features = df_features.dropna()

# Split into training and backtest periods
backtest_mask = (df_features['time'] >= BACKTEST_START) & (df_features['time'] <= BACKTEST_END)
df_train = df_features[~backtest_mask].copy()
df_backtest = df_features[backtest_mask].copy()

print(f"✅ Training data: {len(df_train)} days")
print(f"✅ Backtest data: {len(df_backtest)} days")
print()

# Step 4: Train XGBoost model
print("Step 4: Training XGBoost AI model...")
print("-" * 80)

try:
    # Prepare features and target
    non_feature_cols = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 
                        'target', 'future_return']
    feature_cols = [col for col in df_train.columns if col not in non_feature_cols]
    
    X_train = df_train[feature_cols]
    y_train = df_train['target']
    
    print(f"   Features: {len(feature_cols)}")
    print(f"   Training samples: {len(X_train)}")
    print()
    
    # Train model
    trainer = XGBoostTrainer()
    trainer.train(X_train, y_train)
    
    # Get accuracy
    y_pred_train = trainer.predict(X_train)
    accuracy = (y_pred_train == y_train).mean() * 100
    
    print(f"✅ Model trained successfully!")
    print(f"   Training accuracy: {accuracy:.2f}%")
    print()
    
    # Save model
    model_path = f"ai_screener/models/xgb_NSE_MUTHOOTFIN.pkl"
    trainer.save_model(model_path)
    print(f"✅ Model saved: {model_path}")
    print()
    
except Exception as e:
    print(f"❌ ERROR training model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Generate backtest signals
print("Step 5: Generating trading signals for backtest period...")
print("=" * 80)
print()

X_backtest = df_backtest[feature_cols]
predictions = trainer.predict(X_backtest)
probabilities = trainer.predict_proba(X_backtest)

# Add predictions to backtest dataframe
df_backtest['prediction'] = predictions
df_backtest['confidence'] = np.max(probabilities, axis=1)

# Map predictions to signals
signal_map = {-1: 'SELL', 0: 'HOLD', 1: 'BUY'}
df_backtest['signal'] = df_backtest['prediction'].map(signal_map)

# Step 6: Simulate trades
print("Step 6: Simulating trades with entry/exit tracking...")
print("=" * 80)
print()

trades = []
position = None  # Current position
entry_price = None
entry_date = None
entry_signal = None

PROFIT_TARGET = 0.03  # 3% profit target
STOP_LOSS = 0.015  # 1.5% stop loss
MIN_CONFIDENCE = 0.70  # 70% minimum confidence

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
            
            # Check exit conditions
            if return_pct >= PROFIT_TARGET:
                # Take profit
                profit = (current_price - entry_price) / entry_price * 100
                trades.append({
                    'Entry Date': entry_date.strftime('%Y-%m-%d'),
                    'Entry Signal': entry_signal,
                    'Entry Price': f"₹{entry_price:.2f}",
                    'Exit Date': current_date.strftime('%Y-%m-%d'),
                    'Exit Reason': 'PROFIT TARGET',
                    'Exit Price': f"₹{current_price:.2f}",
                    'Days Held': (current_date - entry_date).days,
                    'Profit %': f"{profit:.2f}%",
                    'Profit ₹': f"₹{(current_price - entry_price):.2f}"
                })
                position = None
                
            elif return_pct <= -STOP_LOSS:
                # Stop loss
                profit = (current_price - entry_price) / entry_price * 100
                trades.append({
                    'Entry Date': entry_date.strftime('%Y-%m-%d'),
                    'Entry Signal': entry_signal,
                    'Entry Price': f"₹{entry_price:.2f}",
                    'Exit Date': current_date.strftime('%Y-%m-%d'),
                    'Exit Reason': 'STOP LOSS',
                    'Exit Price': f"₹{current_price:.2f}",
                    'Days Held': (current_date - entry_date).days,
                    'Profit %': f"{profit:.2f}%",
                    'Profit ₹': f"₹{(current_price - entry_price):.2f}"
                })
                position = None
                
            elif signal == 'SELL' and confidence >= MIN_CONFIDENCE:
                # Exit on sell signal
                profit = (current_price - entry_price) / entry_price * 100
                trades.append({
                    'Entry Date': entry_date.strftime('%Y-%m-%d'),
                    'Entry Signal': entry_signal,
                    'Entry Price': f"₹{entry_price:.2f}",
                    'Exit Date': current_date.strftime('%Y-%m-%d'),
                    'Exit Reason': 'SELL SIGNAL',
                    'Exit Price': f"₹{current_price:.2f}",
                    'Days Held': (current_date - entry_date).days,
                    'Profit %': f"{profit:.2f}%",
                    'Profit ₹': f"₹{(current_price - entry_price):.2f}"
                })
                position = None
    
    # Check for new entry
    if position is None and signal == 'BUY' and confidence >= MIN_CONFIDENCE:
        position = 'LONG'
        entry_price = current_price
        entry_date = current_date
        entry_signal = f"BUY ({confidence*100:.1f}% conf)"

# Close any open position at end
if position is not None:
    current_price = df_backtest.iloc[-1]['close']
    current_date = df_backtest.iloc[-1]['time']
    profit = (current_price - entry_price) / entry_price * 100
    trades.append({
        'Entry Date': entry_date.strftime('%Y-%m-%d'),
        'Entry Signal': entry_signal,
        'Entry Price': f"₹{entry_price:.2f}",
        'Exit Date': current_date.strftime('%Y-%m-%d'),
        'Exit Reason': 'BACKTEST END',
        'Exit Price': f"₹{current_price:.2f}",
        'Days Held': (current_date - entry_date).days,
        'Profit %': f"{profit:.2f}%",
        'Profit ₹': f"₹{(current_price - entry_price):.2f}"
    })

# Step 7: Display results
print("=" * 80)
print("📊 MUTHOOT FINANCE - DETAILED TRADE HISTORY")
print("=" * 80)
print()

if not trades:
    print("⚠️  No trades executed during backtest period")
    print("   Possible reasons:")
    print("   - No BUY signals with >70% confidence")
    print("   - Market conditions didn't meet entry criteria")
else:
    df_trades = pd.DataFrame(trades)
    
    print(f"Total Trades: {len(trades)}")
    print()
    print(df_trades.to_string(index=False))
    print()
    print("=" * 80)
    
    # Calculate statistics
    print("📈 PERFORMANCE STATISTICS")
    print("=" * 80)
    print()
    
    # Extract numeric profit values
    profits = []
    for trade in trades:
        profit_str = trade['Profit %'].replace('%', '')
        profits.append(float(profit_str))
    
    winning_trades = [p for p in profits if p > 0]
    losing_trades = [p for p in profits if p < 0]
    
    win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
    avg_profit = np.mean(profits) if profits else 0
    total_profit = sum(profits)
    
    print(f"Win Rate:           {win_rate:.1f}%")
    print(f"Total Trades:       {len(trades)}")
    print(f"Winning Trades:     {len(winning_trades)}")
    print(f"Losing Trades:      {len(losing_trades)}")
    print(f"Average Profit:     {avg_profit:.2f}%")
    print(f"Best Trade:         {max(profits):.2f}%")
    print(f"Worst Trade:        {min(profits):.2f}%")
    print(f"Total Profit:       {total_profit:.2f}%")
    print()
    
    # Calculate capital growth
    initial_capital = 100000  # ₹1 lakh
    final_capital = initial_capital
    
    for profit_pct in profits:
        final_capital = final_capital * (1 + profit_pct/100)
    
    total_return = (final_capital - initial_capital) / initial_capital * 100
    
    print(f"Initial Capital:    ₹{initial_capital:,.0f}")
    print(f"Final Capital:      ₹{final_capital:,.0f}")
    print(f"Total Return:       {total_return:.2f}%")
    print(f"Profit/Loss:        ₹{final_capital - initial_capital:,.0f}")
    print()
    
    # Save to file
    output_file = f"MUTHOOT_FINANCE_BACKTEST_{BACKTEST_START}_to_{BACKTEST_END}.csv"
    df_trades.to_csv(output_file, index=False)
    print(f"✅ Results saved to: {output_file}")
    print()

print("=" * 80)
print("✅ BACKTEST COMPLETE!")
print("=" * 80)

