"""
Single Stock Model Training & Testing
======================================

Train and evaluate XGBoost model on ONE stock with detailed metrics.
Author: AI Screener Team
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
# import matplotlib.pyplot as plt  # Not needed for basic training
# import seaborn as sns  # Not needed for basic training

# Add ai_screener to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

from ai_screener.data_loader import DataLoader
from ai_screener.feature_engineering import FeatureEngineer
from ai_screener.xgboost_trainer import XGBoostTrainer


class SingleStockTrainer:
    """Train and evaluate model on single stock."""
    
    def __init__(self, stock_symbol='NSE_RELIANCE'):
        """
        Initialize trainer for single stock.
        
        Args:
            stock_symbol: Stock symbol to train on
        """
        self.stock_symbol = stock_symbol
        self.loader = DataLoader()
        self.engineer = FeatureEngineer()
        self.trainer = XGBoostTrainer()
        
        self.df_raw = None
        self.df_features = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.feature_names = None
        
    def load_and_prepare_data(self):
        """Load and prepare stock data."""
        print("="*70)
        print(f"LOADING DATA FOR: {self.stock_symbol}")
        print("="*70)
        
        # Load stock data
        self.df_raw = self.loader.load_stock_data(self.stock_symbol)
        
        if self.df_raw is None or len(self.df_raw) == 0:
            raise ValueError(f"No data found for {self.stock_symbol}")
        
        print(f"✓ Loaded {len(self.df_raw)} days of data")
        print(f"  Date range: {self.df_raw['time'].min()} to {self.df_raw['time'].max()}")
        print(f"  Columns: {list(self.df_raw.columns)}")
        
        # Engineer features
        print("\nEngineering features...")
        self.df_features = self.engineer.engineer_features(self.df_raw)
        print(f"✓ Created {len(self.df_features.columns)} features")
        
        # Show sample of engineered features
        feature_cols = [col for col in self.df_features.columns 
                       if col not in ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume']]
        print(f"\nEngineered features ({len(feature_cols)} total):")
        for i, col in enumerate(feature_cols[:10], 1):
            print(f"  {i}. {col}")
        if len(feature_cols) > 10:
            print(f"  ... and {len(feature_cols) - 10} more")
        
        return self.df_features
    
    def create_labels(self, profit_target=0.03, stop_loss=0.015, 
                     forward_days=5, use_vwap_strategy=True):
        """
        Create buy/sell/hold labels.
        
        Args:
            profit_target: Profit target (e.g., 0.03 = 3%)
            stop_loss: Stop loss (e.g., 0.015 = 1.5%)
            forward_days: Days to look forward
            use_vwap_strategy: Use VWAP ladder strategy labeling
        """
        print("\n" + "="*70)
        print("CREATING LABELS")
        print("="*70)
        
        if use_vwap_strategy:
            print(f"Using VWAP Ladder Strategy labeling:")
            print(f"  Profit Target: {profit_target*100}%")
            print(f"  Forward Days: {forward_days}")
            print(f"  Threshold: Rs 5L (500,000)")
            print(f"  Max Investment: Rs 15,000")
            
            labels = self.trainer.create_vwap_ladder_labels(
                self.df_features,
                profit_target=profit_target,
                threshold_amount=500000,
                max_investment=15000,
                forward_days=forward_days
            )
        else:
            print(f"Using simple forward return labeling:")
            print(f"  Profit Target: {profit_target*100}%")
            print(f"  Stop Loss: {stop_loss*100}%")
            print(f"  Forward Days: {forward_days}")
            
            labels = self.trainer.create_labels(
                self.df_features,
                profit_target=profit_target,
                stop_loss=stop_loss,
                forward_days=forward_days
            )
        
        # Analyze label distribution
        unique, counts = np.unique(labels, return_counts=True)
        total = len(labels)
        
        print(f"\n✓ Created {total} labels")
        print(f"\nLabel Distribution:")
        label_names = {-1: 'Sell', 0: 'Hold', 1: 'Buy'}
        for label, count in zip(unique, counts):
            pct = (count / total) * 100
            name = label_names.get(label, f'Class_{label}')
            print(f"  {name:8s}: {count:5d} ({pct:5.2f}%)")
        
        return labels
    
    def split_data(self, train_ratio=0.7):
        """
        Split data into train/test sets (time-based split).
        
        Args:
            train_ratio: Ratio of training data (0.7 = 70% train, 30% test)
        """
        print("\n" + "="*70)
        print("SPLITTING DATA")
        print("="*70)
        
        # Get feature columns
        self.feature_names = self.trainer.get_feature_columns(self.df_features)
        X = self.df_features[self.feature_names]
        
        # Time-based split (important for time series!)
        split_idx = int(len(X) * train_ratio)
        
        self.X_train = X.iloc[:split_idx]
        self.X_test = X.iloc[split_idx:]
        self.y_train = self.y_train[:split_idx]
        self.y_test = self.y_test[split_idx:]
        
        train_dates = self.df_features.iloc[:split_idx]['time']
        test_dates = self.df_features.iloc[split_idx:]['time']
        
        print(f"Train/Test Ratio: {train_ratio:.0%} / {1-train_ratio:.0%}")
        print(f"\nTraining Set:")
        print(f"  Size: {len(self.X_train)} samples")
        print(f"  Date Range: {train_dates.min()} to {train_dates.max()}")
        print(f"  Features: {len(self.feature_names)}")
        
        print(f"\nTest Set:")
        print(f"  Size: {len(self.X_test)} samples")
        print(f"  Date Range: {test_dates.min()} to {test_dates.max()}")
        
        # Show label distribution in train/test
        print(f"\nTrain Label Distribution:")
        unique, counts = np.unique(self.y_train, return_counts=True)
        for label, count in zip(unique, counts):
            pct = (count / len(self.y_train)) * 100
            label_names = {-1: 'Sell', 0: 'Hold', 1: 'Buy'}
            print(f"  {label_names.get(label, f'Class_{label}'):8s}: {count:5d} ({pct:5.2f}%)")
        
        print(f"\nTest Label Distribution:")
        unique, counts = np.unique(self.y_test, return_counts=True)
        for label, count in zip(unique, counts):
            pct = (count / len(self.y_test)) * 100
            label_names = {-1: 'Sell', 0: 'Hold', 1: 'Buy'}
            print(f"  {label_names.get(label, f'Class_{label}'):8s}: {count:5d} ({pct:5.2f}%)")
    
    def train_model(self, tune_hyperparameters=False, cv_folds=3):
        """
        Train XGBoost model.
        
        Args:
            tune_hyperparameters: Whether to tune hyperparameters (slower but better)
            cv_folds: Number of cross-validation folds
        """
        print("\n" + "="*70)
        print("TRAINING MODEL")
        print("="*70)
        
        if tune_hyperparameters:
            print("Mode: HYPERPARAMETER TUNING (this will take time...)")
        else:
            print("Mode: QUICK TRAINING (default parameters)")
        
        # Train
        results = self.trainer.train(
            self.X_train, 
            self.y_train,
            tune_hyperparameters=tune_hyperparameters,
            cv_folds=cv_folds
        )
        
        if tune_hyperparameters and results['best_params']:
            print(f"\n✓ Best Parameters Found:")
            for param, value in results['best_params'].items():
                print(f"    {param}: {value}")
            print(f"\n  Best CV Score: {results['best_score']:.4f}")
        else:
            print(f"\n✓ Model trained with default parameters")
        
        return results
    
    def evaluate_model(self):
        """Evaluate model on test set."""
        print("\n" + "="*70)
        print("EVALUATING MODEL ON TEST SET")
        print("="*70)
        
        # Get predictions
        results = self.trainer.evaluate(self.X_test, self.y_test)
        
        print(f"\nOverall Metrics:")
        print(f"  Accuracy:  {results['accuracy']:.4f} ({results['accuracy']*100:.2f}%)")
        print(f"  F1 Score:  {results['f1_macro']:.4f}")
        
        print(f"\nPer-Class Performance:")
        print(f"  {'Class':<8s} {'Precision':<12s} {'Recall':<12s} {'F1-Score':<12s} {'Support':<10s}")
        print(f"  {'-'*8} {'-'*12} {'-'*12} {'-'*12} {'-'*10}")
        
        class_names = ['Sell', 'Hold', 'Buy']
        for i, class_name in enumerate(class_names):
            class_key = class_name.lower()
            if class_key in results['classification_report']:
                metrics = results['classification_report'][class_key]
                print(f"  {class_name:<8s} "
                      f"{metrics['precision']:>11.4f} "
                      f"{metrics['recall']:>11.4f} "
                      f"{metrics['f1-score']:>11.4f} "
                      f"{int(metrics['support']):>9d}")
        
        print(f"\nConfusion Matrix:")
        print(f"  Actual →    Sell  Hold   Buy")
        cm = np.array(results['confusion_matrix'])
        for i, class_name in enumerate(class_names):
            print(f"  {class_name:<8s} {cm[i][0]:>6d} {cm[i][1]:>6d} {cm[i][2]:>6d}")
        
        return results
    
    def show_feature_importance(self, top_n=20):
        """Show top N most important features."""
        print("\n" + "="*70)
        print(f"TOP {top_n} MOST IMPORTANT FEATURES")
        print("="*70)
        
        importance_df = self.trainer.get_feature_importance(self.feature_names)
        
        print(f"\n  {'Rank':<6s} {'Feature':<40s} {'Importance':<12s}")
        print(f"  {'-'*6} {'-'*40} {'-'*12}")
        
        for idx, row in importance_df.head(top_n).iterrows():
            rank = idx + 1
            print(f"  {rank:<6d} {row['feature']:<40s} {row['importance']:>11.4f}")
        
        return importance_df
    
    def save_model(self, output_dir='ai_screener/models'):
        """Save trained model."""
        print("\n" + "="*70)
        print("SAVING MODEL")
        print("="*70)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save model
        model_filename = f"xgb_{self.stock_symbol}.pkl"
        model_path = os.path.join(output_dir, model_filename)
        
        self.trainer.save_model(model_path)
        print(f"✓ Model saved: {model_path}")
        
        return model_path
    
    def run_full_pipeline(self, profit_target=0.03, forward_days=5, 
                         use_vwap_strategy=True, tune_hyperparameters=False,
                         train_ratio=0.7, save_model=True):
        """
        Run complete training pipeline.
        
        Args:
            profit_target: Profit target percentage
            forward_days: Days to look forward
            use_vwap_strategy: Use VWAP ladder strategy
            tune_hyperparameters: Tune hyperparameters (slower)
            train_ratio: Training data ratio
            save_model: Whether to save the model
        """
        print("\n" + "="*70)
        print(f"TRAINING PIPELINE FOR: {self.stock_symbol}")
        print("="*70)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = datetime.now()
        
        try:
            # Step 1: Load and prepare data
            self.load_and_prepare_data()
            
            # Step 2: Create labels
            self.y_train = self.create_labels(
                profit_target=profit_target,
                forward_days=forward_days,
                use_vwap_strategy=use_vwap_strategy
            )
            self.y_test = self.y_train.copy()  # Will be split later
            
            # Step 3: Split data
            self.split_data(train_ratio=train_ratio)
            
            # Step 4: Train model
            self.train_model(tune_hyperparameters=tune_hyperparameters)
            
            # Step 5: Evaluate
            results = self.evaluate_model()
            
            # Step 6: Feature importance
            self.show_feature_importance(top_n=20)
            
            # Step 7: Save model
            if save_model:
                model_path = self.save_model()
            
            # Summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("\n" + "="*70)
            print("TRAINING COMPLETED SUCCESSFULLY!")
            print("="*70)
            print(f"Duration: {duration:.1f} seconds")
            print(f"Accuracy: {results['accuracy']:.4f} ({results['accuracy']*100:.2f}%)")
            print(f"F1 Score: {results['f1_macro']:.4f}")
            print("="*70)
            
            return {
                'success': True,
                'accuracy': results['accuracy'],
                'f1_score': results['f1_macro'],
                'duration': duration
            }
            
        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}


def main():
    """Main training function."""
    print("\n" + "="*70)
    print("AI SCREENER - SINGLE STOCK TRAINING")
    print("="*70)
    
    # Get stock symbol from user
    print("\nAvailable stocks in data folder:")
    loader = DataLoader()
    stocks = loader.get_all_stocks()
    
    print("\nTop 10 stocks:")
    for i, stock in enumerate(stocks[:10], 1):
        print(f"  {i}. {stock}")
    if len(stocks) > 10:
        print(f"  ... and {len(stocks) - 10} more")
    
    print(f"\nDefault: RELIANCE (NSE_RELIANCE)")
    stock_input = input("Enter stock symbol (or press Enter for RELIANCE): ").strip()
    
    if not stock_input:
        stock_symbol = 'NSE_RELIANCE'
    else:
        stock_symbol = stock_input if stock_input.startswith('NSE_') else f'NSE_{stock_input}'
    
    print(f"\n✓ Selected: {stock_symbol}")
    
    # Training configuration
    print("\n" + "="*70)
    print("TRAINING CONFIGURATION")
    print("="*70)
    
    profit_target = 0.03  # 3%
    forward_days = 5
    use_vwap_strategy = True
    tune_hyperparameters = False  # Set to True for better accuracy (slower)
    
    print(f"  Profit Target: {profit_target*100}%")
    print(f"  Forward Days: {forward_days}")
    print(f"  Strategy: {'VWAP Ladder' if use_vwap_strategy else 'Simple Forward Return'}")
    print(f"  Hyperparameter Tuning: {'Enabled (SLOW)' if tune_hyperparameters else 'Disabled (FAST)'}")
    print(f"  Train/Test Split: 70% / 30%")
    
    confirm = input("\nProceed with training? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Training cancelled.")
        return
    
    # Run training
    trainer = SingleStockTrainer(stock_symbol=stock_symbol)
    results = trainer.run_full_pipeline(
        profit_target=profit_target,
        forward_days=forward_days,
        use_vwap_strategy=use_vwap_strategy,
        tune_hyperparameters=tune_hyperparameters,
        save_model=True
    )
    
    if results['success']:
        print(f"\n✓✓✓ Training successful!")
        print(f"\nNext steps:")
        print(f"  1. Check if accuracy ({results['accuracy']*100:.2f}%) is satisfactory")
        print(f"  2. If not, try tuning hyperparameters or adjusting parameters")
        print(f"  3. Once satisfied, train all stocks using same settings")
    else:
        print(f"\n✗ Training failed: {results.get('error', 'Unknown error')}")


if __name__ == '__main__':
    main()

