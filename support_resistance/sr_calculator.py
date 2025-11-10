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
    
    def __init__(self, sensitivity: int = 3, min_touches: int = 2):
        """
        Args:
            sensitivity: Window size for finding peaks/troughs (default: 3 - finds more nearby levels)
            min_touches: Minimum times price must touch level (default: 2)
        """
        self.sensitivity = sensitivity
        self.min_touches = min_touches
        self.max_distance_pct = 10.0  # Only show levels within 10% of current price
        self.prefer_recent_days = 90   # Prioritize levels from last 90 days
    
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
        IMPROVED: Prioritizes nearby levels (2-10%) and recent price action
        
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
        
        # IMPROVEMENT: Prioritize recent data (last 90 days)
        recent_df = df.tail(self.prefer_recent_days) if len(df) > self.prefer_recent_days else df
        full_df = df
        
        # Find swing points in RECENT data first (more relevant)
        swing_highs_recent, swing_lows_recent = self.find_swing_highs_lows(recent_df)
        
        # Also find from full data but with lower priority
        swing_highs_full, swing_lows_full = self.find_swing_highs_lows(full_df)
        
        # Get resistance levels (from swing highs) - prioritize recent
        resistance_levels_recent = recent_df.iloc[swing_highs_recent]['high'].tolist() if len(swing_highs_recent) > 0 else []
        resistance_levels_full = full_df.iloc[swing_highs_full]['high'].tolist() if len(swing_highs_full) > 0 else []
        resistance_levels = resistance_levels_recent + resistance_levels_full
        
        # Get support levels (from swing lows) - prioritize recent
        support_levels_recent = recent_df.iloc[swing_lows_recent]['low'].tolist() if len(swing_lows_recent) > 0 else []
        support_levels_full = full_df.iloc[swing_lows_full]['low'].tolist() if len(swing_lows_full) > 0 else []
        support_levels = support_levels_recent + support_levels_full
        
        # Cluster nearby levels into zones
        resistance_levels = self.cluster_levels(resistance_levels)
        support_levels = self.cluster_levels(support_levels)
        
        # Separate levels above (resistance) and below (support) current price
        # IMPROVEMENT: Filter to only show levels within max_distance_pct
        resistances = sorted([
            r for r in resistance_levels 
            if r > current_price and (r - current_price) / current_price * 100 <= self.max_distance_pct
        ])
        
        supports = sorted([
            s for s in support_levels 
            if s < current_price and (current_price - s) / s * 100 <= self.max_distance_pct
        ], reverse=True)
        
        # IMPROVEMENT: If no resistance found, add psychological levels
        if not resistances:
            # Add round number resistances above current price
            round_levels = []
            for multiplier in [50, 100, 250, 500]:
                level = (int(current_price / multiplier) + 1) * multiplier
                if level > current_price and (level - current_price) / current_price * 100 <= self.max_distance_pct:
                    round_levels.append(float(level))
            resistances = sorted(round_levels)[:3]
        
        # IMPROVEMENT: If no support found, add psychological levels
        if not supports:
            # Add round number supports below current price
            round_levels = []
            for multiplier in [50, 100, 250, 500]:
                level = (int(current_price / multiplier)) * multiplier
                if level < current_price and (current_price - level) / level * 100 <= self.max_distance_pct:
                    round_levels.append(float(level))
            supports = sorted(round_levels, reverse=True)[:3]
        
        # Calculate strength for each level
        resistance_data = []
        for level in resistances[:10]:  # Check more levels, will filter by distance
            strength_info = self.calculate_level_strength(df, level)
            distance_pct = ((level - current_price) / current_price) * 100
            
            # IMPROVEMENT: Only include if within max distance or very strong
            if (distance_pct <= self.max_distance_pct or strength_info['strength'] > 80):
                if strength_info['touches'] >= self.min_touches or distance_pct <= 3.0:
                    # Calculate recency bonus (recent levels are more relevant)
                    recency_bonus = 10 if level in resistance_levels_recent else 0
                    adjusted_strength = min(100, strength_info['strength'] + recency_bonus)
                    
                    resistance_data.append({
                        'level': round(level, 2),
                        'distance_pct': round(distance_pct, 2),
                        'zone_upper': round(level * 1.015, 2),
                        'zone_lower': round(level * 0.985, 2),
                        'touches': strength_info['touches'],
                        'volume_factor': strength_info['volume_factor'],
                        'strength': round(adjusted_strength, 1)
                    })
        
        # Sort by distance (nearest first)
        resistance_data = sorted(resistance_data, key=lambda x: x['distance_pct'])[:5]
        
        support_data = []
        for level in supports[:10]:  # Check more levels, will filter by distance
            strength_info = self.calculate_level_strength(df, level)
            distance_pct = ((current_price - level) / level) * 100
            
            # IMPROVEMENT: Only include if within max distance or very strong
            if (distance_pct <= self.max_distance_pct or strength_info['strength'] > 80):
                if strength_info['touches'] >= self.min_touches or distance_pct <= 3.0:
                    # Calculate recency bonus
                    recency_bonus = 10 if level in support_levels_recent else 0
                    adjusted_strength = min(100, strength_info['strength'] + recency_bonus)
                    
                    support_data.append({
                        'level': round(level, 2),
                        'distance_pct': round(distance_pct, 2),
                        'zone_upper': round(level * 1.015, 2),
                        'zone_lower': round(level * 0.985, 2),
                        'touches': strength_info['touches'],
                        'volume_factor': strength_info['volume_factor'],
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
    
    def detect_role_reversals(self, df: pd.DataFrame, sr_data: Dict) -> List[Dict]:
        """
        Detect role reversals - when broken support becomes resistance or vice versa
        
        Args:
            df: Price DataFrame
            sr_data: S&R data from calculate_support_resistance
        
        Returns:
            List of role reversal events
        """
        if df is None or df.empty:
            return []
        
        reversals = []
        current_price = sr_data['current_price']
        
        # Check if we have recent price history (last 20 candles)
        recent_df = df.tail(20)
        
        # Check former support levels (now above current price)
        for support in sr_data['supports']:
            level = support['level']
            
            # Check if price was recently above this level
            was_above = (recent_df['low'] > level).any()
            now_below = current_price < level
            
            # If price crossed below, old support might be new resistance
            if was_above and now_below:
                # Check for rejection (price tried to go up but failed)
                rejection = (recent_df['high'] >= level * 0.99).any() and \
                           (recent_df['close'] < level * 0.99).any()
                
                if rejection:
                    reversals.append({
                        'type': 'SUPPORT_TO_RESISTANCE',
                        'level': level,
                        'status': 'Support broken, now acting as Resistance',
                        'strength': support['strength'],
                        'confidence': 'High' if support['touches'] >= 3 else 'Medium'
                    })
        
        # Check former resistance levels (now below current price)
        for resistance in sr_data['resistances']:
            level = resistance['level']
            
            # Check if price was recently below this level
            was_below = (recent_df['high'] < level).any()
            now_above = current_price > level
            
            # If price crossed above, old resistance might be new support
            if was_below and now_above:
                # Check for bounce (price tried to go down but bounced)
                bounce = (recent_df['low'] <= level * 1.01).any() and \
                        (recent_df['close'] > level * 1.01).any()
                
                if bounce:
                    reversals.append({
                        'type': 'RESISTANCE_TO_SUPPORT',
                        'level': level,
                        'status': 'Resistance broken, now acting as Support',
                        'strength': resistance['strength'],
                        'confidence': 'High' if resistance['touches'] >= 3 else 'Medium'
                    })
        
        return reversals
    
    def detect_breakouts(self, df: pd.DataFrame, sr_data: Dict) -> Dict:
        """
        Detect breakouts - when price breaks through S/R with candle close confirmation
        
        Args:
            df: Price DataFrame
            sr_data: S&R data from calculate_support_resistance
        
        Returns:
            Dict with breakout information
        """
        if df is None or len(df) < 2:
            return {'breakout_detected': False}
        
        # Get last 2 candles
        prev_candle = df.iloc[-2]
        current_candle = df.iloc[-1]
        
        current_price = sr_data['current_price']
        
        breakouts = []
        
        # Check resistance breakouts
        if sr_data['resistances']:
            nearest_resistance = sr_data['resistances'][0]
            level = nearest_resistance['level']
            
            # Breakout conditions:
            # 1. Previous close was below resistance
            # 2. Current close is above resistance
            # 3. Current low is not far below resistance (no false break)
            if (prev_candle['close'] < level and 
                current_candle['close'] > level and
                current_candle['low'] > level * 0.995):
                
                breakouts.append({
                    'type': 'RESISTANCE_BREAKOUT',
                    'level': level,
                    'direction': 'BULLISH',
                    'status': 'Price broke above resistance',
                    'strength': nearest_resistance['strength'],
                    'volume_confirmation': current_candle['volume'] > df['volume'].tail(20).mean() * 1.2
                })
        
        # Check support breakdowns
        if sr_data['supports']:
            nearest_support = sr_data['supports'][0]
            level = nearest_support['level']
            
            # Breakdown conditions:
            # 1. Previous close was above support
            # 2. Current close is below support  
            # 3. Current high is not far above support (no false break)
            if (prev_candle['close'] > level and
                current_candle['close'] < level and
                current_candle['high'] < level * 1.005):
                
                breakouts.append({
                    'type': 'SUPPORT_BREAKDOWN',
                    'level': level,
                    'direction': 'BEARISH',
                    'status': 'Price broke below support',
                    'strength': nearest_support['strength'],
                    'volume_confirmation': current_candle['volume'] > df['volume'].tail(20).mean() * 1.2
                })
        
        if breakouts:
            return {
                'breakout_detected': True,
                'breakouts': breakouts
            }
        
        return {'breakout_detected': False}
    
    def calculate_moving_averages(self, df: pd.DataFrame) -> Dict:
        """
        Calculate moving averages and trend context
        
        Args:
            df: Price DataFrame
        
        Returns:
            Dict with MA values and trend analysis
        """
        if df is None or len(df) < 200:
            return {'available': False, 'reason': 'Insufficient data for 200 MA'}
        
        # Calculate EMAs
        df_copy = df.copy()
        df_copy['EMA50'] = df_copy['close'].ewm(span=50, adjust=False).mean()
        df_copy['EMA200'] = df_copy['close'].ewm(span=200, adjust=False).mean()
        
        # Get current values
        current_price = df_copy['close'].iloc[-1]
        ema50 = df_copy['EMA50'].iloc[-1]
        ema200 = df_copy['EMA200'].iloc[-1]
        
        # Determine trend
        if current_price > ema50 > ema200:
            trend = 'STRONG BULLISH'
            context = 'Price above both MAs - Strong uptrend'
        elif current_price > ema50 and ema50 < ema200:
            trend = 'BULLISH'
            context = 'Price above 50 EMA but below 200 EMA - Bullish with caution'
        elif current_price < ema50 < ema200:
            trend = 'STRONG BEARISH'
            context = 'Price below both MAs - Strong downtrend'
        elif current_price < ema50 and ema50 > ema200:
            trend = 'BEARISH'
            context = 'Price below 50 EMA but above 200 EMA - Bearish with caution'
        else:
            trend = 'NEUTRAL'
            context = 'Mixed signals - Sideways movement'
        
        # Golden/Death Cross
        cross = None
        if len(df_copy) >= 2:
            prev_ema50 = df_copy['EMA50'].iloc[-2]
            prev_ema200 = df_copy['EMA200'].iloc[-2]
            
            if prev_ema50 <= prev_ema200 and ema50 > ema200:
                cross = 'GOLDEN CROSS'
            elif prev_ema50 >= prev_ema200 and ema50 < ema200:
                cross = 'DEATH CROSS'
        
        return {
            'available': True,
            'EMA50': round(ema50, 2),
            'EMA200': round(ema200, 2),
            'current_price': round(current_price, 2),
            'trend': trend,
            'context': context,
            'cross': cross,
            'distance_from_50ema': round(((current_price - ema50) / ema50) * 100, 2),
            'distance_from_200ema': round(((current_price - ema200) / ema200) * 100, 2)
        }
    
    def simulate_weekly_timeframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Simulate weekly timeframe from daily data by resampling
        
        Args:
            df: Daily price DataFrame
        
        Returns:
            Weekly DataFrame with OHLCV data
        """
        if df is None or df.empty:
            return None
        
        # Ensure time column is datetime
        df_copy = df.copy()
        if 'time' in df_copy.columns:
            df_copy['time'] = pd.to_datetime(df_copy['time'])
            df_copy = df_copy.set_index('time')
        
        # Resample to weekly
        weekly = df_copy.resample('W').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        # Reset index to have time as column again
        weekly = weekly.reset_index()
        
        return weekly
    
    def get_multi_timeframe_analysis(self, df_daily: pd.DataFrame) -> Dict:
        """
        Analyze S&R on multiple timeframes and find aligned levels
        
        Args:
            df_daily: Daily price DataFrame
        
        Returns:
            Dict with multi-timeframe S&R analysis
        """
        if df_daily is None or df_daily.empty:
            return {'available': False, 'reason': 'No data provided'}
        
        # Get daily S&R
        daily_sr = self.calculate_support_resistance(df_daily)
        
        # Simulate weekly data
        df_weekly = self.simulate_weekly_timeframe(df_daily)
        
        if df_weekly is None or len(df_weekly) < 10:
            return {
                'available': False,
                'reason': 'Insufficient data for weekly analysis',
                'daily_only': daily_sr
            }
        
        # Get weekly S&R
        weekly_sr = self.calculate_support_resistance(df_weekly)
        
        # Find aligned levels (within 2% tolerance)
        aligned_supports = []
        aligned_resistances = []
        
        tolerance = 0.02  # 2%
        
        # Check for aligned supports
        for d_supp in daily_sr['supports']:
            for w_supp in weekly_sr['supports']:
                if abs(d_supp['level'] - w_supp['level']) / w_supp['level'] < tolerance:
                    aligned_supports.append({
                        'level': round((d_supp['level'] + w_supp['level']) / 2, 2),
                        'daily_strength': d_supp['strength'],
                        'weekly_strength': w_supp['strength'],
                        'combined_strength': round((d_supp['strength'] + w_supp['strength']) / 2, 1),
                        'timeframes': ['Daily', 'Weekly'],
                        'confidence': 'VERY HIGH'
                    })
                    break
        
        # Check for aligned resistances
        for d_res in daily_sr['resistances']:
            for w_res in weekly_sr['resistances']:
                if abs(d_res['level'] - w_res['level']) / w_res['level'] < tolerance:
                    aligned_resistances.append({
                        'level': round((d_res['level'] + w_res['level']) / 2, 2),
                        'daily_strength': d_res['strength'],
                        'weekly_strength': w_res['strength'],
                        'combined_strength': round((d_res['strength'] + w_res['strength']) / 2, 1),
                        'timeframes': ['Daily', 'Weekly'],
                        'confidence': 'VERY HIGH'
                    })
                    break
        
        return {
            'available': True,
            'daily': daily_sr,
            'weekly': weekly_sr,
            'aligned_supports': aligned_supports,
            'aligned_resistances': aligned_resistances,
            'alignment_found': len(aligned_supports) > 0 or len(aligned_resistances) > 0
        }
    
    def generate_trading_signal(self, df: pd.DataFrame, sr_data: Dict, ma_data: Dict, 
                                breakouts: Dict, reversals: List[Dict]) -> Dict:
        """
        Generate comprehensive trading signal: STRONG BUY, BUY, HOLD, SELL, STRONG SELL
        
        Returns:
            Dict with signal, strength, reasons, and confidence score
        """
        current_price = sr_data['current_price']
        signal = 'HOLD'
        reasons = []
        strength = 'NEUTRAL'
        
        # STRONG BUY Conditions
        if sr_data['supports']:
            nearest_support = sr_data['supports'][0]
            support_dist = nearest_support['distance_pct']
            
            if support_dist < 2 and nearest_support['strength'] > 70:
                signal = 'STRONG BUY'
                reasons.append(f"Near STRONG support (₹{nearest_support['level']}, {support_dist:.1f}% away)")
                strength = 'VERY HIGH'
            elif support_dist < 3:
                if signal == 'HOLD':
                    signal = 'BUY'
                reasons.append(f"Near support (₹{nearest_support['level']}, {support_dist:.1f}% away)")
                strength = 'HIGH'
        
        # MA Trend
        if ma_data.get('available'):
            if ma_data['trend'] == 'STRONG BULLISH':
                if signal == 'HOLD':
                    signal = 'BUY'
                reasons.append("Strong bullish trend")
                if strength == 'NEUTRAL':
                    strength = 'MODERATE'
            elif ma_data['trend'] == 'STRONG BEARISH':
                if signal == 'HOLD':
                    signal = 'SELL'
                reasons.append("Strong bearish trend")
                if strength == 'NEUTRAL':
                    strength = 'MODERATE'
        
        # Breakouts
        if breakouts.get('breakout_detected'):
            for br in breakouts['breakouts']:
                if br['direction'] == 'BULLISH' and br['volume_confirmation']:
                    signal = 'STRONG BUY'
                    reasons.append(f"Bullish breakout above ₹{br['level']}")
                    strength = 'VERY HIGH'
                elif br['direction'] == 'BEARISH' and br['volume_confirmation']:
                    signal = 'STRONG SELL'
                    reasons.append(f"Bearish breakdown below ₹{br['level']}")
                    strength = 'VERY HIGH'
        
        # STRONG SELL Conditions
        if sr_data['resistances']:
            nearest_resistance = sr_data['resistances'][0]
            resistance_dist = nearest_resistance['distance_pct']
            
            if resistance_dist < 2 and nearest_resistance['strength'] > 70:
                if signal not in ['STRONG BUY', 'BUY']:
                    signal = 'STRONG SELL'
                    reasons.append(f"Near STRONG resistance (₹{nearest_resistance['level']}, {resistance_dist:.1f}% away)")
                    strength = 'VERY HIGH'
            elif resistance_dist < 3:
                if signal == 'HOLD':
                    signal = 'SELL'
                reasons.append(f"Near resistance (₹{nearest_resistance['level']}, {resistance_dist:.1f}% away)")
                if strength == 'NEUTRAL':
                    strength = 'HIGH'
        
        # Role Reversals
        for rev in reversals:
            if rev['type'] == 'RESISTANCE_TO_SUPPORT' and rev['confidence'] == 'High':
                if signal == 'HOLD':
                    signal = 'BUY'
                reasons.append(f"Role reversal: R→S at ₹{rev['level']}")
            elif rev['type'] == 'SUPPORT_TO_RESISTANCE' and rev['confidence'] == 'High':
                if signal == 'HOLD':
                    signal = 'SELL'
                reasons.append(f"Role reversal: S→R at ₹{rev['level']}")
        
        # Calculate confidence score
        base_score = {'VERY HIGH': 90, 'HIGH': 75, 'MODERATE': 60, 'NEUTRAL': 50}.get(strength, 50)
        bonus = min(10, len(reasons) * 3)
        confidence_score = min(100, base_score + bonus)
        
        return {
            'signal': signal,
            'strength': strength,
            'reasons': reasons,
            'confidence_score': confidence_score
        }

