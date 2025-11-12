# -*- coding: utf-8 -*-
"""
PROFESSIONAL Support & Resistance Calculator - COMPLETE VERSION
================================================================

Features:
- Swing High/Low Detection (Wick-based, accurate)
- Pivot Points (Standard, Fibonacci, Camarilla, Woodie's)
- Fibonacci Retracement & Extension Levels
- Trade Setup Generator (Entry/SL/Target)
- Risk:Reward Calculator
- Position Sizing
- Multi-Timeframe Confluence
- Historical Success Rate
- Backtesting Engine
- Interactive Chart Generator

Based on institutional trading principles and professional analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from scipy.signal import argrelextrema
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class ProfessionalSRCalculator:
    """
    Complete Professional Support & Resistance Analysis System
    """
    
    def __init__(self, sensitivity: int = 3, min_touches: int = 2):
        """
        Args:
            sensitivity: Window size for finding peaks/troughs (3-5 recommended)
            min_touches: Minimum times price must touch level (2-3 recommended)
        """
        self.sensitivity = sensitivity
        self.min_touches = min_touches
        self.max_distance_pct = 10.0  # Show levels within 10% of current price
        self.prefer_recent_days = 90   # Prioritize recent 90 days
        self.zone_tolerance = 0.015    # 1.5% tolerance for zones
        
    # ========================================================================
    # CORE S&R DETECTION (ENHANCED FOR ACCURACY)
    # ========================================================================
    
    def find_swing_highs_lows(self, df: pd.DataFrame) -> Tuple[List[int], List[int]]:
        """
        Find swing highs (peaks) and swing lows (troughs) in price data
        Uses candle WICKS (high/low) for precision - NOT close prices
        
        Returns:
            Tuple of (swing_high_indices, swing_low_indices)
        """
        if df is None or len(df) < self.sensitivity * 2:
            return [], []
        
        # Find local maxima (resistance) using HIGH prices (candle wicks)
        swing_highs = argrelextrema(
            df['high'].values, 
            np.greater, 
            order=self.sensitivity
        )[0]
        
        # Find local minima (support) using LOW prices (candle wicks)
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
        
        Strength factors:
        - Number of touches (more = stronger)
        - Volume at touches (higher = stronger)
        - Recency (recent touches = more relevant)
        - Price action at level (bounces vs breaks)
        
        Returns:
            Dict with touches, volume, recency, and strength score (0-100)
        """
        upper_band = level * (1 + tolerance)
        lower_band = level * (1 - tolerance)
        
        # Count touches (price came within tolerance zone)
        touches_high = ((df['high'] >= lower_band) & (df['high'] <= upper_band)).sum()
        touches_low = ((df['low'] >= lower_band) & (df['low'] <= upper_band)).sum()
        total_touches = touches_high + touches_low
        
        # Volume analysis at touches
        touch_mask = (
            ((df['high'] >= lower_band) & (df['high'] <= upper_band)) |
            ((df['low'] >= lower_band) & (df['low'] <= upper_band))
        )
        avg_volume_at_level = df[touch_mask]['volume'].mean() if touch_mask.any() else 0
        avg_volume_overall = df['volume'].mean()
        volume_factor = avg_volume_at_level / avg_volume_overall if avg_volume_overall > 0 else 1
        
        # Recency factor (recent touches more important)
        if touch_mask.any():
            touch_indices = df[touch_mask].index
            if len(touch_indices) > 0:
                last_touch_idx = touch_indices[-1]
                total_rows = len(df)
                recency_pct = (total_rows - last_touch_idx) / total_rows
                recency_factor = 1.0 + (1.0 - recency_pct)  # Recent = higher factor
            else:
                recency_factor = 1.0
        else:
            recency_factor = 1.0
        
        # Strength score (0-100)
        # Formula: (Touches × 15) + (Volume Factor × 25) + (Recency × 20)
        strength = min(100, 
                      (total_touches * 15) + 
                      (volume_factor * 25) + 
                      (recency_factor * 20))
        
        return {
            'touches': int(total_touches),
            'volume_factor': round(volume_factor, 2),
            'recency_factor': round(recency_factor, 2),
            'strength': round(strength, 1)
        }
    
    def cluster_levels(self, levels: List[float], tolerance: float = None) -> List[float]:
        """
        Cluster nearby levels into zones (S&R as zones, not rigid lines)
        
        Args:
            levels: List of price levels
            tolerance: % tolerance for clustering (default: self.zone_tolerance)
        
        Returns:
            List of clustered level centers
        """
        if not levels:
            return []
        
        tolerance = tolerance or self.zone_tolerance
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
    
    # ========================================================================
    # DUAL S&R SYSTEM (PRIMARY + SECONDARY) - From Video Insights
    # ========================================================================
    
    def find_close_open_clusters(self, df: pd.DataFrame, 
                                 min_cluster_size: int = 2,
                                 tolerance_pct: float = 0.01) -> Dict:
        """
        Find SECONDARY S&R levels based on Close/Open clusters
        
        Video Teaching: "second line is always by candle close/open: multiple times"
        
        This detects "battle zones" where price repeatedly tested a level
        using close/open prices (not wicks).
        
        Args:
            df: Price DataFrame
            min_cluster_size: Min touches to form a cluster (default: 2)
            tolerance_pct: % tolerance for clustering (default: 1%)
        
        Returns:
            Dict with resistance and support clusters
        """
        if df is None or len(df) < 10:
            return {'resistances': [], 'supports': []}
        
        # Combine close and open prices
        close_open_prices = list(df['close'].values) + list(df['open'].values)
        close_open_prices = sorted(close_open_prices)
        
        # Find clusters of close/open prices
        clusters = []
        current_cluster = [close_open_prices[0]]
        
        for price in close_open_prices[1:]:
            # If within tolerance of current cluster
            if abs(price - current_cluster[-1]) / current_cluster[-1] <= tolerance_pct:
                current_cluster.append(price)
            else:
                # Save cluster if it has enough members
                if len(current_cluster) >= min_cluster_size:
                    clusters.append({
                        'level': np.mean(current_cluster),
                        'touches': len(current_cluster),
                        'type': 'close_open_cluster'
                    })
                current_cluster = [price]
        
        # Don't forget last cluster
        if len(current_cluster) >= min_cluster_size:
            clusters.append({
                'level': np.mean(current_cluster),
                'touches': len(current_cluster),
                'type': 'close_open_cluster'
            })
        
        # Separate into resistance and support based on current price
        current_price = df['close'].iloc[-1]
        
        resistances = [c for c in clusters if c['level'] > current_price]
        supports = [c for c in clusters if c['level'] < current_price]
        
        return {
            'resistances': sorted(resistances, key=lambda x: x['level']),
            'supports': sorted(supports, key=lambda x: x['level'], reverse=True)
        }
    
    def calculate_dual_sr(self, df: pd.DataFrame, 
                         current_price: float = None) -> Dict:
        """
        Calculate DUAL S&R System (PRIMARY + SECONDARY)
        
        Based on Video Teaching:
        1. PRIMARY S&R: Wick extremes (HIGH/LOW points)
           - "for marking high or low: wick is to be in consideration"
           - Absolute swing highs and lows
           - These are MAJOR levels
        
        2. SECONDARY S&R: Close/Open clusters (multiple touches)
           - "second line is always by candle close/open: multiple times"
           - Battle zones where price tested multiple times
           - These show REPEATED rejections
        
        Returns:
            Dict with both primary and secondary S&R levels
        """
        if df is None or df.empty:
            return {
                'primary': {'supports': [], 'resistances': []},
                'secondary': {'supports': [], 'resistances': []},
                'current_price': current_price or 0,
                'error': 'Insufficient data'
            }
        
        current_price = current_price or df['close'].iloc[-1]
        
        # ===================================================================
        # PRIMARY S&R: Wick-based swing highs/lows (what we already have)
        # ===================================================================
        swing_highs, swing_lows = self.find_swing_highs_lows(df)
        
        # Get primary resistance levels (from HIGH wicks)
        primary_resistances = []
        if len(swing_highs) > 0:
            for idx in swing_highs:
                level = df['high'].iloc[idx]
                if level > current_price:
                    strength_info = self.calculate_level_strength(df, level)
                    primary_resistances.append({
                        'level': round(level, 2),
                        'type': 'primary',
                        'source': 'wick_high',
                        'strength': strength_info['strength'],
                        'touches': strength_info['touches'],
                        'description': 'Absolute HIGH (wick extreme)'
                    })
        
        # Get primary support levels (from LOW wicks)
        primary_supports = []
        if len(swing_lows) > 0:
            for idx in swing_lows:
                level = df['low'].iloc[idx]
                if level < current_price:
                    strength_info = self.calculate_level_strength(df, level)
                    primary_supports.append({
                        'level': round(level, 2),
                        'type': 'primary',
                        'source': 'wick_low',
                        'strength': strength_info['strength'],
                        'touches': strength_info['touches'],
                        'description': 'Absolute LOW (wick extreme)'
                    })
        
        # Cluster and filter primary levels
        primary_resistance_levels = [r['level'] for r in primary_resistances]
        primary_support_levels = [s['level'] for s in primary_supports]
        
        primary_resistance_levels = self.cluster_levels(primary_resistance_levels)
        primary_support_levels = self.cluster_levels(primary_support_levels)
        
        # Rebuild with clustered levels
        primary_resistances = []
        for level in primary_resistance_levels[:5]:  # Top 5
            distance_pct = ((level - current_price) / current_price) * 100
            if distance_pct <= self.max_distance_pct:
                strength_info = self.calculate_level_strength(df, level)
                primary_resistances.append({
                    'level': round(level, 2),
                    'type': 'primary',
                    'source': 'wick_high',
                    'strength': round(strength_info['strength'], 1),
                    'touches': strength_info['touches'],
                    'distance_pct': round(distance_pct, 2),
                    'description': 'Absolute HIGH (wick extreme)'
                })
        
        primary_supports = []
        for level in primary_support_levels[:5]:  # Top 5
            distance_pct = ((current_price - level) / level) * 100
            if distance_pct <= self.max_distance_pct:
                strength_info = self.calculate_level_strength(df, level)
                primary_supports.append({
                    'level': round(level, 2),
                    'type': 'primary',
                    'source': 'wick_low',
                    'strength': round(strength_info['strength'], 1),
                    'touches': strength_info['touches'],
                    'distance_pct': round(distance_pct, 2),
                    'description': 'Absolute LOW (wick extreme)'
                })
        
        # ===================================================================
        # SECONDARY S&R: Close/Open clusters (battle zones)
        # ===================================================================
        close_open_clusters = self.find_close_open_clusters(df, min_cluster_size=2)
        
        secondary_resistances = []
        for cluster in close_open_clusters['resistances'][:5]:  # Top 5
            distance_pct = ((cluster['level'] - current_price) / current_price) * 100
            if distance_pct <= self.max_distance_pct:
                secondary_resistances.append({
                    'level': round(cluster['level'], 2),
                    'type': 'secondary',
                    'source': 'close_open_cluster',
                    'touches': cluster['touches'],
                    'distance_pct': round(distance_pct, 2),
                    'description': f'Battle Zone (tested {cluster["touches"]} times at close/open)'
                })
        
        secondary_supports = []
        for cluster in close_open_clusters['supports'][:5]:  # Top 5
            distance_pct = ((current_price - cluster['level']) / cluster['level']) * 100
            if distance_pct <= self.max_distance_pct:
                secondary_supports.append({
                    'level': round(cluster['level'], 2),
                    'type': 'secondary',
                    'source': 'close_open_cluster',
                    'touches': cluster['touches'],
                    'distance_pct': round(distance_pct, 2),
                    'description': f'Battle Zone (tested {cluster["touches"]} times at close/open)'
                })
        
        return {
            'primary': {
                'resistances': sorted(primary_resistances, key=lambda x: x['distance_pct']),
                'supports': sorted(primary_supports, key=lambda x: x['distance_pct'])
            },
            'secondary': {
                'resistances': sorted(secondary_resistances, key=lambda x: x['distance_pct']),
                'supports': sorted(secondary_supports, key=lambda x: x['distance_pct'])
            },
            'current_price': round(current_price, 2)
        }
    
    # ========================================================================
    # PIVOT POINTS CALCULATIONS
    # ========================================================================
    
    def calculate_pivot_points(self, df: pd.DataFrame, pivot_type: str = 'standard') -> Dict:
        """
        Calculate Pivot Points (used by ALL professional traders)
        
        Types:
        - standard: Classic Pivot Points (P, R1-R3, S1-S3)
        - fibonacci: Fibonacci-based pivots (38.2%, 61.8%)
        - camarilla: Camarilla equation (intraday trading)
        - woodie: Woodie's Pivots (weighted towards close)
        
        Returns:
            Dict with pivot, resistance, and support levels
        """
        if df is None or len(df) < 2:
            return {'error': 'Insufficient data'}
        
        # Get previous day's OHLC
        prev_high = df['high'].iloc[-2] if len(df) >= 2 else df['high'].iloc[-1]
        prev_low = df['low'].iloc[-2] if len(df) >= 2 else df['low'].iloc[-1]
        prev_close = df['close'].iloc[-2] if len(df) >= 2 else df['close'].iloc[-1]
        prev_open = df['open'].iloc[-2] if len(df) >= 2 and 'open' in df.columns else prev_close
        
        current_price = df['close'].iloc[-1]
        
        if pivot_type == 'standard':
            # Standard Pivot Points (Most Popular)
            pivot = (prev_high + prev_low + prev_close) / 3
            
            r1 = (2 * pivot) - prev_low
            r2 = pivot + (prev_high - prev_low)
            r3 = prev_high + 2 * (pivot - prev_low)
            
            s1 = (2 * pivot) - prev_high
            s2 = pivot - (prev_high - prev_low)
            s3 = prev_low - 2 * (prev_high - pivot)
            
            return {
                'type': 'Standard',
                'pivot': round(pivot, 2),
                'r1': round(r1, 2),
                'r2': round(r2, 2),
                'r3': round(r3, 2),
                's1': round(s1, 2),
                's2': round(s2, 2),
                's3': round(s3, 2),
                'current_price': round(current_price, 2)
            }
        
        elif pivot_type == 'fibonacci':
            # Fibonacci Pivot Points
            pivot = (prev_high + prev_low + prev_close) / 3
            range_hl = prev_high - prev_low
            
            r1 = pivot + (range_hl * 0.382)
            r2 = pivot + (range_hl * 0.618)
            r3 = pivot + (range_hl * 1.000)
            
            s1 = pivot - (range_hl * 0.382)
            s2 = pivot - (range_hl * 0.618)
            s3 = pivot - (range_hl * 1.000)
            
            return {
                'type': 'Fibonacci',
                'pivot': round(pivot, 2),
                'r1': round(r1, 2),
                'r2': round(r2, 2),
                'r3': round(r3, 2),
                's1': round(s1, 2),
                's2': round(s2, 2),
                's3': round(s3, 2),
                'current_price': round(current_price, 2)
            }
        
        elif pivot_type == 'camarilla':
            # Camarilla Pivot Points (Intraday Trading)
            pivot = (prev_high + prev_low + prev_close) / 3
            range_hl = prev_high - prev_low
            
            r1 = prev_close + (range_hl * 1.1 / 12)
            r2 = prev_close + (range_hl * 1.1 / 6)
            r3 = prev_close + (range_hl * 1.1 / 4)
            r4 = prev_close + (range_hl * 1.1 / 2)
            
            s1 = prev_close - (range_hl * 1.1 / 12)
            s2 = prev_close - (range_hl * 1.1 / 6)
            s3 = prev_close - (range_hl * 1.1 / 4)
            s4 = prev_close - (range_hl * 1.1 / 2)
            
            return {
                'type': 'Camarilla',
                'pivot': round(pivot, 2),
                'r1': round(r1, 2),
                'r2': round(r2, 2),
                'r3': round(r3, 2),
                'r4': round(r4, 2),
                's1': round(s1, 2),
                's2': round(s2, 2),
                's3': round(s3, 2),
                's4': round(s4, 2),
                'current_price': round(current_price, 2)
            }
        
        elif pivot_type == 'woodie':
            # Woodie's Pivot Points (Weighted towards close)
            pivot = (prev_high + prev_low + (2 * prev_close)) / 4
            
            r1 = (2 * pivot) - prev_low
            r2 = pivot + (prev_high - prev_low)
            r3 = prev_high + 2 * (pivot - prev_low)
            
            s1 = (2 * pivot) - prev_high
            s2 = pivot - (prev_high - prev_low)
            s3 = prev_low - 2 * (prev_high - pivot)
            
            return {
                'type': 'Woodie',
                'pivot': round(pivot, 2),
                'r1': round(r1, 2),
                'r2': round(r2, 2),
                'r3': round(r3, 2),
                's1': round(s1, 2),
                's2': round(s2, 2),
                's3': round(s3, 2),
                'current_price': round(current_price, 2)
            }
        
        else:
            return self.calculate_pivot_points(df, 'standard')
    
    # ========================================================================
    # FIBONACCI RETRACEMENT & EXTENSION
    # ========================================================================
    
    def calculate_fibonacci_levels(self, df: pd.DataFrame, 
                                   lookback_period: int = 50) -> Dict:
        """
        Calculate Fibonacci Retracement and Extension Levels
        
        Automatically detects recent swing high and low, then calculates:
        - Retracement: 0%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%
        - Extension: 127.2%, 161.8%, 261.8% (profit targets)
        - Golden Zone: 50-61.8% (highest probability reversal area)
        
        Args:
            df: Price DataFrame
            lookback_period: Days to look back for swing points
        
        Returns:
            Dict with Fib levels and trend direction
        """
        if df is None or len(df) < lookback_period:
            return {'error': 'Insufficient data for Fibonacci calculation'}
        
        # Get recent data
        recent_df = df.tail(lookback_period)
        current_price = df['close'].iloc[-1]
        
        # Find swing high and low in recent period
        swing_high = recent_df['high'].max()
        swing_low = recent_df['low'].min()
        swing_range = swing_high - swing_low
        
        # Determine trend (are we in uptrend or downtrend?)
        # Uptrend: Recent high is higher than old high
        # Downtrend: Recent low is lower than old low
        mid_point = len(recent_df) // 2
        first_half_high = recent_df.iloc[:mid_point]['high'].max()
        second_half_high = recent_df.iloc[mid_point:]['high'].max()
        
        trend = 'UPTREND' if second_half_high > first_half_high else 'DOWNTREND'
        
        # Calculate Fibonacci Retracement Levels
        # In uptrend: Retracements from high to low
        # In downtrend: Retracements from low to high
        if trend == 'UPTREND':
            fib_0 = swing_low
            fib_236 = swing_low + (swing_range * 0.236)
            fib_382 = swing_low + (swing_range * 0.382)
            fib_50 = swing_low + (swing_range * 0.50)
            fib_618 = swing_low + (swing_range * 0.618)
            fib_786 = swing_low + (swing_range * 0.786)
            fib_100 = swing_high
            
            # Extension levels (profit targets above swing high)
            ext_1272 = swing_high + (swing_range * 0.272)
            ext_1618 = swing_high + (swing_range * 0.618)
            ext_2618 = swing_high + (swing_range * 1.618)
            
            golden_zone_lower = fib_50
            golden_zone_upper = fib_618
        else:
            fib_0 = swing_high
            fib_236 = swing_high - (swing_range * 0.236)
            fib_382 = swing_high - (swing_range * 0.382)
            fib_50 = swing_high - (swing_range * 0.50)
            fib_618 = swing_high - (swing_range * 0.618)
            fib_786 = swing_high - (swing_range * 0.786)
            fib_100 = swing_low
            
            # Extension levels (profit targets below swing low)
            ext_1272 = swing_low - (swing_range * 0.272)
            ext_1618 = swing_low - (swing_range * 0.618)
            ext_2618 = swing_low - (swing_range * 1.618)
            
            golden_zone_lower = fib_618
            golden_zone_upper = fib_50
        
        # Check if current price is in golden zone
        in_golden_zone = golden_zone_lower <= current_price <= golden_zone_upper
        
        return {
            'trend': trend,
            'swing_high': round(swing_high, 2),
            'swing_low': round(swing_low, 2),
            'current_price': round(current_price, 2),
            'retracement': {
                '0%': round(fib_0, 2),
                '23.6%': round(fib_236, 2),
                '38.2%': round(fib_382, 2),
                '50%': round(fib_50, 2),
                '61.8%': round(fib_618, 2),
                '78.6%': round(fib_786, 2),
                '100%': round(fib_100, 2)
            },
            'extension': {
                '127.2%': round(ext_1272, 2),
                '161.8%': round(ext_1618, 2),
                '261.8%': round(ext_2618, 2)
            },
            'golden_zone': {
                'lower': round(golden_zone_lower, 2),
                'upper': round(golden_zone_upper, 2),
                'in_zone': in_golden_zone
            }
        }
    
    # ========================================================================
    # MAIN S&R CALCULATION (COMPREHENSIVE)
    # ========================================================================
    
    def calculate_support_resistance(self, df: pd.DataFrame, 
                                     current_price: float = None) -> Dict:
        """
        MAIN FUNCTION: Calculate all Support & Resistance levels
        
        Includes:
        - Swing-based S&R (from peaks/troughs)
        - Volume-weighted levels
        - Psychological round numbers
        - Strength scoring
        - Recency weighting
        
        Returns:
            Comprehensive dict with all S&R data
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
                'error': 'Missing required columns'
            }
        
        current_price = current_price or df['close'].iloc[-1]
        
        # Prioritize recent data (last 90 days)
        recent_df = df.tail(self.prefer_recent_days) if len(df) > self.prefer_recent_days else df
        full_df = df
        
        # Find swing points in RECENT data first
        swing_highs_recent, swing_lows_recent = self.find_swing_highs_lows(recent_df)
        
        # Also from full data
        swing_highs_full, swing_lows_full = self.find_swing_highs_lows(full_df)
        
        # Get resistance levels (from swing highs)
        resistance_levels_recent = recent_df.iloc[swing_highs_recent]['high'].tolist() if len(swing_highs_recent) > 0 else []
        resistance_levels_full = full_df.iloc[swing_highs_full]['high'].tolist() if len(swing_highs_full) > 0 else []
        resistance_levels = resistance_levels_recent + resistance_levels_full
        
        # Get support levels (from swing lows)
        support_levels_recent = recent_df.iloc[swing_lows_recent]['low'].tolist() if len(swing_lows_recent) > 0 else []
        support_levels_full = full_df.iloc[swing_lows_full]['low'].tolist() if len(swing_lows_full) > 0 else []
        support_levels = support_levels_recent + support_levels_full
        
        # Cluster nearby levels into zones
        resistance_levels = self.cluster_levels(resistance_levels)
        support_levels = self.cluster_levels(support_levels)
        
        # Separate above (resistance) and below (support) current price
        resistances = sorted([
            r for r in resistance_levels 
            if r > current_price and (r - current_price) / current_price * 100 <= self.max_distance_pct
        ])
        
        supports = sorted([
            s for s in support_levels 
            if s < current_price and (current_price - s) / s * 100 <= self.max_distance_pct
        ], reverse=True)
        
        # Add psychological round number levels if needed
        if not resistances:
            round_levels = []
            for multiplier in [50, 100, 250, 500]:
                level = (int(current_price / multiplier) + 1) * multiplier
                if level > current_price and (level - current_price) / current_price * 100 <= self.max_distance_pct:
                    round_levels.append(float(level))
            resistances = sorted(round_levels)[:3]
        
        if not supports:
            round_levels = []
            for multiplier in [50, 100, 250, 500]:
                level = (int(current_price / multiplier)) * multiplier
                if level < current_price and (current_price - level) / level * 100 <= self.max_distance_pct:
                    round_levels.append(float(level))
            supports = sorted(round_levels, reverse=True)[:3]
        
        # Calculate strength for each resistance level
        resistance_data = []
        for level in resistances[:10]:
            strength_info = self.calculate_level_strength(df, level)
            distance_pct = ((level - current_price) / current_price) * 100
            
            if (distance_pct <= self.max_distance_pct or strength_info['strength'] > 80):
                if strength_info['touches'] >= self.min_touches or distance_pct <= 3.0:
                    recency_bonus = 10 if level in resistance_levels_recent else 0
                    adjusted_strength = min(100, strength_info['strength'] + recency_bonus)
                    
                    resistance_data.append({
                        'level': round(level, 2),
                        'distance_pct': round(distance_pct, 2),
                        'zone_upper': round(level * 1.015, 2),
                        'zone_lower': round(level * 0.985, 2),
                        'touches': strength_info['touches'],
                        'volume_factor': strength_info['volume_factor'],
                        'recency_factor': strength_info['recency_factor'],
                        'strength': round(adjusted_strength, 1)
                    })
        
        # Sort by distance (nearest first)
        resistance_data = sorted(resistance_data, key=lambda x: x['distance_pct'])[:5]
        
        # Calculate strength for each support level
        support_data = []
        for level in supports[:10]:
            strength_info = self.calculate_level_strength(df, level)
            distance_pct = ((current_price - level) / level) * 100
            
            if (distance_pct <= self.max_distance_pct or strength_info['strength'] > 80):
                if strength_info['touches'] >= self.min_touches or distance_pct <= 3.0:
                    recency_bonus = 10 if level in support_levels_recent else 0
                    adjusted_strength = min(100, strength_info['strength'] + recency_bonus)
                    
                    support_data.append({
                        'level': round(level, 2),
                        'distance_pct': round(distance_pct, 2),
                        'zone_upper': round(level * 1.015, 2),
                        'zone_lower': round(level * 0.985, 2),
                        'touches': strength_info['touches'],
                        'volume_factor': strength_info['volume_factor'],
                        'recency_factor': strength_info['recency_factor'],
                        'strength': round(adjusted_strength, 1)
                    })
        
        # Sort by distance (nearest first)
        support_data = sorted(support_data, key=lambda x: x['distance_pct'])[:5]
        
        return {
            'supports': support_data,
            'resistances': resistance_data,
            'current_price': round(current_price, 2),
            'total_support_levels': len(support_data),
            'total_resistance_levels': len(resistance_data)
        }


    # ========================================================================
    # TRADE SETUP GENERATOR
    # ========================================================================
    
    def generate_trade_setups(self, df: pd.DataFrame, sr_data: Dict, 
                             fib_data: Dict = None, pivot_data: Dict = None,
                             risk_per_trade_pct: float = 2.0,
                             capital: float = 100000) -> List[Dict]:
        """
        Generate complete trade setups based on S&R analysis
        
        Generates:
        - Entry price (at support for buy, resistance for short)
        - Stop loss (below support / above resistance with buffer)
        - Target 1 (nearest opposite level)
        - Target 2 (Fib extension if available)
        - Risk:Reward ratio
        - Position size based on risk management
        
        Args:
            df: Price DataFrame
            sr_data: S&R data from calculate_support_resistance()
            fib_data: Fibonacci data (optional)
            pivot_data: Pivot points data (optional)
            risk_per_trade_pct: % of capital to risk per trade (default: 2%)
            capital: Total trading capital
        
        Returns:
            List of trade setups (BUY and/or SELL)
        """
        setups = []
        current_price = sr_data['current_price']
        
        # ===================================================================
        # BUY SETUP (At Support)
        # ===================================================================
        if sr_data['supports']:
            nearest_support = sr_data['supports'][0]
            support_level = nearest_support['level']
            support_strength = nearest_support['strength']
            
            # Entry: At support level
            entry_price = support_level
            
            # Stop Loss: 2% below support (buffer for volatility)
            stop_loss = support_level * 0.98
            
            # Target 1: Nearest resistance
            if sr_data['resistances']:
                target1 = sr_data['resistances'][0]['level']
            else:
                target1 = entry_price * 1.05  # Default 5% target
            
            # Target 2: Fib extension or second resistance
            if fib_data and not fib_data.get('error'):
                target2 = fib_data['extension']['161.8%']
            elif len(sr_data['resistances']) > 1:
                target2 = sr_data['resistances'][1]['level']
            else:
                target2 = entry_price * 1.10  # Default 10% target
            
            # Calculate risk and reward
            risk_per_share = entry_price - stop_loss
            reward1_per_share = target1 - entry_price
            reward2_per_share = target2 - entry_price
            
            # Risk:Reward ratios
            rr_ratio1 = reward1_per_share / risk_per_share if risk_per_share > 0 else 0
            rr_ratio2 = reward2_per_share / risk_per_share if risk_per_share > 0 else 0
            
            # Position sizing (based on risk per trade)
            risk_amount = capital * (risk_per_trade_pct / 100)
            position_size = int(risk_amount / risk_per_share) if risk_per_share > 0 else 0
            
            # Calculate potential profit
            potential_profit1 = reward1_per_share * position_size
            potential_profit2 = reward2_per_share * position_size
            
            # Distance from current price
            distance_pct = ((entry_price - current_price) / current_price) * 100
            
            # Only include if R:R is favorable (at least 1:1.5)
            if rr_ratio1 >= 1.5 and position_size > 0:
                setups.append({
                    'type': 'BUY',
                    'entry_price': round(entry_price, 2),
                    'stop_loss': round(stop_loss, 2),
                    'target1': round(target1, 2),
                    'target2': round(target2, 2),
                    'risk_per_share': round(risk_per_share, 2),
                    'reward1_per_share': round(reward1_per_share, 2),
                    'reward2_per_share': round(reward2_per_share, 2),
                    'rr_ratio1': round(rr_ratio1, 2),
                    'rr_ratio2': round(rr_ratio2, 2),
                    'position_size': position_size,
                    'risk_amount': round(risk_amount, 2),
                    'potential_profit1': round(potential_profit1, 2),
                    'potential_profit2': round(potential_profit2, 2),
                    'support_strength': support_strength,
                    'distance_from_current_pct': round(distance_pct, 2),
                    'status': 'ACTIVE' if abs(distance_pct) < 2 else 'PENDING',
                    'confidence': 'HIGH' if support_strength > 70 and rr_ratio1 > 2 else 'MEDIUM'
                })
        
        # ===================================================================
        # SELL/SHORT SETUP (At Resistance)
        # ===================================================================
        if sr_data['resistances']:
            nearest_resistance = sr_data['resistances'][0]
            resistance_level = nearest_resistance['level']
            resistance_strength = nearest_resistance['strength']
            
            # Entry: At resistance level
            entry_price = resistance_level
            
            # Stop Loss: 2% above resistance
            stop_loss = resistance_level * 1.02
            
            # Target 1: Nearest support
            if sr_data['supports']:
                target1 = sr_data['supports'][0]['level']
            else:
                target1 = entry_price * 0.95  # Default 5% target
            
            # Target 2: Fib extension or second support
            if fib_data and not fib_data.get('error'):
                # For short, extension is below
                target2 = entry_price - (entry_price - target1) * 1.618
            elif len(sr_data['supports']) > 1:
                target2 = sr_data['supports'][1]['level']
            else:
                target2 = entry_price * 0.90  # Default 10% target
            
            # Calculate risk and reward
            risk_per_share = stop_loss - entry_price
            reward1_per_share = entry_price - target1
            reward2_per_share = entry_price - target2
            
            # Risk:Reward ratios
            rr_ratio1 = reward1_per_share / risk_per_share if risk_per_share > 0 else 0
            rr_ratio2 = reward2_per_share / risk_per_share if risk_per_share > 0 else 0
            
            # Position sizing
            risk_amount = capital * (risk_per_trade_pct / 100)
            position_size = int(risk_amount / risk_per_share) if risk_per_share > 0 else 0
            
            # Calculate potential profit
            potential_profit1 = reward1_per_share * position_size
            potential_profit2 = reward2_per_share * position_size
            
            # Distance from current price
            distance_pct = ((entry_price - current_price) / current_price) * 100
            
            # Only include if R:R is favorable
            if rr_ratio1 >= 1.5 and position_size > 0:
                setups.append({
                    'type': 'SELL',
                    'entry_price': round(entry_price, 2),
                    'stop_loss': round(stop_loss, 2),
                    'target1': round(target1, 2),
                    'target2': round(target2, 2),
                    'risk_per_share': round(risk_per_share, 2),
                    'reward1_per_share': round(reward1_per_share, 2),
                    'reward2_per_share': round(reward2_per_share, 2),
                    'rr_ratio1': round(rr_ratio1, 2),
                    'rr_ratio2': round(rr_ratio2, 2),
                    'position_size': position_size,
                    'risk_amount': round(risk_amount, 2),
                    'potential_profit1': round(potential_profit1, 2),
                    'potential_profit2': round(potential_profit2, 2),
                    'resistance_strength': resistance_strength,
                    'distance_from_current_pct': round(distance_pct, 2),
                    'status': 'ACTIVE' if abs(distance_pct) < 2 else 'PENDING',
                    'confidence': 'HIGH' if resistance_strength > 70 and rr_ratio1 > 2 else 'MEDIUM'
                })
        
        return setups
    
    # ========================================================================
    # MULTI-TIMEFRAME CONFLUENCE
    # ========================================================================
    
    def calculate_multi_timeframe_sr(self, df: pd.DataFrame) -> Dict:
        """
        Calculate S&R across multiple timeframes and find confluence zones
        
        Timeframes:
        - Daily (current)
        - Weekly (5-day aggregation)
        - Monthly (20-day aggregation)
        
        Confluence: When multiple timeframes agree on same S&R level
        
        Returns:
            Dict with S&R for each timeframe and confluence zones
        """
        if df is None or len(df) < 60:
            return {'error': 'Insufficient data for multi-timeframe analysis (need 60+ days)'}
        
        current_price = df['close'].iloc[-1]
        
        # Daily S&R (already calculated)
        daily_sr = self.calculate_support_resistance(df, current_price)
        
        # Weekly S&R (resample to weekly)
        try:
            df_weekly = df.copy()
            df_weekly['time'] = pd.to_datetime(df_weekly.index if 'time' not in df_weekly.columns else df_weekly['time'])
            df_weekly.set_index('time', inplace=True)
            
            df_weekly_resampled = df_weekly.resample('W').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
            
            df_weekly_resampled = df_weekly_resampled.reset_index()
            weekly_sr = self.calculate_support_resistance(df_weekly_resampled, current_price)
        except Exception:
            weekly_sr = {'supports': [], 'resistances': [], 'error': 'Weekly calculation failed'}
        
        # Monthly S&R (resample to monthly)
        try:
            df_monthly = df.copy()
            df_monthly['time'] = pd.to_datetime(df_monthly.index if 'time' not in df_monthly.columns else df_monthly['time'])
            df_monthly.set_index('time', inplace=True)
            
            df_monthly_resampled = df_monthly.resample('M').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
            
            df_monthly_resampled = df_monthly_resampled.reset_index()
            monthly_sr = self.calculate_support_resistance(df_monthly_resampled, current_price)
        except Exception:
            monthly_sr = {'supports': [], 'resistances': [], 'error': 'Monthly calculation failed'}
        
        # Find confluence zones (levels that appear in multiple timeframes)
        confluence_zones = []
        tolerance = 0.02  # 2% tolerance for matching levels
        
        # Check each daily support against weekly and monthly
        for daily_sup in daily_sr['supports']:
            daily_level = daily_sup['level']
            matches = ['Daily']
            
            # Check weekly
            for weekly_sup in weekly_sr.get('supports', []):
                if abs(weekly_sup['level'] - daily_level) / daily_level <= tolerance:
                    matches.append('Weekly')
                    break
            
            # Check monthly
            for monthly_sup in monthly_sr.get('supports', []):
                if abs(monthly_sup['level'] - daily_level) / daily_level <= tolerance:
                    matches.append('Monthly')
                    break
            
            if len(matches) >= 2:
                confluence_zones.append({
                    'level': daily_level,
                    'type': 'SUPPORT',
                    'timeframes': matches,
                    'confluence_score': len(matches),
                    'strength': daily_sup['strength']
                })
        
        # Check each daily resistance
        for daily_res in daily_sr['resistances']:
            daily_level = daily_res['level']
            matches = ['Daily']
            
            # Check weekly
            for weekly_res in weekly_sr.get('resistances', []):
                if abs(weekly_res['level'] - daily_level) / daily_level <= tolerance:
                    matches.append('Weekly')
                    break
            
            # Check monthly
            for monthly_res in monthly_sr.get('resistances', []):
                if abs(monthly_res['level'] - daily_level) / daily_level <= tolerance:
                    matches.append('Monthly')
                    break
            
            if len(matches) >= 2:
                confluence_zones.append({
                    'level': daily_level,
                    'type': 'RESISTANCE',
                    'timeframes': matches,
                    'confluence_score': len(matches),
                    'strength': daily_res['strength']
                })
        
        return {
            'daily': daily_sr,
            'weekly': weekly_sr,
            'monthly': monthly_sr,
            'confluence_zones': sorted(confluence_zones, key=lambda x: x['confluence_score'], reverse=True),
            'current_price': current_price
        }
    
    # ========================================================================
    # HISTORICAL SUCCESS RATE
    # ========================================================================
    
    def calculate_historical_success_rate(self, df: pd.DataFrame, 
                                         sr_data: Dict) -> Dict:
        """
        Calculate historical success rate of each S&R level
        
        Success = Price bounced off the level (held)
        Failure = Price broke through the level
        
        Success Rate = Holds / Total Touches × 100%
        
        Returns:
            Dict with success rates for each level
        """
        results = {
            'supports': [],
            'resistances': []
        }
        
        if df is None or len(df) < 20:
            return results
        
        tolerance = 0.02  # 2% tolerance for touching a level
        
        # Check each support level
        for support in sr_data['supports']:
            level = support['level']
            upper_band = level * (1 + tolerance)
            lower_band = level * (1 - tolerance)
            
            # Find all touches
            touches = df[(df['low'] >= lower_band) & (df['low'] <= upper_band)]
            
            if len(touches) == 0:
                continue
            
            holds = 0
            breaks = 0
            
            for idx in touches.index:
                touch_idx = df.index.get_loc(idx)
                
                # Check next 5 candles after touch
                if touch_idx + 5 < len(df):
                    next_candles = df.iloc[touch_idx+1:touch_idx+6]
                    
                    # If price stayed above support, it held
                    if next_candles['low'].min() >= level * 0.98:
                        holds += 1
                    else:
                        breaks += 1
            
            total_tests = holds + breaks
            success_rate = (holds / total_tests * 100) if total_tests > 0 else 0
            
            results['supports'].append({
                'level': level,
                'total_tests': total_tests,
                'holds': holds,
                'breaks': breaks,
                'success_rate': round(success_rate, 1),
                'last_test': touches.index[-1] if len(touches) > 0 else None,
                'confidence': 'HIGH' if success_rate >= 75 else 'MEDIUM' if success_rate >= 50 else 'LOW'
            })
        
        # Check each resistance level
        for resistance in sr_data['resistances']:
            level = resistance['level']
            upper_band = level * (1 + tolerance)
            lower_band = level * (1 - tolerance)
            
            # Find all touches
            touches = df[(df['high'] >= lower_band) & (df['high'] <= upper_band)]
            
            if len(touches) == 0:
                continue
            
            holds = 0
            breaks = 0
            
            for idx in touches.index:
                touch_idx = df.index.get_loc(idx)
                
                # Check next 5 candles
                if touch_idx + 5 < len(df):
                    next_candles = df.iloc[touch_idx+1:touch_idx+6]
                    
                    # If price stayed below resistance, it held
                    if next_candles['high'].max() <= level * 1.02:
                        holds += 1
                    else:
                        breaks += 1
            
            total_tests = holds + breaks
            success_rate = (holds / total_tests * 100) if total_tests > 0 else 0
            
            results['resistances'].append({
                'level': level,
                'total_tests': total_tests,
                'holds': holds,
                'breaks': breaks,
                'success_rate': round(success_rate, 1),
                'last_test': touches.index[-1] if len(touches) > 0 else None,
                'confidence': 'HIGH' if success_rate >= 75 else 'MEDIUM' if success_rate >= 50 else 'LOW'
            })
        
        return results


# Export the enhanced calculator
__all__ = ['ProfessionalSRCalculator']

