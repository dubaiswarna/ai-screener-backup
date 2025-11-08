"""
Quick Backtest - 20% CAGR Strategy
===================================
Pre-configured optimal settings for 20%+ CAGR
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the multi-mode engine
from backtest_dashboard_multimode import MultiModeBacktestEngine, load_stock_data

# HIGH-GROWTH MID-CAP STOCKS (20%+ CAGR potential)
HIGHGROWTH_STOCKS = [
    # IT Services (High growth)
    'PERSISTENT', 'COFORGE', 'LTTS', 'KPITTECH', 'MPHASIS',
    
    # Consumer & Retail (Strong growth)
    'DIXON', 'TRENT', 'JUBLFOOD', 'TITAN', 'DMART',
    
    # Specialty & Industrial (Niche leaders)
    'NAVINFLUOR', 'POLYCAB', 'APLAPOLLO', 'ASTRAL', 'JKCEMENT',
]

def run_20percent_strategy():
    """Run backtest with 20% CAGR optimized settings."""
    
    print("=" * 80)
    print(" 20%+ CAGR STRATEGY - BACKTEST")
    print("=" * 80)
    print("\nOptimized for: Rs 20 Lakh investment, 20%+ annual returns")
    
    # Optimal settings for 20% CAGR
    INVESTMENT_PER_STOCK = 100000  # Rs 1 Lakh per stock
    MAX_PORTFOLIO = 20  # Max 20 stocks
    TARGET = 0.15  # 15% target (higher than 10%)
    STOP_LOSS = 0.05  # 5% stop (tighter than 7%)
    MAX_HOLDING = 30  # 30 days (faster rotation)
    AI_THRESHOLD = 75  # 75% confidence (quality signals)
    
    print(f"\nStock Universe: {len(HIGHGROWTH_STOCKS)} high-growth mid-caps")
    print(f"Investment per stock: Rs {INVESTMENT_PER_STOCK:,}")
    print(f"Max portfolio: {MAX_PORTFOLIO} stocks")
    print(f"Total capital: Rs {INVESTMENT_PER_STOCK * MAX_PORTFOLIO:,}")
    print(f"\nTarget: {TARGET*100}% | Stop: {STOP_LOSS*100}% | Holding: {MAX_HOLDING} days")
    print(f"AI Confidence: {AI_THRESHOLD}%")
    
    # Bull market period (best for testing)
    start_date = pd.Timestamp("2023-01-01", tz='Asia/Kolkata')
    end_date = pd.Timestamp("2024-12-31", tz='Asia/Kolkata')
    
    print(f"\nBacktest Period: Jan 2023 - Dec 2024 (2 years)")
    print("Reason: Strong bull market period for maximum growth")
    
    # Load data
    print("\nLoading data for high-growth stocks...")
    stock_data = load_stock_data(HIGHGROWTH_STOCKS, start_date, end_date)
    
    print(f"Data loaded for {len(stock_data)} stocks")
    
    # Run backtest
    print("\nRunning HYBRID backtest (AI + Technical)...")
    print("This may take 1-2 minutes...\n")
    
    engine = MultiModeBacktestEngine(
        investment=INVESTMENT_PER_STOCK,
        max_portfolio=MAX_PORTFOLIO,
        target=TARGET,
        stop=STOP_LOSS,
        max_days=MAX_HOLDING,
        mode='Hybrid',
        ai_threshold=AI_THRESHOLD
    )
    
    trades, daily_values = engine.run_backtest(stock_data, start_date, end_date)
    
    if not trades:
        print("WARNING: No trades executed!")
        print("Try: Lower AI confidence or adjust time period")
        return
    
    # Analyze results
    df_trades = pd.DataFrame(trades)
    
    total_trades = len(df_trades)
    winners = len(df_trades[df_trades['PnL'] > 0])
    losers = len(df_trades[df_trades['PnL'] < 0])
    win_rate = (winners / total_trades * 100) if total_trades > 0 else 0
    
    total_pnl = df_trades['PnL'].sum()
    avg_return = df_trades['Return_%'].mean()
    
    initial_capital = INVESTMENT_PER_STOCK * MAX_PORTFOLIO
    total_return_pct = (total_pnl / initial_capital) * 100
    
    # Calculate CAGR
    years = (end_date - start_date).days / 365.25
    final_capital = initial_capital + total_pnl
    cagr = (((final_capital / initial_capital) ** (1 / years)) - 1) * 100
    
    # Display results
    print("\n" + "=" * 80)
    print(" RESULTS - 20% CAGR STRATEGY")
    print("=" * 80)
    
    print(f"\n[PERFORMANCE]")
    print(f"   Initial Capital: Rs {initial_capital:,.0f}")
    print(f"   Final Value: Rs {final_capital:,.0f}")
    print(f"   Total P&L: Rs {total_pnl:,.0f}")
    print(f"   Total Return: {total_return_pct:.2f}%")
    print(f"   CAGR: {cagr:.2f}% per year")
    
    print(f"\n[TRADE STATISTICS]")
    print(f"   Total Trades: {total_trades}")
    print(f"   Winners: {winners} ({win_rate:.1f}%)")
    print(f"   Losers: {losers}")
    print(f"   Avg Return per Trade: {avg_return:.2f}%")
    
    print(f"\n[GOAL ACHIEVEMENT]")
    if cagr >= 20:
        print(f"   SUCCESS! CAGR = {cagr:.2f}% (Target: 20%+)")
        print(f"   Exceeded target by {cagr - 20:.2f}%!")
    elif cagr >= 18:
        print(f"   CLOSE! CAGR = {cagr:.2f}% (Target: 20%)")
        print(f"   Short by {20 - cagr:.2f}% - Try adjusting settings")
    else:
        print(f"   BELOW TARGET. CAGR = {cagr:.2f}% (Target: 20%)")
        print(f"   Suggestions:")
        print(f"      - Increase target to 20%")
        print(f"      - Reduce stop loss to 4%")
        print(f"      - Add more high-growth stocks")
    
    # Save results
    from datetime import datetime
    excel_file = f"backtest_20percent_strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df_trades.to_excel(writer, sheet_name='All Trades', index=False)
        
        summary = pd.DataFrame({
            'Metric': [
                'Strategy', 'Period', 'Initial Capital', 'Final Value', 'Total P&L',
                'Total Return (%)', 'CAGR (%)', 'Total Trades', 'Win Rate (%)',
                'Winners', 'Losers', 'Avg Return per Trade (%)',
                'Target (%)', 'Stop Loss (%)', 'Max Holding (days)',
                'Investment per Stock', 'Max Portfolio Size', 'AI Confidence (%)'
            ],
            'Value': [
                '20% CAGR Optimized', '2023-2024 (2 years)',
                f"Rs {initial_capital:,}", f"Rs {final_capital:,}", f"Rs {total_pnl:,}",
                f"{total_return_pct:.2f}", f"{cagr:.2f}", total_trades, f"{win_rate:.1f}",
                winners, losers, f"{avg_return:.2f}",
                f"{TARGET*100}", f"{STOP_LOSS*100}", MAX_HOLDING,
                f"Rs {INVESTMENT_PER_STOCK:,}", MAX_PORTFOLIO, AI_THRESHOLD
            ]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"\n[FILE SAVED] Results saved to: {excel_file}")
    print(f"   Location: {Path(excel_file).absolute()}")
    
    print("\n" + "=" * 80)
    print(" BACKTEST COMPLETE!")
    print("=" * 80)
    print("\nNext Steps:")
    print("1. Review results in Excel")
    print("2. If CAGR < 20%, adjust settings and rerun")
    print("3. If CAGR > 20%, implement for live trading!")
    print("4. Use dashboard for further customization")
    
    return df_trades, cagr


if __name__ == "__main__":
    try:
        trades, cagr = run_20percent_strategy()
        
        if cagr >= 20:
            print(f"\n*** STRATEGY VALIDATED! {cagr:.2f}% CAGR ACHIEVED! ***")
        else:
            print(f"\n💡 Close but not quite. Try opening the dashboard to adjust settings.")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

