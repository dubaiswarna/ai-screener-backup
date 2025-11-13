"""
TREASURE SIGNAL DIAGNOSTIC TOOL
================================
Analyzes why stocks are being filtered out
Shows what's passing/failing for each stock
"""

import sys
import pandas as pd
import yfinance as yf

# Add current directory to path for imports
sys.path.insert(0, '.')

from hybrid_signal_generator import HybridSignalGenerator
from patterns.chart_pattern_detector import ChartPatternDetector
from support_resistance.sr_calculator_enhanced import ProfessionalSRCalculator


def diagnose_stock(symbol, min_confidence=70, verbose=True):
    """Diagnose why a stock passes or fails"""
    
    print(f"\n{'='*80}")
    print(f"🔍 DIAGNOSING: {symbol}")
    print('='*80)
    
    # Fetch data
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        df_raw = ticker.history(period="6mo", interval="1d")
        
        if df_raw.empty:
            print(f"❌ No data available")
            return None
        
        df = pd.DataFrame({
            'time': df_raw.index,
            'open': df_raw['Open'].values,
            'high': df_raw['High'].values,
            'low': df_raw['Low'].values,
            'close': df_raw['Close'].values,
            'volume': df_raw['Volume'].values
        })
        
        current_price = df['close'].iloc[-1]
        print(f"📊 Current Price: ₹{current_price:.2f}")
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None
    
    # Initialize
    hybrid_gen = HybridSignalGenerator(min_confidence=min_confidence, min_rr_ratio=1.5)
    sr_calc = ProfessionalSRCalculator(sensitivity=3, min_touches=2)
    pattern_detector = ChartPatternDetector()
    
    # Analyze each layer
    print("\n" + "-"*80)
    print("LAYER 1: TECHNICAL ANALYSIS")
    print("-"*80)
    tech_result = hybrid_gen.analyze_technical(df)
    print(f"Score: {tech_result['score']}/35 ({tech_result['confidence_pct']:.1f}%)")
    print(f"Signal: {tech_result['signal']}")
    print("Factors:")
    for factor in tech_result['factors']:
        print(f"  ✅ {factor}")
    if not tech_result['factors']:
        print("  ❌ No technical factors found (WEAK)")
    
    print("\n" + "-"*80)
    print("LAYER 2: S&R ANALYSIS")
    print("-"*80)
    sr_result = hybrid_gen.analyze_sr(sr_calc, df, current_price)
    print(f"Score: {sr_result['score']}/40 ({sr_result['confidence_pct']:.1f}%)")
    print(f"Signal: {sr_result['signal']}")
    print("Factors:")
    for factor in sr_result['factors']:
        print(f"  ✅ {factor}")
    if not sr_result['factors']:
        print("  ❌ No S&R factors found (WEAK)")
    
    print("\n" + "-"*80)
    print("LAYER 3: CHART PATTERNS")
    print("-"*80)
    pattern_result = hybrid_gen.analyze_patterns(pattern_detector, df, sr_result['signal'])
    print(f"Score: {pattern_result['score']}/25 ({pattern_result['confidence_pct']:.1f}%)")
    if pattern_result['pattern']:
        pattern = pattern_result['pattern']
        print(f"Pattern: {pattern['pattern']} ({pattern['type']})")
        print(f"Confidence: {pattern['confidence']:.1f}%")
        print(f"Description: {pattern['description']}")
    else:
        print("  ❌ No chart pattern found")
    
    print("\n" + "-"*80)
    print("CONFLUENCE RESULT")
    print("-"*80)
    confluence = hybrid_gen.calculate_confluence(tech_result, sr_result, pattern_result)
    print(f"Total Score: {confluence['total_score']}/100 ({confluence['confidence']:.1f}%)")
    print(f"Final Signal: {confluence['final_signal']}")
    print(f"Is Treasure: {confluence['is_treasure']}")
    print(f"Confluence Count: {confluence['confluence_count']}/3")
    
    print(f"\nTech Signal: {confluence['tech_signal']}")
    print(f"S&R Signal: {confluence['sr_signal']}")
    print(f"Pattern Signal: {confluence['pattern_signal']}")
    
    # Check R:R
    if confluence['is_treasure']:
        trade_setup = hybrid_gen.generate_trade_setup(
            symbol, df, current_price, sr_result.get('sr_data', {}), confluence['final_signal']
        )
        if trade_setup:
            print(f"\nTrade Setup:")
            print(f"  Entry: ₹{trade_setup.get('entry', 0):.2f}")
            print(f"  SL: ₹{trade_setup.get('stop_loss', 0):.2f}")
            print(f"  Target: ₹{trade_setup.get('target1', 0):.2f}")
            print(f"  R:R: 1:{trade_setup.get('rr_ratio', 0):.2f}")
            
            if trade_setup.get('rr_ratio', 0) < hybrid_gen.min_rr_ratio:
                print(f"  ❌ FILTERED: R:R {trade_setup['rr_ratio']:.2f} < {hybrid_gen.min_rr_ratio} (minimum)")
            else:
                print(f"  ✅ PASSED ALL FILTERS!")
    
    # Why filtered?
    print("\n" + "="*80)
    if not confluence['is_treasure']:
        print("❌ FILTERED OUT - REASONS:")
        
        if confluence['confidence'] < 85:
            print(f"  • Confidence too low: {confluence['confidence']:.1f}% < 85%")
        
        if confluence['confluence_count'] < 2:
            print(f"  • Not enough agreement: {confluence['confluence_count']}/3 layers agree")
            print(f"    Tech says: {confluence['tech_signal']}")
            print(f"    S&R says: {confluence['sr_signal']}")
            print(f"    Pattern says: {confluence['pattern_signal']}")
    else:
        print("✅ PASSED ALL FILTERS - TREASURE SIGNAL!")
    print("="*80)
    
    return confluence


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║        TREASURE SIGNAL DIAGNOSTIC TOOL                       ║
║     (Shows why stocks pass or fail filters)                  ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Test with different confidence levels
    test_confidences = [85, 80, 75, 70]
    test_stocks = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'SBIN']
    
    print("\n🔬 TESTING DIFFERENT CONFIDENCE LEVELS...")
    print("="*80)
    
    for conf in test_confidences:
        print(f"\n📊 TESTING WITH MIN CONFIDENCE: {conf}%")
        print("-"*80)
        
        results = []
        for stock in test_stocks:
            result = diagnose_stock(stock, min_confidence=conf, verbose=False)
            if result:
                results.append({'symbol': stock, 'confidence': result['confidence'], 
                              'signal': result['final_signal'], 'is_treasure': result['is_treasure']})
        
        treasures = [r for r in results if r['is_treasure']]
        
        print(f"Stocks Analyzed: {len(results)}")
        print(f"Treasure Signals Found: {len(treasures)}")
        
        if treasures:
            print("✅ SIGNALS:")
            for t in treasures:
                print(f"  💎 {t['symbol']}: {t['signal']} ({t['confidence']:.1f}%)")
    
    # Now do detailed analysis on one stock
    print("\n" + "="*80)
    print("📋 DETAILED ANALYSIS: RELIANCE")
    print("="*80)
    diagnose_stock('RELIANCE', min_confidence=75, verbose=True)
    
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)
    print("""
Based on diagnostic results:

1. If NO signals at 85%: Lower to 80% (Good balance of quality & quantity)
2. If NO signals at 80%: Lower to 75% (Still high quality)
3. If NO signals at 75%: Bull market too strong, wait for pullback

QUALITY LEVELS:
- 85%+: Ultra Premium (1-2 signals per week)
- 80-84%: Premium (3-5 signals per week)
- 75-79%: Good (5-10 signals per week)
- 70-74%: Moderate (10-15 signals per week)
    """)


