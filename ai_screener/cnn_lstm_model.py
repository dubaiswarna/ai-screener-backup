"""
CNN-LSTM Hybrid Model for Candlestick Pattern Recognition
=========================================================

Deep learning model that combines CNNs for local pattern detection
with LSTMs for temporal sequence modeling.
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from typing import Tuple, Dict, List
import os


class CNNLSTMModel:
    """CNN-LSTM hybrid model for stock signal classification."""
    
    def __init__(self, sequence_length: int = 20, n_features: int = 7, n_classes: int = 3):
        """
        Initialize CNN-LSTM model.
        
        Args:
            sequence_length: Number of timesteps (candles) in each sequence
            n_features: Number of input features per timestep (OHLC, VWAP, Volume)
            n_classes: Number of output classes (buy, hold, sell)
        """
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.n_classes = n_classes
        self.model = None
        self.history = None
    
    def build_model(self) -> keras.Model:
        """
        Build CNN-LSTM architecture.
        
        Architecture:
        - Input: (batch, sequence_length, n_features)
        - CNN layers: Extract local candlestick patterns
        - LSTM layers: Capture temporal dependencies
        - Dense layers: Final classification
        
        Returns:
            Compiled Keras model
        """
        inputs = layers.Input(shape=(self.sequence_length, self.n_features))
        
        # CNN layers for pattern extraction
        x = layers.Conv1D(filters=64, kernel_size=3, activation='relu', padding='same')(inputs)
        x = layers.BatchNormalization()(x)
        x = layers.Conv1D(filters=64, kernel_size=3, activation='relu', padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.MaxPooling1D(pool_size=2)(x)
        
        x = layers.Conv1D(filters=32, kernel_size=3, activation='relu', padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Conv1D(filters=32, kernel_size=3, activation='relu', padding='same')(x)
        x = layers.BatchNormalization()(x)
        
        # LSTM layers for sequence modeling
        x = layers.Bidirectional(layers.LSTM(64, return_sequences=True))(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Bidirectional(layers.LSTM(32, return_sequences=False))(x)
        x = layers.Dropout(0.3)(x)
        
        # Dense layers for classification
        x = layers.Dense(64, activation='relu')(x)
        x = layers.Dropout(0.2)(x)
        x = layers.Dense(32, activation='relu')(x)
        x = layers.Dropout(0.2)(x)
        
        # Output layer (3 classes: buy, hold, sell)
        outputs = layers.Dense(self.n_classes, activation='softmax')(x)
        
        # Build model
        model = keras.Model(inputs=inputs, outputs=outputs, name='CNN_LSTM_Stock_Classifier')
        
        # Compile
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', self._precision_metric, self._recall_metric, self._f1_metric]
        )
        
        self.model = model
        return model
    
    @staticmethod
    def _precision_metric(y_true, y_pred):
        """Calculate precision metric."""
        from tensorflow.keras.metrics import Precision
        return Precision()(y_true, tf.argmax(y_pred, axis=1))
    
    @staticmethod
    def _recall_metric(y_true, y_pred):
        """Calculate recall metric."""
        from tensorflow.keras.metrics import Recall
        return Recall()(y_true, tf.argmax(y_pred, axis=1))
    
    @staticmethod
    def _f1_metric(y_true, y_pred):
        """Calculate F1 score metric."""
        from tensorflow.keras.metrics import Precision, Recall
        precision = Precision()(y_true, tf.argmax(y_pred, axis=1))
        recall = Recall()(y_true, tf.argmax(y_pred, axis=1))
        return 2 * ((precision * recall) / (precision + recall + 1e-10))
    
    def prepare_sequences(self, X: np.ndarray) -> np.ndarray:
        """
        Create sliding window sequences from time series data.
        
        Args:
            X: Input data shape (n_samples, n_features)
            
        Returns:
            Sequences shape (n_sequences, sequence_length, n_features)
        """
        sequences = []
        for i in range(len(X) - self.sequence_length + 1):
            sequences.append(X[i:i + self.sequence_length])
        return np.array(sequences)
    
    def prepare_data(self, X: np.ndarray, y: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for training/inference.
        
        Args:
            X: Input features shape (n_samples, n_features)
            y: Optional labels shape (n_samples,)
            
        Returns:
            Tuple of (X_sequences, y_sequences) or (X_sequences,) if y is None
        """
        X_seq = self.prepare_sequences(X)
        
        if y is not None:
            # Align y with sequences (take the last label of each sequence)
            y_seq = y[self.sequence_length - 1:]
            return X_seq, y_seq
        else:
            return X_seq
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray = None, y_val: np.ndarray = None,
              epochs: int = 50, batch_size: int = 32, verbose: int = 1) -> Dict:
        """
        Train the CNN-LSTM model.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Optional validation features
            y_val: Optional validation labels
            epochs: Number of training epochs
            batch_size: Batch size
            verbose: Verbosity level
            
        Returns:
            Training history dictionary
        """
        if self.model is None:
            self.build_model()
        
        # Prepare data
        X_train_seq, y_train_seq = self.prepare_data(X_train, y_train)
        
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss' if X_val is not None else 'loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6,
                verbose=1
            )
        ]
        
        if X_val is not None:
            X_val_seq, y_val_seq = self.prepare_data(X_val, y_val)
            validation_data = (X_val_seq, y_val_seq)
        else:
            validation_data = None
        
        # Train
        history = self.model.fit(
            X_train_seq, y_train_seq,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=verbose
        )
        
        self.history = history.history
        return history.history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Input features
            
        Returns:
            Predicted class probabilities shape (n_sequences, n_classes)
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        X_seq = self.prepare_sequences(X)
        predictions = self.model.predict(X_seq, verbose=0)
        return predictions
    
    def predict_classes(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class labels.
        
        Args:
            X: Input features
            
        Returns:
            Predicted class indices
        """
        predictions = self.predict(X)
        return np.argmax(predictions, axis=1)
    
    def save_model(self, filepath: str):
        """
        Save model to file.
        
        Args:
            filepath: Path to save model
        """
        if self.model is None:
            raise ValueError("No model to save.")
        
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        self.model.save(filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """
        Load model from file.
        
        Args:
            filepath: Path to saved model
        """
        self.model = keras.models.load_model(
            filepath,
            custom_objects={
                '_precision_metric': self._precision_metric,
                '_recall_metric': self._recall_metric,
                '_f1_metric': self._f1_metric
            }
        )
        print(f"Model loaded from {filepath}")
    
    def summary(self):
        """Print model architecture summary."""
        if self.model:
            self.model.summary()
        else:
            print("No model built yet.")


if __name__ == '__main__':
    # Test model
    print("Testing CNN-LSTM Model")
    print("=" * 60)
    
    # Create dummy data
    n_samples = 1000
    sequence_length = 20
    n_features = 7  # OHLC, VWAP, Volume, return_1d
    n_classes = 3   # buy, hold, sell
    
    X = np.random.randn(n_samples, n_features)
    y = np.random.randint(0, n_classes, n_samples)
    
    # Initialize model
    model = CNNLSTMModel(sequence_length=sequence_length, n_features=n_features, n_classes=n_classes)
    model.build_model()
    model.summary()
    
    print("\n" + "=" * 60)
    print("Model Architecture Created Successfully!")
    print("=" * 60)

