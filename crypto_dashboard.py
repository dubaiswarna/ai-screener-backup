"""
Cryptocurrency AI Trading Dashboard
====================================
Real-time AI predictions for 8 major cryptocurrencies
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

import pandas as pd
import numpy as np
from datetime import datetime
import webbrowser
from pathlib import Path
import pickle

from ai_screener.data_loader_universal import UniversalDataLoader
from ai_screener.feature_engineering import FeatureEngineer

def load_crypto_model(symbol):
    """Load trained AI model"""
    models_dir = Path("ai_screener/models")
    
    # Try best model
    for prefix in ['best_', 'xgb_']:
        model_path = models_dir / f"{prefix}{symbol}.pkl"
        if model_path.exists():
            with open(model_path, 'rb') as f:
                return pickle.load(f)
    return None

def get_ai_signal(df, symbol):
    """Get AI prediction for crypto"""
    try:
        model = load_crypto_model(symbol)
        if model is None:
            return 'HOLD', 0.5, 'Model not trained'
        
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
        
        signal = 'BUY' if prediction == 1 else 'HOLD'
        
        # Get key indicators
        rsi = latest['rsi_14'].values[0] if 'rsi_14' in latest.columns else 50
        reason = f"RSI: {rsi:.1f}"
        
        return signal, confidence, reason
        
    except Exception as e:
        return 'HOLD', 0.5, str(e)

def generate_crypto_dashboard():
    """Generate beautiful crypto dashboard"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Load data
    loader = UniversalDataLoader()
    
    cryptos_info = [
        ('CRYPTO_BTC', 'Bitcoin', '🟠', '#F7931A'),
        ('CRYPTO_ETH', 'Ethereum', '🔷', '#627EEA'),
        ('CRYPTO_BNB', 'Binance Coin', '🟡', '#F3BA2F'),
        ('CRYPTO_SOL', 'Solana', '🟣', '#14F195'),
        ('CRYPTO_XRP', 'Ripple', '🔵', '#23292F'),
        ('CRYPTO_ADA', 'Cardano', '🔴', '#0033AD'),
        ('CRYPTO_DOGE', 'Dogecoin', '🟤', '#C2A633'),
        ('CRYPTO_DOT', 'Polkadot', '⚪', '#E6007A')
    ]
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Crypto AI Trading Dashboard</title>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1800px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{ font-size: 3em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.3em; opacity: 0.9; }}
        .timestamp {{ font-size: 0.9em; margin-top: 15px; opacity: 0.8; }}
        
        .crypto-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        .crypto-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }}
        .crypto-card:hover {{ transform: translateY(-5px); }}
        
        .crypto-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
        }}
        .crypto-icon {{ font-size: 2.5em; margin-right: 15px; }}
        .crypto-name {{ font-size: 1.8em; font-weight: bold; color: #333; }}
        
        .price-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
            text-align: center;
        }}
        .current-price {{ font-size: 2.2em; font-weight: bold; }}
        .price-change {{ font-size: 1.2em; margin-top: 5px; }}
        
        .ai-signal {{
            padding: 18px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.2em;
            font-weight: bold;
            margin: 15px 0;
        }}
        .ai-signal.buy {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }}
        .ai-signal.hold {{
            background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
            color: #333;
        }}
        
        .confidence-bar {{
            background: #e0e0e0;
            height: 25px;
            border-radius: 12px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .confidence-fill {{
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.5s;
        }}
        
        .stats {{ margin: 15px 0; }}
        .stat-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .stat-row:last-child {{ border-bottom: none; }}
        .stat-label {{ color: #666; }}
        .stat-value {{ font-weight: bold; color: #333; }}
        
        .footer {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 CRYPTO AI TRADING DASHBOARD</h1>
            <p>AI-Powered Predictions for 8 Major Cryptocurrencies</p>
            <div class="timestamp">Last Updated: {timestamp}</div>
        </div>
        
        <div class="crypto-grid">
"""
    
    # Load and process each crypto
    for symbol, name, icon, color in cryptos_info:
        df = loader.load_symbol_data(symbol)
        
        if df is not None:
            current = df['close'].iloc[-1]
            prev = df['close'].iloc[-2]
            change = current - prev
            change_pct = (change / prev) * 100
            
            # AI prediction
            signal, confidence, reason = get_ai_signal(df, symbol)
            
            # Stats
            high_24h = df['high'].tail(1).values[0]
            low_24h = df['low'].tail(1).values[0]
            high_7d = df['high'].tail(7).max()
            low_7d = df['low'].tail(7).min()
            
            change_color = 'green' if change >= 0 else 'red'
            change_symbol = '+' if change >= 0 else ''
            signal_class = 'buy' if signal == 'BUY' else 'hold'
            signal_icon = '🚀' if signal == 'BUY' else '⏸️'
            
            html += f"""
            <div class="crypto-card">
                <div class="crypto-header">
                    <div class="crypto-icon">{icon}</div>
                    <div class="crypto-name">{name}</div>
                </div>
                
                <div class="price-box">
                    <div class="current-price">${current:,.2f}</div>
                    <div class="price-change" style="color: {change_color}">
                        {change_symbol}${change:.2f} ({change_symbol}{change_pct:.2f}%)
                    </div>
                </div>
                
                <div class="ai-signal {signal_class}">
                    {signal_icon} AI SIGNAL: {signal}
                </div>
                
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {confidence*100}%">
                        {confidence*100:.1f}% Confidence
                    </div>
                </div>
                
                <div class="stats">
                    <div class="stat-row">
                        <span class="stat-label">24H High:</span>
                        <span class="stat-value">${high_24h:,.2f}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">24H Low:</span>
                        <span class="stat-value">${low_24h:,.2f}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">7D High:</span>
                        <span class="stat-value">${high_7d:,.2f}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">7D Low:</span>
                        <span class="stat-value">${low_7d:,.2f}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">AI Analysis:</span>
                        <span class="stat-value">{reason}</span>
                    </div>
                </div>
            </div>
"""
    
    html += """
        </div>
        
        <div class="footer">
            <p style="font-size: 1.3em; font-weight: bold; color: #333; margin-bottom: 10px;">
                🤖 AI-Powered Cryptocurrency Trading System
            </p>
            <p style="color: #666;">
                Trained on 2 years of data | 89 technical features | XGBoost algorithm
            </p>
            <p style="color: #999; margin-top: 15px; font-size: 0.9em;">
                ⚠️ Cryptocurrency trading carries high risk. Trade responsibly.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("\n" + "="*70)
    print("GENERATING CRYPTO AI DASHBOARD")
    print("="*70 + "\n")
    
    html = generate_crypto_dashboard()
    
    output_file = Path("crypto_dashboard.html")
    output_file.write_text(html, encoding='utf-8')
    
    print(f"✅ Dashboard saved to: {output_file.absolute()}")
    print("\n🌐 Opening in browser...")
    
    webbrowser.open(str(output_file.absolute()))
    
    print("\n" + "="*70)
    print("✅ CRYPTO DASHBOARD READY!")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()

