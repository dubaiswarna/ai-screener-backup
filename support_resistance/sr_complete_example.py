# -*- coding: utf-8 -*-
"""
COMPLETE S&R ANALYSIS EXAMPLE
==============================

Demonstrates ALL features of the Professional S&R System:
- Swing-based S&R detection
- Pivot Points (Standard, Fibonacci, Camarilla)
- Fibonacci Retracement & Extension
- Trade Setup Generation
- Multi-Timeframe Confluence
- Historical Success Rate
- Interactive Charts
- Backtesting

Usage:
    python sr_complete_example.py
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Import our professional modules
from sr_calculator_enhanced import ProfessionalSRCalculator
from sr_chart_generator import SRChartGenerator
from sr_backtest_engine import SRBacktestEngine


def fetch_stock_data(symbol: str, period: str = '6mo') -> pd.DataFrame:
    """Fetch stock data from Yahoo Finance"""
    print(f"\n📥 Fetching data for {symbol}...")
    
    ticker = yf.Ticker(f"{symbol}.NS")
    df_raw = ticker.history(period=period, interval="1d")
    
    if df_raw.empty:
        print(f"❌ No data found for {symbol}")
        return None
    
    # Convert to our format
    df = pd.DataFrame({
        'time': df_raw.index,
        'open': df_raw['Open'].values,
        'high': df_raw['High'].values,
        'low': df_raw['Low'].values,
        'close': df_raw['Close'].values,
        'volume': df_raw['Volume'].values
    })
    
    print(f"✅ Fetched {len(df)} days of data")
    return df


def run_complete_analysis(symbol: str = "RELIANCE"):
    """
    Run complete S&R analysis with all features
    """
    print("="*80)
    print(f"🚀 PROFESSIONAL S&R ANALYSIS - {symbol}")
    print("="*80)
    
    # ========================================================================
    # STEP 1: FETCH DATA
    # ========================================================================
    df = fetch_stock_data(symbol)
    if df is None:
        return
    
    current_price = df['close'].iloc[-1]
    print(f"📊 Current Price: ₹{current_price:.2f}")
    
    # ========================================================================
    # STEP 2: INITIALIZE CALCULATOR
    # ========================================================================
    print("\n" + "="*80)
    print("🔧 Initializing Professional S&R Calculator...")
    print("="*80)
    
    sr_calc = ProfessionalSRCalculator(
        sensitivity=3,      # More nearby levels
        min_touches=2       # Min 2 touches for valid level
    )
    
    # ========================================================================
    # STEP 3: CALCULATE SUPPORT & RESISTANCE
    # ========================================================================
    print("\n📊 Calculating Support & Resistance Levels...")
    sr_data = sr_calc.calculate_support_resistance(df, current_price)
    
    print(f"\n✅ Found {sr_data['total_support_levels']} Support Levels")
    print(f"✅ Found {sr_data['total_resistance_levels']} Resistance Levels")
    
    print("\n🟢 TOP 3 SUPPORTS:")
    for i, sup in enumerate(sr_data['supports'][:3], 1):
        print(f"  S{i}: ₹{sup['level']:8.2f} | Strength: {sup['strength']:5.1f} | Touches: {sup['touches']} | Distance: {sup['distance_pct']:+.2f}%")
    
    print("\n🔴 TOP 3 RESISTANCES:")
    for i, res in enumerate(sr_data['resistances'][:3], 1):
        print(f"  R{i}: ₹{res['level']:8.2f} | Strength: {res['strength']:5.1f} | Touches: {res['touches']} | Distance: {res['distance_pct']:+.2f}%")
    
    # ========================================================================
    # STEP 4: CALCULATE PIVOT POINTS
    # ========================================================================
    print("\n" + "="*80)
    print("🎯 Calculating Pivot Points...")
    print("="*80)
    
    # Standard Pivots
    standard_pivots = sr_calc.calculate_pivot_points(df, 'standard')
    print(f"\n📌 STANDARD PIVOTS ({standard_pivots['type']}):")
    print(f"   Pivot: ₹{standard_pivots['pivot']:.2f}")
    print(f"   R1: ₹{standard_pivots['r1']:.2f} | R2: ₹{standard_pivots['r2']:.2f} | R3: ₹{standard_pivots['r3']:.2f}")
    print(f"   S1: ₹{standard_pivots['s1']:.2f} | S2: ₹{standard_pivots['s2']:.2f} | S3: ₹{standard_pivots['s3']:.2f}")
    
    # Fibonacci Pivots
    fib_pivots = sr_calc.calculate_pivot_points(df, 'fibonacci')
    print(f"\n📐 FIBONACCI PIVOTS ({fib_pivots['type']}):")
    print(f"   Pivot: ₹{fib_pivots['pivot']:.2f}")
    print(f"   R1: ₹{fib_pivots['r1']:.2f} | R2: ₹{fib_pivots['r2']:.2f} | R3: ₹{fib_pivots['r3']:.2f}")
    print(f"   S1: ₹{fib_pivots['s1']:.2f} | S2: ₹{fib_pivots['s2']:.2f} | S3: ₹{fib_pivots['s3']:.2f}")
    
    # ========================================================================
    # STEP 5: CALCULATE FIBONACCI LEVELS
    # ========================================================================
    print("\n" + "="*80)
    print("📈 Calculating Fibonacci Retracement & Extension...")
    print("="*80)
    
    fib_data = sr_calc.calculate_fibonacci_levels(df, lookback_period=50)
    
    if not fib_data.get('error'):
        print(f"\nTrend: {fib_data['trend']}")
        print(f"Swing High: ₹{fib_data['swing_high']:.2f}")
        print(f"Swing Low:  ₹{fib_data['swing_low']:.2f}")
        
        print("\n🔄 RETRACEMENT LEVELS:")
        for level, price in fib_data['retracement'].items():
            marker = " ⭐ GOLDEN ZONE" if level in ['50%', '61.8%'] else ""
            print(f"   {level:6s}: ₹{price:.2f}{marker}")
        
        print("\n🎯 EXTENSION TARGETS:")
        for level, price in fib_data['extension'].items():
            print(f"   {level:6s}: ₹{price:.2f}")
        
        if fib_data['golden_zone']['in_zone']:
            print(f"\n⭐ Price is IN GOLDEN ZONE (₹{fib_data['golden_zone']['lower']:.2f} - ₹{fib_data['golden_zone']['upper']:.2f})")
            print("   High probability reversal area!")
    
    # ========================================================================
    # STEP 6: GENERATE TRADE SETUPS
    # ========================================================================
    print("\n" + "="*80)
    print("💡 Generating Trade Setups...")
    print("="*80)
    
    trade_setups = sr_calc.generate_trade_setups(
        df=df,
        sr_data=sr_data,
        fib_data=fib_data,
        pivot_data=standard_pivots,
        risk_per_trade_pct=2.0,
        capital=100000
    )
    
    if trade_setups:
        for setup in trade_setups:
            print(f"\n{'🟢' if setup['type'] == 'BUY' else '🔴'} {setup['type']} SETUP")
            print(f"   Entry:      ₹{setup['entry_price']:.2f} ({setup['status']})")
            print(f"   Stop Loss:  ₹{setup['stop_loss']:.2f}")
            print(f"   Target 1:   ₹{setup['target1']:.2f} (R:R = 1:{setup['rr_ratio1']:.2f})")
            print(f"   Target 2:   ₹{setup['target2']:.2f} (R:R = 1:{setup['rr_ratio2']:.2f})")
            print(f"   Position:   {setup['position_size']} shares")
            print(f"   Risk:       ₹{setup['risk_amount']:,.0f}")
            print(f"   Profit T1:  ₹{setup['potential_profit1']:,.0f}")
            print(f"   Profit T2:  ₹{setup['potential_profit2']:,.0f}")
            print(f"   Confidence: {setup['confidence']}")
    else:
        print("   No favorable trade setups at current price.")
    
    # ========================================================================
    # STEP 7: MULTI-TIMEFRAME CONFLUENCE
    # ========================================================================
    print("\n" + "="*80)
    print("🎯 Calculating Multi-Timeframe Confluence...")
    print("="*80)
    
    mtf_data = sr_calc.calculate_multi_timeframe_sr(df)
    
    if not mtf_data.get('error'):
        confluence_zones = mtf_data.get('confluence_zones', [])
        if confluence_zones:
            print(f"\n✅ Found {len(confluence_zones)} CONFLUENCE ZONES:")
            for zone in confluence_zones[:5]:
                timeframes_str = ", ".join(zone['timeframes'])
                print(f"   {zone['type']:11s}: ₹{zone['level']:.2f} | Score: {zone['confluence_score']}/3 | TF: {timeframes_str}")
        else:
            print("\n   No confluence zones found (levels don't align across timeframes)")
    
    # ========================================================================
    # STEP 8: HISTORICAL SUCCESS RATE
    # ========================================================================
    print("\n" + "="*80)
    print("📊 Calculating Historical Success Rates...")
    print("="*80)
    
    success_data = sr_calc.calculate_historical_success_rate(df, sr_data)
    
    if success_data.get('supports'):
        print("\n🟢 SUPPORT SUCCESS RATES:")
        for sup in success_data['supports'][:3]:
            print(f"   ₹{sup['level']:.2f}: {sup['success_rate']:5.1f}% ({sup['holds']}/{sup['total_tests']} held) - {sup['confidence']}")
    
    if success_data.get('resistances'):
        print("\n🔴 RESISTANCE SUCCESS RATES:")
        for res in success_data['resistances'][:3]:
            print(f"   ₹{res['level']:.2f}: {res['success_rate']:5.1f}% ({res['holds']}/{res['total_tests']} held) - {res['confidence']}")
    
    # ========================================================================
    # STEP 9: BACKTEST STRATEGY
    # ========================================================================
    print("\n" + "="*80)
    print("🔬 Backtesting S&R Bounce Strategy...")
    print("="*80)
    
    backtest_engine = SRBacktestEngine(
        initial_capital=100000,
        commission_pct=0.1,
        slippage_pct=0.05
    )
    
    backtest_results = backtest_engine.backtest_bounce_strategy(
        df=df,
        sr_data=sr_data,
        stop_loss_pct=2.0,
        target_pct=5.0,
        tolerance_pct=1.0
    )
    
    if not backtest_results.get('error'):
        report = backtest_engine.generate_backtest_report(backtest_results)
        print(report)
        
        # Show last 5 trades
        print("\n📋 LAST 5 TRADES:")
        for trade in backtest_results['trades'][-5:]:
            print(f"   {trade['type']:5s} | Entry: ₹{trade['entry_price']:.2f} | Exit: ₹{trade['exit_price']:.2f} | P/L: {trade['pnl_pct']:+.2f}% | {trade['exit_reason']}")
    else:
        print(f"\n❌ Backtest Error: {backtest_results['error']}")
    
    # ========================================================================
    # STEP 10: GENERATE INTERACTIVE CHART
    # ========================================================================
    print("\n" + "="*80)
    print("📊 Generating Interactive Chart...")
    print("="*80)
    
    chart_gen = SRChartGenerator()
    
    fig = chart_gen.create_sr_chart(
        df=df,
        symbol=symbol,
        sr_data=sr_data,
        pivot_data=standard_pivots,
        fib_data=fib_data,
        trade_setups=trade_setups,
        show_volume=True,
        show_ma=True
    )
    
    # Export chart
    chart_filename = f"{symbol}_SR_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    chart_gen.export_chart(fig, chart_filename, format='html')
    
    print(f"\n✅ Chart saved: {chart_filename}.html")
    print("   Open in browser to view interactive chart with all S&R levels!")
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE!")
    print("="*80)
    print(f"""
Summary for {symbol}:
- Current Price: ₹{current_price:.2f}
- Support Levels: {sr_data['total_support_levels']}
- Resistance Levels: {sr_data['total_resistance_levels']}
- Trade Setups: {len(trade_setups)}
- Confluence Zones: {len(mtf_data.get('confluence_zones', []))}
- Backtest Return: {backtest_results.get('total_return_pct', 0):.2f}%
- Backtest Win Rate: {backtest_results.get('win_rate_pct', 0):.1f}%

📊 Interactive chart created: {chart_filename}.html
🎯 All analysis data saved in memory for further processing
    """)


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     PROFESSIONAL SUPPORT & RESISTANCE ANALYSIS SYSTEM        ║
║                    Complete Demonstration                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # You can change the symbol here
    SYMBOL = "RELIANCE"  # Change to any NSE stock
    
    try:
        run_complete_analysis(SYMBOL)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("Thank you for using Professional S&R Analysis System!")
    print("="*80)

