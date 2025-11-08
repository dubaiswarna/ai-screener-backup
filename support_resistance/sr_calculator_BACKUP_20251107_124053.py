# -*- coding: utf-8 -*-
"""
Support & Resistance Level Calculator
Based on: "Unlocking the Market's Hidden Fortress" Strategy
https://youtu.be/17tR6S9tqeM
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from scipy.signal import argrelextrema


class SupportResistanceCalculator:
    """
    Calculate Support and Resistance levels based on swing highs/lows
    Uses candle wicks for precision and volume for confirmation
    """
    
    def __init__(self, sensitivity: int = 5, min_touches: int = 2):
        """
        Args:
            sensitivity: Window size for finding peaks/troughs (default: 5)
            min_touches: Minimum times price must touch level (default: 2)
        """
        self.sensitivity = sensitivity
        self.min_touches = min_touches
    
    def find_swing_highs_lows(self, df: pd.DataFrame) -> Tuple[List[int], List[int]]:
        """
        Find swing highs (peaks) and swing lows (troughs) in price data
        Uses candle wicks (high/low) for precision
        
        Returns:
            Tuple of (swing_high_indices, swing_low_indices)
        """
        # Find local maxima (resistance levels) using HIGH prices
        swing_highs = argrelextrema(
            df['high'].values, 
            np.greater, 
            order=self.sensitivity
        )[0]
        
        # Find local minima (support levels) using LOW prices
        swing_lows = argrelextrema(
            df['low'].values, 
            np.less, 
            order=self.sensitivity
        )[0]
        
        return swing_highs.tolist(), swing_lows.tolist()
    
    def calculate_level_strength(self, df: pd.DataFrame, level: float, 
                                 tolerance: float = 0.02) -> Dict:
        """
        Calculate strength of a support/resistance level
        
        Args:
            df: Price DataFrame
            level: Price level to check
            tolerance: % tolerance for considering a touch (default: 2%)
        
        Returns:
            Dict with touches, volume, and strength score
        """
        upper_band = level * (1 + tolerance)
        lower_band = level * (1 - tolerance)
        
        # Count touches (price came within tolerance zone)
        touches_high = ((df['high'] >= lower_band) & (df['high'] <= upper_band)).sum()
        touches_low = ((df['low'] >= lower_band) & (df['low'] <= upper_band)).sum()
        total_touches = touches_high + touches_low
        
        # Get volume at touches
        touch_mask = (
            ((df['high'] >= lower_band) & (df['high'] <= upper_band)) |
            ((df['low'] >= lower_band) & (df['low'] <= upper_band))
        )
        avg_volume_at_level = df[touch_mask]['volume'].mean() if touch_mask.any() else 0
        avg_volume_overall = df['volume'].mean()
        
        # Volume spike factor (higher = stronger level)
        volume_factor = avg_volume_at_level / avg_volume_overall if avg_volume_overall > 0 else 1
        
        # Strength score (0-100)
        strength = min(100, (total_touches * 20) + (volume_factor * 30))
        
        return {
            'touches': int(total_touches),
            'volume_factor': round(volume_factor, 2),
            'strength': round(strength, 1)
        }
    
    def cluster_levels(self, levels: List[float], tolerance: float = 0.015) -> List[float]:
        """
        Cluster nearby levels into zones (levels as zones, not rigid lines)
        
        Args:
            levels: List of price levels
            tolerance: % tolerance for clustering (default: 1.5%)
        
        Returns:
            List of clustered level centers
        """
        if not levels:
            return []
        
        levels = sorted(levels)
        clusters = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            # If within tolerance of current cluster, add to it
            if level <= current_cluster[-1] * (1 + tolerance):
                current_cluster.append(level)
            else:
                # Start new cluster
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]
        
        # Add last cluster
        clusters.append(np.mean(current_cluster))
        
        return clusters
    
    def calculate_support_resistance(self, df: pd.DataFrame, 
                                     current_price: float = None) -> Dict:
        """
        Main function to calculate Support & Resistance levels
        
        Args:
            df: DataFrame with OHLCV data
            current_price: Current price (if None, uses last close)
        
        Returns:
            Dict with support/resistance levels and metadata
        """
        if df is None or df.empty or len(df) < self.sensitivity * 2:
            return {
                'supports': [],
                'resistances': [],
                'current_price': current_price or 0,
                'error': 'Insufficient data'
            }
        
        # Ensure required columns
        required_cols = ['high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            return {
                'supports': [],
                'resistances': [],
                'current_price': current_price or 0,
                'error': 'Missing required columns (high, low, close, volume)'
            }
        
        current_price = current_price or df['close'].iloc[-1]
        
        # Find swing points
        swing_highs, swing_lows = self.find_swing_highs_lows(df)
        
        # Get resistance levels (from swing highs)
        resistance_levels = df.iloc[swing_highs]['high'].tolist()
        
        # Get support levels (from swing lows)
        support_levels = df.iloc[swing_lows]['low'].tolist()
        
        # Cluster nearby levels into zones
        resistance_levels = self.cluster_levels(resistance_levels)
        support_levels = self.cluster_levels(support_levels)
        
        # Separate levels above (resistance) and below (support) current price
        resistances = sorted([r for r in resistance_levels if r > current_price])
        supports = sorted([s for s in support_levels if s < current_price], reverse=True)
        
        # Calculate strength for each level
        resistance_data = []
        for level in resistances[:5]:  # Top 5 resistance levels
            strength_info = self.calculate_level_strength(df, level)
            if strength_info['touches'] >= self.min_touches:
                resistance_data.append({
                    'level': round(level, 2),
                    'distance_pct': round(((level - current_price) / current_price) * 100, 2),
                    'zone_upper': round(level * 1.015, 2),
                    'zone_lower': round(level * 0.985, 2),
                    **strength_info
                })
        
        support_data = []
        for level in supports[:5]:  # Top 5 support levels
            strength_info = self.calculate_level_strength(df, level)
            if strength_info['touches'] >= self.min_touches:
                support_data.append({
                    'level': round(level, 2),
                    'distance_pct': round(((current_price - level) / level) * 100, 2),
                    'zone_upper': round(level * 1.015, 2),
                    'zone_lower': round(level * 0.985, 2),
                    **strength_info
                })
        
        return {
            'supports': support_data,
            'resistances': resistance_data,
            'current_price': round(current_price, 2),
            'total_support_levels': len(support_data),
            'total_resistance_levels': len(resistance_data)
        }
    
    def get_nearest_sr_levels(self, df: pd.DataFrame, 
                              current_price: float = None) -> Dict:
        """
        Get the nearest Support and Resistance levels to current price
        
        Returns:
            Dict with nearest support and resistance
        """
        sr_data = self.calculate_support_resistance(df, current_price)
        
        nearest_support = sr_data['supports'][0] if sr_data['supports'] else None
        nearest_resistance = sr_data['resistances'][0] if sr_data['resistances'] else None
        
        return {
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'current_price': sr_data['current_price'],
            'support_distance': nearest_support['distance_pct'] if nearest_support else None,
            'resistance_distance': nearest_resistance['distance_pct'] if nearest_resistance else None
        }

