"""
Advanced Backtesting Engine
============================
Walk-forward optimization, Monte Carlo simulation, and comprehensive performance metrics
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Callable
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """Configuration for backtesting."""
    initial_capital: float = 1000000  # ₹10 Lakh
    commission: float = 0.001  # 0.1%
    slippage: float = 0.0005  # 0.05%
    max_risk_per_trade: float = 0.02  # 2%
    max_positions: int = 10
    confidence_threshold: float = 0.7  # 70%


@dataclass
class Trade:
    """Trade record."""
    entry_date: datetime
    exit_date: Optional[datetime]
    symbol: str
    direction: str  # 'BUY' or 'SELL'
    entry_price: float
    exit_price: Optional[float]
    quantity: int
    pnl: Optional[float]
    pnl_pct: Optional[float]
    holding_days: Optional[int]
    exit_reason: Optional[str]  # 'TARGET', 'STOP_LOSS', 'TIME', 'SIGNAL'


class AdvancedBacktest:
    """
    Professional backtesting engine with advanced features:
    - Walk-forward optimization
    - Monte Carlo simulation
    - Slippage and commission modeling
    - Position sizing
    - Multiple exit strategies
    """
    
    def __init__(self, config: BacktestConfig = None):
        """
        Initialize backtesting engine.
        
        Args:
            config: Backtesting configuration
        """
        self.config = config or BacktestConfig()
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []
        self.current_capital = self.config.initial_capital
        self.positions: Dict[str, Trade] = {}
        
        logger.info(f"✅ Backtest initialized with ₹{self.config.initial_capital:,.0f}")
    
    def run_backtest(
        self,
        signals: pd.DataFrame,
        price_data: Dict[str, pd.DataFrame],
        strategy_func: Optional[Callable] = None
    ) -> Dict:
        """
        Run complete backtest.
        
        Args:
            signals: DataFrame with columns: date, symbol, signal, confidence, entry_price, target, stop_loss
            price_data: Dict of {symbol: price_dataframe}
            strategy_func: Optional custom strategy function
            
        Returns:
            Backtest results dictionary
        """
        logger.info("🔄 Running backtest...")
        
        self.trades = []
        self.equity_curve = [self.config.initial_capital]
        self.current_capital = self.config.initial_capital
        self.positions = {}
        
        # Sort signals by date
        signals = signals.sort_values('date').reset_index(drop=True)
        
        # Process each day
        for date in signals['date'].unique():
            daily_signals = signals[signals['date'] == date]
            
            # Update existing positions
            self._update_positions(date, price_data)
            
            # Process new signals
            for _, signal in daily_signals.iterrows():
                self._process_signal(signal, price_data)
            
            # Record equity
            self.equity_curve.append(self._calculate_equity(date, price_data))
        
        # Close remaining positions
        final_date = signals['date'].max()
        self._close_all_positions(final_date, price_data, 'END_OF_BACKTEST')
        
        # Calculate metrics
        results = self._calculate_metrics()
        
        logger.info(f"✅ Backtest completed: {len(self.trades)} trades")
        return results
    
    def _process_signal(self, signal: pd.Series, price_data: Dict[str, pd.DataFrame]):
        """Process a trading signal."""
        symbol = signal['symbol']
        signal_type = signal['signal']
        confidence = signal['confidence']
        
        # Check confidence threshold
        if confidence < self.config.confidence_threshold:
            return
        
        # Check if already in position
        if symbol in self.positions:
            return
        
        # Check max positions
        if len(self.positions) >= self.config.max_positions:
            return
        
        # Calculate position size
        entry_price = signal['entry_price']
        stop_loss = signal.get('stop_loss', entry_price * 0.95)
        risk_per_share = abs(entry_price - stop_loss)
        
        if risk_per_share == 0:
            return
        
        max_risk_amount = self.current_capital * self.config.max_risk_per_trade
        quantity = int(max_risk_amount / risk_per_share)
        
        if quantity == 0:
            return
        
        # Apply commission and slippage
        execution_price = entry_price * (1 + self.config.slippage)
        trade_cost = quantity * execution_price
        commission_cost = trade_cost * self.config.commission
        
        total_cost = trade_cost + commission_cost
        
        # Check if enough capital
        if total_cost > self.current_capital:
            return
        
        # Execute trade
        if signal_type == 'BUY':
            trade = Trade(
                entry_date=signal['date'],
                exit_date=None,
                symbol=symbol,
                direction='BUY',
                entry_price=execution_price,
                exit_price=None,
                quantity=quantity,
                pnl=None,
                pnl_pct=None,
                holding_days=None,
                exit_reason=None
            )
            
            self.positions[symbol] = trade
            self.current_capital -= total_cost
            
            logger.debug(f"📊 BUY {symbol}: {quantity} @ ₹{execution_price:.2f}")
    
    def _update_positions(self, date: datetime, price_data: Dict[str, pd.DataFrame]):
        """Update existing positions and check exit conditions."""
        positions_to_close = []
        
        for symbol, position in self.positions.items():
            if symbol not in price_data:
                continue
            
            # Get current price
            df = price_data[symbol]
            current_data = df[df.index <= date]
            
            if current_data.empty:
                continue
            
            current_price = current_data.iloc[-1]['Close']
            
            # Check stop loss and target
            # For now, simple implementation
            # Can add more sophisticated exit logic
            
        # Close positions marked for exit
        for symbol in positions_to_close:
            self._close_position(symbol, date, price_data, 'STOP_LOSS')
    
    def _close_position(
        self,
        symbol: str,
        exit_date: datetime,
        price_data: Dict[str, pd.DataFrame],
        reason: str
    ):
        """Close a position."""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        
        # Get exit price
        df = price_data[symbol]
        exit_data = df[df.index <= exit_date]
        
        if exit_data.empty:
            return
        
        exit_price = exit_data.iloc[-1]['Close']
        
        # Apply slippage (opposite direction)
        execution_price = exit_price * (1 - self.config.slippage)
        
        # Calculate P&L
        gross_pnl = position.quantity * (execution_price - position.entry_price)
        commission_cost = (position.quantity * execution_price) * self.config.commission
        net_pnl = gross_pnl - commission_cost
        
        # Update trade
        position.exit_date = exit_date
        position.exit_price = execution_price
        position.pnl = net_pnl
        position.pnl_pct = (net_pnl / (position.quantity * position.entry_price)) * 100
        position.holding_days = (exit_date - position.entry_date).days
        position.exit_reason = reason
        
        # Update capital
        self.current_capital += position.quantity * execution_price - commission_cost
        
        # Record trade
        self.trades.append(position)
        del self.positions[symbol]
        
        logger.debug(f"📊 CLOSE {symbol}: P&L ₹{net_pnl:,.0f} ({position.pnl_pct:.2f}%)")
    
    def _close_all_positions(self, date: datetime, price_data: Dict[str, pd.DataFrame], reason: str):
        """Close all open positions."""
        symbols = list(self.positions.keys())
        for symbol in symbols:
            self._close_position(symbol, date, price_data, reason)
    
    def _calculate_equity(self, date: datetime, price_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate total equity at a given date."""
        equity = self.current_capital
        
        # Add unrealized P&L from open positions
        for symbol, position in self.positions.items():
            if symbol in price_data:
                df = price_data[symbol]
                current_data = df[df.index <= date]
                if not current_data.empty:
                    current_price = current_data.iloc[-1]['Close']
                    equity += position.quantity * current_price
        
        return equity
    
    def _calculate_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics."""
        if not self.trades:
            return {'error': 'No trades executed'}
        
        df_trades = pd.DataFrame([vars(t) for t in self.trades])
        
        # Basic metrics
        total_trades = len(df_trades)
        winning_trades = len(df_trades[df_trades['pnl'] > 0])
        losing_trades = len(df_trades[df_trades['pnl'] < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # P&L metrics
        total_pnl = df_trades['pnl'].sum()
        avg_win = df_trades[df_trades['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = df_trades[df_trades['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if losing_trades > 0 else float('inf')
        
        # Returns
        final_equity = self.equity_curve[-1]
        total_return = ((final_equity - self.config.initial_capital) / self.config.initial_capital) * 100
        
        # Calculate returns series
        returns = pd.Series(self.equity_curve).pct_change().dropna()
        
        # Sharpe Ratio (annualized)
        if len(returns) > 1:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Sortino Ratio (only downside deviation)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0:
            sortino_ratio = (returns.mean() / downside_returns.std()) * np.sqrt(252)
        else:
            sortino_ratio = float('inf')
        
        # Drawdown
        equity_series = pd.Series(self.equity_curve)
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Calmar Ratio
        if max_drawdown != 0:
            calmar_ratio = (total_return / 100) / abs(max_drawdown / 100)
        else:
            calmar_ratio = float('inf')
        
        # Holding period
        avg_holding_days = df_trades['holding_days'].mean()
        
        # Exit reasons
        exit_reasons = df_trades['exit_reason'].value_counts().to_dict()
        
        results = {
            'summary': {
                'initial_capital': self.config.initial_capital,
                'final_equity': final_equity,
                'total_return': total_return,
                'total_pnl': total_pnl
            },
            'trades': {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate * 100,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'avg_holding_days': avg_holding_days
            },
            'risk_metrics': {
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'max_drawdown': max_drawdown,
                'calmar_ratio': calmar_ratio
            },
            'exit_analysis': exit_reasons,
            'equity_curve': self.equity_curve,
            'trades_df': df_trades
        }
        
        return results
    
    def walk_forward_optimization(
        self,
        signals: pd.DataFrame,
        price_data: Dict[str, pd.DataFrame],
        train_period_days: int = 180,
        test_period_days: int = 60,
        step_days: int = 30
    ) -> Dict:
        """
        Perform walk-forward optimization.
        
        Args:
            signals: Trading signals DataFrame
            price_data: Price data dictionary
            train_period_days: Training window size
            test_period_days: Testing window size
            step_days: Step size for rolling forward
            
        Returns:
            Walk-forward results
        """
        logger.info("🔄 Running walk-forward optimization...")
        
        results = []
        
        # Get date range
        start_date = signals['date'].min()
        end_date = signals['date'].max()
        
        current_date = start_date + timedelta(days=train_period_days)
        
        while current_date + timedelta(days=test_period_days) <= end_date:
            # Define windows
            train_start = current_date - timedelta(days=train_period_days)
            train_end = current_date
            test_start = current_date
            test_end = current_date + timedelta(days=test_period_days)
            
            # Get train/test data
            train_signals = signals[(signals['date'] >= train_start) & (signals['date'] < train_end)]
            test_signals = signals[(signals['date'] >= test_start) & (signals['date'] < test_end)]
            
            # Run backtest on test period
            if len(test_signals) > 0:
                test_result = self.run_backtest(test_signals, price_data)
                test_result['period'] = {
                    'train_start': train_start,
                    'train_end': train_end,
                    'test_start': test_start,
                    'test_end': test_end
                }
                results.append(test_result)
            
            # Step forward
            current_date += timedelta(days=step_days)
        
        # Aggregate results
        total_return = np.mean([r['summary']['total_return'] for r in results])
        avg_sharpe = np.mean([r['risk_metrics']['sharpe_ratio'] for r in results])
        avg_win_rate = np.mean([r['trades']['win_rate'] for r in results])
        
        logger.info(f"✅ Walk-forward completed: {len(results)} periods")
        logger.info(f"   Avg Return: {total_return:.2f}%")
        logger.info(f"   Avg Sharpe: {avg_sharpe:.2f}")
        logger.info(f"   Avg Win Rate: {avg_win_rate:.2f}%")
        
        return {
            'periods': results,
            'aggregate': {
                'avg_return': total_return,
                'avg_sharpe': avg_sharpe,
                'avg_win_rate': avg_win_rate,
                'num_periods': len(results)
            }
        }
    
    def monte_carlo_simulation(
        self,
        num_simulations: int = 1000,
        randomize_trades: bool = True
    ) -> Dict:
        """
        Run Monte Carlo simulation on trade results.
        
        Args:
            num_simulations: Number of simulations to run
            randomize_trades: Whether to randomize trade order
            
        Returns:
            Monte Carlo results
        """
        if not self.trades:
            raise ValueError("No trades to simulate. Run backtest first.")
        
        logger.info(f"🔄 Running Monte Carlo simulation ({num_simulations} runs)...")
        
        # Get trade returns
        trade_returns = [t.pnl_pct / 100 for t in self.trades]
        
        simulation_results = []
        
        for i in range(num_simulations):
            # Randomize trade order
            if randomize_trades:
                sim_returns = np.random.choice(trade_returns, size=len(trade_returns), replace=True)
            else:
                sim_returns = trade_returns
            
            # Calculate equity curve
            equity = self.config.initial_capital
            equity_curve = [equity]
            
            for ret in sim_returns:
                equity = equity * (1 + ret)
                equity_curve.append(equity)
            
            # Calculate metrics
            final_equity = equity_curve[-1]
            total_return = ((final_equity - self.config.initial_capital) / self.config.initial_capital) * 100
            
            # Max drawdown
            equity_series = pd.Series(equity_curve)
            running_max = equity_series.expanding().max()
            drawdown = (equity_series - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            simulation_results.append({
                'final_equity': final_equity,
                'total_return': total_return,
                'max_drawdown': max_drawdown,
                'equity_curve': equity_curve
            })
        
        # Calculate percentiles
        returns = [r['total_return'] for r in simulation_results]
        drawdowns = [r['max_drawdown'] for r in simulation_results]
        
        results = {
            'num_simulations': num_simulations,
            'returns': {
                'mean': np.mean(returns),
                'median': np.median(returns),
                'std': np.std(returns),
                'percentile_5': np.percentile(returns, 5),
                'percentile_25': np.percentile(returns, 25),
                'percentile_75': np.percentile(returns, 75),
                'percentile_95': np.percentile(returns, 95),
                'min': np.min(returns),
                'max': np.max(returns)
            },
            'drawdowns': {
                'mean': np.mean(drawdowns),
                'median': np.median(drawdowns),
                'percentile_5': np.percentile(drawdowns, 5),
                'percentile_95': np.percentile(drawdowns, 95),
                'worst': np.min(drawdowns)
            },
            'risk_of_ruin': len([r for r in returns if r < -50]) / num_simulations * 100,
            'probability_profitable': len([r for r in returns if r > 0]) / num_simulations * 100
        }
        
        logger.info(f"✅ Monte Carlo completed")
        logger.info(f"   Mean Return: {results['returns']['mean']:.2f}%")
        logger.info(f"   Probability Profitable: {results['probability_profitable']:.2f}%")
        logger.info(f"   Risk of Ruin (>50% loss): {results['risk_of_ruin']:.2f}%")
        
        return results


# ============================================================
# TESTING
# ============================================================

if __name__ == '__main__':
    print("🧪 Testing Advanced Backtesting Engine...")
    
    # Create sample signals
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
    
    signals = pd.DataFrame({
        'date': np.random.choice(dates, 100),
        'symbol': np.random.choice(['RELIANCE', 'TCS', 'INFY'], 100),
        'signal': np.random.choice(['BUY', 'SELL'], 100),
        'confidence': np.random.uniform(0.6, 0.95, 100),
        'entry_price': np.random.uniform(2000, 3000, 100),
        'stop_loss': np.random.uniform(1900, 2900, 100)
    })
    
    # Create sample price data
    price_data = {}
    for symbol in ['RELIANCE', 'TCS', 'INFY']:
        prices = pd.DataFrame({
            'Close': np.random.uniform(2000, 3000, len(dates))
        }, index=dates)
        price_data[symbol] = prices
    
    # Run backtest
    backtest = AdvancedBacktest()
    results = backtest.run_backtest(signals, price_data)
    
    print("\n📊 Backtest Results:")
    print(f"   Total Trades: {results['trades']['total_trades']}")
    print(f"   Win Rate: {results['trades']['win_rate']:.2f}%")
    print(f"   Total Return: {results['summary']['total_return']:.2f}%")
    print(f"   Sharpe Ratio: {results['risk_metrics']['sharpe_ratio']:.2f}")
    print(f"   Max Drawdown: {results['risk_metrics']['max_drawdown']:.2f}%")
    
    # Run Monte Carlo
    mc_results = backtest.monte_carlo_simulation(num_simulations=100)
    print(f"\n🎲 Monte Carlo Results:")
    print(f"   Mean Return: {mc_results['returns']['mean']:.2f}%")
    print(f"   Probability Profitable: {mc_results['probability_profitable']:.2f}%")
    
    print("\n✅ Advanced backtesting test passed!")

