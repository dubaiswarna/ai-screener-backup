"""
XGBoost Model Trainer
=====================

Trains XGBoost classifier with engineered features for trading signals.
"""

import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import joblib
import os
from typing import Dict, List, Tuple


class XGBoostTrainer:
    """XGBoost classifier for stock trading signals."""
    
    def __init__(self, n_classes: int = 3, random_state: int = 42):
        """
        Initialize XGBoost trainer.
        
        Args:
            n_classes: Number of classes (buy, hold, sell)
            random_state: Random seed for reproducibility
        """
        self.n_classes = n_classes
        self.random_state = random_state
        self.model = None
        self.best_params = None
        self.feature_importance = None
        
    def create_labels(self, df: pd.DataFrame, profit_target: float = 0.03, 
                     stop_loss: float = 0.015, forward_days: int = 1) -> np.ndarray:
        """
        Create buy/sell/hold labels based on forward returns.
        
        Args:
            df: DataFrame with price data
            profit_target: Profit target threshold (e.g., 0.03 = 3%)
            stop_loss: Stop loss threshold (e.g., 0.015 = 1.5%)
            forward_days: Number of days forward to check
            
        Returns:
            Array of labels (1=buy, 0=hold, -1=sell)
        """
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
    
    def create_vwap_ladder_labels(self, df: pd.DataFrame, profit_target: float = 0.03, 
                                  threshold_amount: float = 500000, max_investment: float = 15000,
                                  forward_days: int = 5) -> np.ndarray:
        """
        Create labels based on VWAP Ladder Strategy logic.
        Labels indicate whether a buy signal would be profitable.
        
        Args:
            df: DataFrame with price data (must have: high, low, vwap, close)
            profit_target: Profit target threshold (e.g., 0.03 = 3%)
            threshold_amount: Maximum investment threshold (e.g., 500000 = 5L)
            max_investment: Max investment per day for all 4 orders
            forward_days: Number of days forward to check for target
            
        Returns:
            Array of labels (1=buy signal profitable, 0=no signal/hold)
        """
        labels = []
        n = len(df)
        
        # VWAP strategy parameters
        r_low_discount = 0.01  # 1% discount from Low
        r_vwap_discount = 0.01  # 1% discount from VWAP
        total_charges = 0.01  # 1% total (0.7% charges + 0.3% brokerage)
        
        for i in range(n - 1):
            if i + forward_days >= n:
                labels.append(0)
                continue
            
            # Get current day data
            current_day = df.iloc[i]
            current_low = current_day['low']
            current_vwap = current_day['vwap']
            
            # Calculate entry levels for TODAY (would be set based on previous day)
            e1_price = current_low
            e2_price = current_low * (1 - r_low_discount)
            e3_price = current_vwap
            e4_price = current_vwap * (1 - r_vwap_discount)
            
            # Calculate dynamic quantity
            total_entry_price = e1_price + e2_price + e3_price + e4_price
            calculated_qty = max(1, int(max_investment / total_entry_price))
            
            # Check which orders would get filled (check if next day's low hits entry price)
            next_day = df.iloc[i + 1]
            next_low = next_day['low']
            
            filled_orders = []
            for price in [e1_price, e2_price, e3_price, e4_price]:
                if next_low <= price:
                    filled_orders.append(price)
            
            # If no orders filled, no signal
            if not filled_orders:
                labels.append(0)
                continue
            
            # Calculate average entry price and total cost (with charges)
            avg_entry_price = np.mean(filled_orders)
            total_shares = calculated_qty * len(filled_orders)
            total_value = sum(price * calculated_qty for price in filled_orders)
            total_cost_with_charges = total_value * (1 + total_charges)
            avg_cost = total_cost_with_charges / total_shares
            
            # Determine target price based on investment amount
            if total_cost_with_charges <= threshold_amount:
                target_price = avg_cost * (1 + profit_target)
            else:
                target_price = avg_cost  # Breakeven if above threshold
            
            # Check if target is hit in forward days
            future_highs = df.iloc[i+1:i+1+forward_days]['high'].values
            max_future_high = np.max(future_highs) if len(future_highs) > 0 else 0
            
            if max_future_high >= target_price:
                labels.append(1)  # Profitable buy signal
            else:
                labels.append(0)  # No profitable signal
        
        # Last day
        labels.append(0)
        
        return np.array(labels)
    
    def get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of engineered feature columns.
        
        Args:
            df: DataFrame with features
            
        Returns:
            List of feature column names
        """
        # Exclude non-feature columns
        exclude_cols = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume']
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Only numeric features
        feature_cols = [col for col in feature_cols if df[col].dtype in [np.int64, np.float64]]
        
        return feature_cols
    
    def train(self, X: pd.DataFrame, y: np.ndarray, 
              tune_hyperparameters: bool = True,
              cv_folds: int = 3) -> Dict:
        """
        Train XGBoost model with optional hyperparameter tuning.
        
        Args:
            X: Training features
            y: Training labels
            tune_hyperparameters: Whether to perform grid search
            cv_folds: Number of cross-validation folds
            
        Returns:
            Training results dictionary
        """
        # Convert X to numpy if DataFrame
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        # Map labels to 0, 1, 2 for XGBoost (original: -1, 0, 1)
        y_mapped = y + 1  # -1 -> 0, 0 -> 1, 1 -> 2
        
        if tune_hyperparameters:
            # Hyperparameter grid
            param_grid = {
                'max_depth': [3, 5, 7],
                'n_estimators': [100, 200, 300],
                'learning_rate': [0.05, 0.1, 0.15],
                'subsample': [0.8, 0.9, 1.0],
                'colsample_bytree': [0.8, 0.9, 1.0]
            }
            
            # Use TimeSeriesSplit for time series data
            tscv = TimeSeriesSplit(n_splits=cv_folds)
            
            # Base model
            base_model = XGBClassifier(
                objective='multi:softprob',
                num_class=self.n_classes,
                eval_metric='mlogloss',
                random_state=self.random_state,
                use_label_encoder=False
            )
            
            # Grid search
            print("Tuning hyperparameters...")
            grid_search = GridSearchCV(
                estimator=base_model,
                param_grid=param_grid,
                cv=tscv,
                scoring='f1_macro',
                n_jobs=-1,
                verbose=1
            )
            
            grid_search.fit(X, y_mapped)
            
            self.model = grid_search.best_estimator_
            self.best_params = grid_search.best_params_
            
            print(f"\nBest parameters: {self.best_params}")
            print(f"Best CV score: {grid_search.best_score_:.4f}")
        
        else:
            # Train with default parameters
            self.model = XGBClassifier(
                max_depth=5,
                n_estimators=200,
                learning_rate=0.1,
                objective='multi:softprob',
                num_class=self.n_classes,
                eval_metric='mlogloss',
                random_state=self.random_state,
                use_label_encoder=False
            )
            
            self.model.fit(X, y_mapped)
        
        # Get feature importance
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = self.model.feature_importances_
        
        return {
            'best_params': self.best_params,
            'best_score': grid_search.best_score_ if tune_hyperparameters else None
        }
    
    def evaluate(self, X: pd.DataFrame, y: np.ndarray) -> Dict:
        """
        Evaluate model performance.
        
        Args:
            X: Test features
            y: Test labels (true labels: -1, 0, 1)
            
        Returns:
            Evaluation metrics dictionary
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Convert X to numpy if DataFrame
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        # Map labels
        y_mapped = y + 1
        
        # Predictions
        y_pred = self.model.predict(X)
        
        # Map back to original labels
        y_pred_original = y_pred - 1
        
        # Metrics
        accuracy = accuracy_score(y, y_pred_original)
        f1 = f1_score(y, y_pred_original, average='macro', zero_division=0)
        
        # Classification report
        class_names = ['Sell', 'Hold', 'Buy']
        report = classification_report(y, y_pred_original, 
                                      target_names=class_names, 
                                      output_dict=True,
                                      zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y, y_pred_original, labels=[-1, 0, 1])
        
        results = {
            'accuracy': accuracy,
            'f1_macro': f1,
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'predicted_classes': y_pred_original.tolist()
        }
        
        return results
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Get prediction probabilities.
        
        Args:
            X: Input features
            
        Returns:
            Probabilities for each class [sell, hold, buy]
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        proba = self.model.predict_proba(X)
        return proba
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict class labels.
        
        Args:
            X: Input features
            
        Returns:
            Predicted classes (-1=sell, 0=hold, 1=buy)
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        y_pred = self.model.predict(X)
        # Map back to original labels
        y_pred_original = y_pred - 1
        return y_pred_original
    
    def get_feature_importance(self, feature_names: List[str] = None) -> pd.DataFrame:
        """
        Get feature importance scores.
        
        Args:
            feature_names: Optional list of feature names
            
        Returns:
            DataFrame with feature importance
        """
        if self.feature_importance is None:
            raise ValueError("No feature importance available.")
        
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(len(self.feature_importance))]
        
        df_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': self.feature_importance
        }).sort_values('importance', ascending=False)
        
        return df_importance
    
    def save_model(self, filepath: str):
        """
        Save trained model to file.
        
        Args:
            filepath: Path to save model
        """
        if self.model is None:
            raise ValueError("No model to save.")
        
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        joblib.dump(self.model, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """
        Load trained model from file.
        
        Args:
            filepath: Path to saved model
        """
        self.model = joblib.load(filepath)
        print(f"Model loaded from {filepath}")


if __name__ == '__main__':
    print("Testing XGBoost Trainer")
    print("=" * 60)
    
    # Create dummy data
    from data_loader import DataLoader
    from feature_engineering import FeatureEngineer
    
    loader = DataLoader()  # Uses default Nify50_data
    stocks = loader.get_all_stocks()
    
    if stocks:
        # Load one stock
        df = loader.load_stock_data(stocks[0])
        
        # Engineer features
        engineer = FeatureEngineer()
        df_features = engineer.engineer_features(df)
        
        # Prepare data
        X = df_features[[col for col in df_features.columns if col not in ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume']]]
        
        # Create labels
        trainer = XGBoostTrainer()
        y = trainer.create_labels(df_features, profit_target=0.03, stop_loss=0.015)
        
        print(f"\nData shape: X={X.shape}, y={y.shape}")
        print(f"Label distribution: {np.bincount(y + 1)}")
        
        # Split data (time-based)
        split_idx = int(len(X) * 0.7)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        print(f"\nTraining data: {len(X_train)} samples")
        print(f"Test data: {len(X_test)} samples")
        
        # Train (without hyperparameter tuning for speed)
        print("\nTraining model...")
        trainer.train(X_train, y_train, tune_hyperparameters=False)
        
        # Evaluate
        print("\nEvaluating...")
        results = trainer.evaluate(X_test, y_test)
        
        print(f"\nAccuracy: {results['accuracy']:.4f}")
        print(f"F1 Score: {results['f1_macro']:.4f}")
        
        # Feature importance
        feature_names = X.columns.tolist()
        importance_df = trainer.get_feature_importance(feature_names)
        print(f"\nTop 10 Most Important Features:")
        print(importance_df.head(10))

