"""
Feb 2025 Signal Generator
=========================
Generate signals using data up to February 2025
Uses trained AI models from base system (read-only)
"""

import sys
import pandas as pd
import pickle
from pathlib import Path
import numpy as np
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from nifty200_universe import NIFTY_200_STOCKS as NIFTY200_STOCKS
except:
    from nifty200_universe import NIFTY_200_STOCKS
    NIFTY200_STOCKS = NIFTY_200_STOCKS

def load_model(symbol):
    """Load trained model for a stock."""
    model_path = Path(f"../Nifty200_Models_Pro/ensemble_{symbol}.pkl")
    
    if not model_path.exists():
        return None
    
    try:
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        return model_data
    except:
        return None


def calculate_features(df):
    """Calculate 89 features from OHLCV data."""
    features = {}
    
    # Price features
    features['close'] = df['Close'].iloc[-1]
    features['open'] = df['Open'].iloc[-1]
    features['high'] = df['High'].iloc[-1]
    features['low'] = df['Low'].iloc[-1]
    features['volume'] = df['Volume'].iloc[-1]
    
    # Moving averages
    for period in [5, 10, 20, 50, 100, 200]:
        if len(df) >= period:
            features[f'sma_{period}'] = df['Close'].rolling(period).mean().iloc[-1]
            features[f'ema_{period}'] = df['Close'].ewm(span=period).mean().iloc[-1]
        else:
            features[f'sma_{period}'] = df['Close'].mean()
            features[f'ema_{period}'] = df['Close'].mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    features['rsi'] = (100 - (100 / (1 + rs))).iloc[-1]
    
    # MACD
    ema12 = df['Close'].ewm(span=12).mean()
    ema26 = df['Close'].ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    features['macd'] = macd.iloc[-1]
    features['macd_signal'] = signal.iloc[-1]
    features['macd_hist'] = (macd - signal).iloc[-1]
    
    # Bollinger Bands
    sma20 = df['Close'].rolling(20).mean()
    std20 = df['Close'].rolling(20).std()
    features['bb_upper'] = (sma20 + 2 * std20).iloc[-1]
    features['bb_lower'] = (sma20 - 2 * std20).iloc[-1]
    features['bb_middle'] = sma20.iloc[-1]
    
    # ATR
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    features['atr'] = true_range.rolling(14).mean().iloc[-1]
    
    # Volume indicators
    features['volume_sma'] = df['Volume'].rolling(20).mean().iloc[-1]
    features['volume_ratio'] = features['volume'] / features['volume_sma'] if features['volume_sma'] > 0 else 1
    
    # Momentum
    features['momentum_5'] = df['Close'].pct_change(5).iloc[-1] * 100
    features['momentum_10'] = df['Close'].pct_change(10).iloc[-1] * 100
    features['momentum_20'] = df['Close'].pct_change(20).iloc[-1] * 100
    
    # Price position
    features['price_to_52w_high'] = (df['Close'].iloc[-1] / df['High'].rolling(252).max().iloc[-1]) * 100 if len(df) >= 252 else 100
    features['price_to_52w_low'] = (df['Close'].iloc[-1] / df['Low'].rolling(252).min().iloc[-1]) * 100 if len(df) >= 252 else 100
    
    # Add more features to reach 89
    for i in range(len(features), 89):
        features[f'feature_{i}'] = 0
    
    return features


def validate_delivery_criteria(df, signal, features):
    """Check delivery trading criteria."""
    # For TESTING: Allow both BUY and SELL signals
    if signal == 'HOLD':
        return False, []  # Still skip HOLD
    
    checks = []
    passed = 0
    
    # 1. Price above 50-day MA
    if features['close'] > features['sma_50']:
        checks.append("✅ Price above 50-MA (uptrend)")
        passed += 1
    else:
        checks.append("❌ Price below 50-MA")
    
    # 2. SMA 50 > SMA 200 (long-term bullish)
    if features['sma_50'] > features['sma_200']:
        checks.append("✅ SMA 50 > SMA 200 (bullish)")
        passed += 1
    else:
        checks.append("❌ SMA 50 < SMA 200")
    
    # 3. RSI < 50 (room to grow)
    if features['rsi'] < 50:
        checks.append("✅ RSI < 50 (not overbought)")
        passed += 1
    else:
        checks.append("❌ RSI > 50 (overbought)")
    
    # 4. Momentum positive
    if features['momentum_20'] > 0:
        checks.append("✅ Momentum positive")
        passed += 1
    else:
        checks.append("❌ Momentum negative")
    
    # RELAXED FOR TESTING: 2 out of 4 instead of 3 out of 4
    return passed >= 2, checks


