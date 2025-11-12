# -*- coding: utf-8 -*-
"""
S&R Strategy Backtesting Engine
================================

Test Support & Resistance trading strategies on historical data

Strategies:
1. Bounce Trading: Buy at support bounce, sell at resistance rejection
2. Breakout Trading: Buy above resistance, sell below support
3. Combined: Use both strategies

Metrics:
- Total Trades
- Win Rate
- Average Profit/Loss
- Max Drawdown
- Sharpe Ratio
- Total Return
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime


class SRBacktestEngine:
    """
    Backtest Support & Resistance trading strategies
    """
    
    def __init__(self, initial_capital: float = 100000,
                 commission_pct: float = 0.1,
                 slippage_pct: float = 0.05):
        """
        Args:
            initial_capital: Starting capital (default: 1,00,000)
            commission_pct: Commission per trade in % (default: 0.1%)
            slippage_pct: Slippage in % (default: 0.05%)
        """
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct / 100
        self.slippage_pct = slippage_pct / 100
        
    def backtest_bounce_strategy(self, 
                                 df: pd.DataFrame,
                                 sr_data: Dict,
                                 stop_loss_pct: float = 2.0,
                                 target_pct: float = 5.0,
                                 tolerance_pct: float = 1.0) -> Dict:
        """
        Backtest: Buy at support bounce, Sell at resistance rejection
        
        Rules:
        1. BUY when price touches support (+/- tolerance) and bounces
        2. SELL at target or stop loss
        3. SHORT when price touches resistance and rejects
        4. COVER at target or stop loss
        
        Args:
            df: Price DataFrame
            sr_data: S&R levels
            stop_loss_pct: Stop loss % (default: 2%)
            target_pct: Profit target % (default: 5%)
            tolerance_pct: Price tolerance for touching level (default: 1%)
        
        Returns:
            Dict with backtest results
        """
        if df is None or len(df) < 20:
            return {'error': 'Insufficient data'}
        
        capital = self.initial_capital
        position = None  # 'LONG' or 'SHORT'
        entry_price = 0
        entry_date = None
        stop_loss = 0
        target = 0
        
        trades = []
        equity_curve = []
        
        supports = [s['level'] for s in sr_data.get('supports', [])]
        resistances = [r['level'] for r in sr_data.get('resistances', [])]
        
        for i in range(1, len(df)):
            current_date = df.index[i] if 'time' not in df.columns else df['time'].iloc[i]
            current_price = df['close'].iloc[i]
            prev_price = df['close'].iloc[i-1]
            high = df['high'].iloc[i]
            low = df['low'].iloc[i]
            
            # ===============================================================
            # CLOSE EXISTING POSITION
            # ===============================================================
            if position == 'LONG':
                # Check stop loss
                if low <= stop_loss:
                    exit_price = stop_loss * (1 - self.slippage_pct)
                    pnl = (exit_price - entry_price) / entry_price * 100
                    commission = exit_price * self.commission_pct * 2  # Entry + Exit
                    capital_change = capital * (pnl / 100) - commission
                    capital += capital_change
                    
                    trades.append({
                        'entry_date': entry_date,
                        'exit_date': current_date,
                        'type': 'LONG',
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'pnl_pct': round(pnl, 2),
                        'capital': round(capital, 2),
                        'exit_reason': 'Stop Loss'
                    })
                    position = None
                
                # Check target
                elif high >= target:
                    exit_price = target * (1 - self.slippage_pct)
                    pnl = (exit_price - entry_price) / entry_price * 100
                    commission = exit_price * self.commission_pct * 2
                    capital_change = capital * (pnl / 100) - commission
                    capital += capital_change
                    
                    trades.append({
                        'entry_date': entry_date,
                        'exit_date': current_date,
                        'type': 'LONG',
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'pnl_pct': round(pnl, 2),
                        'capital': round(capital, 2),
                        'exit_reason': 'Target'
                    })
                    position = None
            
            elif position == 'SHORT':
                # Check stop loss (price goes up)
                if high >= stop_loss:
                    exit_price = stop_loss * (1 + self.slippage_pct)
                    pnl = (entry_price - exit_price) / entry_price * 100
                    commission = exit_price * self.commission_pct * 2
                    capital_change = capital * (pnl / 100) - commission
                    capital += capital_change
                    
                    trades.append({
                        'entry_date': entry_date,
                        'exit_date': current_date,
                        'type': 'SHORT',
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'pnl_pct': round(pnl, 2),
                        'capital': round(capital, 2),
                        'exit_reason': 'Stop Loss'
                    })
                    position = None
                
                # Check target (price goes down)
                elif low <= target:
                    exit_price = target * (1 + self.slippage_pct)
                    pnl = (entry_price - exit_price) / entry_price * 100
                    commission = exit_price * self.commission_pct * 2
                    capital_change = capital * (pnl / 100) - commission
                    capital += capital_change
                    
                    trades.append({
                        'entry_date': entry_date,
                        'exit_date': current_date,
                        'type': 'SHORT',
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'pnl_pct': round(pnl, 2),
                        'capital': round(capital, 2),
                        'exit_reason': 'Target'
                    })
                    position = None
            
            # ===============================================================
            # OPEN NEW POSITION
            # ===============================================================
            if position is None:
                # Check for LONG entry (bounce at support)
                for support_level in supports:
                    tolerance = support_level * (tolerance_pct / 100)
                    
                    # Price touched support
                    if (low <= support_level + tolerance and 
                        low >= support_level - tolerance):
                        
                        # Bounced (close higher than open)
                        if current_price > df['open'].iloc[i]:
                            position = 'LONG'
                            entry_price = current_price * (1 + self.slippage_pct)
                            entry_date = current_date
                            stop_loss = entry_price * (1 - stop_loss_pct / 100)
                            target = entry_price * (1 + target_pct / 100)
                            break
                
                # Check for SHORT entry (rejection at resistance)
                if position is None:
                    for resistance_level in resistances:
                        tolerance = resistance_level * (tolerance_pct / 100)
                        
                        # Price touched resistance
                        if (high >= resistance_level - tolerance and 
                            high <= resistance_level + tolerance):
                            
                            # Rejected (close lower than open)
                            if current_price < df['open'].iloc[i]:
                                position = 'SHORT'
                                entry_price = current_price * (1 - self.slippage_pct)
                                entry_date = current_date
                                stop_loss = entry_price * (1 + stop_loss_pct / 100)
                                target = entry_price * (1 - target_pct / 100)
                                break
            
            # Track equity curve
            equity_curve.append({
                'date': current_date,
                'capital': round(capital, 2)
            })
        
        # ===============================================================
        # CALCULATE METRICS
        # ===============================================================
        if not trades:
            return {
                'error': 'No trades executed',
                'initial_capital': self.initial_capital,
                'final_capital': capital
            }
        
        total_trades = len(trades)
        winning_trades = [t for t in trades if t['pnl_pct'] > 0]
        losing_trades = [t for t in trades if t['pnl_pct'] <= 0]
        
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        avg_win = np.mean([t['pnl_pct'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl_pct'] for t in losing_trades]) if losing_trades else 0
        
        total_return = ((capital - self.initial_capital) / self.initial_capital * 100)
        
        # Max Drawdown
        equity_values = [e['capital'] for e in equity_curve]
        peak = equity_values[0]
        max_dd = 0
        for value in equity_values:
            if value > peak:
                peak = value
            dd = ((peak - value) / peak * 100)
            if dd > max_dd:
                max_dd = dd
        
        # Sharpe Ratio (simplified)
        returns = [t['pnl_pct'] for t in trades]
        if len(returns) > 1:
            sharpe = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        else:
            sharpe = 0
        
        return {
            'strategy': 'Bounce Trading (Support/Resistance)',
            'initial_capital': self.initial_capital,
            'final_capital': round(capital, 2),
            'total_return_pct': round(total_return, 2),
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate_pct': round(win_rate, 1),
            'avg_win_pct': round(avg_win, 2),
            'avg_loss_pct': round(avg_loss, 2),
            'max_drawdown_pct': round(max_dd, 2),
            'sharpe_ratio': round(sharpe, 2),
            'trades': trades,
            'equity_curve': equity_curve
        }
    
    def backtest_breakout_strategy(self,
                                   df: pd.DataFrame,
                                   sr_data: Dict,
                                   stop_loss_pct: float = 3.0,
                                   target_pct: float = 10.0,
                                   confirmation_candles: int = 1) -> Dict:
        """
        Backtest: Buy on resistance breakout, Sell on support breakdown
        
        Rules:
        1. BUY when price breaks ABOVE resistance with volume confirmation
        2. SELL at target or stop loss
        3. SHORT when price breaks BELOW support
        4. COVER at target or stop loss
        
        Args:
            df: Price DataFrame
            sr_data: S&R levels
            stop_loss_pct: Stop loss % (default: 3%)
            target_pct: Profit target % (default: 10%)
            confirmation_candles: Candles to confirm breakout (default: 1)
        
        Returns:
            Dict with backtest results
        """
        # Implementation similar to bounce strategy
        # ... (code continues)
        return {
            'strategy': 'Breakout Trading',
            'message': 'Breakout strategy implementation in progress'
        }
    
    def generate_backtest_report(self, results: Dict) -> str:
        """
        Generate formatted backtest report
        
        Args:
            results: Backtest results dict
        
        Returns:
            Formatted string report
        """
        if results.get('error'):
            return f"❌ Error: {results['error']}"
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           S&R STRATEGY BACKTEST REPORT                       ║
╚══════════════════════════════════════════════════════════════╝

Strategy: {results['strategy']}

📊 PERFORMANCE METRICS
═══════════════════════════════════════════════════════════════
Initial Capital:     ₹{results['initial_capital']:,}
Final Capital:       ₹{results['final_capital']:,}
Total Return:        {results['total_return_pct']:+.2f}%

🎯 TRADE STATISTICS
═══════════════════════════════════════════════════════════════
Total Trades:        {results['total_trades']}
Winning Trades:      {results['winning_trades']} ({results['win_rate_pct']:.1f}%)
Losing Trades:       {results['losing_trades']} ({100-results['win_rate_pct']:.1f}%)

💰 PROFIT/LOSS
═══════════════════════════════════════════════════════════════
Average Win:         +{results['avg_win_pct']:.2f}%
Average Loss:        {results['avg_loss_pct']:.2f}%
Max Drawdown:        -{results['max_drawdown_pct']:.2f}%

📈 RISK-ADJUSTED RETURNS
═══════════════════════════════════════════════════════════════
Sharpe Ratio:        {results['sharpe_ratio']:.2f}

✅ VERDICT
═══════════════════════════════════════════════════════════════
"""
        
        # Add verdict based on performance
        if results['total_return_pct'] > 20 and results['win_rate_pct'] > 60:
            report += "🎉 EXCELLENT STRATEGY! High returns with good win rate.\n"
        elif results['total_return_pct'] > 10 and results['win_rate_pct'] > 50:
            report += "✅ PROFITABLE STRATEGY! Consider using with proper risk management.\n"
        elif results['total_return_pct'] > 0:
            report += "⚠️  MARGINALLY PROFITABLE. Optimize parameters or combine with other indicators.\n"
        else:
            report += "❌ LOSING STRATEGY. Do NOT use in live trading. Revise approach.\n"
        
        report += "═══════════════════════════════════════════════════════════════\n"
        
        return report


# Export
__all__ = ['SRBacktestEngine']

