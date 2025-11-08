"""
AI Stock Screener - Daily Scanner
==================================

Scans all 42 Nifty stocks using trained AI models.
Identifies BUY signals for VWAP Ladder strategy.

Usage: python daily_screener.py
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import joblib

# Add path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

from ai_screener.data_loader import DataLoader
from ai_screener.feature_engineering import FeatureEngineer
from ai_screener.xgboost_trainer import XGBoostTrainer


# Stock tiers based on training performance
TIER_1_STOCKS = [
    'NSE_BAJAJFINSV', 'NSE_REFEX', 'NSE_MAXHEALTH', 'NSE_RELINFRA',
    'NSE_M&M', 'NSE_ETERNAL', 'NSE_ICICIBANK', 'NSE_ONGC',
    'NSE_ADANIENT', 'NSE_SHRIRAMFIN'
]

TIER_2_STOCKS = [
    'NSE_ADANIPORTS', 'NSE_HINDALCO', 'NSE_TATASTEEL', 'NSE_BIOCON',
    'NSE_EICHERMOT', 'NSE_POWERGRID', 'NSE_PTC', 'NSE_HDFCLIFE',
    'NSE_SBILIFE', 'NSE_TMPV', 'NSE_AXISBANK', 'NSE_JSWSTEEL',
    'NSE_KOTAKBANK', 'NSE_HCLTECH', 'NSE_TECHM'
]

# Low confidence stocks (Tier 3) - will show but marked as low priority
TIER_3_STOCKS = [
    'NSE_NTPC', 'NSE_INFY', 'NSE_TCS', 'NSE_HDFCBANK', 'NSE_NESTLEIND',
    'NSE_RELIANCE', 'NSE_CIPLA', 'NSE_HINDUNILVR', 'NSE_DRREDDY',
    'NSE_GRASIM', 'NSE_SBIN', 'NSE_SUNPHARMA', 'NSE_TATACONSUM',
    'NSE_TITAN', 'NSE_ASIANPAINT', 'NSE_BERGEPAINT', 'NSE_BHARTIARTL'
]


class DailyScreener:
    """Daily stock screener using AI models."""
    
    def __init__(self, models_dir='ai_screener/models'):
        """Initialize screener with trained models."""
        self.models_dir = models_dir
        self.loader = DataLoader()
        self.engineer = FeatureEngineer()
        self.trainer = XGBoostTrainer()
        self.models = {}
        self.results = []
        
    def load_models(self):
        """Load all trained models."""
        print("Loading trained models...", flush=True)
        
        # Get all stocks
        all_stocks = self.loader.get_all_stocks()
        
        loaded = 0
        failed = 0
        
        for stock in all_stocks:
            model_path = os.path.join(self.models_dir, f'xgb_{stock}.pkl')
            
            if os.path.exists(model_path):
                try:
                    model = joblib.load(model_path)
                    self.models[stock] = model
                    loaded += 1
                except Exception as e:
                    print(f"  Warning: Failed to load {stock}: {e}")
                    failed += 1
            else:
                failed += 1
        
        print(f"✓ Loaded {loaded} models ({failed} failed/missing)")
        return loaded > 0
    
    def get_stock_tier(self, stock):
        """Get tier classification for stock."""
        if stock in TIER_1_STOCKS:
            return 1, "HIGH"
        elif stock in TIER_2_STOCKS:
            return 2, "MEDIUM"
        else:
            return 3, "LOW"
    
    def predict_stock(self, stock):
        """Get prediction for single stock."""
        try:
            # Load data
            df = self.loader.load_stock_data(stock)
            
            if df is None or len(df) < 50:
                return None
            
            # Engineer features
            df_features = self.engineer.engineer_features(df)
            
            # Get latest data point
            latest = df_features.iloc[-1]
            
            # Get feature columns
            feature_cols = self.trainer.get_feature_columns(df_features)
            X = df_features[feature_cols].values[-1:] # Last row
            
            # Predict
            model = self.models[stock]
            prediction = model.predict(X)[0]
            proba = model.predict_proba(X)[0]
            
            # Get confidence (probability of predicted class)
            confidence = proba[prediction]
            
            # Get signal
            signal = "BUY" if prediction == 1 else "HOLD"
            
            # Get tier
            tier, tier_label = self.get_stock_tier(stock)
            
            # Get latest price info
            latest_price = df.iloc[-1]['close']
            latest_date = df.iloc[-1]['time']
            
            return {
                'stock': stock.replace('NSE_', ''),
                'signal': signal,
                'confidence': confidence * 100,
                'tier': tier,
                'tier_label': tier_label,
                'price': latest_price,
                'date': latest_date,
                'buy_proba': proba[1] * 100 if len(proba) > 1 else 0
            }
            
        except Exception as e:
            print(f"  Error predicting {stock}: {e}")
            return None
    
    def scan_all_stocks(self):
        """Scan all stocks and get predictions."""
        print("\nScanning stocks...", flush=True)
        
        self.results = []
        
        for stock in self.models.keys():
            result = self.predict_stock(stock)
            if result:
                self.results.append(result)
        
        print(f"✓ Scanned {len(self.results)} stocks")
    
    def get_buy_signals(self, min_confidence=0):
        """Get stocks with BUY signals."""
        buy_signals = [r for r in self.results if r['signal'] == 'BUY' and r['confidence'] >= min_confidence]
        # Sort by tier first, then confidence
        buy_signals.sort(key=lambda x: (x['tier'], -x['confidence']))
        return buy_signals
    
    def display_results(self):
        """Display screening results."""
        print("\n" + "="*80)
        print(f"AI SCREENER RESULTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        buy_signals = self.get_buy_signals()
        
        if not buy_signals:
            print("\n⚠ No BUY signals found today.")
            print("Market conditions may not be favorable for VWAP strategy.")
            return
        
        # Count by tier
        tier1_count = len([s for s in buy_signals if s['tier'] == 1])
        tier2_count = len([s for s in buy_signals if s['tier'] == 2])
        tier3_count = len([s for s in buy_signals if s['tier'] == 3])
        
        print(f"\nTotal BUY Signals: {len(buy_signals)}")
        print(f"  Tier 1 (HIGH):   {tier1_count} signals")
        print(f"  Tier 2 (MEDIUM): {tier2_count} signals")
        print(f"  Tier 3 (LOW):    {tier3_count} signals")
        
        # Tier 1 Signals (High Priority)
        tier1_signals = [s for s in buy_signals if s['tier'] == 1]
        if tier1_signals:
            print("\n" + "="*80)
            print("🌟 TIER 1 - HIGH CONFIDENCE SIGNALS (Trade These!)")
            print("="*80)
            print(f"{'Stock':<15} {'Signal':<8} {'Confidence':<12} {'Price':<10} {'Date':<12}")
            print("-"*80)
            
            for s in tier1_signals:
                print(f"{s['stock']:<15} {s['signal']:<8} {s['confidence']:>10.1f}% "
                      f"Rs {s['price']:>7.2f}  {s['date'].strftime('%Y-%m-%d')}")
        
        # Tier 2 Signals (Medium Priority)
        tier2_signals = [s for s in buy_signals if s['tier'] == 2]
        if tier2_signals:
            print("\n" + "="*80)
            print("✓ TIER 2 - MEDIUM CONFIDENCE SIGNALS (Consider These)")
            print("="*80)
            print(f"{'Stock':<15} {'Signal':<8} {'Confidence':<12} {'Price':<10} {'Date':<12}")
            print("-"*80)
            
            for s in tier2_signals[:10]:  # Show top 10
                print(f"{s['stock']:<15} {s['signal']:<8} {s['confidence']:>10.1f}% "
                      f"Rs {s['price']:>7.2f}  {s['date'].strftime('%Y-%m-%d')}")
            
            if len(tier2_signals) > 10:
                print(f"  ... and {len(tier2_signals) - 10} more")
        
        # Tier 3 Signals (Low Priority)
        tier3_signals = [s for s in buy_signals if s['tier'] == 3]
        if tier3_signals:
            print("\n" + "="*80)
            print("⚠ TIER 3 - LOW CONFIDENCE SIGNALS (Use Caution)")
            print("="*80)
            print(f"  {len(tier3_signals)} signals (not recommended for VWAP strategy)")
        
        # Recommendations
        print("\n" + "="*80)
        print("📋 RECOMMENDED ACTION PLAN")
        print("="*80)
        
        if tier1_count > 0:
            print(f"\n1. PRIORITY: Focus on {tier1_count} Tier 1 stocks")
            print("   - Run VWAPfilter backtest on these")
            print("   - Pick best 2-3 based on profit potential")
        
        if tier2_count > 0:
            print(f"\n2. SECONDARY: Consider top {min(5, tier2_count)} Tier 2 stocks")
            print("   - If Tier 1 doesn't look good")
            print("   - Or for additional positions")
        
        if tier3_count > 0:
            print(f"\n3. AVOID: Skip {tier3_count} Tier 3 stocks")
            print("   - Low accuracy for VWAP strategy")
            print("   - Stable/low volatility stocks")
        
        print("\n" + "="*80)
    
    def export_to_excel(self, filename='daily_screener_results.xlsx'):
        """Export results to Excel."""
        if not self.results:
            print("No results to export")
            return
        
        # Create DataFrame
        df = pd.DataFrame(self.results)
        
        # Sort by signal (BUY first), then tier, then confidence
        df['signal_rank'] = df['signal'].map({'BUY': 0, 'HOLD': 1})
        df = df.sort_values(['signal_rank', 'tier', 'confidence'], ascending=[True, True, False])
        df = df.drop('signal_rank', axis=1)
        
        # Format columns
        df['confidence'] = df['confidence'].round(1)
        df['buy_proba'] = df['buy_proba'].round(1)
        df['price'] = df['price'].round(2)
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        
        # Rename columns
        df.columns = ['Stock', 'Signal', 'Confidence %', 'Tier', 'Tier Label', 
                     'Price (Rs)', 'Date', 'Buy Probability %']
        
        # Create Excel with formatting
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # All results
            df.to_excel(writer, sheet_name='All Stocks', index=False)
            
            # BUY signals only
            buy_df = df[df['Signal'] == 'BUY'].copy()
            if not buy_df.empty:
                buy_df.to_excel(writer, sheet_name='BUY Signals', index=False)
            
            # By Tier
            for tier in [1, 2, 3]:
                tier_df = df[df['Tier'] == tier].copy()
                if not tier_df.empty:
                    tier_df.to_excel(writer, sheet_name=f'Tier {tier}', index=False)
        
        print(f"\n✓ Results exported to: {filename}")
    
    def run(self, export=True):
        """Run complete screening process."""
        print("\n" + "="*80)
        print("AI STOCK SCREENER - DAILY SCAN")
        print("="*80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Strategy: VWAP Ladder (3% target, 5-day forward)")
        
        # Load models
        if not self.load_models():
            print("Error: No models loaded. Run training first!")
            return False
        
        # Scan stocks
        self.scan_all_stocks()
        
        # Display results
        self.display_results()
        
        # Export to Excel
        if export:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'screener_results_{timestamp}.xlsx'
            self.export_to_excel(filename)
        
        print("\n" + "="*80)
        print("SCAN COMPLETED!")
        print("="*80)
        
        return True


def main():
    """Main function."""
    screener = DailyScreener()
    screener.run(export=True)


if __name__ == '__main__':
    main()

