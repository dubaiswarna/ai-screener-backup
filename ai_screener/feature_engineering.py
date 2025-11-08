"""
Feature Engineering for AI Stock Screener
==========================================

Creates 50+ technical indicators and candlestick pattern features
for machine learning models.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineer:
    """Generate comprehensive technical features from OHLCV data."""
    
    def __init__(self):
        """Initialize feature engineer."""
        self.feature_names: List[str] = []
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all technical features to dataframe.
        
        Args:
            df: DataFrame with columns: time, open, high, low, close, vwap, volume
            
        Returns:
            DataFrame with original columns + engineered features
        """
        df = df.copy()
        
        # Ensure datetime index for easier calculation
        df = df.set_index('time').sort_index()
        
        # 1. Basic Price Features
        df = self._add_price_features(df)
        
        # 2. Candlestick Patterns
        df = self._add_candle_patterns(df)
        
        # 3. Moving Averages & Trends
        df = self._add_trend_features(df)
        
        # 4. Momentum Indicators
        df = self._add_momentum_features(df)
        
        # 5. Volatility Indicators
        df = self._add_volatility_features(df)
        
        # 6. Volume Features
        df = self._add_volume_features(df)
        
        # 7. VWAP Features
        df = self._add_vwap_features(df)
        
        # 8. Statistical Features
        df = self._add_statistical_features(df)
        
        # 9. Multi-timeframe Features
        df = self._add_multitimeframe_features(df)
        
        # Reset index
        df = df.reset_index()
        
        # Remove infinite and very large values
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Fill NaN values with forward fill then backward fill
        df = df.ffill().bfill()
        
        return df
    
    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add basic price-derived features."""
        # Returns
        df['return_1d'] = df['close'].pct_change(1)
        df['return_5d'] = df['close'].pct_change(5)
        df['return_10d'] = df['close'].pct_change(10)
        
        # High-Low Range
        df['hl_range'] = df['high'] - df['low']
        df['hl_range_pct'] = df['hl_range'] / df['close']
        
        # Gap features
        df['gap'] = df['open'] - df['close'].shift(1)
        df['gap_pct'] = df['gap'] / df['close'].shift(1)
        df['gap_up'] = (df['gap'] > 0).astype(int)
        df['gap_down'] = (df['gap'] < 0).astype(int)
        
        # Price position in daily range
        df['price_position'] = (df['close'] - df['low']) / (df['high'] - df['low'] + 1e-10)
        
        self.feature_names.extend([
            'return_1d', 'return_5d', 'return_10d',
            'hl_range', 'hl_range_pct', 'gap', 'gap_pct', 'gap_up', 'gap_down', 'price_position'
        ])
        
        return df
    
    def _add_candle_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add candlestick pattern features."""
        # Body and wick ratios
        df['body'] = abs(df['close'] - df['open'])
        df['upper_wick'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_wick'] = df[['open', 'close']].min(axis=1) - df['low']
        df['total_range'] = df['high'] - df['low']
        
        df['body_ratio'] = df['body'] / (df['total_range'] + 1e-10)
        df['upper_wick_ratio'] = df['upper_wick'] / (df['total_range'] + 1e-10)
        df['lower_wick_ratio'] = df['lower_wick'] / (df['total_range'] + 1e-10)
        
        # Candle type
        df['is_bullish'] = (df['close'] > df['open']).astype(int)
        df['is_bearish'] = (df['close'] < df['open']).astype(int)
        
        # Doji pattern (small body)
        df['is_doji'] = (df['body_ratio'] < 0.1).astype(int)
        
        # Hammer/Shooting Star (long lower/upper wick)
        df['is_hammer'] = ((df['lower_wick_ratio'] > 0.6) & (df['body_ratio'] < 0.3)).astype(int)
        df['is_shooting_star'] = ((df['upper_wick_ratio'] > 0.6) & (df['body_ratio'] < 0.3)).astype(int)
        
        # Engulfing patterns
        prev_bullish = df['is_bullish'].shift(1)
        prev_bearish = df['is_bearish'].shift(1)
        df['bullish_engulfing'] = ((prev_bearish == 1) & (df['is_bullish'] == 1) & 
                                   (df['open'] < df['close'].shift(1)) & 
                                   (df['close'] > df['open'].shift(1))).astype(int)
        df['bearish_engulfing'] = ((prev_bullish == 1) & (df['is_bearish'] == 1) & 
                                   (df['open'] > df['close'].shift(1)) & 
                                   (df['close'] < df['open'].shift(1))).astype(int)
        
        # Consecutive candles
        bullish_shifts = (df['is_bullish'] != df['is_bullish'].shift()).cumsum()
        bearish_shifts = (df['is_bearish'] != df['is_bearish'].shift()).cumsum()
        df['consecutive_green'] = (df.groupby(bullish_shifts).cumcount() + 1) * df['is_bullish']
        df['consecutive_red'] = (df.groupby(bearish_shifts).cumcount() + 1) * df['is_bearish']
        
        self.feature_names.extend([
            'body', 'upper_wick', 'lower_wick', 'total_range',
            'body_ratio', 'upper_wick_ratio', 'lower_wick_ratio',
            'is_bullish', 'is_bearish', 'is_doji',
            'is_hammer', 'is_shooting_star',
            'bullish_engulfing', 'bearish_engulfing',
            'consecutive_green', 'consecutive_red'
        ])
        
        return df
    
    def _add_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add moving average and trend features."""
        # Simple Moving Averages
        df['sma_5'] = df['close'].rolling(window=5).mean()
        df['sma_10'] = df['close'].rolling(window=10).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        # Exponential Moving Averages
        df['ema_5'] = df['close'].ewm(span=5, adjust=False).mean()
        df['ema_10'] = df['close'].ewm(span=10, adjust=False).mean()
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        
        # Price vs MA
        df['price_vs_sma20'] = (df['close'] - df['sma_20']) / df['sma_20']
        df['price_vs_sma50'] = (df['close'] - df['sma_50']) / df['sma_50']
        
        # MA slopes (trend direction)
        df['sma20_slope'] = (df['sma_20'] - df['sma_20'].shift(5)) / df['sma_20'].shift(5)
        df['sma50_slope'] = (df['sma_50'] - df['sma_50'].shift(5)) / df['sma_50'].shift(5)
        
        # MA crossovers
        df['ma_cross'] = ((df['sma_5'] > df['sma_20']) & (df['sma_5'].shift(1) <= df['sma_20'].shift(1))).astype(int)
        df['ma_death_cross'] = ((df['sma_5'] < df['sma_20']) & (df['sma_5'].shift(1) >= df['sma_20'].shift(1))).astype(int)
        
        # Aroon Indicator
        period = 14
        df['aroon_up'] = self._aroon_up(df['high'], period)
        df['aroon_down'] = self._aroon_down(df['low'], period)
        df['aroon_oscillator'] = df['aroon_up'] - df['aroon_down']
        
        self.feature_names.extend([
            'sma_5', 'sma_10', 'sma_20', 'sma_50',
            'ema_5', 'ema_10', 'ema_20',
            'price_vs_sma20', 'price_vs_sma50',
            'sma20_slope', 'sma50_slope',
            'ma_cross', 'ma_death_cross',
            'aroon_up', 'aroon_down', 'aroon_oscillator'
        ])
        
        return df
    
    def _add_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum oscillator features."""
        # RSI
        df['rsi_14'] = self._rsi(df['close'], 14)
        df['rsi_oversold'] = (df['rsi_14'] < 30).astype(int)
        df['rsi_overbought'] = (df['rsi_14'] > 70).astype(int)
        
        # MACD
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        df['macd_cross'] = ((df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))).astype(int)
        
        # Stochastic Oscillator
        period = 14
        lowest_low = df['low'].rolling(window=period).min()
        highest_high = df['high'].rolling(window=period).max()
        df['stoch_k'] = 100 * (df['close'] - lowest_low) / (highest_high - lowest_low + 1e-10)
        df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
        
        # Williams %R
        df['williams_r'] = -100 * (highest_high - df['close']) / (highest_high - lowest_low + 1e-10)
        
        # CCI (Commodity Channel Index)
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        sma_tp = typical_price.rolling(window=20).mean()
        mad = typical_price.rolling(window=20).apply(lambda x: abs(x - x.mean()).mean())
        df['cci'] = (typical_price - sma_tp) / (0.015 * mad + 1e-10)
        
        # ROC (Rate of Change)
        df['roc_10'] = df['close'].pct_change(10) * 100
        
        self.feature_names.extend([
            'rsi_14', 'rsi_oversold', 'rsi_overbought',
            'macd', 'macd_signal', 'macd_histogram', 'macd_cross',
            'stoch_k', 'stoch_d',
            'williams_r',
            'cci',
            'roc_10'
        ])
        
        return df
    
    def _add_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility and band features."""
        # ATR (Average True Range) - simplified calculation
        df['tr'] = df['high'] - df['low']
        df['atr_14'] = df['tr'].rolling(window=14).mean()
        df['atr_pct'] = df['atr_14'] / df['close']
        
        # Bollinger Bands
        sma20 = df['close'].rolling(window=20).mean()
        std20 = df['close'].rolling(window=20).std()
        df['bb_upper'] = sma20 + 2 * std20
        df['bb_lower'] = sma20 - 2 * std20
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        df['bb_width_pct'] = df['bb_width'] / df['close']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_width'] + 1e-10)
        df['bb_squeeze'] = (df['bb_width_pct'] < df['bb_width_pct'].rolling(window=20).quantile(0.25)).astype(int)
        
        # Keltner Channels
        ema20 = df['close'].ewm(span=20, adjust=False).mean()
        df['kc_upper'] = ema20 + 1.5 * df['atr_14']
        df['kc_lower'] = ema20 - 1.5 * df['atr_14']
        df['kc_width'] = df['kc_upper'] - df['kc_lower']
        
        # Price position in bands
        df['price_vs_bb'] = (df['close'] - df['bb_lower']) / (df['bb_width'] + 1e-10)
        df['price_vs_kc'] = (df['close'] - df['kc_lower']) / (df['kc_width'] + 1e-10)
        
        self.feature_names.extend([
            'tr', 'atr_14', 'atr_pct',
            'bb_upper', 'bb_lower', 'bb_width', 'bb_width_pct', 'bb_position', 'bb_squeeze',
            'kc_upper', 'kc_lower', 'kc_width',
            'price_vs_bb', 'price_vs_kc'
        ])
        
        return df
    
    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based features."""
        # Volume MA
        df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / (df['volume_sma_20'] + 1e-10)
        
        # Volume spikes
        df['volume_spike'] = (df['volume_ratio'] > 2.0).astype(int)
        
        # OBV (On Balance Volume)
        df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        df['obv_sma'] = df['obv'].rolling(window=20).mean()
        df['obv_change'] = df['obv'].pct_change()
        
        # Volume-Weighted Momentum
        df['vwm'] = (df['close'].diff() * df['volume']).rolling(window=10).sum()
        
        # Accumulation/Distribution
        clv = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'] + 1e-10)
        df['ad'] = (clv * df['volume']).fillna(0).cumsum()
        
        self.feature_names.extend([
            'volume_sma_20', 'volume_ratio', 'volume_spike',
            'obv', 'obv_sma', 'obv_change',
            'vwm',
            'ad'
        ])
        
        return df
    
    def _add_vwap_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add VWAP-related features."""
        # VWAP deviation
        df['vwap_deviation'] = df['close'] - df['vwap']
        df['vwap_deviation_pct'] = df['vwap_deviation'] / df['vwap']
        
        # Price vs VWAP bands
        if 'upper band #1' in df.columns or 'upper band 1' in df.columns:
            upper_col = 'upper band #1' if 'upper band #1' in df.columns else 'upper band 1'
            lower_col = 'lower band #1' if 'lower band #1' in df.columns else 'lower band 1'
            df['vwap_band_width'] = df[upper_col] - df[lower_col]
            df['vwap_band_position'] = (df['close'] - df[lower_col]) / (df['vwap_band_width'] + 1e-10)
        
        # VWAP trend
        df['vwap_slope'] = df['vwap'].diff(5)
        df['vwap_above'] = (df['close'] > df['vwap']).astype(int)
        
        self.feature_names.extend([
            'vwap_deviation', 'vwap_deviation_pct',
            'vwap_slope', 'vwap_above'
        ])
        
        return df
    
    def _add_statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add statistical features."""
        # Rolling skewness and kurtosis
        df['skewness_20'] = df['close'].rolling(window=20).skew()
        df['kurtosis_20'] = df['close'].rolling(window=20).apply(lambda x: x.kurtosis())
        
        # Z-score
        df['zscore_20'] = (df['close'] - df['close'].rolling(window=20).mean()) / (df['close'].rolling(window=20).std() + 1e-10)
        
        # ADX (Average Directional Index) - simplified
        plus_dm = np.where((df['high'].diff() > df['low'].diff().abs()), df['high'].diff(), 0)
        minus_dm = np.where(df['low'].diff().abs() > df['high'].diff(), df['low'].diff().abs(), 0)
        atr = df['atr_14'] if 'atr_14' in df.columns else df['tr'].rolling(window=14).mean()
        plus_di = 100 * pd.Series(plus_dm).rolling(window=14).mean() / atr
        minus_di = 100 * pd.Series(minus_dm).rolling(window=14).mean() / atr
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
        df['adx'] = dx.rolling(window=14).mean()
        
        self.feature_names.extend([
            'skewness_20', 'kurtosis_20',
            'zscore_20',
            'adx'
        ])
        
        return df
    
    def _add_multitimeframe_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add multi-timeframe aggregated features."""
        try:
            # Weekly aggregates (need datetime index)
            if isinstance(df.index, pd.DatetimeIndex):
                df['close_wkly'] = df['close'].resample('W').last()
                df['close_wkly_sma'] = df['close'].resample('W').mean()
                
                # Forward fill to align with daily data
                df['close_wkly'] = df['close_wkly'].ffill()
                df['close_wkly_sma'] = df['close_wkly_sma'].ffill()
                
                # Price vs weekly levels
                df['price_vs_weekly'] = df['close'] / df['close_wkly'] - 1
                
                # Daily vs weekly momentum
                df['momentum_daily'] = df['close'].pct_change(1)
                df['momentum_weekly'] = df['close_wkly'].pct_change(1)
                
                self.feature_names.extend([
                    'close_wkly', 'close_wkly_sma',
                    'price_vs_weekly',
                    'momentum_daily', 'momentum_weekly'
                ])
            else:
                # Skip weekly features if not datetime index
                pass
        except Exception as e:
            # Skip if error (not critical)
            print(f"Warning: Could not add multi-timeframe features: {e}")
        
        return df
    
    # Helper functions for technical indicators
    
    def _rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _aroon_up(self, highs: pd.Series, period: int) -> pd.Series:
        """Calculate Aroon Up."""
        # Simplified Aroon calculation
        aroon_up = []
        highs_list = highs.values
        for i in range(len(highs_list)):
            if i < period:
                aroon_up.append(np.nan)
            else:
                window = highs_list[i-period+1:i+1]
                max_pos = np.argmax(window)
                periods_since_high = period - 1 - max_pos
                aroon = 100 * (period - periods_since_high) / period
                aroon_up.append(aroon)
        return pd.Series(aroon_up, index=highs.index)
    
    def _aroon_down(self, lows: pd.Series, period: int) -> pd.Series:
        """Calculate Aroon Down."""
        # Simplified Aroon calculation
        aroon_down = []
        lows_list = lows.values
        for i in range(len(lows_list)):
            if i < period:
                aroon_down.append(np.nan)
            else:
                window = lows_list[i-period+1:i+1]
                min_pos = np.argmin(window)
                periods_since_low = period - 1 - min_pos
                aroon = 100 * (period - periods_since_low) / period
                aroon_down.append(aroon)
        return pd.Series(aroon_down, index=lows.index)
    
    def get_feature_names(self) -> List[str]:
        """Get list of engineered feature names."""
        return self.feature_names


if __name__ == '__main__':
    # Test feature engineering
    from data_loader import DataLoader
    
    # Load sample data
    loader = DataLoader()  # Uses default Nify50_data
    stocks = loader.get_all_stocks()
    
    if stocks:
        df = loader.load_stock_data(stocks[0])
        print(f"\nOriginal data shape: {df.shape}")
        
        # Engineer features
        engineer = FeatureEngineer()
        df_features = engineer.engineer_features(df)
        
        print(f"\nData with features shape: {df_features.shape}")
        print(f"\nTotal engineered features: {len(engineer.get_feature_names())}")
        print(f"\nFeature categories:")
        print(f"  - Price features: ~10")
        print(f"  - Candlestick patterns: ~16")
        print(f"  - Trend features: ~17")
        print(f"  - Momentum features: ~12")
        print(f"  - Volatility features: ~14")
        print(f"  - Volume features: ~8")
        print(f"  - VWAP features: ~4")
        print(f"  - Statistical features: ~4")
        print(f"  - Multi-timeframe features: ~5")
        
        print(f"\nSample features:")
        feature_cols = [col for col in df_features.columns if col not in ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume']]
        print(df_features[feature_cols[:10]].tail())

