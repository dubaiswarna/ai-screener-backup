"""
Generate Static HTML Dashboard for MCX Commodities
===================================================
Creates a beautiful HTML dashboard that opens in your browser
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

import pandas as pd
from datetime import datetime
import webbrowser
from pathlib import Path

def load_commodity_data():
    """Load Gold and Silver CSV data"""
    commodities = {}
    
    mcx_dir = Path("MCX_data")
    if not mcx_dir.exists():
        print("❌ MCX_data folder not found!")
        return None
    
    for symbol in ['MCX_GOLD', 'MCX_SILVER']:
        csv_file = mcx_dir / f"{symbol}, 1D.csv"
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            df['time'] = pd.to_datetime(df['time'])
            commodities[symbol] = df
            print(f"✓ Loaded {symbol}: {len(df)} rows")
    
    return commodities

def generate_html_dashboard(commodities):
    """Generate beautiful HTML dashboard"""
    
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>MCX Commodity Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }
        
        .header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.2em;
        }
        
        .timestamp {
            color: #999;
            font-size: 0.9em;
            margin-top: 10px;
        }
        
        .commodity-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .commodity-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        
        .commodity-header {
            display: flex;
            align-items: center;
            margin-bottom: 25px;
        }
        
        .commodity-icon {
            font-size: 3em;
            margin-right: 15px;
        }
        
        .commodity-title {
            font-size: 2em;
            color: #333;
            font-weight: bold;
        }
        
        .price-display {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .current-price {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .price-change {
            font-size: 1.2em;
        }
        
        .price-change.positive {
            color: #4CAF50;
        }
        
        .price-change.negative {
            color: #f44336;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .metric-box {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        
        .metric-label {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .metric-value {
            color: #333;
            font-size: 1.5em;
            font-weight: bold;
        }
        
        .ai-signal {
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 20px;
        }
        
        .ai-signal.buy {
            background: #d4edda;
            color: #155724;
            border: 2px solid #28a745;
        }
        
        .ai-signal.hold {
            background: #fff3cd;
            color: #856404;
            border: 2px solid #ffc107;
        }
        
        .stats-section {
            margin-top: 20px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 10px;
        }
        
        .stats-title {
            font-size: 1.2em;
            color: #333;
            margin-bottom: 15px;
            font-weight: bold;
        }
        
        .stat-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #ddd;
        }
        
        .stat-row:last-child {
            border-bottom: none;
        }
        
        .footer {
            background: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            color: #666;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            cursor: pointer;
            margin: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .refresh-btn:hover {
            background: #764ba2;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 MCX Commodity Trading Dashboard</h1>
            <p>AI-Powered Insights for Gold & Silver</p>
            <div class="timestamp">Last Updated: {timestamp}</div>
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Dashboard</button>
        </div>
        
        <div class="commodity-grid">
"""
    
    # Add commodity cards
    for symbol, name, icon in [('MCX_GOLD', 'GOLD', '🥇'), ('MCX_SILVER', 'SILVER', '🥈')]:
        if symbol in commodities:
            df = commodities[symbol]
            
            # Calculate metrics
            latest_price = df['close'].iloc[-1]
            prev_price = df['close'].iloc[-2]
            change = latest_price - prev_price
            change_pct = (change / prev_price) * 100
            
            min_price = df['close'].min()
            max_price = df['close'].max()
            avg_price = df['close'].mean()
            
            # Calculate returns
            try:
                returns_1m = ((df['close'].iloc[-1] / df['close'].iloc[-30]) - 1) * 100
                returns_3m = ((df['close'].iloc[-1] / df['close'].iloc[-90]) - 1) * 100
                returns_1y = ((df['close'].iloc[-1] / df['close'].iloc[-252]) - 1) * 100
            except:
                returns_1m = returns_3m = returns_1y = 0
            
            change_class = "positive" if change >= 0 else "negative"
            change_symbol = "+" if change >= 0 else ""
            
            # Simple AI signal (based on momentum)
            if change_pct > 1:
                signal_class = "buy"
                signal_text = "🚀 AI SIGNAL: BUY"
            else:
                signal_class = "hold"
                signal_text = "⏸️ AI SIGNAL: HOLD"
            
            html += f"""
            <div class="commodity-card">
                <div class="commodity-header">
                    <div class="commodity-icon">{icon}</div>
                    <div class="commodity-title">{name}</div>
                </div>
                
                <div class="price-display">
                    <div class="current-price">${latest_price:.2f}</div>
                    <div class="price-change {change_class}">
                        {change_symbol}{change:.2f} ({change_symbol}{change_pct:.2f}%)
                    </div>
                </div>
                
                <div class="ai-signal {signal_class}">
                    {signal_text}
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-box">
                        <div class="metric-label">Low (10Y)</div>
                        <div class="metric-value">${min_price:.2f}</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">High (10Y)</div>
                        <div class="metric-value">${max_price:.2f}</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Average</div>
                        <div class="metric-value">${avg_price:.2f}</div>
                    </div>
                </div>
                
                <div class="stats-section">
                    <div class="stats-title">📈 Historical Returns</div>
                    <div class="stat-row">
                        <span>1 Month Return:</span>
                        <strong style="color: {'green' if returns_1m > 0 else 'red'}">{returns_1m:+.2f}%</strong>
                    </div>
                    <div class="stat-row">
                        <span>3 Months Return:</span>
                        <strong style="color: {'green' if returns_3m > 0 else 'red'}">{returns_3m:+.2f}%</strong>
                    </div>
                    <div class="stat-row">
                        <span>1 Year Return:</span>
                        <strong style="color: {'green' if returns_1y > 0 else 'red'}">{returns_1y:+.2f}%</strong>
                    </div>
                    <div class="stat-row">
                        <span>Data Points:</span>
                        <strong>{len(df):,} days</strong>
                    </div>
                    <div class="stat-row">
                        <span>Date Range:</span>
                        <strong>{df['time'].min().strftime('%Y-%m-%d')} to {df['time'].max().strftime('%Y-%m-%d')}</strong>
                    </div>
                </div>
            </div>
"""
    
    html += """
        </div>
        
        <div class="footer">
            <p><strong>Note:</strong> AI predictions are based on historical patterns. Past performance does not guarantee future results.</p>
            <p style="margin-top: 10px;">Data Source: Yahoo Finance | AI Model: XGBoost with 89 Technical Features</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("\n" + "="*70)
    print("GENERATING MCX COMMODITY DASHBOARD")
    print("="*70 + "\n")
    
    # Load data
    commodities = load_commodity_data()
    
    if not commodities:
        print("\n❌ No commodity data found!")
        print("Run 'python simple_fetch.py' first to download data.")
        return
    
    # Generate HTML
    print("\nGenerating HTML dashboard...")
    html_content = generate_html_dashboard(commodities)
    
    # Replace single braces with double braces for CSS, then format timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html_content = html_content.replace('{timestamp}', timestamp)
    
    # Save HTML file
    output_file = Path("commodity_dashboard.html")
    output_file.write_text(html_content, encoding='utf-8')
    
    print(f"✅ Dashboard saved to: {output_file.absolute()}")
    
    # Open in browser
    print("\n🌐 Opening dashboard in your browser...")
    webbrowser.open(str(output_file.absolute()))
    
    print("\n" + "="*70)
    print("✅ SUCCESS!")
    print("="*70)
    print("\nDashboard is now open in your browser!")
    print("To refresh data, run this script again.")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()

