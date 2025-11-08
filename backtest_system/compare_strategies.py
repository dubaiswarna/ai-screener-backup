"""
Compare 3 Strategies for 20%+ CAGR
===================================
Test Conservative, Balanced, and Aggressive approaches
"""

import warnings
warnings.filterwarnings('ignore')

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backtest_dashboard_multimode import MultiModeBacktestEngine, load_stock_data
import pandas as pd

def test_strategy(name, stocks, investment, target, stop, holding, ai_conf):
    """Test a strategy configuration."""
    
    print(f"\n{'='*80}")
    print(f" TESTING: {name}")
    print(f"{'='*80}")
    
    start = pd.Timestamp("2023-01-01", tz='Asia/Kolkata')
    end = pd.Timestamp("2024-12-31", tz='Asia/Kolkata')
    
    stock_data = load_stock_data(stocks, start, end)
    
    if len(stock_data) < 5:
        print(f"ERROR: Only {len(stock_data)} stocks have data")
        return None
    
    engine = MultiModeBacktestEngine(
        investment=investment,
        max_portfolio=20,
        target=target,
        stop=stop,
        max_days=holding,
        mode='Hybrid',
        ai_threshold=ai_conf
    )
    
    trades, daily_values = engine.run_backtest(stock_data, start, end)
    
    if not trades:
        print("No trades executed!")
        return None
    
    df = pd.DataFrame(trades)
    
    total_pnl = df['PnL'].sum()
    win_rate = (len(df[df['PnL'] > 0]) / len(df) * 100)
    initial = investment * 20
    total_return = (total_pnl / initial) * 100
    
    years = 2
    final = initial + total_pnl
    cagr = (((final / initial) ** (1 / years)) - 1) * 100
    
    print(f"\nRESULTS:")
    print(f"  Total Trades: {len(df)}")
    print(f"  Win Rate: {win_rate:.1f}%")
    print(f"  Total P&L: Rs {total_pnl:,.0f}")
    print(f"  Total Return: {total_return:.2f}%")
    print(f"  CAGR: {cagr:.2f}% per year")
    
    if cagr >= 20:
        print(f"  STATUS: SUCCESS! Exceeds 20% target by {cagr-20:.2f}%")
    else:
        print(f"  STATUS: Below target by {20-cagr:.2f}%")
    
    return {
        'Strategy': name,
        'CAGR': cagr,
        'Win_Rate': win_rate,
        'Total_PnL': total_pnl,
        'Trades': len(df)
    }

def main():
    print("="*80)
    print(" COMPARING 3 STRATEGIES FOR 20%+ CAGR")
    print("="*80)
    print("\nTesting on Rs 20L capital, 2 years (2023-2024)")
    
    results = []
    
    # STRATEGY 1: Conservative (Current settings)
    stocks1 = ['PERSISTENT', 'COFORGE', 'LTTS', 'DIXON', 'TRENT', 
               'JUBLFOOD', 'NAVINFLUOR', 'POLYCAB', 'APLAPOLLO', 'JKCEMENT']
    r1 = test_strategy(
        "Conservative",
        stocks=stocks1,
        investment=100000,
        target=0.15,
        stop=0.05,
        holding=30,
        ai_conf=75
    )
    if r1: results.append(r1)
    
    # STRATEGY 2: Balanced (Better settings)
    stocks2 = ['DIXON', 'TRENT', 'PERSISTENT', 'COFORGE', 'LTTS',
               'NAVINFLUOR', 'POLYCAB', 'JUBLFOOD', 'JKCEMENT', 'COROMANDEL',
               'ASTRAL', 'APLAPOLLO', 'TATAELXSI', 'NAUKRI', 'MPHASIS']
    r2 = test_strategy(
        "Balanced",
        stocks=stocks2,
        investment=100000,
        target=0.18,
        stop=0.045,
        holding=25,
        ai_conf=78
    )
    if r2: results.append(r2)
    
    # STRATEGY 3: Aggressive (Max growth)
    stocks3 = ['DIXON', 'TRENT', 'PERSISTENT', 'COFORGE', 'NAVINFLUOR',
               'POLYCAB', 'ASTRAL', 'APLAPOLLO', 'TATAELXSI', 'COROMANDEL',
               'JKCEMENT', 'NAUKRI', 'PAGEIND', 'JUBLFOOD', 'SRF']
    r3 = test_strategy(
        "Aggressive",
        stocks=stocks3,
        investment=100000,
        target=0.20,
        stop=0.04,
        holding=20,
        ai_conf=80
    )
    if r3: results.append(r3)
    
    # Compare results
    print("\n" + "="*80)
    print(" COMPARISON SUMMARY")
    print("="*80)
    
    df_results = pd.DataFrame(results)
    
    print("\n")
    print(df_results.to_string(index=False))
    
    best = df_results.loc[df_results['CAGR'].idxmax()]
    
    print(f"\n{'='*80}")
    print(f" WINNER: {best['Strategy']}")
    print(f"{'='*80}")
    print(f"CAGR: {best['CAGR']:.2f}%")
    print(f"Win Rate: {best['Win_Rate']:.1f}%")
    print(f"Total P&L: Rs {best['Total_PnL']:,.0f}")
    
    if best['CAGR'] >= 20:
        print(f"\nSUCCESS! {best['Strategy']} strategy achieves 20%+ CAGR!")
        print(f"Use this configuration for live trading.")
    else:
        print(f"\nClosest: {best['Strategy']} with {best['CAGR']:.2f}% CAGR")
        print(f"Need {20 - best['CAGR']:.2f}% more - try dashboard for fine-tuning")

if __name__ == "__main__":
    main()

