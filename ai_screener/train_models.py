"""
Model Training Pipeline
=======================

Train CNN-LSTM and XGBoost models on all stocks.
"""

import os
import yaml
import numpy as np
import pandas as pd
from typing import Dict, List
from datetime import datetime

from data_loader import DataLoader
from feature_engineering import FeatureEngineer

try:
    from xgboost_trainer import XGBoostTrainer
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("Warning: XGBoost not available. Only CNN-LSTM can be trained.")

try:
    from cnn_lstm_model import CNNLSTMModel
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("Warning: TensorFlow not available. Only XGBoost can be trained.")


class ModelTrainer:
    """Train models on all stocks."""
    
    def __init__(self, config_file: str = "config.yaml", use_vwap_strategy: bool = True):
        """
        Initialize model trainer.
        
        Args:
            config_file: Path to configuration file
            use_vwap_strategy: If True, train models with VWAP ladder strategy labels
        """
        self.config = self._load_config(config_file)
        self.loader = DataLoader(data_dir=self.config['data']['data_dir'])
        self.engineer = FeatureEngineer()
        self.use_vwap_strategy = use_vwap_strategy
        
        self.xgb_trainer = XGBoostTrainer() if XGBOOST_AVAILABLE else None
        self.cnn_lstm_model = None  # Will be created per stock or globally
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from YAML file."""
        from pathlib import Path
        
        # Try current directory first, then ai_screener directory
        config_path = Path(config_file)
        if not config_path.exists():
            config_path = Path(__file__).parent / config_file
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config if config else {}
    
    def load_and_prepare_data(self):
        """Load and prepare data for all stocks."""
        print("Loading data for all stocks...")
        self.loader.load_all_stocks()
        
        print("Engineering features...")
        self.featured_data = {}
        for symbol, df in self.loader.stock_data.items():
            df_features = self.engineer.engineer_features(df)
            self.featured_data[symbol] = df_features
        
        print(f"Prepared data for {len(self.featured_data)} stocks.")
        
    def create_labels(self, df: pd.DataFrame, use_vwap_strategy: bool = True) -> np.ndarray:
        """
        Create buy/sell/hold labels.
        
        Args:
            df: DataFrame with features
            use_vwap_strategy: If True, use VWAP ladder strategy labels
            
        Returns:
            Array of labels
        """
        profit_target = self.config['trading']['profit_target']
        stop_loss = self.config['trading']['stop_loss']
        forward_days = self.config['trading']['forward_days']
        
        if self.xgb_trainer:
            if use_vwap_strategy and hasattr(self.xgb_trainer, 'create_vwap_ladder_labels'):
                # Use VWAP ladder strategy labels
                return self.xgb_trainer.create_vwap_ladder_labels(
                    df, 
                    profit_target=profit_target,
                    threshold_amount=500000,  # 5L threshold
                    max_investment=15000,     # 15K max investment
                    forward_days=forward_days
                )
            else:
                # Use simple return-based labels
                return self.xgb_trainer.create_labels(df, profit_target, stop_loss, forward_days)
        else:
            # Fallback label creation
            labels = []
            for i in range(len(df)):
                if i + forward_days >= len(df):
                    labels.append(0)  # hold
                    continue
                
                current_price = df.iloc[i]['close']
                future_price = df.iloc[i + forward_days]['close']
                return_pct = (future_price - current_price) / current_price
                
                if return_pct >= profit_target:
                    labels.append(1)  # buy
                elif return_pct <= -stop_loss:
                    labels.append(-1)  # sell
                else:
                    labels.append(0)  # hold
            
            return np.array(labels)
    
    def split_data(self, df: pd.DataFrame, y: np.ndarray):
        """
        Split data into train/val/test sets (time-based).
        
        Args:
            df: Feature DataFrame
            y: Labels array
            
        Returns:
            Tuple of (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        train_split = self.config['data']['train_split']
        val_split = self.config['data']['val_split']
        
        n_total = len(df)
        n_train = int(n_total * train_split)
        n_val = int(n_total * val_split)
        
        # Split indices
        train_end = n_train
        val_end = n_train + n_val
        
        # Get feature columns
        feature_cols = self.engineer.get_feature_names()
        
        # Split
        X_train = df[feature_cols].iloc[:train_end]
        X_val = df[feature_cols].iloc[train_end:val_end]
        X_test = df[feature_cols].iloc[val_end:]
        
        y_train = y[:train_end]
        y_val = y[train_end:val_end]
        y_test = y[val_end:]
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def train_xgboost(self, symbol: str, save_model: bool = True):
        """
        Train XGBoost model for a stock.
        
        Args:
            symbol: Stock symbol
            save_model: Whether to save the model
        """
        if not XGBOOST_AVAILABLE:
            print(f"XGBoost not available. Skipping {symbol}.")
            return None
        
        print(f"\nTraining XGBoost for {symbol}...")
        
        df = self.featured_data[symbol]
        
        # Create labels using VWAP strategy if enabled
        y = self.create_labels(df, use_vwap_strategy=self.use_vwap_strategy)
        
        # Remove samples with insufficient forward data
        n_remove = self.config['trading']['forward_days']
        df = df.iloc[:-n_remove] if n_remove > 0 else df
        y = y[:-n_remove] if n_remove > 0 else y
        
        # Split data
        X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(df, y)
        
        # Train
        train_results = self.xgb_trainer.train(
            X_train, y_train,
            tune_hyperparameters=False  # Set to True for full tuning
        )
        
        # Evaluate
        print("Evaluating on validation set...")
        val_results = self.xgb_trainer.evaluate(X_val, y_val)
        
        print(f"Validation Accuracy: {val_results['accuracy']:.4f}")
        print(f"Validation F1 Score: {val_results['f1_macro']:.4f}")
        
        # Save model
        if save_model:
            os.makedirs("models", exist_ok=True)
            model_path = f"models/xgb_{symbol}.pkl"
            self.xgb_trainer.save_model(model_path)
        
        return {
            'model': self.xgb_trainer.model,
            'val_accuracy': val_results['accuracy'],
            'val_f1': val_results['f1_macro']
        }
    
    def train_all_models(self, save_models: bool = True):
        """
        Train models for all stocks.
        
        Args:
            save_models: Whether to save trained models
        """
        if not hasattr(self, 'featured_data'):
            self.load_and_prepare_data()
        
        print("\n" + "=" * 80)
        print("TRAINING MODELS FOR ALL STOCKS")
        print("=" * 80)
        
        results = {}
        
        for i, symbol in enumerate(self.featured_data.keys(), 1):
            print(f"\n[{i}/{len(self.featured_data)}] Processing {symbol}...")
            
            try:
                if XGBOOST_AVAILABLE:
                    result = self.train_xgboost(symbol, save_models)
                    if result:
                        results[symbol] = result
                    
                # Add CNN-LSTM training here if needed
                
            except Exception as e:
                print(f"Error training {symbol}: {e}")
                continue
        
        print("\n" + "=" * 80)
        print("TRAINING COMPLETE")
        print("=" * 80)
        
        # Summary
        if results:
            print(f"\nSuccessfully trained models for {len(results)} stocks")
            avg_accuracy = np.mean([r['val_accuracy'] for r in results.values()])
            print(f"Average validation accuracy: {avg_accuracy:.4f}")
        
        return results


def main():
    """Main training function."""
    from pathlib import Path
    
    print("AI Stock Screener - Model Training Pipeline (VWAP Strategy)")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Get config path
    config_file = Path(__file__).parent / "config.yaml"
    
    # Initialize trainer with VWAP strategy enabled
    trainer = ModelTrainer(config_file=str(config_file), use_vwap_strategy=True)
    
    # Train all models
    results = trainer.train_all_models(save_models=True)
    
    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == '__main__':
    main()

