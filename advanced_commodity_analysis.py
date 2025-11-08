"""
Advanced Commodity Analysis Dashboard
======================================
Shows support/resistance levels and trade entry/exit points for Gold & Silver
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import webbrowser
from pathlib import Path

def calculate_support_resistance(df, timeframe='daily'):
    """
    Calculate support and resistance levels for different timeframes
    timeframe: 'intraday' (5 days), 'daily' (20 days), 'monthly' (60 days)
    """
    # Get recent data based on timeframe
    if timeframe == 'intraday':
        lookback = 3
        period = 30  # Last 30 days
    elif timeframe == 'daily':
        lookback = 5
        period = 90  # Last 90 days
    else:  # monthly
        lookback = 10
        period = 252  # Last year
    
    df_recent = df.tail(period).reset_index(drop=True)
    current_price = df['close'].iloc[-1]
    
    highs = []
    lows = []
    
    # Find swing highs and lows
    for i in range(lookback, len(df_recent) - lookback):
        # Swing high
        if df_recent['high'].iloc[i] == df_recent['high'].iloc[i-lookback:i+lookback+1].max():
            highs.append(df_recent['high'].iloc[i])
        
        # Swing low
        if df_recent['low'].iloc[i] == df_recent['low'].iloc[i-lookback:i+lookback+1].min():
            lows.append(df_recent['low'].iloc[i])
    
    # Get levels close to current price (within ±15%)
    price_tolerance = current_price * 0.15
    
    # Filter and sort support (below current price)
    support_candidates = [l for l in lows if l < current_price and l > (current_price - price_tolerance)]
    support_levels = sorted(set(support_candidates), reverse=True)[:3]  # Top 3 closest
    
    # Filter and sort resistance (above current price)
    resistance_candidates = [h for h in highs if h > current_price and h < (current_price + price_tolerance)]
    resistance_levels = sorted(set(resistance_candidates))[:3]  # Top 3 closest
    
    # If not enough levels found, add recent high/low
    if len(support_levels) < 3:
        recent_lows = df_recent['low'].tail(20).nsmallest(5).tolist()
        for low in recent_lows:
            if low < current_price and low not in support_levels:
                support_levels.append(low)
            if len(support_levels) >= 3:
                break
        support_levels = sorted(set(support_levels), reverse=True)
    
    if len(resistance_levels) < 3:
        recent_highs = df_recent['high'].tail(20).nlargest(5).tolist()
        for high in recent_highs:
            if high > current_price and high not in resistance_levels:
                resistance_levels.append(high)
            if len(resistance_levels) >= 3:
                break
        resistance_levels = sorted(set(resistance_levels))
    
    return support_levels[:3], resistance_levels[:3]

def find_trade_signals(df, support, resistance):
    """
    Find buy/sell signals based on support/resistance and price action
    More sensitive to capture recent trades
    """
    signals = []
    
    # Last year data
    one_year_ago = df['time'].max() - timedelta(days=365)
    df_year = df[df['time'] >= one_year_ago].copy().reset_index(drop=True)
    
    for i in range(2, len(df_year)):
        row = df_year.iloc[i]
        prev = df_year.iloc[i-1]
        prev2 = df_year.iloc[i-2]
        
        # Buy signal: Price near support with bullish candle
        for sup in support:
            tolerance = sup * 0.03  # 3% tolerance
            if (row['low'] <= sup + tolerance and row['low'] >= sup - tolerance and
                row['close'] > row['open'] and  # Bullish candle
                row['close'] > prev['close']):  # Higher close
                signals.append({
                    'date': row['time'],
                    'type': 'BUY',
                    'price': row['close'],
                    'reason': f'Support bounce ${sup:.2f}'
                })
                break
        
        # Sell signal: Price near resistance with bearish candle
        for res in resistance:
            tolerance = res * 0.03  # 3% tolerance
            if (row['high'] >= res - tolerance and row['high'] <= res + tolerance and
                row['close'] < row['open'] and  # Bearish candle
                row['close'] < prev['close']):  # Lower close
                signals.append({
                    'date': row['time'],
                    'type': 'SELL',
                    'price': row['close'],
                    'reason': f'Resistance reject ${res:.2f}'
                })
                break
        
        # Additional momentum signals
        # Buy on breakout above resistance
        if resistance:
            highest_res = max(resistance)
            if (prev['high'] < highest_res and row['close'] > highest_res and
                row['volume'] > df_year['volume'].tail(20).mean() * 1.2):
                signals.append({
                    'date': row['time'],
                    'type': 'BUY',
                    'price': row['close'],
                    'reason': f'Breakout above ${highest_res:.2f}'
                })
        
        # Sell on breakdown below support
        if support:
            lowest_sup = min(support)
            if (prev['low'] > lowest_sup and row['close'] < lowest_sup and
                row['volume'] > df_year['volume'].tail(20).mean() * 1.2):
                signals.append({
                    'date': row['time'],
                    'type': 'SELL',
                    'price': row['close'],
                    'reason': f'Breakdown below ${lowest_sup:.2f}'
                })
    
    return signals

def calculate_trade_performance(signals):
    """Calculate performance from entry/exit pairs"""
    trades = []
    entry = None
    
    for signal in signals:
        if signal['type'] == 'BUY' and entry is None:
            entry = signal
        elif signal['type'] == 'SELL' and entry is not None:
            profit = signal['price'] - entry['price']
            profit_pct = (profit / entry['price']) * 100
            
            trades.append({
                'entry_date': entry['date'],
                'entry_price': entry['price'],
                'exit_date': signal['date'],
                'exit_price': signal['price'],
                'profit': profit,
                'profit_pct': profit_pct,
                'holding_days': (signal['date'] - entry['date']).days
            })
            entry = None
    
    return trades

def generate_advanced_dashboard(commodities):
    """Generate advanced HTML dashboard with support/resistance"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MCX Advanced Analysis Dashboard</title>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{ max-width: 1600px; margin: 0 auto; }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .header h1 {{ color: #333; font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ color: #666; font-size: 1.2em; }}
        .timestamp {{ color: #999; font-size: 0.9em; margin-top: 10px; }}
        
        .commodity-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        
        .commodity-title {{
            font-size: 2.5em;
            color: #333;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .price-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        
        .price-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .price-label {{ font-size: 0.9em; opacity: 0.9; margin-bottom: 5px; }}
        .price-value {{ font-size: 2em; font-weight: bold; }}
        
        .levels-section {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 25px;
        }}
        
        .level-box {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
        }}
        
        .level-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }}
        
        .support-title {{ color: #28a745; }}
        .resistance-title {{ color: #dc3545; }}
        
        .level-item {{
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            font-size: 1.1em;
        }}
        
        .support-level {{
            background: #d4edda;
            color: #155724;
            border-left: 4px solid #28a745;
        }}
        
        .resistance-level {{
            background: #f8d7da;
            color: #721c24;
            border-left: 4px solid #dc3545;
        }}
        
        .trades-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .trades-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        
        .trades-table td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        
        .trades-table tr:hover {{
            background: #f5f5f5;
        }}
        
        .buy-signal {{
            background: #d4edda;
            color: #155724;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
        }}
        
        .sell-signal {{
            background: #f8d7da;
            color: #721c24;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
        }}
        
        .profit-positive {{ color: #28a745; font-weight: bold; }}
        .profit-negative {{ color: #dc3545; font-weight: bold; }}
        
        .summary-box {{
            background: #fff3cd;
            border-left: 5px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        
        .summary-title {{
            font-size: 1.3em;
            font-weight: bold;
            color: #856404;
            margin-bottom: 10px;
        }}
        
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 MCX Advanced Analysis Dashboard</h1>
            <p>Support/Resistance Levels & Trade Signals (Last 12 Months)</p>
            <div class="timestamp">Last Updated: {timestamp}</div>
        </div>
"""
    
    # Process each commodity
    for symbol, name, icon in [('MCX_GOLD', 'GOLD', '🥇'), ('MCX_SILVER', 'SILVER', '🥈')]:
        if symbol in commodities:
            df = commodities[symbol]
            
            # Current price info
            current_price = df['close'].iloc[-1]
            prev_price = df['close'].iloc[-2]
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100
            
            # Calculate support and resistance for multiple timeframes
            support_intra, resistance_intra = calculate_support_resistance(df, 'intraday')
            support_daily, resistance_daily = calculate_support_resistance(df, 'daily')
            support_monthly, resistance_monthly = calculate_support_resistance(df, 'monthly')
            
            # Combine all levels for signals
            all_support = list(set(support_intra + support_daily + support_monthly))
            all_resistance = list(set(resistance_intra + resistance_daily + resistance_monthly))
            
            # Find trade signals
            signals = find_trade_signals(df, all_support, all_resistance)
            
            # Calculate trades
            trades = calculate_trade_performance(signals)
            
            # Calculate statistics
            if trades:
                total_trades = len(trades)
                profitable_trades = len([t for t in trades if t['profit'] > 0])
                win_rate = (profitable_trades / total_trades) * 100
                total_profit = sum(t['profit'] for t in trades)
                avg_profit = sum(t['profit_pct'] for t in trades) / total_trades
            else:
                total_trades = profitable_trades = win_rate = total_profit = avg_profit = 0
            
            change_color = 'green' if change >= 0 else 'red'
            change_symbol = '+' if change >= 0 else ''
            
            html += f"""
        <div class="commodity-section">
            <h2 class="commodity-title">{icon} {name}</h2>
            
            <div class="price-grid">
                <div class="price-box">
                    <div class="price-label">Current Price</div>
                    <div class="price-value">${current_price:.2f}</div>
                    <div style="font-size: 1.2em; margin-top: 5px;">
                        <span style="color: {change_color}">{change_symbol}{change:.2f} ({change_symbol}{change_pct:.2f}%)</span>
                    </div>
                </div>
                <div class="price-box">
                    <div class="price-label">Year High</div>
                    <div class="price-value">${df['high'].tail(252).max():.2f}</div>
                </div>
                <div class="price-box">
                    <div class="price-label">Year Low</div>
                    <div class="price-value">${df['low'].tail(252).min():.2f}</div>
                </div>
                <div class="price-box">
                    <div class="price-label">Year Avg</div>
                    <div class="price-value">${df['close'].tail(252).mean():.2f}</div>
                </div>
            </div>
            
            <h3 style="margin: 20px 0; color: #333;">📍 INTRADAY LEVELS (1-2 Day Hold)</h3>
            <div class="levels-section">
                <div class="level-box">
                    <div class="level-title support-title">🛡️ SUPPORT</div>
"""
            
            for i, level in enumerate(support_intra, 1):
                distance = ((level - current_price) / current_price) * 100
                html += f'<div class="level-item support-level">S{i}: ${level:.2f} ({distance:.2f}% from current)</div>\n'
            
            html += """
                </div>
                <div class="level-box">
                    <div class="level-title resistance-title">🔝 RESISTANCE</div>
"""
            
            for i, level in enumerate(resistance_intra, 1):
                distance = ((level - current_price) / current_price) * 100
                html += f'<div class="level-item resistance-level">R{i}: ${level:.2f} (+{distance:.2f}% from current)</div>\n'
            
            html += f"""
                </div>
            </div>
            
            <h3 style="margin: 20px 0; color: #333;">📆 DAILY LEVELS (3-5 Day Hold)</h3>
            <div class="levels-section">
                <div class="level-box">
                    <div class="level-title support-title">🛡️ SUPPORT</div>
"""
            
            for i, level in enumerate(support_daily, 1):
                distance = ((level - current_price) / current_price) * 100
                html += f'<div class="level-item support-level">S{i}: ${level:.2f} ({distance:.2f}% from current)</div>\n'
            
            html += """
                </div>
                <div class="level-box">
                    <div class="level-title resistance-title">🔝 RESISTANCE</div>
"""
            
            for i, level in enumerate(resistance_daily, 1):
                distance = ((level - current_price) / current_price) * 100
                html += f'<div class="level-item resistance-level">R{i}: ${level:.2f} (+{distance:.2f}% from current)</div>\n'
            
            html += f"""
                </div>
            </div>
            
            <h3 style="margin: 20px 0; color: #333;">📅 MONTHLY LEVELS (10+ Day Hold)</h3>
            <div class="levels-section">
                <div class="level-box">
                    <div class="level-title support-title">🛡️ SUPPORT</div>
"""
            
            for i, level in enumerate(support_monthly, 1):
                distance = ((level - current_price) / current_price) * 100
                html += f'<div class="level-item support-level">S{i}: ${level:.2f} ({distance:.2f}% from current)</div>\n'
            
            html += """
                </div>
                <div class="level-box">
                    <div class="level-title resistance-title">🔝 RESISTANCE</div>
"""
            
            for i, level in enumerate(resistance_monthly, 1):
                distance = ((level - current_price) / current_price) * 100
                html += f'<div class="level-item resistance-level">R{i}: ${level:.2f} (+{distance:.2f}% from current)</div>\n'
            
            html += f"""
                </div>
            </div>
            
            <div class="summary-box">
                <div class="summary-title">📊 1-Year Trading Performance (Based on S/R Levels)</div>
                <div class="summary-stats">
                    <div class="stat-item">
                        <div class="stat-value">{total_trades}</div>
                        <div class="stat-label">Total Trades</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{win_rate:.1f}%</div>
                        <div class="stat-label">Win Rate</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" style="color: {'green' if total_profit > 0 else 'red'}">${total_profit:.2f}</div>
                        <div class="stat-label">Total Profit</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" style="color: {'green' if avg_profit > 0 else 'red'}">{avg_profit:+.2f}%</div>
                        <div class="stat-label">Avg Profit %</div>
                    </div>
                </div>
            </div>
            
            <h3 style="margin: 20px 0; color: #333;">📈 Recent Trade Signals (Last 10)</h3>
            <table class="trades-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Signal</th>
                        <th>Entry Price</th>
                        <th>Exit Price</th>
                        <th>Profit/Loss</th>
                        <th>Return %</th>
                        <th>Days Held</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            # Show last 10 trades
            for trade in trades[-10:]:
                profit_class = 'profit-positive' if trade['profit'] > 0 else 'profit-negative'
                profit_symbol = '+' if trade['profit'] > 0 else ''
                
                html += f"""
                    <tr>
                        <td>{trade['entry_date'].strftime('%Y-%m-%d')}</td>
                        <td>
                            <span class="buy-signal">BUY</span> → 
                            <span class="sell-signal">SELL</span>
                        </td>
                        <td>${trade['entry_price']:.2f}</td>
                        <td>${trade['exit_price']:.2f}</td>
                        <td class="{profit_class}">{profit_symbol}${trade['profit']:.2f}</td>
                        <td class="{profit_class}">{profit_symbol}{trade['profit_pct']:.2f}%</td>
                        <td>{trade['holding_days']} days</td>
                    </tr>
"""
            
            html += """
                </tbody>
            </table>
        </div>
"""
    
    html += """
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("\n" + "="*70)
    print("ADVANCED MCX COMMODITY ANALYSIS")
    print("="*70 + "\n")
    
    # Load data
    print("Loading commodity data...")
    commodities = {}
    
    mcx_dir = Path("MCX_data")
    if not mcx_dir.exists():
        print("❌ MCX_data folder not found!")
        print("Run 'python simple_fetch.py' first to download data.")
        return
    
    for symbol in ['MCX_GOLD', 'MCX_SILVER']:
        csv_file = mcx_dir / f"{symbol}, 1D.csv"
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            df['time'] = pd.to_datetime(df['time'])
            commodities[symbol] = df
            print(f"✓ Loaded {symbol}: {len(df)} rows")
    
    if not commodities:
        print("\n❌ No commodity data found!")
        return
    
    # Generate HTML
    print("\nCalculating support/resistance levels...")
    print("Analyzing trade signals...")
    print("Generating advanced dashboard...")
    
    html_content = generate_advanced_dashboard(commodities)
    
    # Save HTML
    output_file = Path("advanced_commodity_dashboard.html")
    output_file.write_text(html_content, encoding='utf-8')
    
    print(f"\n✅ Dashboard saved to: {output_file.absolute()}")
    
    # Open in browser
    print("\n🌐 Opening dashboard in your browser...")
    webbrowser.open(str(output_file.absolute()))
    
    print("\n" + "="*70)
    print("✅ SUCCESS!")
    print("="*70)
    print("\nDashboard Features:")
    print("✓ Support & Resistance levels (Price Action based)")
    print("✓ Entry/Exit signals for last 12 months")
    print("✓ Trade performance statistics")
    print("✓ Win rate and profit calculations")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()

