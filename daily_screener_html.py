"""
AI Stock Screener - HTML Report Generator
==========================================

Generates beautiful HTML report and opens in browser.
No server needed - just double-click!

Usage: python daily_screener_html.py
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
import webbrowser

# Add path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

from ai_screener.data_loader import DataLoader
from ai_screener.feature_engineering import FeatureEngineer
from ai_screener.xgboost_trainer import XGBoostTrainer


# Stock tiers
TIER_1_STOCKS = [
    'NSE_BAJAJFINSV', 'NSE_REFEX', 'NSE_MAXHEALTH', 'NSE_RELINFRA',
    'NSE_M&M', 'NSE_ETERNAL', 'NSE_ICICIBANK', 'NSE_ONGC',
    'NSE_ADANIENT', 'NSE_SHRIRAMFIN'
]

TIER_2_STOCKS = [
    'NSE_ADANIPORTS', 'NSE_HINDALCO', 'NSE_TATASTEEL', 'NSE_BIOCON',
    'NSE_EICHERMOT', 'NSE_POWERGRID', 'NSE_PTC', 'NSE_HDFCLIFE',
    'NSE_SBILIFE', 'NSE_TMPV', 'NSE_AXISBANK', 'NSE_JSWSTEEL',
    'NSE_KOTAKBANK', 'NSE_HCLTECH', 'NSE_TECHM'
]


def generate_html_report(df_results, filename='screener_report.html'):
    """Generate beautiful HTML report."""
    
    # Filter BUY signals
    buy_signals = df_results[df_results['Signal'] == 'BUY'].copy()
    buy_signals = buy_signals.sort_values(['Tier', 'Confidence'], ascending=[True, False])
    
    # Count by tier
    tier1_count = len(buy_signals[buy_signals['Tier'] == 1])
    tier2_count = len(buy_signals[buy_signals['Tier'] == 2])
    tier3_count = len(buy_signals[buy_signals['Tier'] == 3])
    
    # Split by tier
    tier1_signals = buy_signals[buy_signals['Tier'] == 1]
    tier2_signals = buy_signals[buy_signals['Tier'] == 2]
    tier3_signals = buy_signals[buy_signals['Tier'] == 3]
    
    # HTML Template
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Stock Screener - {datetime.now().strftime('%Y-%m-%d')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}
        
        .header h1 {{
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2rem;
            color: #666;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        .summary-card h2 {{
            font-size: 3rem;
            margin-bottom: 10px;
        }}
        
        .summary-card p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .tier-section {{
            margin-bottom: 40px;
        }}
        
        .tier-header {{
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 1.5rem;
            font-weight: bold;
        }}
        
        .tier1-header {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
        }}
        
        .tier2-header {{
            background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
            color: white;
        }}
        
        .tier3-header {{
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
        }}
        
        .signal-card {{
            background: white;
            border: 2px solid #ddd;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s;
        }}
        
        .signal-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}
        
        .tier1-card {{
            border-left: 8px solid #28a745;
            background: #f8fff9;
        }}
        
        .tier2-card {{
            border-left: 8px solid #ffc107;
            background: #fffef8;
        }}
        
        .tier3-card {{
            border-left: 8px solid #dc3545;
            background: #fff8f8;
        }}
        
        .signal-card h3 {{
            font-size: 1.8rem;
            margin-bottom: 15px;
            color: #333;
        }}
        
        .signal-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }}
        
        .info-item {{
            text-align: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .info-label {{
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .info-value {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #333;
        }}
        
        .confidence-high {{
            color: #28a745;
        }}
        
        .confidence-medium {{
            color: #ffc107;
        }}
        
        .confidence-low {{
            color: #dc3545;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background: #667eea;
            color: white;
            font-weight: bold;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        .action-plan {{
            background: #e7f3ff;
            border-left: 5px solid #0066cc;
            padding: 25px;
            border-radius: 10px;
            margin-top: 40px;
        }}
        
        .action-plan h2 {{
            color: #0066cc;
            margin-bottom: 20px;
        }}
        
        .action-plan ol {{
            font-size: 1.1rem;
            line-height: 2rem;
            margin-left: 20px;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            color: #666;
        }}
        
        .refresh-btn {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #667eea;
            color: white;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 1.1rem;
            cursor: pointer;
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
            text-decoration: none;
            display: inline-block;
        }}
        
        .refresh-btn:hover {{
            background: #764ba2;
            transform: scale(1.05);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 AI Stock Screener</h1>
            <p>Daily Scan for VWAP Ladder Strategy</p>
            <p style="font-size: 1rem; color: #999;">{datetime.now().strftime('%A, %B %d, %Y • %I:%M %p')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h2>{len(df_results)}</h2>
                <p>Stocks Scanned</p>
            </div>
            <div class="summary-card">
                <h2>{len(buy_signals)}</h2>
                <p>BUY Signals</p>
            </div>
            <div class="summary-card">
                <h2>{tier1_count}</h2>
                <p>Tier 1 (HIGH)</p>
            </div>
            <div class="summary-card">
                <h2>{buy_signals['Confidence'].mean():.1f}%</h2>
                <p>Avg Confidence</p>
            </div>
        </div>
"""

    # TIER 1 SIGNALS
    if not tier1_signals.empty:
        html += """
        <div class="tier-section">
            <div class="tier-header tier1-header">
                🌟 TIER 1 - HIGH CONFIDENCE SIGNALS (Trade These!)
            </div>
"""
        for idx, row in tier1_signals.iterrows():
            conf_class = 'confidence-high' if row['Confidence'] >= 70 else 'confidence-medium'
            html += f"""
            <div class="signal-card tier1-card">
                <h3>🎯 {row['Stock']}</h3>
                <div class="signal-info">
                    <div class="info-item">
                        <div class="info-label">Confidence</div>
                        <div class="info-value {conf_class}">{row['Confidence']:.1f}%</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Buy Probability</div>
                        <div class="info-value">{row['Buy_Probability']:.1f}%</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Current Price</div>
                        <div class="info-value">Rs {row['Price']:.2f}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Date</div>
                        <div class="info-value">{row['Date'].strftime('%Y-%m-%d')}</div>
                    </div>
                </div>
            </div>
"""
        html += "</div>"
    
    # TIER 2 SIGNALS
    if not tier2_signals.empty:
        html += """
        <div class="tier-section">
            <div class="tier-header tier2-header">
                ✓ TIER 2 - MEDIUM CONFIDENCE SIGNALS (Consider These)
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Stock</th>
                        <th>Confidence</th>
                        <th>Buy Probability</th>
                        <th>Price (Rs)</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
"""
        for idx, row in tier2_signals.iterrows():
            html += f"""
                    <tr>
                        <td><strong>{row['Stock']}</strong></td>
                        <td>{row['Confidence']:.1f}%</td>
                        <td>{row['Buy_Probability']:.1f}%</td>
                        <td>Rs {row['Price']:.2f}</td>
                        <td>{row['Date'].strftime('%Y-%m-%d')}</td>
                    </tr>
"""
        html += """
                </tbody>
            </table>
        </div>
"""
    
    # TIER 3 SIGNALS
    if not tier3_signals.empty:
        html += f"""
        <div class="tier-section">
            <div class="tier-header tier3-header">
                ⚠️ TIER 3 - LOW CONFIDENCE SIGNALS ({len(tier3_signals)} stocks - Not Recommended)
            </div>
            <p style="padding: 15px; background: #fff3cd; border-radius: 8px;">
                These signals are from low-volatility stocks. Not suitable for VWAP Ladder strategy.
            </p>
        </div>
"""
    
    # Action Plan
    html += f"""
        <div class="action-plan">
            <h2>📋 Recommended Action Plan</h2>
            <ol>
"""
    
    if tier1_count > 0:
        html += f"""
                <li><strong>PRIORITY:</strong> Focus on {tier1_count} Tier 1 stocks above
                    <ul style="margin-top: 10px;">
                        <li>Copy their CSV files from Nify50_data folder</li>
                        <li>Run VWAP Filter backtest: <code>python RVwapfilter_ssc.py</code></li>
                        <li>Leave profit % blank for comparison mode (3%, 6%, 10%)</li>
                        <li>Select best 2-3 stocks based on profit potential</li>
                    </ul>
                </li>
"""
    
    if tier2_count > 0:
        html += f"""
                <li><strong>SECONDARY:</strong> Consider top 5 from {tier2_count} Tier 2 stocks
                    <ul style="margin-top: 10px;">
                        <li>Use only if Tier 1 signals look limited</li>
                        <li>Verify carefully with VWAP backtest</li>
                    </ul>
                </li>
"""
    
    html += """
                <li><strong>EXECUTE:</strong> Trade selected stocks using VWAP Ladder Strategy
                    <ul style="margin-top: 10px;">
                        <li>4 entry levels: E1=Prev LOW, E2=LOW-1%, E3=Prev VWAP, E4=VWAP-1%</li>
                        <li>Target: 3%, 6%, or 10% based on backtest</li>
                        <li>Exit when target hit</li>
                    </ul>
                </li>
            </ol>
        </div>
        
        <div class="footer">
            <p><strong>AI Stock Screener</strong> | VWAP Ladder Strategy</p>
            <p>Models trained on {datetime.now().strftime('%Y-%m-%d')} | Average Buy Precision: 28.6%</p>
            <p style="margin-top: 15px; font-size: 0.9rem;">
                ⚠️ <em>Use signals as screening tool only. Always verify with VWAP backtest and your own analysis.</em>
            </p>
        </div>
    </div>
    
    <a href="javascript:location.reload()" class="refresh-btn">🔄 Refresh</a>
    
    <script>
        // Auto-refresh every 5 minutes
        setTimeout(function(){{
            location.reload();
        }}, 300000);
    </script>
</body>
</html>
"""
    
    # Save HTML
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return filename


