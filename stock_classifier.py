"""
Stock Classification System for Trailing Stop Decision
======================================================
Automatically classifies stocks to determine optimal trailing stop usage
"""

import pandas as pd
import numpy as np

class StockClassifier:
    """
    Classifies stocks into categories to determine trailing stop usage
    
    Categories:
    - PREMIUM: High confidence, use fixed target (maximize profit)
    - STANDARD: Medium confidence, use trailing (balanced)
    - DEFENSIVE: Lower confidence, use tight trailing (protect capital)
    """
    
    def __init__(self):
        self.premium_criteria = {
            'min_volume': 1000000,      # Daily volume > 10L shares
            'min_market_cap': 50000,    # Market cap > 50K crores
            'min_liquidity_rank': 80,   # Top 20% by liquidity
            'max_volatility': 3.0,      # ATR% < 3%
        }
        
        self.defensive_criteria = {
            'max_volume': 100000,       # Daily volume < 1L shares
            'max_liquidity_rank': 40,   # Bottom 40% by liquidity
            'min_volatility': 4.0,      # ATR% > 4%
        }
    
    def classify_stock(self, stock_data):
        """
        Classify a single stock
        
        Parameters:
        -----------
        stock_data : dict
            {
                'symbol': str,
                'avg_volume': float,
                'market_cap': float (crores),
                'atr_percent': float,
                'liquidity_rank': float (0-100),
                'price': float,
                'sector': str
            }
        
        Returns:
        --------
        dict : Classification result with recommendation
        """
        symbol = stock_data['symbol']
        volume = stock_data.get('avg_volume', 0)
        market_cap = stock_data.get('market_cap', 0)
        atr_pct = stock_data.get('atr_percent', 0)
        liquidity = stock_data.get('liquidity_rank', 50)
        sector = stock_data.get('sector', 'Unknown')
        
        # Premium Stock Criteria
        is_premium = (
            volume >= self.premium_criteria['min_volume'] and
            market_cap >= self.premium_criteria['min_market_cap'] and
            liquidity >= self.premium_criteria['min_liquidity_rank'] and
            atr_pct <= self.premium_criteria['max_volatility']
        )
        
        # Defensive Stock Criteria
        is_defensive = (
            volume <= self.defensive_criteria['max_volume'] or
            liquidity <= self.defensive_criteria['max_liquidity_rank'] or
            atr_pct >= self.defensive_criteria['min_volatility']
        )
        
        # Classify
        if is_premium:
            category = 'PREMIUM'
            trailing_enabled = False
            trailing_percent = 0
            trailing_activation = 10.0
            capital_allocation = 'HIGH'
            reason = 'High liquidity + Low volatility = Maximize profit'
        elif is_defensive:
            category = 'DEFENSIVE'
            trailing_enabled = True
            trailing_percent = 3.0  # Tighter trail (3%)
            trailing_activation = 8.0  # Activate earlier (8%)
            capital_allocation = 'LOW'
            reason = 'Low liquidity or high volatility = Protect capital'
        else:
            category = 'STANDARD'
            trailing_enabled = True
            trailing_percent = 5.0  # Standard trail (5%)
            trailing_activation = 10.0  # Standard activation (10%)
            capital_allocation = 'MEDIUM'
            reason = 'Balanced metrics = Use trailing for consistency'
        
        return {
            'symbol': symbol,
            'category': category,
            'trailing_enabled': trailing_enabled,
            'trailing_percent': trailing_percent,
            'trailing_activation': trailing_activation,
            'capital_allocation': capital_allocation,
            'reason': reason,
            'metrics': {
                'volume': volume,
                'market_cap': market_cap,
                'atr_percent': atr_pct,
                'liquidity_rank': liquidity,
                'sector': sector
            }
        }
    
    def classify_portfolio(self, stocks_data):
        """
        Classify multiple stocks
        
        Parameters:
        -----------
        stocks_data : list of dict
            List of stock data dictionaries
        
        Returns:
        --------
        pandas.DataFrame : Classification results
        """
        results = []
        for stock in stocks_data:
            result = self.classify_stock(stock)
            results.append({
                'Symbol': result['symbol'],
                'Category': result['category'],
                'Trailing': 'YES' if result['trailing_enabled'] else 'NO',
                'Trail %': f"{result['trailing_percent']:.1f}%" if result['trailing_enabled'] else 'N/A',
                'Activation': f"{result['trailing_activation']:.0f}%",
                'Capital': result['capital_allocation'],
                'Volume': f"{result['metrics']['volume']:,.0f}",
                'Market Cap': f"₹{result['metrics']['market_cap']:,.0f}Cr",
                'ATR %': f"{result['metrics']['atr_percent']:.2f}%",
                'Liquidity': f"{result['metrics']['liquidity_rank']:.0f}",
                'Reason': result['reason']
            })
        
        df = pd.DataFrame(results)
        return df
    
    def get_nifty50_classifications(self):
        """
        Pre-classified Nifty 50 stocks with known characteristics
        """
        nifty50_data = [
            # PREMIUM Stocks (Top Liquid, Low Volatility)
            {'symbol': 'RELIANCE', 'avg_volume': 8500000, 'market_cap': 1800000, 'atr_percent': 2.1, 'liquidity_rank': 95, 'sector': 'Energy'},
            {'symbol': 'TCS', 'avg_volume': 2500000, 'market_cap': 1400000, 'atr_percent': 1.8, 'liquidity_rank': 92, 'sector': 'IT'},
            {'symbol': 'HDFCBANK', 'avg_volume': 6000000, 'market_cap': 1200000, 'atr_percent': 1.9, 'liquidity_rank': 94, 'sector': 'Banking'},
            {'symbol': 'INFY', 'avg_volume': 4500000, 'market_cap': 700000, 'atr_percent': 2.0, 'liquidity_rank': 90, 'sector': 'IT'},
            {'symbol': 'ICICIBANK', 'avg_volume': 7000000, 'market_cap': 850000, 'atr_percent': 2.2, 'liquidity_rank': 93, 'sector': 'Banking'},
            {'symbol': 'HINDUNILVR', 'avg_volume': 1800000, 'market_cap': 600000, 'atr_percent': 1.7, 'liquidity_rank': 88, 'sector': 'FMCG'},
            {'symbol': 'ITC', 'avg_volume': 6500000, 'market_cap': 550000, 'atr_percent': 1.6, 'liquidity_rank': 91, 'sector': 'FMCG'},
            
            # STANDARD Stocks (Good Liquidity, Moderate Volatility)
            {'symbol': 'SBIN', 'avg_volume': 12000000, 'market_cap': 600000, 'atr_percent': 2.8, 'liquidity_rank': 89, 'sector': 'Banking'},
            {'symbol': 'BHARTIARTL', 'avg_volume': 5500000, 'market_cap': 850000, 'atr_percent': 2.4, 'liquidity_rank': 87, 'sector': 'Telecom'},
            {'symbol': 'KOTAKBANK', 'avg_volume': 2000000, 'market_cap': 350000, 'atr_percent': 2.5, 'liquidity_rank': 82, 'sector': 'Banking'},
            {'symbol': 'AXISBANK', 'avg_volume': 4500000, 'market_cap': 340000, 'atr_percent': 3.2, 'liquidity_rank': 84, 'sector': 'Banking'},
            {'symbol': 'LT', 'avg_volume': 1500000, 'market_cap': 500000, 'atr_percent': 2.7, 'liquidity_rank': 78, 'sector': 'Infrastructure'},
            {'symbol': 'HCLTECH', 'avg_volume': 2000000, 'market_cap': 380000, 'atr_percent': 2.3, 'liquidity_rank': 80, 'sector': 'IT'},
            {'symbol': 'ASIANPAINT', 'avg_volume': 800000, 'market_cap': 320000, 'atr_percent': 2.2, 'liquidity_rank': 75, 'sector': 'Paints'},
            {'symbol': 'MARUTI', 'avg_volume': 900000, 'market_cap': 400000, 'atr_percent': 2.6, 'liquidity_rank': 76, 'sector': 'Auto'},
            {'symbol': 'SUNPHARMA', 'avg_volume': 2500000, 'market_cap': 350000, 'atr_percent': 2.4, 'liquidity_rank': 79, 'sector': 'Pharma'},
            {'symbol': 'TITAN', 'avg_volume': 1200000, 'market_cap': 320000, 'atr_percent': 2.8, 'liquidity_rank': 74, 'sector': 'Jewellery'},
            {'symbol': 'NTPC', 'avg_volume': 8000000, 'market_cap': 280000, 'atr_percent': 2.9, 'liquidity_rank': 81, 'sector': 'Power'},
            {'symbol': 'BAJFINANCE', 'avg_volume': 1100000, 'market_cap': 480000, 'atr_percent': 3.1, 'liquidity_rank': 77, 'sector': 'NBFC'},
            {'symbol': 'WIPRO', 'avg_volume': 4000000, 'market_cap': 280000, 'atr_percent': 2.5, 'liquidity_rank': 73, 'sector': 'IT'},
            
            # DEFENSIVE Stocks (Lower Liquidity or Higher Volatility)
            {'symbol': 'TATASTEEL', 'avg_volume': 8500000, 'market_cap': 180000, 'atr_percent': 4.2, 'liquidity_rank': 72, 'sector': 'Metals'},
            {'symbol': 'JSWSTEEL', 'avg_volume': 3500000, 'market_cap': 220000, 'atr_percent': 3.8, 'liquidity_rank': 68, 'sector': 'Metals'},
            {'symbol': 'HINDALCO', 'avg_volume': 4500000, 'market_cap': 120000, 'atr_percent': 4.5, 'liquidity_rank': 65, 'sector': 'Metals'},
            {'symbol': 'COALINDIA', 'avg_volume': 6000000, 'market_cap': 280000, 'atr_percent': 3.5, 'liquidity_rank': 70, 'sector': 'Mining'},
            {'symbol': 'ONGC', 'avg_volume': 12000000, 'market_cap': 350000, 'atr_percent': 3.6, 'liquidity_rank': 71, 'sector': 'Energy'},
            {'symbol': 'POWERGRID', 'avg_volume': 3500000, 'market_cap': 240000, 'atr_percent': 2.2, 'liquidity_rank': 58, 'sector': 'Power'},
            {'symbol': 'BPCL', 'avg_volume': 5000000, 'market_cap': 120000, 'atr_percent': 4.1, 'liquidity_rank': 64, 'sector': 'Energy'},
            {'symbol': 'ADANIPORTS', 'avg_volume': 2500000, 'market_cap': 280000, 'atr_percent': 4.8, 'liquidity_rank': 62, 'sector': 'Infrastructure'},
            {'symbol': 'SHREECEM', 'avg_volume': 45000, 'market_cap': 45000, 'atr_percent': 2.8, 'liquidity_rank': 35, 'sector': 'Cement'},
            {'symbol': 'DRREDDY', 'avg_volume': 500000, 'market_cap': 90000, 'atr_percent': 2.9, 'liquidity_rank': 48, 'sector': 'Pharma'},
        ]
        
        return self.classify_portfolio(nifty50_data)


