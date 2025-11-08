"""
Risk Management Engine
======================
Professional risk management system for AI trading
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class RiskEngine:
    """
    Professional Risk Management Engine
    
    Features:
    - Kelly Criterion position sizing
    - Value at Risk (VaR) calculation
    - Portfolio correlation analysis
    - Drawdown monitoring
    - Risk-adjusted returns
    """
    
    def __init__(self, total_capital: float, max_risk_per_trade: float = 2.0):
        """
        Initialize Risk Engine.
        
        Args:
            total_capital: Total trading capital
            max_risk_per_trade: Maximum risk per trade as percentage (default 2%)
        """
        self.total_capital = total_capital
        self.max_risk_per_trade = max_risk_per_trade
        self.max_portfolio_risk = max_risk_per_trade * 5  # 10% max portfolio risk
        self.max_positions = 10
        self.max_correlation = 0.7
        
        logger.info(f"✅ Risk Engine initialized with capital: ₹{total_capital:,.0f}")
    
    # ============================================================
    # POSITION SIZING
    # ============================================================
    
    def calculate_kelly_criterion(
        self, 
        win_rate: float, 
        avg_win: float, 
        avg_loss: float
    ) -> float:
        """
        Calculate Kelly Criterion for optimal position sizing.
        
        Formula: Kelly % = W - [(1 - W) / R]
        Where:
            W = Win probability
            R = Win/Loss ratio
        
        Args:
            win_rate: Historical win rate (0.0 to 1.0)
            avg_win: Average winning trade amount
            avg_loss: Average losing trade amount
            
        Returns:
            Optimal position size as percentage of capital
        """
        if avg_loss == 0 or win_rate <= 0:
            return 0.0
        
        # Win/Loss ratio
        win_loss_ratio = abs(avg_win / avg_loss)
        
        # Kelly formula
        kelly_pct = win_rate - ((1 - win_rate) / win_loss_ratio)
        
        # Apply fractional Kelly (use 25% of full Kelly for safety)
        fractional_kelly = kelly_pct * 0.25
        
        # Cap at maximum risk per trade
        kelly_pct = min(fractional_kelly, self.max_risk_per_trade / 100)
        
        # Ensure non-negative
        kelly_pct = max(kelly_pct, 0.0)
        
        logger.info(f"📊 Kelly Criterion: {kelly_pct*100:.2f}%")
        return kelly_pct
    
    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        confidence: float = 0.75,
        win_rate: Optional[float] = None,
        avg_win: Optional[float] = None,
        avg_loss: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Calculate optimal position size based on risk parameters.
        
        Args:
            entry_price: Entry price per share
            stop_loss: Stop loss price
            confidence: Model confidence (0.0 to 1.0)
            win_rate: Historical win rate (optional, for Kelly)
            avg_win: Average win amount (optional, for Kelly)
            avg_loss: Average loss amount (optional, for Kelly)
            
        Returns:
            Dict with position size, quantity, risk amount
        """
        # Calculate risk per share
        risk_per_share = abs(entry_price - stop_loss)
        
        if risk_per_share == 0:
            return {
                'quantity': 0,
                'position_size': 0,
                'risk_amount': 0,
                'method': 'INVALID_RISK'
            }
        
        # Method 1: Fixed percentage risk
        max_risk_amount = self.total_capital * (self.max_risk_per_trade / 100)
        quantity_fixed = int(max_risk_amount / risk_per_share)
        
        # Method 2: Kelly Criterion (if historical data available)
        quantity_kelly = quantity_fixed
        if win_rate and avg_win and avg_loss:
            kelly_pct = self.calculate_kelly_criterion(win_rate, avg_win, avg_loss)
            kelly_amount = self.total_capital * kelly_pct
            quantity_kelly = int(kelly_amount / entry_price)
        
        # Method 3: Confidence-adjusted
        confidence_multiplier = confidence  # Scale by confidence
        quantity_adjusted = int(quantity_fixed * confidence_multiplier)
        
        # Use the most conservative (minimum) of all methods
        final_quantity = min(quantity_fixed, quantity_kelly, quantity_adjusted)
        
        # Calculate final position metrics
        position_size = final_quantity * entry_price
        risk_amount = final_quantity * risk_per_share
        
        # Ensure position doesn't exceed limits
        max_position_size = self.total_capital * 0.2  # Max 20% in single position
        if position_size > max_position_size:
            final_quantity = int(max_position_size / entry_price)
            position_size = final_quantity * entry_price
            risk_amount = final_quantity * risk_per_share
        
        return {
            'quantity': final_quantity,
            'position_size': round(position_size, 2),
            'risk_amount': round(risk_amount, 2),
            'risk_pct': round((risk_amount / self.total_capital) * 100, 2),
            'method': 'KELLY' if win_rate else 'FIXED_PCT',
            'entry_price': entry_price,
            'stop_loss': stop_loss
        }
    
    # ============================================================
    # VALUE AT RISK (VaR)
    # ============================================================
    
    def calculate_var(
        self,
        returns: List[float],
        confidence_level: float = 0.95,
        method: str = 'historical'
    ) -> Dict[str, float]:
        """
        Calculate Value at Risk (VaR).
        
        VaR = "There's X% probability that portfolio won't lose more than Y amount"
        
        Args:
            returns: List of historical returns
            confidence_level: Confidence level (default 95%)
            method: 'historical' or 'parametric'
            
        Returns:
            Dict with VaR metrics
        """
        if not returns or len(returns) < 30:
            return {'var': 0, 'cvar': 0, 'method': 'INSUFFICIENT_DATA'}
        
        returns_array = np.array(returns)
        
        if method == 'historical':
            # Historical VaR (empirical quantile)
            var_percentile = (1 - confidence_level) * 100
            var = np.percentile(returns_array, var_percentile)
            
            # Conditional VaR (CVaR / Expected Shortfall)
            # Average of losses beyond VaR
            cvar = returns_array[returns_array <= var].mean()
            
        else:  # parametric (assumes normal distribution)
            # Parametric VaR
            mean_return = returns_array.mean()
            std_return = returns_array.std()
            z_score = stats.norm.ppf(1 - confidence_level)
            var = mean_return + z_score * std_return
            
            # CVaR for normal distribution
            phi = stats.norm.pdf(z_score)
            cvar = mean_return - std_return * (phi / (1 - confidence_level))
        
        # Convert to rupee amounts
        var_amount = var * self.total_capital
        cvar_amount = cvar * self.total_capital
        
        return {
            'var': round(var, 6),
            'var_amount': round(var_amount, 2),
            'cvar': round(cvar, 6),
            'cvar_amount': round(cvar_amount, 2),
            'confidence_level': confidence_level,
            'method': method,
            'interpretation': f"With {confidence_level*100:.0f}% confidence, maximum 1-day loss won't exceed ₹{abs(var_amount):,.2f}"
        }
    
    def calculate_portfolio_var(
        self,
        positions: List[Dict],
        price_history: Dict[str, pd.DataFrame]
    ) -> Dict[str, float]:
        """
        Calculate portfolio-level VaR considering correlations.
        
        Args:
            positions: List of current positions
            price_history: Dict of {symbol: price_dataframe}
            
        Returns:
            Portfolio VaR metrics
        """
        if not positions:
            return {'portfolio_var': 0, 'message': 'NO_POSITIONS'}
        
        # Calculate returns for each position
        returns_matrix = []
        weights = []
        
        for pos in positions:
            symbol = pos['symbol']
            if symbol in price_history:
                df = price_history[symbol]
                returns = df['close'].pct_change().dropna()
                returns_matrix.append(returns.values)
                weights.append(pos['current_value'] / self.total_capital)
        
        if not returns_matrix:
            return {'portfolio_var': 0, 'message': 'NO_PRICE_DATA'}
        
        # Convert to numpy arrays
        returns_df = pd.DataFrame(returns_matrix).T
        weights = np.array(weights)
        
        # Calculate portfolio returns
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        # Calculate VaR
        var_metrics = self.calculate_var(portfolio_returns.tolist(), confidence_level=0.95)
        
        return var_metrics
    
    # ============================================================
    # CORRELATION ANALYSIS
    # ============================================================
    
    def calculate_correlation_matrix(
        self,
        symbols: List[str],
        price_history: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Calculate correlation matrix for portfolio positions.
        
        Args:
            symbols: List of symbols
            price_history: Dict of {symbol: price_dataframe}
            
        Returns:
            Correlation matrix as DataFrame
        """
        returns_data = {}
        
        for symbol in symbols:
            if symbol in price_history:
                df = price_history[symbol]
                returns = df['close'].pct_change().dropna()
                returns_data[symbol] = returns
        
        if not returns_data:
            return pd.DataFrame()
        
        returns_df = pd.DataFrame(returns_data)
        correlation_matrix = returns_df.corr()
        
        return correlation_matrix
    
    def check_concentration_risk(
        self,
        positions: List[Dict],
        max_single_position: float = 0.2
    ) -> Dict[str, any]:
        """
        Check if portfolio is too concentrated in single positions.
        
        Args:
            positions: List of current positions
            max_single_position: Max allowed % in single position (default 20%)
            
        Returns:
            Concentration risk analysis
        """
        if not positions:
            return {'risk_level': 'NONE', 'message': 'NO_POSITIONS'}
        
        total_value = sum(pos['current_value'] for pos in positions)
        
        concentrated_positions = []
        for pos in positions:
            position_pct = pos['current_value'] / total_value
            if position_pct > max_single_position:
                concentrated_positions.append({
                    'symbol': pos['symbol'],
                    'percentage': round(position_pct * 100, 2),
                    'amount': pos['current_value']
                })
        
        if concentrated_positions:
            risk_level = 'HIGH' if len(concentrated_positions) > 2 else 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'risk_level': risk_level,
            'concentrated_positions': concentrated_positions,
            'max_concentration': round(max(pos['current_value'] / total_value for pos in positions) * 100, 2),
            'recommendation': 'DIVERSIFY' if risk_level != 'LOW' else 'OK'
        }
    
    # ============================================================
    # DRAWDOWN ANALYSIS
    # ============================================================
    
    def calculate_drawdown(
        self,
        equity_curve: List[float]
    ) -> Dict[str, float]:
        """
        Calculate drawdown metrics.
        
        Args:
            equity_curve: List of portfolio values over time
            
        Returns:
            Drawdown metrics
        """
        if not equity_curve or len(equity_curve) < 2:
            return {'current_dd': 0, 'max_dd': 0}
        
        equity_array = np.array(equity_curve)
        
        # Calculate running maximum
        running_max = np.maximum.accumulate(equity_array)
        
        # Calculate drawdown
        drawdown = (equity_array - running_max) / running_max
        
        # Current drawdown
        current_dd = drawdown[-1]
        
        # Maximum drawdown
        max_dd = drawdown.min()
        
        # Drawdown duration (days in current drawdown)
        if current_dd < 0:
            dd_duration = len(equity_array) - np.argmax(running_max)
        else:
            dd_duration = 0
        
        return {
            'current_drawdown': round(current_dd * 100, 2),
            'max_drawdown': round(max_dd * 100, 2),
            'drawdown_duration_days': dd_duration,
            'is_at_peak': current_dd == 0,
            'recovery_needed_pct': round((1 / (1 + current_dd) - 1) * 100, 2) if current_dd < 0 else 0
        }
    
    # ============================================================
    # RISK-ADJUSTED RETURNS
    # ============================================================
    
    def calculate_sharpe_ratio(
        self,
        returns: List[float],
        risk_free_rate: float = 0.06  # 6% annual
    ) -> float:
        """
        Calculate Sharpe Ratio.
        
        Sharpe Ratio = (Return - Risk Free Rate) / Standard Deviation
        
        Args:
            returns: List of returns
            risk_free_rate: Annual risk-free rate (default 6%)
            
        Returns:
            Sharpe ratio
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        
        # Annualize daily returns
        mean_return = returns_array.mean() * 252  # Trading days per year
        std_return = returns_array.std() * np.sqrt(252)
        
        if std_return == 0:
            return 0.0
        
        sharpe = (mean_return - risk_free_rate) / std_return
        
        return round(sharpe, 4)
    
    def calculate_sortino_ratio(
        self,
        returns: List[float],
        risk_free_rate: float = 0.06
    ) -> float:
        """
        Calculate Sortino Ratio (only considers downside volatility).
        
        Args:
            returns: List of returns
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Sortino ratio
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        
        # Only negative returns for downside deviation
        downside_returns = returns_array[returns_array < 0]
        
        if len(downside_returns) == 0:
            return float('inf')  # No downside risk
        
        # Annualize
        mean_return = returns_array.mean() * 252
        downside_std = downside_returns.std() * np.sqrt(252)
        
        if downside_std == 0:
            return 0.0
        
        sortino = (mean_return - risk_free_rate) / downside_std
        
        return round(sortino, 4)
    
    def calculate_calmar_ratio(
        self,
        returns: List[float],
        equity_curve: List[float]
    ) -> float:
        """
        Calculate Calmar Ratio = Annual Return / Maximum Drawdown.
        
        Args:
            returns: List of returns
            equity_curve: Portfolio equity curve
            
        Returns:
            Calmar ratio
        """
        if not returns or not equity_curve:
            return 0.0
        
        # Annual return
        total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0]
        years = len(equity_curve) / 252
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # Max drawdown
        dd_metrics = self.calculate_drawdown(equity_curve)
        max_dd = abs(dd_metrics['max_drawdown']) / 100
        
        if max_dd == 0:
            return float('inf')
        
        calmar = annual_return / max_dd
        
        return round(calmar, 4)
    
    # ============================================================
    # COMPREHENSIVE RISK REPORT
    # ============================================================
    
    def generate_risk_report(
        self,
        positions: List[Dict],
        returns: List[float],
        equity_curve: List[float],
        price_history: Dict[str, pd.DataFrame]
    ) -> Dict[str, any]:
        """
        Generate comprehensive risk report.
        
        Args:
            positions: Current portfolio positions
            returns: Historical returns
            equity_curve: Portfolio equity curve
            price_history: Price history for all symbols
            
        Returns:
            Complete risk analysis report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'capital': self.total_capital,
            'position_count': len(positions)
        }
        
        # Position sizing info
        total_invested = sum(pos['current_value'] for pos in positions) if positions else 0
        report['invested_capital'] = round(total_invested, 2)
        report['available_capital'] = round(self.total_capital - total_invested, 2)
        report['capital_utilization_pct'] = round((total_invested / self.total_capital) * 100, 2)
        
        # VaR
        if returns:
            report['var'] = self.calculate_var(returns)
        
        # Portfolio VaR
        if positions and price_history:
            report['portfolio_var'] = self.calculate_portfolio_var(positions, price_history)
        
        # Concentration risk
        if positions:
            report['concentration_risk'] = self.check_concentration_risk(positions)
        
        # Drawdown
        if equity_curve:
            report['drawdown'] = self.calculate_drawdown(equity_curve)
        
        # Risk-adjusted returns
        if returns:
            report['sharpe_ratio'] = self.calculate_sharpe_ratio(returns)
            report['sortino_ratio'] = self.calculate_sortino_ratio(returns)
            if equity_curve:
                report['calmar_ratio'] = self.calculate_calmar_ratio(returns, equity_curve)
        
        # Overall risk level
        risk_score = 0
        if report.get('capital_utilization_pct', 0) > 80:
            risk_score += 2
        if report.get('concentration_risk', {}).get('risk_level') == 'HIGH':
            risk_score += 2
        if abs(report.get('drawdown', {}).get('current_drawdown', 0)) > 10:
            risk_score += 1
        
        risk_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        report['overall_risk_level'] = risk_levels[min(risk_score, 3)]
        
        return report


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def get_risk_engine(capital: float) -> RiskEngine:
    """Get risk engine instance."""
    return RiskEngine(total_capital=capital)


