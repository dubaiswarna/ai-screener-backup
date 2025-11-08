"""
Advanced Portfolio Tracker for AI Screener
==========================================
Track your trades, analyze performance, and optimize your strategy

Features:
- Real-time P&L tracking
- Win/loss statistics
- Trade journal integration
- Performance analytics
- Risk metrics
- Comparison with backtest results
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os


class PortfolioTracker:
    """
    Track and analyze your trading portfolio performance.
    """
    
    def __init__(self, portfolio_file='portfolio_trades.json'):
        """
        Initialize portfolio tracker.
        
        Args:
            portfolio_file: JSON file to store trade history
        """
        self.portfolio_file = portfolio_file
        self.trades = self._load_trades()
        self.open_positions = {}
        
    def _load_trades(self) -> List[Dict]:
        """Load trade history from file."""
        if os.path.exists(self.portfolio_file):
            with open(self.portfolio_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_trades(self):
        """Save trade history to file."""
        with open(self.portfolio_file, 'w') as f:
            json.dump(self.trades, f, indent=2, default=str)
    
    def add_trade(self, 
                  symbol: str,
                  signal: str,
                  entry_price: float,
                  entry_date: str,
                  target_price: float,
                  stop_loss: float,
                  quantity: int,
                  confidence: float,
                  notes: str = ""):
        """
        Add a new trade to the portfolio.
        
        Args:
            symbol: Stock symbol
            signal: buy/sell/short
            entry_price: Entry price
            entry_date: Entry date (YYYY-MM-DD)
            target_price: Target price
            stop_loss: Stop loss price
            quantity: Number of shares
            confidence: AI confidence (0-1)
            notes: Optional notes
        """
        trade_id = f"{symbol}_{entry_date}_{datetime.now().strftime('%H%M%S')}"
        
        trade = {
            'trade_id': trade_id,
            'symbol': symbol,
            'signal': signal,
            'entry_price': entry_price,
            'entry_date': entry_date,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'quantity': quantity,
            'confidence': confidence,
            'status': 'OPEN',
            'exit_price': None,
            'exit_date': None,
            'pnl': 0,
            'pnl_percent': 0,
            'days_held': 0,
            'notes': notes,
            'created_at': datetime.now().isoformat()
        }
        
        self.trades.append(trade)
        self.open_positions[trade_id] = trade
        self._save_trades()
        
        return trade_id
    
    def close_trade(self,
                   trade_id: str,
                   exit_price: float,
                   exit_date: str,
                   outcome: str = 'TARGET'):
        """
        Close an existing trade.
        
        Args:
            trade_id: Trade ID to close
            exit_price: Exit price
            exit_date: Exit date (YYYY-MM-DD)
            outcome: TARGET/STOP/MANUAL
        """
        # Find trade
        trade = None
        for t in self.trades:
            if t['trade_id'] == trade_id:
                trade = t
                break
        
        if not trade:
            raise ValueError(f"Trade {trade_id} not found")
        
        if trade['status'] != 'OPEN':
            raise ValueError(f"Trade {trade_id} is already closed")
        
        # Calculate P&L
        quantity = trade['quantity']
        entry_price = trade['entry_price']
        
        if trade['signal'].lower() in ['buy', 'long']:
            pnl = (exit_price - entry_price) * quantity
        else:  # short/sell
            pnl = (entry_price - exit_price) * quantity
        
        pnl_percent = ((exit_price - entry_price) / entry_price) * 100
        if trade['signal'].lower() not in ['buy', 'long']:
            pnl_percent = -pnl_percent
        
        # Calculate days held
        entry_dt = datetime.strptime(entry_date, '%Y-%m-%d')
        exit_dt = datetime.strptime(exit_date, '%Y-%m-%d')
        days_held = (exit_dt - entry_dt).days
        
        # Update trade
        trade['status'] = 'CLOSED'
        trade['exit_price'] = exit_price
        trade['exit_date'] = exit_date
        trade['pnl'] = round(pnl, 2)
        trade['pnl_percent'] = round(pnl_percent, 2)
        trade['days_held'] = days_held
        trade['outcome'] = outcome
        trade['closed_at'] = datetime.now().isoformat()
        
        # Remove from open positions
        if trade_id in self.open_positions:
            del self.open_positions[trade_id]
        
        self._save_trades()
        
        return trade
    
    def get_open_positions(self) -> pd.DataFrame:
        """Get all open positions as DataFrame."""
        open_trades = [t for t in self.trades if t['status'] == 'OPEN']
        if not open_trades:
            return pd.DataFrame()
        return pd.DataFrame(open_trades)
    
    def get_closed_trades(self) -> pd.DataFrame:
        """Get all closed trades as DataFrame."""
        closed_trades = [t for t in self.trades if t['status'] == 'CLOSED']
        if not closed_trades:
            return pd.DataFrame()
        return pd.DataFrame(closed_trades)
    
    def get_performance_summary(self) -> Dict:
        """
        Get comprehensive performance summary.
        
        Returns:
            Dictionary with performance metrics
        """
        closed_df = self.get_closed_trades()
        
        if closed_df.empty:
            return {
                'total_trades': 0,
                'message': 'No closed trades yet'
            }
        
        # Basic metrics
        total_trades = len(closed_df)
        winning_trades = len(closed_df[closed_df['pnl'] > 0])
        losing_trades = len(closed_df[closed_df['pnl'] <= 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # P&L metrics
        total_pnl = closed_df['pnl'].sum()
        avg_win = closed_df[closed_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = closed_df[closed_df['pnl'] <= 0]['pnl'].mean() if losing_trades > 0 else 0
        profit_factor = abs(closed_df[closed_df['pnl'] > 0]['pnl'].sum() / 
                           closed_df[closed_df['pnl'] <= 0]['pnl'].sum()) if losing_trades > 0 else float('inf')
        
        # Return metrics
        avg_return = closed_df['pnl_percent'].mean()
        best_trade = closed_df.loc[closed_df['pnl'].idxmax()]
        worst_trade = closed_df.loc[closed_df['pnl'].idxmin()]
        
        # Time metrics
        avg_holding_days = closed_df['days_held'].mean()
        
        # Confidence analysis
        avg_confidence = closed_df['confidence'].mean() * 100
        high_conf_trades = closed_df[closed_df['confidence'] >= 0.75]
        high_conf_win_rate = (len(high_conf_trades[high_conf_trades['pnl'] > 0]) / 
                              len(high_conf_trades) * 100) if len(high_conf_trades) > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'avg_return_percent': round(avg_return, 2),
            'best_trade': {
                'symbol': best_trade['symbol'],
                'pnl': round(best_trade['pnl'], 2),
                'return': round(best_trade['pnl_percent'], 2)
            },
            'worst_trade': {
                'symbol': worst_trade['symbol'],
                'pnl': round(worst_trade['pnl'], 2),
                'return': round(worst_trade['pnl_percent'], 2)
            },
            'avg_holding_days': round(avg_holding_days, 1),
            'avg_confidence': round(avg_confidence, 1),
            'high_conf_win_rate': round(high_conf_win_rate, 2)
        }
    
    def get_stock_performance(self, symbol: str) -> Dict:
        """Get performance for specific stock."""
        closed_df = self.get_closed_trades()
        stock_trades = closed_df[closed_df['symbol'] == symbol]
        
        if stock_trades.empty:
            return {'symbol': symbol, 'trades': 0}
        
        winning = len(stock_trades[stock_trades['pnl'] > 0])
        total = len(stock_trades)
        
        return {
            'symbol': symbol,
            'trades': total,
            'win_rate': round(winning/total*100, 2),
            'total_pnl': round(stock_trades['pnl'].sum(), 2),
            'avg_return': round(stock_trades['pnl_percent'].mean(), 2)
        }
    
    def compare_with_backtest(self, backtest_win_rate: float = 86.9) -> Dict:
        """
        Compare live performance with backtest results.
        
        Args:
            backtest_win_rate: Expected win rate from backtest (default 86.9%)
        
        Returns:
            Comparison metrics
        """
        summary = self.get_performance_summary()
        
        if summary.get('total_trades', 0) == 0:
            return {'message': 'No trades to compare yet'}
        
        live_win_rate = summary['win_rate']
        difference = live_win_rate - backtest_win_rate
        
        return {
            'backtest_win_rate': backtest_win_rate,
            'live_win_rate': live_win_rate,
            'difference': round(difference, 2),
            'performance': 'OUTPERFORMING' if difference > 0 else 'UNDERPERFORMING' if difference < -5 else 'ON_TRACK',
            'total_trades': summary['total_trades'],
            'confidence_level': 'HIGH' if summary['total_trades'] >= 30 else 'MEDIUM' if summary['total_trades'] >= 10 else 'LOW'
        }
    
    def generate_trade_journal(self, output_file='trade_journal.xlsx'):
        """
        Generate comprehensive Excel trade journal.
        
        Args:
            output_file: Output Excel file name
        """
        if not self.trades:
            print("No trades to export")
            return
        
        df = pd.DataFrame(self.trades)
        
        # Create Excel writer
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # All trades
            df.to_excel(writer, sheet_name='All Trades', index=False)
            
            # Open positions
            open_df = df[df['status'] == 'OPEN']
            if not open_df.empty:
                open_df.to_excel(writer, sheet_name='Open Positions', index=False)
            
            # Closed trades
            closed_df = df[df['status'] == 'CLOSED']
            if not closed_df.empty:
                closed_df.to_excel(writer, sheet_name='Closed Trades', index=False)
            
            # Performance summary
            summary = self.get_performance_summary()
            summary_df = pd.DataFrame([summary])
            summary_df.to_excel(writer, sheet_name='Performance Summary', index=False)
            
            # By stock
            if not closed_df.empty:
                stock_performance = []
                for symbol in closed_df['symbol'].unique():
                    stock_performance.append(self.get_stock_performance(symbol))
                stock_df = pd.DataFrame(stock_performance).sort_values('total_pnl', ascending=False)
                stock_df.to_excel(writer, sheet_name='By Stock', index=False)
        
        print(f"✅ Trade journal saved to: {output_file}")
        return output_file
    
    def print_dashboard(self):
        """Print a beautiful dashboard to console."""
        print("\n" + "="*80)
        print("📊 PORTFOLIO PERFORMANCE DASHBOARD")
        print("="*80)
        
        # Open positions
        open_df = self.get_open_positions()
        print(f"\n🔄 OPEN POSITIONS: {len(open_df)}")
        if not open_df.empty:
            print("-"*80)
            for _, pos in open_df.iterrows():
                print(f"   {pos['symbol']:20s} | {pos['signal']:4s} | "
                      f"Entry: ₹{pos['entry_price']:8.2f} | "
                      f"Target: ₹{pos['target_price']:8.2f} | "
                      f"Conf: {pos['confidence']*100:5.1f}%")
        
        # Performance summary
        summary = self.get_performance_summary()
        if summary.get('total_trades', 0) > 0:
            print(f"\n📈 PERFORMANCE SUMMARY")
            print("-"*80)
            print(f"   Total Trades: {summary['total_trades']}")
            print(f"   Win Rate: {summary['win_rate']}% (Target: 86.9%)")
            print(f"   Total P&L: ₹{summary['total_pnl']:,.2f}")
            print(f"   Avg Return: {summary['avg_return_percent']}%")
            print(f"   Profit Factor: {summary['profit_factor']}")
            print(f"   Avg Holding: {summary['avg_holding_days']} days")
            
            print(f"\n🏆 BEST TRADE: {summary['best_trade']['symbol']} "
                  f"(+₹{summary['best_trade']['pnl']:,.2f}, "
                  f"+{summary['best_trade']['return']}%)")
            
            print(f"📉 WORST TRADE: {summary['worst_trade']['symbol']} "
                  f"(₹{summary['worst_trade']['pnl']:,.2f}, "
                  f"{summary['worst_trade']['return']}%)")
            
            # Backtest comparison
            comparison = self.compare_with_backtest()
            if 'performance' in comparison:
                print(f"\n🎯 VS BACKTEST: {comparison['performance']}")
                print(f"   Live: {comparison['live_win_rate']}% | "
                      f"Backtest: {comparison['backtest_win_rate']}% | "
                      f"Diff: {comparison['difference']:+.2f}%")
        else:
            print("\n💡 No closed trades yet. Start trading to see performance!")
        
        print("\n" + "="*80)


if __name__ == '__main__':
    # Demo
    print("📊 AI Screener Portfolio Tracker")
    print("="*60)
    
    tracker = PortfolioTracker()
    tracker.print_dashboard()
    
    print("\n✅ Portfolio tracker ready!")
    print("💡 Use tracker.add_trade() to log your trades")
    print("="*60)

