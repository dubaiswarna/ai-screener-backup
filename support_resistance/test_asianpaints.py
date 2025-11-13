# Quick test for ASIANPAINTS S&R analysis

import yfinance as yf
import pandas as pd
from sr_calculator_enhanced import ProfessionalSRCalculator

print("="*80)
print("🎨 ASIANPAINTS - DUAL S&R ANALYSIS")
print("="*80)

# Fetch data
print("\n📥 Fetching ASIANPAINTS data from Yahoo Finance...")
ticker = yf.Ticker('ASIANPAINT.NS')
df_raw = ticker.history(period='6mo', interval='1d')

if df_raw.empty:
    print("❌ No data found for ASIANPAINTS")
    exit()

# Convert to our format
df = pd.DataFrame({
    'time': df_raw.index,
    'open': df_raw['Open'].values,
    'high': df_raw['High'].values,
    'low': df_raw['Low'].values,
    'close': df_raw['Close'].values,
    'volume': df_raw['Volume'].values
})

print(f"✅ Data Available: {len(df)} days")
print(f"📊 Latest Price: ₹{df['close'].iloc[-1]:.2f}")
print(f"📅 Range: {df['time'].iloc[0].strftime('%Y-%m-%d')} to {df['time'].iloc[-1].strftime('%Y-%m-%d')}")
print(f"📈 6-Month High: ₹{df['high'].max():.2f}")
print(f"📉 6-Month Low: ₹{df['low'].min():.2f}")

current_price = df['close'].iloc[-1]

# Initialize calculator
sr_calc = ProfessionalSRCalculator(sensitivity=3, min_touches=2)

# Calculate DUAL S&R
print("\n" + "="*80)
print("🔍 CALCULATING DUAL S&R SYSTEM...")
print("="*80)

dual_sr = sr_calc.calculate_dual_sr(df, current_price)

# Display results
print(f"\n💰 Current Price: ₹{current_price:.2f}")
print("\n" + "="*80)
print("🟢 SUPPORT LEVELS")
print("="*80)

if dual_sr['primary']['supports']:
    print("\n⭐ PRIMARY SUPPORT (Wick Lows - Major Levels):")
    for i, sup in enumerate(dual_sr['primary']['supports'][:3], 1):
        print(f"  S{i}: ₹{sup['level']:8.2f} | Distance: {sup['distance_pct']:+6.2f}% | Strength: {sup['strength']:5.1f} | Touches: {sup['touches']}")
        print(f"       → {sup['description']}")

if dual_sr['secondary']['supports']:
    print("\n🔸 SECONDARY SUPPORT (Battle Zones - Close/Open):")
    for i, sup in enumerate(dual_sr['secondary']['supports'][:3], 1):
        print(f"  S{i}: ₹{sup['level']:8.2f} | Distance: {sup['distance_pct']:+6.2f}% | Tests: {sup['touches']}x")
        print(f"       → {sup['description']}")

print("\n" + "="*80)
print("🔴 RESISTANCE LEVELS")
print("="*80)

if dual_sr['primary']['resistances']:
    print("\n⭐ PRIMARY RESISTANCE (Wick Highs - Major Levels):")
    for i, res in enumerate(dual_sr['primary']['resistances'][:3], 1):
        print(f"  R{i}: ₹{res['level']:8.2f} | Distance: {res['distance_pct']:+6.2f}% | Strength: {res['strength']:5.1f} | Touches: {res['touches']}")
        print(f"       → {res['description']}")

if dual_sr['secondary']['resistances']:
    print("\n🔸 SECONDARY RESISTANCE (Battle Zones - Close/Open):")
    for i, res in enumerate(dual_sr['secondary']['resistances'][:3], 1):
        print(f"  R{i}: ₹{res['level']:8.2f} | Distance: {res['distance_pct']:+6.2f}% | Tests: {res['touches']}x")
        print(f"       → {res['description']}")

# Calculate additional features
print("\n" + "="*80)
print("📍 PIVOT POINTS (Standard)")
print("="*80)

pivots = sr_calc.calculate_pivot_points(df, 'standard')
print(f"\nPivot: ₹{pivots['pivot']:8.2f}")
print(f"R1: ₹{pivots['r1']:8.2f} | R2: ₹{pivots['r2']:8.2f} | R3: ₹{pivots['r3']:8.2f}")
print(f"S1: ₹{pivots['s1']:8.2f} | S2: ₹{pivots['s2']:8.2f} | S3: ₹{pivots['s3']:8.2f}")

# Fibonacci
print("\n" + "="*80)
print("📈 FIBONACCI LEVELS")
print("="*80)

fib = sr_calc.calculate_fibonacci_levels(df, lookback_period=50)
if not fib.get('error'):
    print(f"\nTrend: {fib['trend']}")
    print(f"Swing High: ₹{fib['swing_high']:.2f} | Swing Low: ₹{fib['swing_low']:.2f}")
    
    print("\n🔄 RETRACEMENT:")
    for level, price in fib['retracement'].items():
        marker = " ⭐ GOLDEN ZONE" if level in ['50%', '61.8%'] else ""
        print(f"  {level:6s}: ₹{price:8.2f}{marker}")
    
    print("\n🎯 EXTENSION TARGETS:")
    for level, price in fib['extension'].items():
        print(f"  {level:6s}: ₹{price:8.2f}")
    
    if fib['golden_zone']['in_zone']:
        print(f"\n⭐ Price is IN GOLDEN ZONE!")

print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE!")
print("="*80)