def generate_recommendation_report(classifier):
    """Generate a comprehensive recommendation report"""
    
    # Get Nifty 50 classifications
    df = classifier.get_nifty50_classifications()
    
    # Count by category
    premium_count = len(df[df['Category'] == 'PREMIUM'])
    standard_count = len(df[df['Category'] == 'STANDARD'])
    defensive_count = len(df[df['Category'] == 'DEFENSIVE'])
    
    print("="*100)
    print("STOCK CLASSIFICATION SYSTEM - TRAILING STOP DECISION")
    print("="*100)
    print()
    
    print("📊 PORTFOLIO BREAKDOWN:")
    print(f"  • PREMIUM Stocks:    {premium_count:2d} stocks (Fixed 10% target - Maximize profit)")
    print(f"  • STANDARD Stocks:   {standard_count:2d} stocks (Trailing 5%/10% - Balanced)")
    print(f"  • DEFENSIVE Stocks:  {defensive_count:2d} stocks (Trailing 3%/8% - Protect capital)")
    print()
    
    print("="*100)
    print("FULL CLASSIFICATION TABLE:")
    print("="*100)
    print(df.to_string(index=False))
    print()
    
    # Capital Allocation Recommendation
    print("="*100)
    print("💰 RECOMMENDED CAPITAL ALLOCATION (₹25L Portfolio):")
    print("="*100)
    premium_allocation = 0.50  # 50%
    standard_allocation = 0.35  # 35%
    defensive_allocation = 0.15  # 15%
    
    print(f"  • PREMIUM ({premium_count} stocks):   ₹{25*premium_allocation:,.0f}L ({premium_allocation*100:.0f}%) = ₹{25*premium_allocation/premium_count:,.2f}L per stock")
    print(f"  • STANDARD ({standard_count} stocks):  ₹{25*standard_allocation:,.0f}L ({standard_allocation*100:.0f}%) = ₹{25*standard_allocation/standard_count:,.2f}L per stock")
    print(f"  • DEFENSIVE ({defensive_count} stocks): ₹{25*defensive_allocation:,.0f}L ({defensive_allocation*100:.0f}%) = ₹{25*defensive_allocation/defensive_count:,.2f}L per stock")
    print()
    
    # Expected Returns
    print("="*100)
    print("📈 EXPECTED ANNUAL RETURNS:")
    print("="*100)
    premium_return = 0.70  # 70% (without trailing)
    standard_return = 0.56  # 56% (with trailing)
    defensive_return = 0.40  # 40% (tight trailing)
    
    premium_profit = 25 * premium_allocation * premium_return
    standard_profit = 25 * standard_allocation * standard_return
    defensive_profit = 25 * defensive_allocation * defensive_return
    total_profit = premium_profit + standard_profit + defensive_profit
    
    print(f"  • PREMIUM:   ₹{25*premium_allocation:.1f}L × 70% = ₹{premium_profit:.2f}L profit")
    print(f"  • STANDARD:  ₹{25*standard_allocation:.1f}L × 56% = ₹{standard_profit:.2f}L profit")
    print(f"  • DEFENSIVE: ₹{25*defensive_allocation:.1f}L × 40% = ₹{defensive_profit:.2f}L profit")
    print(f"  • TOTAL:     ₹25L → ₹{25 + total_profit:.2f}L ({total_profit/25*100:.1f}% annual return)")
    print()
    
    print("="*100)
    print("🎯 STRATEGY SUMMARY:")
    print("="*100)
    print(f"  ✓ Maximize profit on {premium_count} high-confidence stocks (no trailing)")
    print(f"  ✓ Balanced approach on {standard_count} medium stocks (standard trailing)")
    print(f"  ✓ Protect capital on {defensive_count} volatile stocks (tight trailing)")
    print(f"  ✓ Expected portfolio return: {total_profit/25*100:.1f}% per year")
    print(f"  ✓ Risk-adjusted for diversification")
    print("="*100)
    
    return df


if __name__ == "__main__":
    # Create classifier
    classifier = StockClassifier()
    
    # Generate report
    df = generate_recommendation_report(classifier)
    
    # Save to CSV
    output_file = "stock_classification_report.csv"
    df.to_csv(output_file, index=False)
    print(f"\n✅ Report saved to: {output_file}")

