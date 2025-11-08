"""
3-Year Backtest - Top 5 Stocks with Portfolio Management
=========================================================
Realistic backtest with entry/exit dates, P&L tracking, and portfolio limits
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

# Top 5 most liquid stocks for reliable backtesting
TOP_5_STOCKS = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']

INVESTMENT_PER_STOCK = 200000  # 2 Lakh per stock
MAX_PORTFOLIO_SIZE = 20  # Maximum 20 stocks at a time
TARGET_RETURN = 0.10  # 10% target
STOP_LOSS = 0.07  # 7% stop loss
HOLDING_PERIOD = 60  # Maximum 60 days holding


class PortfolioBacktest:
    """Portfolio-based backtesting with realistic constraints."""
    
    def __init__(self):
        self.portfolio = []  # Current holdings
        self.trades = []  # Completed trades
        self.daily_portfolio_value = []
        
    def can_enter_trade(self):
        """Check if we can enter a new trade."""
        return len(self.portfolio) < MAX_PORTFOLIO_SIZE
    
    def enter_trade(self, symbol, entry_date, entry_price, confidence):
        """Enter a new position."""
        quantity = int(INVESTMENT_PER_STOCK / entry_price)
        investment = quantity * entry_price
        
        position = {
            'symbol': symbol,
            'entry_date': entry_date,
            'entry_price': entry_price,
            'quantity': quantity,
            'investment': investment,
            'confidence': confidence,
            'target_price': entry_price * (1 + TARGET_RETURN),
            'stop_price': entry_price * (1 - STOP_LOSS),
            'max_holding_date': entry_date + timedelta(days=HOLDING_PERIOD)
        }
        
        self.portfolio.append(position)
        return position
    
    def check_exit_conditions(self, position, current_date, current_price):
        """Check if position should be exited."""
        
        # Target hit
        if current_price >= position['target_price']:
            return 'TARGET', current_price
        
        # Stop loss hit
        if current_price <= position['stop_price']:
            return 'STOP_LOSS', current_price
        
        # Maximum holding period
        if current_date >= position['max_holding_date']:
            return 'TIME_EXIT', current_price
        
        return None, None
    
    def exit_trade(self, position, exit_date, exit_price, exit_reason):
        """Exit a position and record the trade."""
        
        exit_value = position['quantity'] * exit_price
        pnl = exit_value - position['investment']
        pnl_pct = (pnl / position['investment']) * 100
        holding_days = (exit_date - position['entry_date']).days
        
        trade = {
            'Symbol': position['symbol'],
            'Entry_Date': position['entry_date'].strftime('%Y-%m-%d'),
            'Entry_Price': f"Rs{position['entry_price']:.2f}",
            'Exit_Date': exit_date.strftime('%Y-%m-%d'),
            'Exit_Price': f"Rs{exit_price:.2f}",
            'Exit_Reason': exit_reason,
            'Investment': f"Rs{position['investment']:.2f}",
            'Exit_Value': f"Rs{exit_value:.2f}",
            'PnL': f"Rs{pnl:.2f}",
            'Return_%': f"{pnl_pct:.2f}%",
            'Holding_Days': holding_days,
            'Confidence': f"{position['confidence']:.1f}%"
        }
        
        self.trades.append(trade)
        return trade


def load_model_and_features(symbol):
    """Load trained model for a stock."""
    model_path = Path(f"../Nifty200_Models_Pro/ensemble_{symbol}.pkl")
    
    if not model_path.exists():
        return None
    
    try:
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    except:
        return None


def calculate_features(df):
    """Calculate features from OHLCV data."""
    features = {}
    
    # Price features
    features['close'] = df['Close'].iloc[-1]
    features['volume'] = df['Volume'].iloc[-1]
    
    # Moving averages
    for period in [5, 10, 20, 50, 100, 200]:
        if len(df) >= period:
            features[f'sma_{period}'] = df['Close'].rolling(period).mean().iloc[-1]
            features[f'ema_{period}'] = df['Close'].ewm(span=period).mean().iloc[-1]
        else:
            features[f'sma_{period}'] = df['Close'].mean()
            features[f'ema_{period}'] = df['Close'].mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    features['rsi'] = (100 - (100 / (1 + rs))).iloc[-1]
    
    # MACD
    ema12 = df['Close'].ewm(span=12).mean()
    ema26 = df['Close'].ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    features['macd'] = macd.iloc[-1]
    features['macd_signal'] = signal.iloc[-1]
    features['macd_hist'] = (macd - signal).iloc[-1]
    
    # Bollinger Bands
    sma20 = df['Close'].rolling(20).mean()
    std20 = df['Close'].rolling(20).std()
    features['bb_upper'] = (sma20 + 2 * std20).iloc[-1]
    features['bb_lower'] = (sma20 - 2 * std20).iloc[-1]
    
    # ATR
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    features['atr'] = true_range.rolling(14).mean().iloc[-1]
    
    # Volume
    features['volume_sma'] = df['Volume'].rolling(20).mean().iloc[-1]
    features['volume_ratio'] = features['volume'] / features['volume_sma'] if features['volume_sma'] > 0 else 1
    
    # Momentum
    features['momentum_5'] = df['Close'].pct_change(5).iloc[-1] * 100
    features['momentum_10'] = df['Close'].pct_change(10).iloc[-1] * 100
    features['momentum_20'] = df['Close'].pct_change(20).iloc[-1] * 100
    
    # Price position
    if len(df) >= 252:
        features['price_to_52w_high'] = (df['Close'].iloc[-1] / df['High'].rolling(252).max().iloc[-1]) * 100
        features['price_to_52w_low'] = (df['Close'].iloc[-1] / df['Low'].rolling(252).min().iloc[-1]) * 100
    else:
        features['price_to_52w_high'] = 100
        features['price_to_52w_low'] = 100
    
    # Pad to 89 features
    for i in range(len(features), 89):
        features[f'feature_{i}'] = 0
    
    return features


def run_3year_backtest():
    """Run 3-year backtest on top 5 stocks."""
    
    print("=" * 80)
    print(" 3-YEAR BACKTEST - TOP 5 STOCKS")
    print("=" * 80)
    print(f"\nStocks: {', '.join(TOP_5_STOCKS)}")
    print(f"Investment per stock: Rs{INVESTMENT_PER_STOCK:,}")
    print(f"Max portfolio size: {MAX_PORTFOLIO_SIZE} stocks")
    print(f"Target: +{TARGET_RETURN*100}% | Stop: -{STOP_LOSS*100}%")
    print(f"Max holding: {HOLDING_PERIOD} days")
    
    # Date range: Last 3 years
    end_date = pd.Timestamp("2025-02-28", tz='Asia/Kolkata')  # Feb 2025
    start_date = pd.Timestamp("2022-03-01", tz='Asia/Kolkata')  # March 2022 (3 years back)
    
    print(f"\nBacktest period: {start_date.strftime('%B %Y')} to {end_date.strftime('%B %Y')}")
    print(f"Duration: 3 years")
    
    # Initialize portfolio
    backtest = PortfolioBacktest()
    
    # Load data for all stocks
    print("\nLoading data...")
    stock_data = {}
    models = {}
    
    for symbol in TOP_5_STOCKS:
        data_file = Path(f"../Nifty200_Data/NSE_{symbol}_1D.csv")
        if not data_file.exists():
            print(f"  ERROR: Data not found for {symbol}")
            continue
        
        df = pd.read_csv(data_file, parse_dates=['time'])
        df = df.rename(columns={'time': 'Date', 'open': 'Open', 'high': 'High', 
                                'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
        df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        
        if len(df) < 200:
            print(f"  SKIP: {symbol} - Not enough data ({len(df)} days)")
            continue
        
        stock_data[symbol] = df
        models[symbol] = load_model_and_features(symbol)
        
        if models[symbol]:
            print(f"  Loaded: {symbol} - {len(df)} days of data")
        else:
            print(f"  SKIP: {symbol} - Model not found")
    
    print(f"\nReady to backtest: {len(stock_data)} stocks")
    
    # Simulate trading day by day
    print("\nRunning backtest...")
    all_dates = sorted(set([date for df in stock_data.values() for date in df['Date']]))
    
    signal_count = 0
    
    for current_date in all_dates:
        # Check exits for current portfolio
        positions_to_exit = []
        
        for position in backtest.portfolio:
            symbol = position['symbol']
            if symbol not in stock_data:
                continue
            
            df = stock_data[symbol]
            day_data = df[df['Date'] == current_date]
            
            if day_data.empty:
                continue
            
            current_price = day_data['Close'].iloc[0]
            exit_reason, exit_price = backtest.check_exit_conditions(position, current_date, current_price)
            
            if exit_reason:
                positions_to_exit.append((position, current_date, exit_price, exit_reason))
        
        # Exit positions
        for position, exit_date, exit_price, exit_reason in positions_to_exit:
            backtest.exit_trade(position, exit_date, exit_price, exit_reason)
            backtest.portfolio.remove(position)
        
        # Look for new entries (daily scanning for more opportunities)
        if backtest.can_enter_trade():
            for symbol in stock_data.keys():
                if not backtest.can_enter_trade():
                    break
                
                # Check if already in portfolio
                if any(p['symbol'] == symbol for p in backtest.portfolio):
                    continue
                
                df = stock_data[symbol]
                historical = df[df['Date'] <= current_date]
                
                if len(historical) < 200:
                    continue
                
                # Calculate features
                try:
                    features = calculate_features(historical.tail(500))
                    model_data = models[symbol]
                    
                    if not model_data:
                        continue
                    
                    feature_cols = model_data.get('feature_cols', [])
                    if not feature_cols:
                        continue
                    
                    # Prepare feature vector
                    feature_values = [features.get(col, 0) for col in feature_cols]
                    feature_vector = np.array([feature_values])
                    
                    # Predict
                    xgb_model = model_data.get('xgb_model')
                    lgb_model = model_data.get('lgb_model')
                    
                    if not xgb_model or not lgb_model:
                        continue
                    
                    xgb_pred = xgb_model.predict_proba(feature_vector)[0]
                    lgb_pred = lgb_model.predict_proba(feature_vector)[0]
                    
                    avg_proba = (xgb_pred + lgb_pred) / 2
                    prediction = np.argmax(avg_proba)
                    confidence = avg_proba[prediction] * 100
                    
                    # Signal mapping: 0=SELL, 1=HOLD, 2=BUY
                    if prediction == 2 and confidence >= 60:  # BUY with 60%+ confidence (lowered for more signals)
                        entry_price = historical['Close'].iloc[-1]
                        backtest.enter_trade(symbol, current_date, entry_price, confidence)
                        signal_count += 1
                
                except Exception as e:
                    continue
    
    # Close all remaining positions at end date
    for position in backtest.portfolio[:]:
        symbol = position['symbol']
        df = stock_data[symbol]
        final_price = df['Close'].iloc[-1]
        backtest.exit_trade(position, end_date, final_price, 'BACKTEST_END')
        backtest.portfolio.remove(position)
    
    print(f"\nBacktest complete!")
    print(f"Total signals generated: {signal_count}")
    print(f"Total trades executed: {len(backtest.trades)}")
    
    return backtest.trades


def main():
    """Main backtest execution."""
    
    trades = run_3year_backtest()
    
    if not trades:
        print("\n[WARNING] No trades were executed!")
        print("Possible reasons:")
        print("  - Models not generating BUY signals with 70%+ confidence")
        print("  - Market conditions were bearish during test period")
        return
    
    # Convert to DataFrame
    df_trades = pd.DataFrame(trades)
    
    # Calculate statistics
    print("\n" + "=" * 80)
    print(" BACKTEST RESULTS SUMMARY")
    print("=" * 80)
    
    total_trades = len(df_trades)
    
    # Extract numeric values for calculations
    df_trades['PnL_Numeric'] = df_trades['PnL'].str.replace('Rs', '').astype(float)
    df_trades['Return_Numeric'] = df_trades['Return_%'].str.rstrip('%').astype(float)
    
    winning_trades = len(df_trades[df_trades['PnL_Numeric'] > 0])
    losing_trades = len(df_trades[df_trades['PnL_Numeric'] < 0])
    breakeven_trades = len(df_trades[df_trades['PnL_Numeric'] == 0])
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    total_pnl = df_trades['PnL_Numeric'].sum()
    avg_return = df_trades['Return_Numeric'].mean()
    best_trade = df_trades.loc[df_trades['PnL_Numeric'].idxmax()]
    worst_trade = df_trades.loc[df_trades['PnL_Numeric'].idxmin()]
    avg_holding = df_trades['Holding_Days'].mean()
    
    print(f"\nTotal Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades} ({win_rate:.1f}%)")
    print(f"Losing Trades: {losing_trades}")
    print(f"Breakeven Trades: {breakeven_trades}")
    
    print(f"\nTotal P&L: Rs{total_pnl:,.2f}")
    print(f"Average Return: {avg_return:.2f}%")
    print(f"Average Holding Period: {avg_holding:.0f} days")
    
    print(f"\nBest Trade:")
    print(f"  {best_trade['Symbol']} - {best_trade['Return_%']} ({best_trade['PnL']})")
    
    print(f"\nWorst Trade:")
    print(f"  {worst_trade['Symbol']} - {worst_trade['Return_%']} ({worst_trade['PnL']})")
    
    # Save to Excel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_file = f"backtest_3years_{timestamp}.xlsx"
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # All trades
        df_trades_export = df_trades.drop(['PnL_Numeric', 'Return_Numeric'], axis=1)
        df_trades_export.to_excel(writer, sheet_name='All Trades', index=False)
        
        # Winning trades
        df_wins = df_trades_export[df_trades['PnL_Numeric'] > 0]
        if len(df_wins) > 0:
            df_wins.to_excel(writer, sheet_name='Winning Trades', index=False)
        
        # Losing trades
        df_losses = df_trades_export[df_trades['PnL_Numeric'] < 0]
        if len(df_losses) > 0:
            df_losses.to_excel(writer, sheet_name='Losing Trades', index=False)
        
        # Summary
        summary = pd.DataFrame({
            'Metric': [
                'Total Trades',
                'Winning Trades',
                'Losing Trades',
                'Win Rate (%)',
                'Total P&L (Rs)',
                'Average Return (%)',
                'Average Holding (days)',
                'Best Trade (%)',
                'Worst Trade (%)',
                'Investment per Trade (Rs)',
                'Max Portfolio Size'
            ],
            'Value': [
                total_trades,
                winning_trades,
                losing_trades,
                f"{win_rate:.2f}",
                f"{total_pnl:,.2f}",
                f"{avg_return:.2f}",
                f"{avg_holding:.0f}",
                best_trade['Return_%'],
                worst_trade['Return_%'],
                f"{INVESTMENT_PER_STOCK:,}",
                MAX_PORTFOLIO_SIZE
            ]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"\nResults saved to: {excel_file}")
    print(f"Location: {Path(excel_file).absolute()}")
    
    print("\n" + "=" * 80)
    print(" BACKTEST COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()

