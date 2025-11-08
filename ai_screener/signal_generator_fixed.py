"""
Fixed Signal Generator - Ensures Feature Alignment
================================================
Matches exactly with training features for 89-feature models
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import os
import pickle


class SignalGeneratorFixed:
    """Generate signals with proper feature alignment."""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.models = {}
        self.feature_names = {}  # Store feature names for each model
        
    def load_model(self, symbol: str) -> bool:
        """Load model and its feature names."""
        model_path = os.path.join(self.models_dir, f"xgb_{symbol}.pkl")
        
        if not os.path.exists(model_path):
            print(f"⚠️  Model not found: {model_path}")
            return False
        
        try:
            from xgboost_trainer import XGBoostTrainer
            trainer = XGBoostTrainer()
            trainer.load_model(model_path)
            self.models[symbol] = trainer
            
            # Try to get feature names from model
            if hasattr(trainer.model, 'feature_names'):
                self.feature_names[symbol] = trainer.model.feature_names
            else:
                # Use default feature set
                self.feature_names[symbol] = self._get_default_features()
            
            print(f"✅ Loaded {symbol}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading {symbol}: {e}")
            return False
    
    def _get_default_features(self) -> List[str]:
        """Get the standard 89 features used in training."""
        # Exclude these non-feature columns
        non_features = [
            'time', 'Date', 'date', 'datetime',
            'open', 'high', 'low', 'close', 'volume', 'vwap',
            'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'VWAP',
            'series', 'CH_TIMESTAMP', 'target', 'future_return'
        ]
        return non_features
    
    def align_features(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Align features to match model training."""
        
        # Get non-feature columns
        non_features = self._get_default_features()
        
        # Get all feature columns
        feature_cols = [col for col in df.columns if col not in non_features]
        
        # If we have more than 89, take first 89
        if len(feature_cols) > 89:
            feature_cols = sorted(feature_cols)[:89]
            print(f"   Reduced from {len(df.columns)} to 89 features")
        
        # Return only feature columns
        return df[feature_cols]
    
    def generate_signal(self, symbol: str, df_features: pd.DataFrame) -> Dict:
        """Generate trading signal for a stock."""
        
        if symbol not in self.models:
            return {
                'symbol': symbol,
                'signal': 'HOLD',
                'confidence': 0.0,
                'error': 'Model not loaded'
            }
        
        try:
            # Get last row (most recent data)
            X = self.align_features(df_features.tail(1), symbol)
            
            # Predict
            model = self.models[symbol]
            prediction = model.predict(X)[0]
            probabilities = model.predict_proba(X)[0]
            confidence = np.max(probabilities)
            
            # Map prediction to signal
            signal_map = {-1: 'SELL', 0: 'HOLD', 1: 'BUY'}
            signal = signal_map.get(prediction, 'HOLD')
            
            # Get current price and VWAP
            latest = df_features.iloc[-1]
            current_price = latest.get('close', 0)
            vwap = latest.get('vwap', current_price)
            
            # Calculate target and stop loss
            if signal == 'BUY':
                target_price = current_price * 1.03  # 3% profit
                stop_loss = current_price * 0.985   # 1.5% stop
            elif signal == 'SELL':
                target_price = current_price * 0.97  # 3% profit
                stop_loss = current_price * 1.015   # 1.5% stop
            else:
                target_price = None
                stop_loss = None
            
            # Calculate VWAP deviation
            vwap_dev = ((current_price - vwap) / vwap * 100) if vwap else 0
            
            return {
                'symbol': symbol,
                'signal': signal,
                'confidence': float(confidence),
                'current_price': float(current_price),
                'target_price': float(target_price) if target_price else None,
                'stop_loss': float(stop_loss) if stop_loss else None,
                'vwap': float(vwap),
                'vwap_deviation': float(vwap_dev),
                'prediction': int(prediction)
            }
            
        except Exception as e:
            print(f"❌ Error generating signal for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return {
                'symbol': symbol,
                'signal': 'HOLD',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def generate_signals_batch(self, symbols: List[str], 
                               featured_data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """Generate signals for multiple stocks."""
        signals = []
        
        for symbol in symbols:
            if symbol not in featured_data:
                print(f"⚠️  No data for {symbol}")
                continue
            
            signal = self.generate_signal(symbol, featured_data[symbol])
            signals.append(signal)
        
        return signals

