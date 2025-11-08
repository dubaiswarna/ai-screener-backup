"""
AI Stock Screener - HTML Dashboard with Interactive Charts
===========================================================

Features:
- Scans all stocks
- Shows BUY signals
- Click "View Chart" button to see:
  * Candlestick chart
  * VWAP line
  * Entry levels (E1, E2, E3, E4) marked
  * AI signals marked
  * Exit levels shown
  
Opens charts in new browser tab!
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import webbrowser
import json

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


def generate_chart_html(stock_name, df_stock, ai_signals=None, num_days=60):
    """Generate interactive chart HTML for a stock."""
    
    # Get last N days
    df_chart = df_stock.tail(num_days).copy()
    df_chart['date_str'] = df_chart['time'].dt.strftime('%Y-%m-%d')
    
    # Calculate VWAP and entry levels for visualization
    if 'vwap' in df_chart.columns:
        latest_vwap = df_chart['vwap'].iloc[-2]  # Previous day VWAP
        latest_low = df_chart['low'].iloc[-2]    # Previous day LOW
    else:
        latest_vwap = df_chart['close'].iloc[-2]
        latest_low = df_chart['low'].iloc[-2]
    
    # Calculate entry levels (from previous day)
    e1_level = latest_low
    e2_level = latest_low * 0.99
    e3_level = latest_vwap
    e4_level = latest_vwap * 0.99
    
    # Calculate target levels (assuming 10% profit)
    current_price = df_chart['close'].iloc[-1]
    target_3pct = current_price * 1.03
    target_6pct = current_price * 1.06
    target_10pct = current_price * 1.10
    
    # Prepare data for chart
    chart_data = {
        'dates': df_chart['date_str'].tolist(),
        'open': df_chart['open'].tolist() if 'open' in df_chart.columns else df_chart['close'].tolist(),
        'high': df_chart['high'].tolist(),
        'low': df_chart['low'].tolist(),
        'close': df_chart['close'].tolist(),
        'vwap': df_chart['vwap'].tolist() if 'vwap' in df_chart.columns else df_chart['close'].tolist(),
        'volume': df_chart['volume'].tolist() if 'volume' in df_chart.columns else [0] * len(df_chart)
    }
    
    # Create HTML with TradingView-style chart
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{stock_name} - AI Signal Chart</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0e1117;
            color: white;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5rem;
        }}
        .info-panel {{
            background: #1e222d;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .info-card {{
            background: #262b3d;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .info-label {{
            font-size: 0.9rem;
            color: #888;
            margin-bottom: 8px;
        }}
        .info-value {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #fff;
        }}
        .legend {{
            background: #1e222d;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 25px;
            margin-bottom: 10px;
        }}
        .legend-color {{
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-right: 8px;
            vertical-align: middle;
            border-radius: 3px;
        }}
        #chart {{
            background: #1e222d;
            border-radius: 10px;
            padding: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {stock_name} - AI Trading Signal</h1>
            <p>Last {num_days} Days | VWAP Ladder Strategy</p>
        </div>
        
        <div class="info-panel">
            <div class="info-card">
                <div class="info-label">Current Price</div>
                <div class="info-value">Rs {current_price:.2f}</div>
            </div>
            <div class="info-card">
                <div class="info-label">AI Signal</div>
                <div class="info-value" style="color: #00ff00;">BUY</div>
            </div>
            <div class="info-card">
                <div class="info-label">10% Target</div>
                <div class="info-value" style="color: #ffd700;">Rs {target_10pct:.2f}</div>
            </div>
            <div class="info-card">
                <div class="info-label">Upside Potential</div>
                <div class="info-value" style="color: #00d4ff;">+10%</div>
            </div>
        </div>
        
        <div id="chart"></div>
        
        <div class="legend">
            <h3 style="margin-bottom: 15px;">📌 Entry & Exit Levels</h3>
            <div class="legend-item">
                <span class="legend-color" style="background: #ff4444;"></span>
                <span>E1: Prev LOW (Rs {e1_level:.2f})</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #ff6666;"></span>
                <span>E2: Prev LOW-1% (Rs {e2_level:.2f})</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #ff8844;"></span>
                <span>E3: Prev VWAP (Rs {e3_level:.2f})</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #ffaa66;"></span>
                <span>E4: Prev VWAP-1% (Rs {e4_level:.2f})</span>
            </div>
            <br>
            <div class="legend-item">
                <span class="legend-color" style="background: #00ff00;"></span>
                <span>Target 3% (Rs {target_3pct:.2f})</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #00ff88;"></span>
                <span>Target 6% (Rs {target_6pct:.2f})</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #00ffff;"></span>
                <span>Target 10% (Rs {target_10pct:.2f})</span>
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background: #4444ff;"></span>
                <span>VWAP Line</span>
            </div>
        </div>
    </div>
    
    <script>
        var chartData = {json.dumps(chart_data)};
        
        // Candlestick trace
        var candlestick = {{
            type: 'candlestick',
            x: chartData.dates,
            open: chartData.open,
            high: chartData.high,
            low: chartData.low,
            close: chartData.close,
            name: '{stock_name}',
            increasing: {{line: {{color: '#00ff00'}}, fillcolor: '#00ff00'}},
            decreasing: {{line: {{color: '#ff0000'}}, fillcolor: '#ff0000'}}
        }};
        
        // VWAP line
        var vwap = {{
            type: 'scatter',
            x: chartData.dates,
            y: chartData.vwap,
            name: 'VWAP',
            line: {{color: '#4444ff', width: 2}},
            mode: 'lines'
        }};
        
        // Entry levels (horizontal lines)
        var e1_line = {{
            type: 'scatter',
            x: [chartData.dates[chartData.dates.length-10], chartData.dates[chartData.dates.length-1]],
            y: [{e1_level}, {e1_level}],
            name: 'E1: Prev LOW',
            line: {{color: '#ff4444', width: 2, dash: 'dash'}},
            mode: 'lines'
        }};
        
        var e2_line = {{
            type: 'scatter',
            x: [chartData.dates[chartData.dates.length-10], chartData.dates[chartData.dates.length-1]],
            y: [{e2_level}, {e2_level}],
            name: 'E2: LOW-1%',
            line: {{color: '#ff6666', width: 2, dash: 'dash'}},
            mode: 'lines'
        }};
        
        var e3_line = {{
            type: 'scatter',
            x: [chartData.dates[chartData.dates.length-10], chartData.dates[chartData.dates.length-1]],
            y: [{e3_level}, {e3_level}],
            name: 'E3: Prev VWAP',
            line: {{color: '#ff8844', width: 2, dash: 'dash'}},
            mode: 'lines'
        }};
        
        var e4_line = {{
            type: 'scatter',
            x: [chartData.dates[chartData.dates.length-10], chartData.dates[chartData.dates.length-1]],
            y: [{e4_level}, {e4_level}],
            name: 'E4: VWAP-1%',
            line: {{color: '#ffaa66', width: 2, dash: 'dash'}},
            mode: 'lines'
        }};
        
        // Target levels
        var target_3 = {{
            type: 'scatter',
            x: [chartData.dates[chartData.dates.length-10], chartData.dates[chartData.dates.length-1]],
            y: [{target_3pct}, {target_3pct}],
            name: 'Target 3%',
            line: {{color: '#00ff00', width: 2, dash: 'dot'}},
            mode: 'lines'
        }};
        
        var target_6 = {{
            type: 'scatter',
            x: [chartData.dates[chartData.dates.length-10], chartData.dates[chartData.dates.length-1]],
            y: [{target_6pct}, {target_6pct}],
            name: 'Target 6%',
            line: {{color: '#00ff88', width: 2, dash: 'dot'}},
            mode: 'lines'
        }};
        
        var target_10 = {{
            type: 'scatter',
            x: [chartData.dates[chartData.dates.length-10], chartData.dates[chartData.dates.length-1]],
            y: [{target_10pct}, {target_10pct}],
            name: 'Target 10%',
            line: {{color: '#00ffff', width: 2, dash: 'dot'}},
            mode: 'lines'
        }};
        
        // Volume bars
        var volume = {{
            type: 'bar',
            x: chartData.dates,
            y: chartData.volume,
            name: 'Volume',
            marker: {{color: 'rgba(100, 100, 200, 0.3)'}},
            yaxis: 'y2'
        }};
        
        var data = [candlestick, vwap, e1_line, e2_line, e3_line, e4_line, 
                    target_3, target_6, target_10, volume];
        
        var layout = {{
            title: {{
                text: '{stock_name} - VWAP Ladder Strategy',
                font: {{size: 24, color: 'white'}}
            }},
            paper_bgcolor: '#1e222d',
            plot_bgcolor: '#262b3d',
            xaxis: {{
                title: 'Date',
                gridcolor: '#333',
                color: 'white',
                rangeslider: {{visible: false}}
            }},
            yaxis: {{
                title: 'Price (Rs)',
                gridcolor: '#333',
                color: 'white',
                side: 'right'
            }},
            yaxis2: {{
                title: 'Volume',
                overlaying: 'y',
                side: 'left',
                showgrid: false,
                color: 'white'
            }},
            legend: {{
                font: {{color: 'white'}},
                bgcolor: 'rgba(30, 34, 45, 0.8)',
                bordercolor: '#666',
                borderwidth: 1
            }},
            hovermode: 'x unified',
            height: 700,
            margin: {{l: 80, r: 80, t: 80, b: 80}}
        }};
        
        var config = {{
            displayModeBar: true,
            displaylogo: false,
            responsive: true
        }};
        
        Plotly.newPlot('chart', data, layout, config);
    </script>
</body>
</html>
"""
    
    return html


