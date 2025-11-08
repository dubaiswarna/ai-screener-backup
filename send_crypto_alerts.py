"""
Cryptocurrency Telegram Alert System
=====================================
Sends real-time AI predictions for 8 major cryptos to your Telegram
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

import pandas as pd
import numpy as np
from pathlib import Path
import pickle

from ai_screener.alert_system import AlertSystem
from ai_screener.data_loader_universal import UniversalDataLoader
from ai_screener.feature_engineering import FeatureEngineer

def load_crypto_model(symbol):
    """Load trained crypto model"""
    models_dir = Path("ai_screener/models")
    for prefix in ['best_', 'xgb_']:
        model_path = models_dir / f"{prefix}{symbol}.pkl"
        if model_path.exists():
            with open(model_path, 'rb') as f:
                return pickle.load(f)
    return None

def get_crypto_prediction(df, symbol, crypto_name):
    """Get AI prediction for cryptocurrency"""
    try:
        model = load_crypto_model(symbol)
        if model is None:
            return None
        
        engineer = FeatureEngineer()
        df_features = engineer.create_features(df.copy())
        latest = df_features.iloc[-1:]
        
        exclude_cols = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume']
        feature_cols = [col for col in df_features.columns if col not in exclude_cols]
        feature_cols = [col for col in feature_cols if df_features[col].dtype in [np.int64, np.float64]]
        
        X = latest[feature_cols].fillna(0).values
        prediction = model.predict(X)[0]
        
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(X)[0]
            confidence = float(proba[prediction])
        else:
            confidence = 0.75
        
        signal = 'buy' if prediction == 1 else 'hold'
        current_price = df['close'].iloc[-1]
        
        # Crypto-specific targets (5% profit, 2% stop)
        target_price = current_price * 1.05
        stop_loss = current_price * 0.98
        
        vwap = df['vwap'].iloc[-1]
        vwap_dev = ((current_price - vwap) / vwap) * 100
        
        prev_price = df['close'].iloc[-2]
        change_pct = ((current_price - prev_price) / prev_price) * 100
        
        return {
            'symbol': symbol,
            'name': crypto_name,
            'signal': signal,
            'confidence': confidence,
            'current_price': current_price,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'vwap_deviation': vwap_dev,
            'change_pct': change_pct
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_crypto_alerts():
    """Send crypto alerts to Telegram"""
    print("\n" + "="*70)
    print("CRYPTOCURRENCY TELEGRAM ALERT SYSTEM")
    print("="*70 + "\n")
    
    alert_system = AlertSystem()
    
    if not alert_system.config['telegram']['enabled']:
        print("❌ Telegram is DISABLED!")
        return False
    
    print("✅ Telegram enabled")
    
    # Load data
    loader = UniversalDataLoader()
    
    cryptos = [
        ('CRYPTO_BTC', 'Bitcoin 🟠'),
        ('CRYPTO_ETH', 'Ethereum 🔷'),
        ('CRYPTO_BNB', 'BNB 🟡'),
        ('CRYPTO_SOL', 'Solana 🟣'),
        ('CRYPTO_XRP', 'XRP 🔵'),
        ('CRYPTO_ADA', 'Cardano 🔴'),
        ('CRYPTO_DOGE', 'Doge 🟤'),
        ('CRYPTO_DOT', 'Polkadot ⚪')
    ]
    
    signals = []
    
    print("Getting AI predictions...")
    for symbol, name in cryptos:
        df = loader.load_symbol_data(symbol)
        if df is not None:
            pred = get_crypto_prediction(df, symbol, name)
            if pred:
                signals.append(pred)
                print(f"✓ {name}: {pred['signal'].upper()} ({pred['confidence']*100:.1f}%)")
    
    if not signals:
        print("\n❌ No predictions!")
        return False
    
    print(f"\n📤 Sending {len(signals)} crypto alerts to Telegram...")
    result = alert_system.send_telegram_alert(signals)
    
    if result:
        print("\n🎉 SUCCESS! Check your Telegram!")
        buy_signals = [s for s in signals if s['signal'] == 'buy']
        if buy_signals:
            print(f"\n🚀 BUY SIGNALS ({len(buy_signals)}):")
            for s in buy_signals:
                print(f"   • {s['name']}: ${s['current_price']:,.2f}")
    else:
        print("\n❌ Failed to send alerts")
    
    print("\n" + "="*70 + "\n")
    return result

if __name__ == '__main__':
    send_crypto_alerts()

