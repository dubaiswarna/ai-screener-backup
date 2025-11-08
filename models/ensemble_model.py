"""
Ensemble Model System
=====================
Combines LSTM and XGBoost models with voting mechanism for improved accuracy
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import pickle
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Try to import TensorFlow/Keras for LSTM
try:
    from tensorflow import keras
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("TensorFlow not available. LSTM models will be disabled.")

# XGBoost
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost not available.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LSTMModel:
    """
    LSTM Model for Time Series Prediction
    Captures temporal patterns and sequences in stock data
    """
    
    def __init__(self, sequence_length: int = 60, features: int = 10):
        """
        Initialize LSTM model.
        
        Args:
            sequence_length: Number of time steps to look back
            features: Number of features per time step
        """
        self.sequence_length = sequence_length
        self.features = features
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
    def build_model(self):
        """Build LSTM architecture."""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow not installed. Install with: pip install tensorflow")
        
        model = Sequential([
            # First LSTM layer with return sequences
            LSTM(128, return_sequences=True, input_shape=(self.sequence_length, self.features)),
            Dropout(0.2),
            BatchNormalization(),
            
            # Second LSTM layer
            LSTM(64, return_sequences=True),
            Dropout(0.2),
            BatchNormalization(),
            
            # Third LSTM layer
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            
            # Dense layers
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(16, activation='relu'),
            
            # Output layer (3 classes: BUY, HOLD, SELL)
            Dense(3, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        logger.info(f"✅ LSTM model built: {model.count_params()} parameters")
        
    def prepare_sequences(self, data: pd.DataFrame, target: Optional[pd.Series] = None) -> Tuple:
        """
        Prepare sequential data for LSTM.
        
        Args:
            data: Feature DataFrame
            target: Target Series (optional, for training)
            
        Returns:
            X_sequences, y (if target provided)
        """
        # Scale features
        scaled_data = self.scaler.fit_transform(data)
        
        X_sequences = []
        y_sequences = []
        
        for i in range(self.sequence_length, len(scaled_data)):
            X_sequences.append(scaled_data[i-self.sequence_length:i])
            if target is not None:
                y_sequences.append(target.iloc[i])
        
        X_sequences = np.array(X_sequences)
        
        if target is not None:
            y_sequences = np.array(y_sequences)
            return X_sequences, y_sequences
        
        return X_sequences
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None,
              epochs: int = 50, batch_size: int = 32) -> Dict:
        """
        Train LSTM model.
        
        Args:
            X_train: Training sequences
            y_train: Training targets
            X_val: Validation sequences (optional)
            y_val: Validation targets (optional)
            epochs: Number of training epochs
            batch_size: Batch size
            
        Returns:
            Training history
        """
        if self.model is None:
            self.build_model()
        
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-7)
        ]
        
        validation_data = (X_val, y_val) if X_val is not None else None
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("✅ LSTM training completed")
        return history.history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Input sequences
            
        Returns:
            Predictions (probabilities for each class)
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        predictions = self.model.predict(X, verbose=0)
        return predictions
    
    def save(self, path: str):
        """Save model to file."""
        if self.model is None:
            raise ValueError("No model to save")
        
        # Save Keras model
        self.model.save(path)
        
        # Save scaler separately
        scaler_path = path.replace('.h5', '_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        logger.info(f"✅ LSTM model saved to {path}")
    
    def load(self, path: str):
        """Load model from file."""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow not installed")
        
        self.model = load_model(path)
        
        # Load scaler
        scaler_path = path.replace('.h5', '_scaler.pkl')
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
        
        logger.info(f"✅ LSTM model loaded from {path}")


class EnsembleModel:
    """
    Ensemble Model combining LSTM and XGBoost
    Uses voting mechanism to improve prediction accuracy
    """
    
    def __init__(self, use_lstm: bool = True, use_xgboost: bool = True):
        """
        Initialize ensemble model.
        
        Args:
            use_lstm: Whether to use LSTM model
            use_xgboost: Whether to use XGBoost model
        """
        self.use_lstm = use_lstm and TENSORFLOW_AVAILABLE
        self.use_xgboost = use_xgboost and XGBOOST_AVAILABLE
        
        self.lstm_model = None
        self.xgb_model = None
        
        self.lstm_weight = 0.5
        self.xgb_weight = 0.5
        
        if not (self.use_lstm or self.use_xgboost):
            raise ValueError("At least one model type must be available")
        
        logger.info(f"✅ Ensemble initialized: LSTM={self.use_lstm}, XGBoost={self.use_xgboost}")
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series,
              X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None) -> Dict:
        """
        Train all models in the ensemble.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            
        Returns:
            Training results
        """
        results = {}
        
        # Train LSTM
        if self.use_lstm:
            logger.info("🔄 Training LSTM model...")
            self.lstm_model = LSTMModel(sequence_length=60, features=X_train.shape[1])
            
            # Prepare sequences
            X_train_seq, y_train_seq = self.lstm_model.prepare_sequences(X_train, y_train)
            
            if X_val is not None:
                X_val_seq, y_val_seq = self.lstm_model.prepare_sequences(X_val, y_val)
            else:
                X_val_seq, y_val_seq = None, None
            
            # Convert targets to one-hot encoding
            from tensorflow.keras.utils import to_categorical
            y_train_cat = to_categorical(y_train_seq, num_classes=3)
            y_val_cat = to_categorical(y_val_seq, num_classes=3) if y_val_seq is not None else None
            
            history = self.lstm_model.train(X_train_seq, y_train_cat, X_val_seq, y_val_cat)
            results['lstm'] = history
        
        # Train XGBoost
        if self.use_xgboost:
            logger.info("🔄 Training XGBoost model...")
            self.xgb_model = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=7,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                objective='multi:softprob',
                num_class=3,
                random_state=42,
                n_jobs=-1
            )
            
            eval_set = [(X_val, y_val)] if X_val is not None else None
            
            self.xgb_model.fit(
                X_train, y_train,
                eval_set=eval_set,
                early_stopping_rounds=20,
                verbose=False
            )
            
            results['xgboost'] = {
                'train_accuracy': self.xgb_model.score(X_train, y_train),
                'val_accuracy': self.xgb_model.score(X_val, y_val) if X_val is not None else None
            }
            
            logger.info(f"✅ XGBoost trained - Accuracy: {results['xgboost']['train_accuracy']:.4f}")
        
        # Optimize weights based on validation performance
        if X_val is not None and y_val is not None:
            self._optimize_weights(X_val, y_val)
        
        return results
    
    def _optimize_weights(self, X_val: pd.DataFrame, y_val: pd.Series):
        """
        Optimize ensemble weights based on validation performance.
        
        Args:
            X_val: Validation features
            y_val: Validation targets
        """
        if not (self.use_lstm and self.use_xgboost):
            return  # No need to optimize if only one model
        
        logger.info("🔄 Optimizing ensemble weights...")
        
        # Get predictions from both models
        lstm_pred = self._get_lstm_predictions(X_val)
        xgb_pred = self.xgb_model.predict_proba(X_val)
        
        # Try different weight combinations
        best_accuracy = 0
        best_weights = (0.5, 0.5)
        
        for lstm_w in np.arange(0.1, 1.0, 0.1):
            xgb_w = 1.0 - lstm_w
            
            # Weighted ensemble
            ensemble_pred = lstm_w * lstm_pred + xgb_w * xgb_pred
            predictions = np.argmax(ensemble_pred, axis=1)
            
            # Calculate accuracy
            accuracy = np.mean(predictions == y_val)
            
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_weights = (lstm_w, xgb_w)
        
        self.lstm_weight, self.xgb_weight = best_weights
        logger.info(f"✅ Optimal weights: LSTM={self.lstm_weight:.2f}, XGBoost={self.xgb_weight:.2f}")
        logger.info(f"✅ Ensemble accuracy: {best_accuracy:.4f}")
    
    def _get_lstm_predictions(self, X: pd.DataFrame) -> np.ndarray:
        """Get predictions from LSTM model."""
        if not self.use_lstm or self.lstm_model is None:
            return np.zeros((len(X), 3))
        
        X_seq = self.lstm_model.prepare_sequences(X)
        
        # Handle sequence length
        if len(X_seq) < len(X):
            # Pad with zeros for initial sequences
            padding = np.zeros((len(X) - len(X_seq), 3))
            predictions = self.lstm_model.predict(X_seq)
            return np.vstack([padding, predictions])
        
        return self.lstm_model.predict(X_seq)
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make ensemble predictions.
        
        Args:
            X: Input features
            
        Returns:
            Predictions (class labels)
        """
        predictions = []
        weights = []
        
        # LSTM predictions
        if self.use_lstm and self.lstm_model is not None:
            lstm_pred = self._get_lstm_predictions(X)
            predictions.append(lstm_pred)
            weights.append(self.lstm_weight)
        
        # XGBoost predictions
        if self.use_xgboost and self.xgb_model is not None:
            xgb_pred = self.xgb_model.predict_proba(X)
            predictions.append(xgb_pred)
            weights.append(self.xgb_weight)
        
        # Weighted average
        if len(predictions) == 0:
            raise ValueError("No trained models available")
        
        # Normalize weights
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        # Weighted ensemble
        ensemble_pred = sum(w * p for w, p in zip(weights, predictions))
        
        # Get class labels
        class_predictions = np.argmax(ensemble_pred, axis=1)
        
        return class_predictions
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Get prediction probabilities.
        
        Args:
            X: Input features
            
        Returns:
            Prediction probabilities for each class
        """
        predictions = []
        weights = []
        
        # LSTM predictions
        if self.use_lstm and self.lstm_model is not None:
            lstm_pred = self._get_lstm_predictions(X)
            predictions.append(lstm_pred)
            weights.append(self.lstm_weight)
        
        # XGBoost predictions
        if self.use_xgboost and self.xgb_model is not None:
            xgb_pred = self.xgb_model.predict_proba(X)
            predictions.append(xgb_pred)
            weights.append(self.xgb_weight)
        
        # Normalize weights
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        # Weighted ensemble
        ensemble_pred = sum(w * p for w, p in zip(weights, predictions))
        
        return ensemble_pred
    
    def get_signal(self, X: pd.DataFrame, threshold: float = 0.6) -> Dict:
        """
        Get trading signal with confidence.
        
        Args:
            X: Input features
            threshold: Confidence threshold for signal generation
            
        Returns:
            Signal dict with type and confidence
        """
        proba = self.predict_proba(X)
        
        # Get last prediction
        last_proba = proba[-1]
        
        # Class 0: BUY, Class 1: HOLD, Class 2: SELL
        signal_map = {0: 'BUY', 1: 'HOLD', 2: 'SELL'}
        
        predicted_class = np.argmax(last_proba)
        confidence = last_proba[predicted_class]
        
        # Only generate signal if confidence > threshold
        if confidence < threshold:
            signal_type = 'HOLD'
        else:
            signal_type = signal_map[predicted_class]
        
        return {
            'signal': signal_type,
            'confidence': float(confidence * 100),
            'probabilities': {
                'BUY': float(last_proba[0] * 100),
                'HOLD': float(last_proba[1] * 100),
                'SELL': float(last_proba[2] * 100)
            }
        }
    
    def save(self, directory: str, symbol: str):
        """
        Save ensemble models.
        
        Args:
            directory: Directory to save models
            symbol: Stock symbol
        """
        save_dir = Path(directory)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Save LSTM
        if self.use_lstm and self.lstm_model is not None:
            lstm_path = save_dir / f"lstm_{symbol}.h5"
            self.lstm_model.save(str(lstm_path))
        
        # Save XGBoost
        if self.use_xgboost and self.xgb_model is not None:
            xgb_path = save_dir / f"xgb_{symbol}.pkl"
            with open(xgb_path, 'wb') as f:
                pickle.dump(self.xgb_model, f)
        
        # Save weights
        weights_path = save_dir / f"ensemble_weights_{symbol}.pkl"
        with open(weights_path, 'wb') as f:
            pickle.dump({
                'lstm_weight': self.lstm_weight,
                'xgb_weight': self.xgb_weight
            }, f)
        
        logger.info(f"✅ Ensemble models saved to {save_dir}")
    
    def load(self, directory: str, symbol: str):
        """
        Load ensemble models.
        
        Args:
            directory: Directory containing models
            symbol: Stock symbol
        """
        load_dir = Path(directory)
        
        # Load LSTM
        if self.use_lstm:
            lstm_path = load_dir / f"lstm_{symbol}.h5"
            if lstm_path.exists():
                self.lstm_model = LSTMModel()
                self.lstm_model.load(str(lstm_path))
        
        # Load XGBoost
        if self.use_xgboost:
            xgb_path = load_dir / f"xgb_{symbol}.pkl"
            if xgb_path.exists():
                with open(xgb_path, 'rb') as f:
                    self.xgb_model = pickle.load(f)
        
        # Load weights
        weights_path = load_dir / f"ensemble_weights_{symbol}.pkl"
        if weights_path.exists():
            with open(weights_path, 'rb') as f:
                weights = pickle.load(f)
                self.lstm_weight = weights['lstm_weight']
                self.xgb_weight = weights['xgb_weight']
        
        logger.info(f"✅ Ensemble models loaded from {load_dir}")


# ============================================================
# TESTING
# ============================================================

if __name__ == '__main__':
    print("🧪 Testing Ensemble Model...")
    
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    X = pd.DataFrame(np.random.randn(n_samples, n_features))
    y = pd.Series(np.random.randint(0, 3, n_samples))
    
    # Split data
    split = int(0.8 * n_samples)
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]
    
    # Train ensemble
    if TENSORFLOW_AVAILABLE and XGBOOST_AVAILABLE:
        print("\n✅ Both TensorFlow and XGBoost available")
        ensemble = EnsembleModel(use_lstm=True, use_xgboost=True)
        results = ensemble.train(X_train, y_train, X_val, y_val)
        
        # Test prediction
        signal = ensemble.get_signal(X_val.tail(60))
        print(f"\n📊 Test Signal: {signal['signal']}")
        print(f"   Confidence: {signal['confidence']:.2f}%")
        print(f"   Probabilities: {signal['probabilities']}")
        
        print("\n✅ Ensemble model test passed!")
    else:
        print("\n⚠️ TensorFlow or XGBoost not available")
        print("   Install with: pip install tensorflow xgboost")

