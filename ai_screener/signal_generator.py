"""
Signal Generator with Ensemble Logic
====================================

Combines CNN-LSTM and XGBoost predictions with ensemble weighting.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import os


class SignalGenerator:
    """Generate trading signals using ensemble of models."""
    
    def __init__(self, config: Dict, data_dir: str = None, models_dir: str = None):
        """
        Initialize signal generator.
        
        Args:
            config: Configuration dictionary
            data_dir: Optional data directory path
            models_dir: Optional models directory path
        """
        self.config = config
        self.data_dir = data_dir or config.get('data_dir', 'Nify50_data')
        self.models_dir = models_dir or config.get('models_dir', 'models')
        self.cnn_lstm_models = {}
        self.xgb_models = {}
        
    def load_model(self, symbol: str, model_type: str = 'xgboost'):
        """
        Load trained model for a stock.
        
        Args:
            symbol: Stock symbol
            model_type: 'xgboost' or 'cnn_lstm'
        """
        if model_type == 'xgboost':
            try:
                from xgboost_trainer import XGBoostTrainer
                trainer = XGBoostTrainer()
                model_path = os.path.join(self.models_dir, f"xgb_{symbol}.pkl")
                if os.path.exists(model_path):
                    trainer.load_model(model_path)
                    self.xgb_models[symbol] = trainer
                    print(f"✅ Loaded model for {symbol}")
                    return True
                else:
                    print(f"⚠️ Model file not found: {model_path}")
            except Exception as e:
                print(f"❌ Could not load XGBoost model for {symbol}: {e}")
                import traceback
                traceback.print_exc()
        
        elif model_type == 'cnn_lstm':
            try:
                from cnn_lstm_model import CNNLSTMModel
                model = CNNLSTMModel()
                model_path = os.path.join(self.models_dir, f"cnn_lstm_{symbol}.h5")
                if os.path.exists(model_path):
                    model.load_model(model_path)
                    self.cnn_lstm_models[symbol] = model
                    return True
            except Exception as e:
                print(f"Could not load CNN-LSTM model for {symbol}: {e}")
        
        return False
    
    def predict_cnn_lstm(self, symbol: str, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get CNN-LSTM predictions.
        
        Args:
            symbol: Stock symbol
            X: Input features
            
        Returns:
            Tuple of (probabilities, predicted_classes)
        """
        if symbol not in self.cnn_lstm_models:
            return None, None
        
        model = self.cnn_lstm_models[symbol]
        
        # Prepare data for CNN-LSTM (need raw OHLCV)
        # This would require converting features back to sequences
        # For now, return None if not available
        
        return None, None
    
    def predict_xgboost(self, symbol: str, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get XGBoost predictions.
        
        Args:
            symbol: Stock symbol
            X: Input features (full DataFrame)
            
        Returns:
            Tuple of (probabilities, predicted_classes)
        """
        if symbol not in self.xgb_models:
            return None, None
        
        model = self.xgb_models[symbol]
        
        # Extract only feature columns (exclude OHLCV and other non-feature columns)
        non_feature_cols = ['time', 'Date', 'open', 'high', 'low', 'close', 'vwap', 'volume', 
                           'OPEN', 'HIGH', 'LOW', 'VOLUME', 'VWAP', 'series', 'CH_TIMESTAMP']
        feature_cols = [col for col in X.columns if col not in non_feature_cols]
        X_features = X[feature_cols]
        
        proba = model.predict_proba(X_features)
        pred = model.predict(X_features)
        
        return proba, pred
    
    def generate_ensemble_signal(self, symbol: str, X: pd.DataFrame) -> Dict:
        """
        Generate ensemble signal combining CNN-LSTM and XGBoost.
        
        Args:
            symbol: Stock symbol
            X: Input features (single row for current prediction)
            
        Returns:
            Signal dictionary with predictions and confidence
        """
        cnn_lstm_weight = self.config['models']['ensemble']['cnn_lstm_weight']
        xgb_weight = self.config['models']['ensemble']['xgboost_weight']
        min_confidence = self.config['models']['ensemble']['min_confidence']
        
        # Get predictions
        cnn_proba, cnn_pred = self.predict_cnn_lstm(symbol, X)
        xgb_proba, xgb_pred = self.predict_xgboost(symbol, X)
        
        # Combine predictions
        if cnn_proba is not None and xgb_proba is not None:
            # Both models available: ensemble
            ensemble_proba = (cnn_lstm_weight * cnn_proba + 
                             xgb_weight * xgb_proba)
            ensemble_pred = np.argmax(ensemble_proba)
            confidence = np.max(ensemble_proba)
            
        elif xgb_proba is not None:
            # Only XGBoost available
            ensemble_proba = xgb_proba
            ensemble_pred = xgb_pred[0] if isinstance(xgb_pred, np.ndarray) else xgb_pred
            confidence = np.max(ensemble_proba)
        
        elif cnn_proba is not None:
            # Only CNN-LSTM available
            ensemble_proba = cnn_proba
            ensemble_pred = np.argmax(ensemble_proba)
            confidence = np.max(ensemble_proba)
        
        else:
            # No models available
            return {
                'signal': 'hold',
                'confidence': 0.0,
                'probabilities': None
            }
        
        # Map prediction to signal
        # XGBoost: -1=sell, 0=hold, 1=buy
        if isinstance(ensemble_pred, np.ndarray):
            ensemble_pred = ensemble_pred[0]
        
        signal_map = {-1: 'sell', 0: 'hold', 1: 'buy'}
        signal = signal_map.get(ensemble_pred, 'hold')
        
        # Check minimum confidence
        if confidence < min_confidence:
            signal = 'hold'
            confidence = 0.0
        
        return {
            'signal': signal,
            'confidence': float(confidence),
            'probabilities': ensemble_proba,
            'predicted_class': int(ensemble_pred)
        }
    
    def generate_signals_for_stocks(self, symbols: List[str], 
                                    X_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Generate signals for multiple stocks.
        
        Args:
            symbols: List of stock symbols
            X_data: Dictionary mapping symbols to feature DataFrames
            
        Returns:
            DataFrame with signals for each stock
        """
        results = []
        
        for symbol in symbols:
            if symbol not in X_data:
                continue
            
            # Get last row (most recent data)
            X = X_data[symbol].tail(1)
            
            # Load models if not already loaded
            self.load_model(symbol, 'xgboost')
            self.load_model(symbol, 'cnn_lstm')
            
            # Generate signal
            signal_dict = self.generate_ensemble_signal(symbol, X)
            
            # Add additional info
            result = {
                'symbol': symbol,
                'signal': signal_dict['signal'],
                'confidence': signal_dict['confidence'],
                'current_price': X_data[symbol].iloc[-1]['close'] if 'close' in X_data[symbol].columns else None,
                'vwap': X_data[symbol].iloc[-1]['vwap'] if 'vwap' in X_data[symbol].columns else None,
            }
            
            # Calculate VWAP deviation
            if result['current_price'] and result['vwap']:
                result['vwap_deviation_pct'] = ((result['current_price'] - result['vwap']) / result['vwap']) * 100
            else:
                result['vwap_deviation_pct'] = None
            
            # Add target and stop loss
            profit_target = self.config['trading']['profit_target']
            stop_loss = self.config['trading']['stop_loss']
            
            if result['current_price']:
                if signal_dict['signal'] == 'buy':
                    result['target_price'] = result['current_price'] * (1 + profit_target)
                    result['stop_loss_price'] = result['current_price'] * (1 - stop_loss)
                elif signal_dict['signal'] == 'sell':
                    result['target_price'] = result['current_price'] * (1 - profit_target)
                    result['stop_loss_price'] = result['current_price'] * (1 + stop_loss)
                else:
                    result['target_price'] = None
                    result['stop_loss_price'] = None
            else:
                result['target_price'] = None
                result['stop_loss_price'] = None
            
            results.append(result)
        
        # Create DataFrame
        df_signals = pd.DataFrame(results)
        
        # Sort by confidence
        df_signals = df_signals.sort_values('confidence', ascending=False)
        
        return df_signals


if __name__ == '__main__':
    print("Testing Signal Generator")
    print("=" * 60)
    
    # Note: This requires trained models
    print("\nSignal generator module loaded successfully.")
    print("To use, you need to:")
    print("1. Train models using train_models.py")
    print("2. Have model files in the 'models' directory")
    print("3. Call generate_signals_for_stocks() with data")