def scan_and_generate_dashboard():
    """Scan stocks and generate dashboard with chart links."""
    
    print("="*80)
    print("AI SCREENER - GENERATING DASHBOARD WITH CHARTS")
    print("="*80)
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
    stock_data_cache = {}  # Cache stock data for chart generation
    
    for idx, (stock, model) in enumerate(models.items(), 1):
        print(f"  [{idx}/{len(models)}] {stock}...", end=" ", flush=True)
        
        try:
            df = loader.load_stock_data(stock)
            if df is None or len(df) < 50:
                print("✗")
                continue
            
            # Cache for charts
            stock_data_cache[stock] = df
            
            df_features = engineer.engineer_features(df)
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
                'Stock_Full': stock,
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
            print(f"✗")
    
    print(f"\n✓ Scanned {len(results)} stocks")
    
    # Generate charts for BUY signals
    print("\nGenerating charts for BUY signals...")
    
    chart_files = {}
    buy_signals = [r for r in results if r['Signal'] == 'BUY']
    
    for sig in buy_signals:
        stock_full = sig['Stock_Full']
        stock_name = sig['Stock']
        
        if stock_full in stock_data_cache:
            print(f"  Creating chart for {stock_name}...", end=" ", flush=True)
            
            chart_html = generate_chart_html(
                stock_name=stock_name,
                df_stock=stock_data_cache[stock_full],
                num_days=60
            )
            
            chart_filename = f'chart_{stock_name}.html'
            with open(chart_filename, 'w', encoding='utf-8') as f:
                f.write(chart_html)
            
            chart_files[stock_name] = chart_filename
            print("✓")
    
    # Generate main dashboard
    print("\nGenerating main dashboard...")
    
    df_results = pd.DataFrame(results)
    buy_signals_df = df_results[df_results['Signal'] == 'BUY'].copy()
    buy_signals_df = buy_signals_df.sort_values(['Tier', 'Confidence'], ascending=[True, False])
    
    # Count by tier
    tier1_count = len(buy_signals_df[buy_signals_df['Tier'] == 1])
    tier2_count = len(buy_signals_df[buy_signals_df['Tier'] == 2])
    tier3_count = len(buy_signals_df[buy_signals_df['Tier'] == 3])
    
    tier1_signals = buy_signals_df[buy_signals_df['Tier'] == 1]
    tier2_signals = buy_signals_df[buy_signals_df['Tier'] == 2]
    tier3_signals = buy_signals_df[buy_signals_df['Tier'] == 3]
    
    # Main dashboard HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Stock Screener - Dashboard</title>
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
        
        .signal-card {{
            background: white;
            border: 2px solid #ddd;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s;
            position: relative;
        }}
        
        .signal-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }}
        
        .tier1-card {{
            border-left: 8px solid #28a745;
            background: linear-gradient(to right, #f8fff9 0%, white 100%);
        }}
        
        .tier2-card {{
            border-left: 8px solid #ffc107;
            background: linear-gradient(to right, #fffef8 0%, white 100%);
        }}
        
        .signal-card h3 {{
            font-size: 2rem;
            margin-bottom: 20px;
            color: #333;
        }}
        
        .signal-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .info-item {{
            text-align: center;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .info-label {{
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .info-value {{
            font-size: 1.6rem;
            font-weight: bold;
            color: #333;
        }}
        
        .confidence-high {{
            color: #28a745;
        }}
        
        .chart-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1rem;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s;
            font-weight: bold;
        }}
        
        .chart-btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        }}
        
        .tier-header {{
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0 20px 0;
            font-size: 1.8rem;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 AI Stock Screener</h1>
            <p>Daily Scan with Interactive Charts</p>
            <p style="font-size: 1rem; color: #999;">{datetime.now().strftime('%A, %B %d, %Y • %I:%M %p')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h2>{len(df_results)}</h2>
                <p>Stocks Scanned</p>
            </div>
            <div class="summary-card">
                <h2>{len(buy_signals_df)}</h2>
                <p>BUY Signals</p>
            </div>
            <div class="summary-card">
                <h2>{tier1_count}</h2>
                <p>Tier 1 (HIGH)</p>
            </div>
            <div class="summary-card">
                <h2>{buy_signals_df['Confidence'].mean():.1f}%</h2>
                <p>Avg Confidence</p>
            </div>
        </div>
"""
    
    # TIER 1 SIGNALS
    if not tier1_signals.empty:
        html += """
        <div class="tier-header tier1-header">
            🌟 TIER 1 - HIGH CONFIDENCE SIGNALS (Trade These!)
        </div>
"""
        for idx, row in tier1_signals.iterrows():
            stock_name = row['Stock']
            chart_link = chart_files.get(stock_name, '#')
            
            html += f"""
        <div class="signal-card tier1-card">
            <h3>🎯 {stock_name}</h3>
            <div class="signal-info">
                <div class="info-item">
                    <div class="info-label">Confidence</div>
                    <div class="info-value confidence-high">{row['Confidence']:.1f}%</div>
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
                    <div class="info-label">10% Target</div>
                    <div class="info-value" style="color: #ffc107;">Rs {row['Price']*1.10:.2f}</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 15px;">
                <button class="chart-btn" onclick="window.open('{chart_link}', '_blank')">
                    📊 View Chart with Entry/Exit Levels
                </button>
            </div>
        </div>
"""
    
    # TIER 2 SIGNALS
    if not tier2_signals.empty:
        html += """
        <div class="tier-header tier2-header">
            ✓ TIER 2 - MEDIUM CONFIDENCE SIGNALS
        </div>
"""
        for idx, row in tier2_signals.iterrows():
            stock_name = row['Stock']
            chart_link = chart_files.get(stock_name, '#')
            
            html += f"""
        <div class="signal-card tier2-card">
            <h3>{stock_name}</h3>
            <div class="signal-info">
                <div class="info-item">
                    <div class="info-label">Confidence</div>
                    <div class="info-value">{row['Confidence']:.1f}%</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Price</div>
                    <div class="info-value">Rs {row['Price']:.2f}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">10% Target</div>
                    <div class="info-value">Rs {row['Price']*1.10:.2f}</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 15px;">
                <button class="chart-btn" onclick="window.open('{chart_link}', '_blank')">
                    📊 View Chart
                </button>
            </div>
        </div>
"""
    
    # Footer
    html += f"""
        <div style="text-align: center; margin-top: 50px; padding-top: 30px; border-top: 2px solid #ddd; color: #666;">
            <p><strong>AI Stock Screener</strong> | VWAP Ladder Strategy</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {len(chart_files)} Interactive Charts Created</p>
            <p style="margin-top: 15px; font-size: 0.9rem;">
                ⚠️ <em>Click "View Chart" to see entry/exit levels and TradingView-style analysis</em>
            </p>
        </div>
    </div>
    
    <a href="javascript:location.reload()" class="refresh-btn">🔄 Refresh Scan</a>
</body>
</html>
"""
    
    # Save main dashboard
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    main_file = f'screener_dashboard_{timestamp}.html'
    
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✓ Main dashboard: {main_file}")
    print(f"✓ Generated {len(chart_files)} interactive charts")
    
    # Open in browser
    print(f"\nOpening dashboard in browser...")
    full_path = os.path.abspath(main_file)
    webbrowser.open('file://' + full_path)
    
    print("\n" + "="*80)
    print("DASHBOARD READY!")
    print("="*80)
    print(f"\nFiles created:")
    print(f"  - Main Dashboard: {main_file}")
    print(f"  - Individual Charts: {len(chart_files)} files (chart_*.html)")
    print(f"\nClick 'View Chart' buttons to see TradingView-style analysis!")
    print("="*80)


if __name__ == '__main__':
    scan_and_generate_dashboard()