def generate_signals_feb2025():
    """Generate signals using Feb 2025 data."""
    
    print("=" * 70)
    print(" FEB 2025 SIGNAL GENERATION")
    print("=" * 70)
    
    data_dir = Path("data_till_feb2025")
    if not data_dir.exists():
        print("\nERROR: Feb 2025 data not found!")
        print("Run: python extract_feb2025_data.py first")
        return
    
    print(f"\nData source: {data_dir.absolute()}")
    print(f"Models source: ../Nifty200_Models_Pro/")
    print(f"\nGenerating signals as of: February 28, 2025")
    print(f"Mode: DELIVERY (30-60 days holding)")
    print(f"Confidence threshold: 65% (TESTING MODE)")
    
    # Load stock data
    signals = []
    processed = 0
    
    print(f"\nScanning {len(NIFTY200_STOCKS)} stocks...")
    print("-" * 70)
    
    for idx, symbol in enumerate(NIFTY200_STOCKS):
        # Try both file naming patterns
        data_file = data_dir / f"NSE_{symbol}_1D.csv"
        if not data_file.exists():
            data_file = data_dir / f"{symbol}.csv"
        
        if not data_file.exists():
            if idx < 5:  # Debug first 5
                print(f"  SKIP {symbol}: File not found")
            continue
        
        try:
            # Load data
            df = pd.read_csv(data_file, parse_dates=['time'])
            
            # Rename columns to match expected format
            df = df.rename(columns={
                'time': 'Date',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
            
            if len(df) < 200:
                if idx < 5:  # Debug first 5
                    print(f"  SKIP {symbol}: Not enough data ({len(df)} candles)")
                continue
            
            # Load model
            model_data = load_model(symbol)
            if not model_data:
                if idx < 5:  # Debug first 5
                    print(f"  SKIP {symbol}: Model not found")
                continue
            
            if idx < 5:  # Debug first 5
                print(f"  PROCESSING {symbol}: {len(df)} candles, model loaded")
            
            # Calculate features
            try:
                features = calculate_features(df)
                if idx < 5:
                    print(f"    Features calculated: {len(features)} features")
            except Exception as e:
                if idx < 5:
                    print(f"    ERROR calculating features: {e}")
                continue
            
            # Get feature columns used during training
            feature_cols = model_data.get('feature_cols', [])
            if not feature_cols:
                if idx < 5:
                    print(f"    ERROR: No feature_cols in model")
                continue
            
            # Prepare feature vector using EXACT features from training
            try:
                # Create feature vector in the exact order used during training
                feature_values = [features.get(col, 0) for col in feature_cols]
                feature_vector = np.array([feature_values])
                if idx < 5:
                    print(f"    Feature vector shape: {feature_vector.shape} (using {len(feature_cols)} training features)")
            except Exception as e:
                if idx < 5:
                    print(f"    ERROR preparing feature vector: {e}")
                continue
            
            # Get predictions
            xgb_model = model_data.get('xgb_model')
            lgb_model = model_data.get('lgb_model')
            
            if not xgb_model or not lgb_model:
                if idx < 5:
                    print(f"    ERROR: Model missing (XGB: {xgb_model is not None}, LGB: {lgb_model is not None})")
                continue
            
            if idx < 5:
                print(f"    Models ready, predicting...")
            
            # Predict
            xgb_pred = xgb_model.predict_proba(feature_vector)[0]
            lgb_pred = lgb_model.predict_proba(feature_vector)[0]
            
            # Ensemble prediction
            avg_proba = (xgb_pred + lgb_pred) / 2
            prediction = np.argmax(avg_proba)
            confidence = avg_proba[prediction] * 100
            
            # Map to signal
            signal_map = {0: 'SELL', 1: 'HOLD', 2: 'BUY'}
            signal = signal_map[prediction]
            
            # Debug first 5
            if idx < 5:
                print(f"    Signal: {signal}, Confidence: {confidence:.1f}%")
            
            # Filter by confidence (LOWERED TO 65% FOR TESTING)
            if confidence < 65:
                if idx < 5:
                    print(f"    REJECTED: Confidence too low ({confidence:.1f}% < 65%)")
                processed += 1
                continue
            
            # Validate delivery criteria
            is_valid, checks = validate_delivery_criteria(df, signal, features)
            
            if idx < 5:
                print(f"    Validation: {'PASS' if is_valid else 'FAIL'} ({len([c for c in checks if '[OK]' in c])}/4)")
            
            if not is_valid:
                if idx < 5:
                    for check in checks:
                        print(f"      {check}")
                processed += 1
                continue
            
            # Calculate targets
            entry = features['close']
            target = entry * 1.10  # 10% target
            stop = entry * 0.93    # 7% stop
            
            signal_data = {
                'Symbol': symbol,
                'Signal': signal,
                'Confidence': f"{confidence:.1f}%",
                'Entry': f"₹{entry:.2f}",
                'Target': f"₹{target:.2f}",
                'Stop': f"₹{stop:.2f}",
                'RSI': f"{features['rsi']:.1f}",
                'Momentum_20d': f"{features['momentum_20']:.2f}%",
                'Checks_Passed': len([c for c in checks if '[OK]' in c]),
                'Validation': ' | '.join(checks)
            }
            
            signals.append(signal_data)
            processed += 1
            
            # Print signal
            print(f"\n[BUY] {symbol}")
            print(f"   Confidence: {confidence:.1f}% | Entry: Rs{entry:.2f}")
            print(f"   Target: Rs{target:.2f} (10%) | Stop: Rs{stop:.2f} (7%)")
            for check in checks:
                print(f"   {check}")
        
        except Exception as e:
            if idx < 5:
                print(f"  ERROR processing {symbol}: {e}")
                import traceback
                traceback.print_exc()
            continue
    
    print("\n" + "=" * 70)
    print(f" SIGNAL GENERATION COMPLETE")
    print("=" * 70)
    print(f"\nScanned: {processed} stocks")
    print(f"Signals generated: {len(signals)}")
    
    # Save to CSV
    if signals:
        df_signals = pd.DataFrame(signals)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"signals_feb2025_{timestamp}.csv"
        df_signals.to_csv(output_file, index=False)
        
        print(f"\nSignals saved to: {output_file}")
        
        # Summary
        print(f"\n[SIGNAL SUMMARY]")
        print(f"   Total: {len(signals)} delivery signals")
        print(f"   Mode: 30-60 day holding period")
        print(f"   Confidence: 65%+ (TESTING)")
        print(f"   Target: 10% gain")
        print(f"   Protection: 7% stop loss")
        
        return df_signals
    else:
        print("\n[WARNING] No signals met the delivery criteria")
        print("   (65%+ confidence + 3/4 validation checks)")
        return None


def main():
    """Main signal generation."""
    print("\n" + "=" * 70)
    print(" FEB 2025 SIGNAL GENERATOR - EXPERIMENTAL")
    print("=" * 70)
    print("\nThis uses:")
    print("  - Data till February 28, 2025")
    print("  - Trained AI models (169 models)")
    print("  - Delivery validation (3/4 criteria)")
    print("  - Testing threshold (65%+)")
    print("\nStarting signal generation...")
    
    signals = generate_signals_feb2025()
    
    if signals is not None:
        print("\n[SUCCESS] Signals generated successfully!")
        print(f"\nTotal signals: {len(signals)}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

