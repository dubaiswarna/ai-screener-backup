"""
Single Commodity Trainer - Adapted for MCX Gold/Silver
========================================================
Train AI models on individual commodities (Gold, Silver, etc.)
"""

import pandas as pd
import numpy as np
import time
from pathlib import Path
from typing import Dict, Optional
import warnings
warnings.filterwarnings('ignore')

# Import existing modules
from data_loader import DataLoader
from feature_engineering import FeatureEngineer
from xgboost_trainer import XGBoostTrainer


class CommodityDataLoader(DataLoader):
    """Modified data loader for commodities."""
    
    def __init__(self, data_dir: str = "Commodity_data"):
        """Initialize with Commodity_data directory."""
        super().__init__(data_dir)
    
    def get_all_commodities(self):
        """Get list of all commodities from CSV filenames."""
        csv_files = list(self.data_dir.glob("MCX_*.csv"))
        commodities = []
        for file in csv_files:
            # Extract symbol from filename like "MCX_GOLD, 1D.csv"
            symbol = file.stem.split(",")[0]
            commodities.append(symbol)
        return sorted(commodities)
    
    def load_commodity_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Load data for a single commodity."""
        return self.load_stock_data(symbol)


class SingleCommodityTrainer:
    """Train AI model on a single commodity."""
    
    def __init__(self, commodity_symbol: str):
        """
        Initialize trainer for a specific commodity.
        
        Args:
            commodity_symbol: Commodity symbol (e.g., 'MCX_GOLD', 'MCX_SILVER')
        """
        self.commodity_symbol = commodity_symbol
        self.data_loader = CommodityDataLoader()
        self.feature_engineer = FeatureEngineer()
        self.trainer = XGBoostTrainer()
        self.raw_data = None
        self.features_df = None
        
    def load_data(self) -> bool:
        """Load commodity data."""
        print(f"\n📊 Loading data for {self.commodity_symbol}...")
        self.raw_data = self.data_loader.load_commodity_data(self.commodity_symbol)
        
        if self.raw_data is None or len(self.raw_data) < 100:
            print(f"❌ Insufficient data for {self.commodity_symbol}")
            return False
        
        print(f"✓ Loaded {len(self.raw_data)} data points")
        return True
    
    def engineer_features(self) -> bool:
        """Generate technical indicators and features."""
        print("\n🔧 Engineering features...")
        
        try:
            self.features_df = self.feature_engineer.add_all_features(
                self.raw_data.copy()
            )
            
            if self.features_df is None or self.features_df.empty:
                print("❌ Feature engineering failed")
                return False
            
            print(f"✓ Generated {len(self.features_df.columns)} features")
            return True
            
        except Exception as e:
            print(f"❌ Error in feature engineering: {e}")
            return False
    
    def create_labels(self, profit_target: float = 0.03, forward_days: int = 5) -> bool:
        """
        Create binary labels for buy signals.
        
        Args:
            profit_target: Target profit percentage (e.g., 0.03 = 3%)
            forward_days: Days to look ahead for profit
        """
        print(f"\n🎯 Creating labels (Target: {profit_target*100}%, Forward: {forward_days} days)...")
        
        try:
            close_prices = self.features_df['close'].values
            labels = []
            
            for i in range(len(close_prices)):
                # Look ahead up to forward_days
                if i + forward_days < len(close_prices):
                    future_prices = close_prices[i+1:i+forward_days+1]
                    max_future_price = np.max(future_prices)
                    
                    # Check if profit target is reached
                    profit = (max_future_price - close_prices[i]) / close_prices[i]
                    label = 1 if profit >= profit_target else 0
                else:
                    label = 0  # Not enough future data
                
                labels.append(label)
            
            self.features_df['target'] = labels
            
            buy_signals = sum(labels)
            buy_pct = (buy_signals / len(labels)) * 100
            
            print(f"✓ Created {len(labels)} labels")
            print(f"  Buy signals: {buy_signals} ({buy_pct:.1f}%)")
            print(f"  Hold signals: {len(labels) - buy_signals} ({100-buy_pct:.1f}%)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating labels: {e}")
            return False
    
    def train_model(self, train_ratio: float = 0.7, 
                   tune_hyperparameters: bool = False) -> Dict:
        """
        Train XGBoost model.
        
        Args:
            train_ratio: Train/test split ratio
            tune_hyperparameters: Whether to tune hyperparameters
        """
        print(f"\n🤖 Training XGBoost model...")
        print(f"  Train ratio: {train_ratio*100}%")
        print(f"  Hyperparameter tuning: {'ON' if tune_hyperparameters else 'OFF'}")
        
        try:
            # Prepare features (exclude non-feature columns)
            exclude_cols = ['time', 'target', 'open', 'high', 'low', 'close', 'volume', 'vwap']
            feature_cols = [col for col in self.features_df.columns 
                          if col not in exclude_cols]
            
            X = self.features_df[feature_cols].values
            y = self.features_df['target'].values
            
            # Split train/test
            split_idx = int(len(X) * train_ratio)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            print(f"  Train samples: {len(X_train)}")
            print(f"  Test samples: {len(X_test)}")
            
            # Train model
            start_time = time.time()
            
            if tune_hyperparameters:
                results = self.trainer.train_with_tuning(
                    X_train, y_train, X_test, y_test
                )
            else:
                results = self.trainer.train(
                    X_train, y_train, X_test, y_test
                )
            
            duration = time.time() - start_time
            results['duration'] = duration
            
            if results['success']:
                print(f"\n✓ Training completed in {duration:.1f} seconds")
                print(f"  Accuracy: {results['accuracy']*100:.2f}%")
                print(f"  F1 Score: {results['f1_score']:.4f}")
            else:
                print(f"\n❌ Training failed: {results.get('error')}")
            
            return results
            
        except Exception as e:
            print(f"❌ Training error: {e}")
            return {'success': False, 'error': str(e)}
    
    def save_model(self) -> str:
        """Save trained model to disk."""
        print("\n💾 Saving model...")
        
        # Create models directory if not exists
        models_dir = Path("ai_screener/models")
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model
        model_path = models_dir / f"{self.commodity_symbol}_model.pkl"
        self.trainer.save_model(str(model_path))
        
        print(f"✓ Model saved: {model_path}")
        return str(model_path)
    
    def run_full_pipeline(self, 
                         profit_target: float = 0.03,
                         forward_days: int = 5,
                         use_vwap_strategy: bool = True,
                         tune_hyperparameters: bool = False,
                         train_ratio: float = 0.7,
                         save_model: bool = True) -> Dict:
        """
        Run complete training pipeline.
        
        Args:
            profit_target: Target profit percentage
            forward_days: Days to look ahead
            use_vwap_strategy: Use VWAP-based strategy
            tune_hyperparameters: Tune hyperparameters
            train_ratio: Train/test split
            save_model: Save model after training
        
        Returns:
            Dictionary with results
        """
        print("\n" + "=" * 70)
        print(f"TRAINING PIPELINE: {self.commodity_symbol}")
        print("=" * 70)
        
        start_time = time.time()
        
        # Step 1: Load data
        if not self.load_data():
            return {'success': False, 'error': 'Data loading failed'}
        
        # Step 2: Engineer features
        if not self.engineer_features():
            return {'success': False, 'error': 'Feature engineering failed'}
        
        # Step 3: Create labels
        if not self.create_labels(profit_target, forward_days):
            return {'success': False, 'error': 'Label creation failed'}
        
        # Step 4: Train model
        results = self.train_model(train_ratio, tune_hyperparameters)
        
        if not results['success']:
            return results
        
        # Step 5: Save model
        if save_model:
            model_path = self.save_model()
            results['model_path'] = model_path
        
        # Add total duration
        total_duration = time.time() - start_time
        results['total_duration'] = total_duration
        
        print("\n" + "=" * 70)
        print("PIPELINE COMPLETED")
        print("=" * 70)
        
        return results


if __name__ == '__main__':
    # Test with Gold
    print("Testing with MCX GOLD...")
    trainer = SingleCommodityTrainer(commodity_symbol='MCX_GOLD')
    results = trainer.run_full_pipeline(
        profit_target=0.03,
        forward_days=5,
        tune_hyperparameters=False,
        save_model=True
    )
    
    print("\nFinal Results:")
    print(results)