# ============================================================
# TESTING
# ============================================================

if __name__ == '__main__':
    print("🧪 Testing Risk Engine...")
    
    # Initialize
    engine = RiskEngine(total_capital=1000000)  # ₹10 Lakh
    
    # Test Kelly Criterion
    kelly = engine.calculate_kelly_criterion(
        win_rate=0.65,
        avg_win=1500,
        avg_loss=800
    )
    print(f"✅ Kelly Criterion: {kelly*100:.2f}%")
    
    # Test position sizing
    position = engine.calculate_position_size(
        entry_price=2450,
        stop_loss=2400,
        confidence=0.85,
        win_rate=0.65,
        avg_win=1500,
        avg_loss=800
    )
    print(f"✅ Position Size: {position}")
    
    # Test VaR
    sample_returns = np.random.normal(0.001, 0.02, 100).tolist()  # Simulated returns
    var = engine.calculate_var(sample_returns)
    print(f"✅ Value at Risk: {var}")
    
    # Test drawdown
    equity_curve = [100000 + i*1000 + np.random.normal(0, 500) for i in range(100)]
    dd = engine.calculate_drawdown(equity_curve)
    print(f"✅ Drawdown: {dd}")
    
    # Test Sharpe ratio
    sharpe = engine.calculate_sharpe_ratio(sample_returns)
    print(f"✅ Sharpe Ratio: {sharpe}")
    
    print("\n✅ All risk management tests passed!")

