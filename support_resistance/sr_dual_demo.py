# -*- coding: utf-8 -*-
"""
DUAL S&R SYSTEM DEMO - Based on Video Insights
===============================================

Demonstrates the enhanced S&R detection with:
- PRIMARY S&R: Wick extremes (absolute highs/lows)
- SECONDARY S&R: Close/Open clusters (battle zones)

Based on video teaching:
- "for marking high or low: wick is to be in consideration"
- "second line is always by candle close/open: multiple times"
"""

import pandas as pd
import yfinance as yf
from datetime import datetime

from sr_calculator_enhanced import ProfessionalSRCalculator
from sr_chart_generator import SRChartGenerator


def fetch_data(symbol: str, period: str = '6mo') -> pd.DataFrame:
    """Fetch stock data from Yahoo Finance"""
    print(f"\n📥 Fetching {symbol} data...")
    
    ticker = yf.Ticker(f"{symbol}.NS")
    df_raw = ticker.history(period=period, interval="1d")
    
    if df_raw.empty:
        return None
    
    df = pd.DataFrame({
        'time': df_raw.index,
        'open': df_raw['Open'].values,
        'high': df_raw['High'].values,
        'low': df_raw['Low'].values,
        'close': df_raw['Close'].values,
        'volume': df_raw['Volume'].values
    })
    
    print(f"✅ Fetched {len(df)} days")
    return df