def main():
    """Main function."""
    print("="*70)
    print("AI STOCK SCREENER - HTML REPORT GENERATOR")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load models
    print("Loading models...", flush=True)
    models_dir = 'ai_screener/models'
    loader = DataLoader()
    all_stocks = loader.get_all_stocks()
    
    models = {}
    for stock in all_stocks:
        model_path = os.path.join(models_dir, f'xgb_{stock}.pkl')
        if os.path.exists(model_path):
            try:
                models[stock] = joblib.load(model_path)
            except:
                pass
    
    print(f"✓ Loaded {len(models)} models\n")
    
    # Scan stocks
    print("Scanning stocks...")
    engineer = FeatureEngineer()
    trainer = XGBoostTrainer()
    
    results = []
    
    for idx, (stock, model) in enumerate(models.items(), 1):
        print(f"  [{idx}/{len(models)}] {stock}...", end=" ", flush=True)
        
        try:
            df = loader.load_stock_data(stock)
            if df is None or len(df) < 50:
                print("✗ No data")
                continue
            
            df_features = engineer.engineer_features(df)
            latest = df_features.iloc[-1]
            feature_cols = trainer.get_feature_columns(df_features)
            X = df_features[feature_cols].values[-1:]
            
            prediction = model.predict(X)[0]
            proba = model.predict_proba(X)[0]
            
            confidence = proba[prediction] * 100
            buy_proba = proba[1] * 100 if len(proba) > 1 else 0
            signal = "BUY" if prediction == 1 else "HOLD"
            
            if stock in TIER_1_STOCKS:
                tier, tier_label = 1, "HIGH"
            elif stock in TIER_2_STOCKS:
                tier, tier_label = 2, "MEDIUM"
            else:
                tier, tier_label = 3, "LOW"
            
            latest_price = df.iloc[-1]['close']
            latest_date = df.iloc[-1]['time']
            
            results.append({
                'Stock': stock.replace('NSE_', ''),
                'Signal': signal,
                'Confidence': confidence,
                'Buy_Probability': buy_proba,
                'Tier': tier,
                'Tier_Label': tier_label,
                'Price': latest_price,
                'Date': latest_date
            })
            
            print("✓")
            
        except Exception as e:
            print(f"✗ {str(e)[:30]}")
    
    df_results = pd.DataFrame(results)
    
    print(f"\n✓ Scanned {len(df_results)} stocks")
    
    # Generate HTML
    print("\nGenerating HTML report...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'screener_report_{timestamp}.html'
    html_file = generate_html_report(df_results, filename)
    
    print(f"✓ Report generated: {html_file}")
    
    # Also save Excel
    excel_file = f'screener_results_{timestamp}.xlsx'
    buy_signals = df_results[df_results['Signal'] == 'BUY'].sort_values(['Tier', 'Confidence'], ascending=[True, False])
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        buy_signals.to_excel(writer, sheet_name='BUY Signals', index=False)
        df_results.to_excel(writer, sheet_name='All Stocks', index=False)
    
    print(f"✓ Excel saved: {excel_file}")
    
    # Open in browser
    print(f"\nOpening HTML report in browser...")
    full_path = os.path.abspath(html_file)
    webbrowser.open('file://' + full_path)
    
    print("\n" + "="*70)
    print("SCAN COMPLETED!")
    print("="*70)
    print(f"\nFiles created:")
    print(f"  - HTML Report: {html_file}")
    print(f"  - Excel File:  {excel_file}")
    print(f"\nHTML report opened in your browser!")
    print("="*70)


if __name__ == '__main__':
    main()

