"""
3-Year Backtest - HYBRID (AI + Technical Analysis)
==================================================
When AI doesn't give BUY signals, use proven technical analysis
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime, timedelta
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

TOP_5_STOCKS = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']

INVESTMENT_PER_STOCK = 200000  # 2 Lakh
MAX_PORTFOLIO_SIZE = 20
TARGET_RETURN = 0.10  # 10%
STOP_LOSS = 0.07  # 7%
HOLDING_PERIOD = 60  # days


class BacktestPortfolio:
    """Portfolio management for backtesting."""
    
    def __init__(self):
        self.portfolio = []
        self.trades = []
    
    def can_enter(self):
        return len(self.portfolio) < MAX_PORTFOLIO_SIZE
    
    def enter_position(self, symbol, date, price, reason, confidence=None):
        qty = int(INVESTMENT_PER_STOCK / price)
        pos = {
            'symbol': symbol,
            'entry_date': date,
            'entry_price': price,
            'qty': qty,
            'investment': qty * price,
            'reason': reason,
            'confidence': confidence,
            'target': price * (1 + TARGET_RETURN),
            'stop': price * (1 - STOP_LOSS),
            'max_date': date + timedelta(days=HOLDING_PERIOD)
        }
        self.portfolio.append(pos)
        return pos
    
    def check_exit(self, pos, date, price):
        if price >= pos['target']:
            return 'TARGET', price
        if price <= pos['stop']:
            return 'STOP_LOSS', price
        if date >= pos['max_date']:
            return 'TIME_EXIT', price
        return None, None
    
    def exit_position(self, pos, date, price, reason):
        exit_value = pos['qty'] * price
        pnl = exit_value - pos['investment']
        pnl_pct = (pnl / pos['investment']) * 100
        days = (date - pos['entry_date']).days
        
        trade = {
            'Symbol': pos['symbol'],
            'Entry_Date': pos['entry_date'].strftime('%Y-%m-%d'),
            'Entry_Price': f"Rs{pos['entry_price']:.2f}",
            'Exit_Date': date.strftime('%Y-%m-%d'),
            'Exit_Price': f"Rs{price:.2f}",
            'Exit_Reason': reason,
            'Investment': f"Rs{pos['investment']:,.2f}",
            'Exit_Value': f"Rs{exit_value:,.2f}",
            'PnL': f"Rs{pnl:,.2f}",
            'Return_%': f"{pnl_pct:.2f}%",
            'Holding_Days': days,
            'Entry_Reason': pos['reason'],
            'Confidence': f"{pos['confidence']:.1f}%" if pos['confidence'] else 'N/A'
        }
        self.trades.append(trade)
        return trade


def calculate_technical_signal(df):
    """Generate signal using RSI + Moving Average crossover."""
    
    if len(df) < 50:
        return False, 0, "Insufficient data"
    
    # Calculate indicators
    close = df['Close']
    
    # RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]
    
    # Moving averages
    sma_20 = close.rolling(20).mean()
    sma_50 = close.rolling(50).mean()
    
    current_price = close.iloc[-1]
    current_sma20 = sma_20.iloc[-1]
    current_sma50 = sma_50.iloc[-1]
    prev_sma20 = sma_20.iloc[-2]
    prev_sma50 = sma_50.iloc[-2]
    
    # Signal logic
    buy_signal = False
    confidence = 0
    reason = ""
    
    # Golden Cross + RSI oversold
    if (current_sma20 > current_sma50 and prev_sma20 <= prev_sma50 and 
        current_rsi < 40 and current_price > current_sma20):
        buy_signal = True
        confidence = 85
        reason = "Golden Cross + RSI Oversold"
    
    # Price above both MAs + RSI moderate
    elif (current_price > current_sma20 and current_price > current_sma50 and
          30 < current_rsi < 70 and current_sma20 > current_sma50):
        buy_signal = True
        confidence = 75
        reason = "Uptrend + Healthy RSI"
    
    # Pullback to 20 SMA in uptrend
    elif (current_sma20 > current_sma50 and 
          abs(current_price - current_sma20) / current_sma20 < 0.02 and
          current_rsi < 50):
        buy_signal = True
        confidence = 70
        reason = "Pullback to SMA20"
    
    return buy_signal, confidence, reason


def run_hybrid_backtest():
    """Run 3-year backtest with hybrid strategy."""
    
    print("=" * 80)
    print(" 3-YEAR BACKTEST - HYBRID STRATEGY (AI + Technical)")
    print("=" * 80)
    print(f"\nStocks: {', '.join(TOP_5_STOCKS)}")
    print(f"Investment: Rs{INVESTMENT_PER_STOCK:,} per stock")
    print(f"Max portfolio: {MAX_PORTFOLIO_SIZE} stocks")
    print(f"Target: +{TARGET_RETURN*100}% | Stop: -{STOP_LOSS*100}%")
    print(f"Holding: {HOLDING_PERIOD} days max")
    
    start_date = pd.Timestamp("2022-03-01", tz='Asia/Kolkata')
    end_date = pd.Timestamp("2025-02-28", tz='Asia/Kolkata')
    
    print(f"\nPeriod: March 2022 to February 2025 (3 years)")
    
    # Load data
    print("\nLoading data...")
    stock_data = {}
    
    for symbol in TOP_5_STOCKS:
        data_file = Path(f"../Nifty200_Data/NSE_{symbol}_1D.csv")
        if not data_file.exists():
            continue
        
        df = pd.read_csv(data_file, parse_dates=['time'])
        df = df.rename(columns={'time': 'Date', 'open': 'Open', 'high': 'High',
                                'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
        df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        
        if len(df) >= 200:
            stock_data[symbol] = df
            print(f"  {symbol}: {len(df)} days")
    
    if not stock_data:
        print("ERROR: No data loaded!")
        return []
    
    # Run backtest
    print("\nRunning backtest...")
    portfolio = BacktestPortfolio()
    all_dates = sorted(set([d for df in stock_data.values() for d in df['Date']]))
    
    signals_generated = 0
    
    for current_date in all_dates:
        # Check exits
        to_exit = []
        
        for pos in portfolio.portfolio:
            symbol = pos['symbol']
            if symbol not in stock_data:
                continue
            
            day_data = stock_data[symbol][stock_data[symbol]['Date'] == current_date]
            if day_data.empty:
                continue
            
            current_price = day_data['Close'].iloc[0]
            reason, exit_price = portfolio.check_exit(pos, current_date, current_price)
            
            if reason:
                to_exit.append((pos, current_date, exit_price, reason))
        
        for pos, date, price, reason in to_exit:
            portfolio.exit_position(pos, date, price, reason)
            portfolio.portfolio.remove(pos)
        
        # Look for entries (check once per week to reduce computation)
        if current_date.weekday() == 0 and portfolio.can_enter():  # Monday
            for symbol in stock_data.keys():
                if not portfolio.can_enter():
                    break
                
                # Skip if already in portfolio
                if any(p['symbol'] == symbol for p in portfolio.portfolio):
                    continue
                
                df = stock_data[symbol]
                historical = df[df['Date'] <= current_date]
                
                if len(historical) < 50:
                    continue
                
                # Check technical signal
                buy_signal, confidence, reason = calculate_technical_signal(historical.tail(200))
                
                if buy_signal:
                    entry_price = historical['Close'].iloc[-1]
                    portfolio.enter_position(symbol, current_date, entry_price, reason, confidence)
                    signals_generated += 1
    
    # Close all positions at end
    for pos in portfolio.portfolio[:]:
        symbol = pos['symbol']
        final_price = stock_data[symbol]['Close'].iloc[-1]
        portfolio.exit_position(pos, end_date, final_price, 'BACKTEST_END')
        portfolio.portfolio.remove(pos)
    
    print(f"\nBacktest complete!")
    print(f"Signals generated: {signals_generated}")
    print(f"Trades executed: {len(portfolio.trades)}")
    
    return portfolio.trades


def main():
    """Main execution."""
    
    trades = run_hybrid_backtest()
    
    if not trades:
        print("\n[ERROR] No trades executed!")
        return
    
    df = pd.DataFrame(trades)
    
    # Statistics
    print("\n" + "=" * 80)
    print(" BACKTEST RESULTS")
    print("=" * 80)
    
    df['PnL_Num'] = df['PnL'].str.replace('Rs', '').str.replace(',', '').astype(float)
    df['Return_Num'] = df['Return_%'].str.rstrip('%').astype(float)
    
    total = len(df)
    wins = len(df[df['PnL_Num'] > 0])
    losses = len(df[df['PnL_Num'] < 0])
    win_rate = (wins / total * 100) if total > 0 else 0
    
    total_pnl = df['PnL_Num'].sum()
    avg_return = df['Return_Num'].mean()
    avg_win = df[df['PnL_Num'] > 0]['Return_Num'].mean() if wins > 0 else 0
    avg_loss = df[df['PnL_Num'] < 0]['Return_Num'].mean() if losses > 0 else 0
    best = df.loc[df['PnL_Num'].idxmax()]
    worst = df.loc[df['PnL_Num'].idxmin()]
    avg_days = df['Holding_Days'].mean()
    
    print(f"\nTotal Trades: {total}")
    print(f"Winners: {wins} ({win_rate:.1f}%)")
    print(f"Losers: {losses}")
    
    print(f"\nTotal P&L: Rs{total_pnl:,.2f}")
    print(f"Average Return: {avg_return:.2f}%")
    print(f"Average Win: {avg_win:.2f}%")
    print(f"Average Loss: {avg_loss:.2f}%")
    print(f"Average Holding: {avg_days:.0f} days")
    
    print(f"\nBest Trade: {best['Symbol']} - {best['Return_%']} ({best['PnL']})")
    print(f"Worst Trade: {worst['Symbol']} - {worst['Return_%']} ({worst['PnL']})")
    
    # Export to Excel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_file = f"backtest_3years_hybrid_{timestamp}.xlsx"
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df_export = df.drop(['PnL_Num', 'Return_Num'], axis=1)
        df_export.to_excel(writer, sheet_name='All Trades', index=False)
        
        df_wins = df_export[df['PnL_Num'] > 0]
        if len(df_wins) > 0:
            df_wins.to_excel(writer, sheet_name='Winners', index=False)
        
        df_losses = df_export[df['PnL_Num'] < 0]
        if len(df_losses) > 0:
            df_losses.to_excel(writer, sheet_name='Losers', index=False)
        
        summary = pd.DataFrame({
            'Metric': [
                'Period', 'Total Trades', 'Winners', 'Losers', 'Win Rate (%)',
                'Total P&L (Rs)', 'Avg Return (%)', 'Avg Win (%)', 'Avg Loss (%)',
                'Avg Holding (days)', 'Best Trade (%)', 'Worst Trade (%)',
                'Investment per Trade', 'Max Portfolio Size'
            ],
            'Value': [
                'March 2022 - Feb 2025', total, wins, losses, f"{win_rate:.2f}",
                f"{total_pnl:,.2f}", f"{avg_return:.2f}", f"{avg_win:.2f}", f"{avg_loss:.2f}",
                f"{avg_days:.0f}", best['Return_%'], worst['Return_%'],
                f"Rs{INVESTMENT_PER_STOCK:,}", MAX_PORTFOLIO_SIZE
            ]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"\nExcel saved: {excel_file}")
    print(f"Location: {Path(excel_file).absolute()}")
    
    # Open the file
    import subprocess
    subprocess.Popen(['start', excel_file], shell=True)
    
    print("\n" + "=" * 80)
    print(" COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()