def demo_dual_sr_system(symbol: str = "RELIANCE"):
    """
    Demonstrate DUAL S&R System
    """
    print("="*80)
    print("🎯 DUAL S&R SYSTEM DEMO - Video Insights Implementation")
    print("="*80)
    print(f"\nSymbol: {symbol}")
    print("\nConcepts from Video:")
    print("- PRIMARY S&R: Wick extremes (HIGH/LOW) → Absolute levels")
    print("- SECONDARY S&R: Close/Open clusters → Battle zones (multiple tests)")
    print("="*80)
    
    # Fetch data
    df = fetch_data(symbol)
    if df is None:
        print("❌ Failed to fetch data")
        return
    
    current_price = df['close'].iloc[-1]
    print(f"\n💰 Current Price: ₹{current_price:.2f}")
    
    # Initialize calculator
    sr_calc = ProfessionalSRCalculator(sensitivity=3, min_touches=2)
    
    # ========================================================================
    # CALCULATE DUAL S&R SYSTEM
    # ========================================================================
    print("\n" + "="*80)
    print("🔍 CALCULATING DUAL S&R LEVELS...")
    print("="*80)
    
    dual_sr = sr_calc.calculate_dual_sr(df, current_price)
    
    # ========================================================================
    # DISPLAY PRIMARY S&R (Wick Extremes)
    # ========================================================================
    print("\n🔴 PRIMARY RESISTANCE (Wick Highs - Absolute Levels)")
    print("-" * 80)
    if dual_sr['primary']['resistances']:
        for i, res in enumerate(dual_sr['primary']['resistances'], 1):
            print(f"  R{i}: ₹{res['level']:8.2f} | "
                  f"Distance: {res['distance_pct']:+5.2f}% | "
                  f"Strength: {res['strength']:5.1f} | "
                  f"Touches: {res['touches']}")
            print(f"       → {res['description']}")
    else:
        print("  No primary resistance found")
    
    print("\n🟢 PRIMARY SUPPORT (Wick Lows - Absolute Levels)")
    print("-" * 80)
    if dual_sr['primary']['supports']:
        for i, sup in enumerate(dual_sr['primary']['supports'], 1):
            print(f"  S{i}: ₹{sup['level']:8.2f} | "
                  f"Distance: {sup['distance_pct']:+5.2f}% | "
                  f"Strength: {sup['strength']:5.1f} | "
                  f"Touches: {sup['touches']}")
            print(f"       → {sup['description']}")
    else:
        print("  No primary support found")
    
    # ========================================================================
    # DISPLAY SECONDARY S&R (Close/Open Clusters)
    # ========================================================================
    print("\n🟠 SECONDARY RESISTANCE (Battle Zones - Close/Open Multiple Tests)")
    print("-" * 80)
    if dual_sr['secondary']['resistances']:
        for i, res in enumerate(dual_sr['secondary']['resistances'], 1):
            print(f"  R{i}: ₹{res['level']:8.2f} | "
                  f"Distance: {res['distance_pct']:+5.2f}% | "
                  f"Touches: {res['touches']}")
            print(f"       → {res['description']}")
    else:
        print("  No secondary resistance found (no repeated close/open tests)")
    
    print("\n🟢 SECONDARY SUPPORT (Battle Zones - Close/Open Multiple Tests)")
    print("-" * 80)
    if dual_sr['secondary']['supports']:
        for i, sup in enumerate(dual_sr['secondary']['supports'], 1):
            print(f"  S{i}: ₹{sup['level']:8.2f} | "
                  f"Distance: {sup['distance_pct']:+5.2f}% | "
                  f"Touches: {sup['touches']}")
            print(f"       → {sup['description']}")
    else:
        print("  No secondary support found (no repeated close/open tests)")
    
    # ========================================================================
    # INTERPRETATION
    # ========================================================================
    print("\n" + "="*80)
    print("📊 INTERPRETATION")
    print("="*80)
    
    print("\n🎯 PRIMARY S&R (Solid Thick Lines):")
    print("  - Absolute wick extremes")
    print("  - MAJOR psychological levels")
    print("  - Highest priority for stop loss placement")
    print("  - Breaking these = Strong trend")
    
    print("\n🎯 SECONDARY S&R (Dashed Lines):")
    print("  - Battle zones (repeated close/open tests)")
    print("  - Shows where traders defended levels multiple times")
    print("  - Good for entry/exit zones")
    print("  - Confirms primary levels when they overlap")
    
    # ========================================================================
    # GENERATE INTERACTIVE CHART
    # ========================================================================
    print("\n" + "="*80)
    print("📊 GENERATING INTERACTIVE CHART WITH DUAL S&R...")
    print("="*80)
    
    chart_gen = SRChartGenerator()
    
    # Create chart with BOTH dual S&R and legacy sr_data
    legacy_sr = sr_calc.calculate_support_resistance(df, current_price)
    
    fig = chart_gen.create_sr_chart(
        df=df,
        symbol=symbol,
        sr_data=legacy_sr,  # Legacy format (for backward compatibility)
        dual_sr_data=dual_sr,  # NEW: Dual S&R system
        show_volume=True,
        show_ma=True
    )
    
    # Export chart
    filename = f"{symbol}_Dual_SR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    chart_gen.export_chart(fig, filename, format='html')
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE!")
    print("="*80)
    
    primary_r_count = len(dual_sr['primary']['resistances'])
    primary_s_count = len(dual_sr['primary']['supports'])
    secondary_r_count = len(dual_sr['secondary']['resistances'])
    secondary_s_count = len(dual_sr['secondary']['supports'])
    
    print(f"""
📊 Summary for {symbol}:
  Current Price: ₹{current_price:.2f}
  
  PRIMARY S&R:
    - Resistances: {primary_r_count} (wick highs)
    - Supports: {primary_s_count} (wick lows)
  
  SECONDARY S&R:
    - Resistances: {secondary_r_count} (battle zones)
    - Supports: {secondary_s_count} (battle zones)
  
  Total Levels: {primary_r_count + primary_s_count + secondary_r_count + secondary_s_count}
  
📈 Chart saved: {filename}.html
  - PRIMARY: Solid thick lines (red/green)
  - SECONDARY: Dashed lines (orange/dark green)
  - Open in browser for interactive view!
    """)
    
    print("="*80)
    print("🎯 VIDEO INSIGHTS SUCCESSFULLY IMPLEMENTED!")
    print("="*80)
    print("""
Key Learnings Applied:
1. ✅ PRIMARY S&R from wick extremes (HIGH/LOW)
2. ✅ SECONDARY S&R from close/open clusters
3. ✅ Visual distinction (solid vs dashed)
4. ✅ Battle zones identified
5. ✅ Matches video teaching exactly!
    """)


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         DUAL S&R SYSTEM - Video Insights Demo                 ║
║              PRIMARY + SECONDARY Detection                     ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Change symbol here
    SYMBOL = "RELIANCE"  # Try: RELIANCE, TCS, INFY, HDFCBANK, etc.
    
    try:
        demo_dual_sr_system(SYMBOL)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("Thank you for using Dual S&R System!")
    print("="*80)

