"""
MCX Commodity Telegram Alert System
====================================
Sends real-time AI predictions for Gold & Silver to your Telegram
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import pickle

from ai_screener.alert_system import AlertSystem
from ai_screener.data_loader_universal import UniversalDataLoader
from ai_screener.feature_engineering import FeatureEngineer

def load_best_model(symbol):
    """Load the best trained model"""
    models_dir = Path("ai_screener/models")
    
    # Try best ensemble first
    best_path = models_dir / f"best_{symbol}.pkl"
    if best_path.exists():
        with open(best_path, 'rb') as f:
            return pickle.load(f), "Ensemble"
    
    # Try single XGBoost
    xgb_path = models_dir / f"xgb_{symbol}.pkl"
    if xgb_path.exists():
        with open(xgb_path, 'rb') as f:
            return pickle.load(f), "XGBoost"
    
    return None, None

def get_commodity_prediction(df, symbol, commodity_name):
    """Get AI prediction for commodity"""
    try:
        # Load model
        model, model_type = load_best_model(symbol)
        if model is None:
            return None
        
        # Engineer features
        engineer = FeatureEngineer()
        df_features = engineer.create_features(df.copy())
        
        # Get latest data
        latest = df_features.iloc[-1:]
        
        # Get feature columns
        exclude_cols = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume']
        feature_cols = [col for col in df_features.columns if col not in exclude_cols]
        feature_cols = [col for col in feature_cols if df_features[col].dtype in [np.int64, np.float64]]
        
        X = latest[feature_cols].fillna(0).values
        
        # Make prediction
        prediction = model.predict(X)[0]
        
        # Get confidence
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(X)[0]
            confidence = float(proba[prediction])
        else:
            confidence = 0.80
        
        # Map to signal
        signal_map = {0: 'hold', 1: 'buy'}
        signal = signal_map.get(prediction, 'hold')
        
        # Current price
        current_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2]
        change_pct = ((current_price - prev_price) / prev_price) * 100
        
        # Calculate target and stop loss (3% profit target, 1.5% stop loss)
        if signal == 'buy':
            target_price = current_price * 1.03
            stop_loss = current_price * 0.985
        else:
            target_price = current_price
            stop_loss = current_price
        
        # Calculate VWAP deviation
        vwap = df['vwap'].iloc[-1]
        vwap_dev = ((current_price - vwap) / vwap) * 100
        
        # Get technical indicators
        rsi = latest['rsi_14'].values[0] if 'rsi_14' in latest.columns else 50
        
        return {
            'symbol': symbol,
            'name': commodity_name,
            'signal': signal,
            'confidence': confidence,
            'current_price': current_price,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'vwap_deviation': vwap_dev,
            'change_pct': change_pct,
            'rsi': rsi,
            'model_type': model_type
        }
        
    except Exception as e:
        print(f"Error getting prediction for {commodity_name}: {e}")
        return None

def send_commodity_alerts():
    """Send MCX commodity alerts to Telegram"""
    print("\n" + "="*70)
    print("MCX COMMODITY TELEGRAM ALERT SYSTEM")
    print("="*70 + "\n")
    
    # Initialize alert system
    alert_system = AlertSystem()
    
    # Check if Telegram is enabled
    if not alert_system.config['telegram']['enabled']:
        print("❌ Telegram is DISABLED!")
        print("\nTo enable:")
        print("1. Edit: ai_screener/alert_config.json")
        print("2. Set 'enabled': true under 'telegram'")
        return False
    
    print("✅ Telegram is enabled")
    print(f"   Bot configured: {alert_system.config['telegram']['bot_token'][:20]}...")
    print(f"   Chat IDs: {alert_system.config['telegram']['chat_ids']}\n")
    
    # Load data
    print("Loading commodity data...")
    loader = UniversalDataLoader()
    
    commodities_data = {}
    for symbol in ['MCX_GOLD', 'MCX_SILVER']:
        df = loader.load_symbol_data(symbol)
        if df is not None:
            commodities_data[symbol] = df
            print(f"✓ Loaded {symbol}")
    
    if not commodities_data:
        print("\n❌ No commodity data found!")
        return False
    
    # Get predictions
    print("\nGetting AI predictions...")
    signals = []
    
    for symbol, commodity_name in [('MCX_GOLD', 'GOLD 🥇'), ('MCX_SILVER', 'SILVER 🥈')]:
        if symbol in commodities_data:
            prediction = get_commodity_prediction(
                commodities_data[symbol], 
                symbol, 
                commodity_name
            )
            
            if prediction:
                signals.append(prediction)
                print(f"✓ {commodity_name}: {prediction['signal'].upper()} (Confidence: {prediction['confidence']*100:.1f}%)")
    
    if not signals:
        print("\n❌ No predictions generated!")
        return False
    
    # Send to Telegram
    print(f"\n📤 Sending alerts to Telegram...")
    print("   Check your Telegram app!")
    
    result = alert_system.send_telegram_alert(signals)
    
    print("\n" + "="*70)
    if result:
        print("🎉 SUCCESS! MCX Alerts sent to Telegram!")
        print("="*70)
        print("\n✅ Check your Telegram for:")
        for sig in signals:
            print(f"   • {sig['name']}: {sig['signal'].upper()}")
    else:
        print("❌ FAILED to send alerts")
        print("="*70)
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify bot_token in alert_config.json")
        print("3. Verify chat_id in alert_config.json")
    
    print("\n" + "="*70 + "\n")
    return result

def main():
    """Main function"""
    send_commodity_alerts()

if __name__ == '__main__':
    main()

