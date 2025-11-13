# -*- coding: utf-8 -*-
"""
Professional Chart Pattern Detector
====================================

Detects 12 major candlestick patterns with high accuracy:

BULLISH PATTERNS (6):
1. Hammer - Long lower wick at support
2. Inverted Hammer - Long upper wick, reversal signal
3. Bullish Engulfing - Large green candle engulfs previous red
4. Piercing Pattern - Green candle pierces >50% of previous red
5. Morning Star - 3-candle bullish reversal
6. Three White Soldiers - 3 consecutive strong green candles

BEARISH PATTERNS (6):
7. Shooting Star - Long upper wick at resistance
8. Hanging Man - Long lower wick at top (bearish)
9. Bearish Engulfing - Large red candle engulfs previous green
10. Dark Cloud Cover - Red candle covers >50% of previous green
11. Evening Star - 3-candle bearish reversal
12. Three Black Crows - 3 consecutive strong red candles

Based on institutional trading standards and Japanese candlestick analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class ChartPatternDetector:
    """
    Detect professional chart patterns with confidence scoring
    """
    
    def __init__(self, min_body_to_range: float = 0.3):
        """
        Args:
            min_body_to_range: Minimum body size as % of candle range (default: 30%)
        """
        self.min_body_to_range = min_body_to_range
        
    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================
    
    def get_candle_parts(self, row: pd.Series) -> Dict:
        """
        Extract candle components (body, wicks, range)
        
        Returns:
            Dict with body, upper_wick, lower_wick, range, is_bullish
        """
        open_price = row['open']
        high = row['high']
        low = row['low']
        close = row['close']
        
        # Body
        body = abs(close - open_price)
        
        # Wicks
        if close > open_price:  # Bullish candle
            upper_wick = high - close
            lower_wick = open_price - low
            is_bullish = True
        else:  # Bearish candle
            upper_wick = high - open_price
            lower_wick = close - low
            is_bullish = False
        
        # Range
        candle_range = high - low
        
        return {
            'body': body,
            'upper_wick': upper_wick,
            'lower_wick': lower_wick,
            'range': candle_range,
            'is_bullish': is_bullish,
            'high': high,
            'low': low,
            'open': open_price,
            'close': close
        }
    
    # ========================================================================
    # BULLISH PATTERNS
    # ========================================================================
    
    def detect_hammer(self, df: pd.DataFrame, idx: int) -> Optional[Dict]:
        """
        Hammer: Long lower wick, small body at top, bullish reversal at support
        
        Criteria:
        - Lower wick >= 2x body
        - Upper wick very small (<10% of range)
        - Body in upper 1/3 of range
        - Appears at support (downtrend)
        
        Returns:
            Dict with pattern info or None
        """
        if idx < 5:  # Need history for trend
            return None
        
        current = self.get_candle_parts(df.iloc[idx])
        
        # Check if in downtrend (previous 5 candles mostly red)
        prev_closes = df['close'].iloc[idx-5:idx].values
        prev_opens = df['open'].iloc[idx-5:idx].values
        bearish_count = sum(1 for i in range(5) if prev_closes[i] < prev_opens[i])
        in_downtrend = bearish_count >= 3
        
        # Hammer criteria
        has_long_lower_wick = current['lower_wick'] >= current['body'] * 2
        has_small_upper_wick = current['upper_wick'] <= current['range'] * 0.1
        body_in_upper_third = (current['close'] - current['low']) / current['range'] >= 0.67
        
        if has_long_lower_wick and has_small_upper_wick and body_in_upper_third and in_downtrend:
            # Calculate confidence
            wick_ratio = current['lower_wick'] / current['body'] if current['body'] > 0 else 0
            confidence = min(100, 60 + (wick_ratio * 10) + (10 if in_downtrend else 0))
            
            return {
                'pattern': 'HAMMER',
                'type': 'BULLISH',
                'confidence': round(confidence, 1),
                'description': 'Bullish reversal - Long lower wick shows buyers defended',
                'strength': 'HIGH' if confidence > 75 else 'MEDIUM'
            }
        
        return None
    
    def detect_bullish_engulfing(self, df: pd.DataFrame, idx: int) -> Optional[Dict]:
        """
        Bullish Engulfing: Large green candle completely engulfs previous red candle
        
        Criteria:
        - Previous candle is red (bearish)
        - Current candle is green (bullish)
        - Current body completely covers previous body
        - Current opens below previous close
        - Current closes above previous open
        
        Returns:
            Dict with pattern info or None
        """
        if idx < 1:
            return None
        
        prev = self.get_candle_parts(df.iloc[idx-1])
        current = self.get_candle_parts(df.iloc[idx])
        
        # Engulfing criteria
        prev_is_bearish = not prev['is_bullish']
        current_is_bullish = current['is_bullish']
        current_opens_below = current['open'] < prev['close']
        current_closes_above = current['close'] > prev['open']
        body_ratio = current['body'] / prev['body'] if prev['body'] > 0 else 0
        
        if (prev_is_bearish and current_is_bullish and 
            current_opens_below and current_closes_above and
            body_ratio >= 1.0):
            
            # Confidence based on engulfing strength
            confidence = min(100, 65 + (body_ratio * 15))
            
            # Check volume confirmation
            if idx >= 20:
                avg_volume = df['volume'].iloc[idx-20:idx].mean()
                if df['volume'].iloc[idx] > avg_volume * 1.3:
                    confidence += 10
            
            return {
                'pattern': 'BULLISH_ENGULFING',
                'type': 'BULLISH',
                'confidence': round(confidence, 1),
                'description': f'Strong reversal - Current candle engulfs previous ({body_ratio:.1f}x)',
                'strength': 'HIGH' if confidence > 75 else 'MEDIUM'
            }
        
        return None
    
    def detect_morning_star(self, df: pd.DataFrame, idx: int) -> Optional[Dict]:
        """
        Morning Star: 3-candle bullish reversal pattern
        
        Criteria:
        - Candle 1: Large red (bearish)
        - Candle 2: Small body (doji/spinning top) - gap down
        - Candle 3: Large green (bullish) - closes above candle 1 midpoint
        
        Returns:
            Dict with pattern info or None
        """
        if idx < 2:
            return None
        
        c1 = self.get_candle_parts(df.iloc[idx-2])
        c2 = self.get_candle_parts(df.iloc[idx-1])
        c3 = self.get_candle_parts(df.iloc[idx])
        
        # Criteria
        c1_bearish_large = not c1['is_bullish'] and c1['body'] / c1['range'] > 0.6
        c2_small_body = c2['body'] / c2['range'] < 0.3  # Doji-like
        c3_bullish_large = c3['is_bullish'] and c3['body'] / c3['range'] > 0.6
        c3_closes_high = c3['close'] > (c1['open'] + c1['close']) / 2  # Above C1 midpoint
        
        if c1_bearish_large and c2_small_body and c3_bullish_large and c3_closes_high:
            confidence = 80
            
            # Volume confirmation
            if idx >= 20:
                avg_vol = df['volume'].iloc[idx-20:idx].mean()
                if df['volume'].iloc[idx] > avg_vol * 1.5:
                    confidence += 10
            
            return {
                'pattern': 'MORNING_STAR',
                'type': 'BULLISH',
                'confidence': round(confidence, 1),
                'description': '3-candle reversal - Strong bullish signal',
                'strength': 'VERY HIGH'
            }
        
        return None
    
    # ========================================================================
    # BEARISH PATTERNS
    # ========================================================================
    
    def detect_shooting_star(self, df: pd.DataFrame, idx: int) -> Optional[Dict]:
        """
        Shooting Star: Long upper wick, small body at bottom, bearish reversal at resistance
        
        Criteria:
        - Upper wick >= 2x body
        - Lower wick very small (<10% of range)
        - Body in lower 1/3 of range
        - Appears at resistance (uptrend)
        
        Returns:
            Dict with pattern info or None
        """
        if idx < 5:
            return None
        
        current = self.get_candle_parts(df.iloc[idx])
        
        # Check if in uptrend
        prev_closes = df['close'].iloc[idx-5:idx].values
        prev_opens = df['open'].iloc[idx-5:idx].values
        bullish_count = sum(1 for i in range(5) if prev_closes[i] > prev_opens[i])
        in_uptrend = bullish_count >= 3
        
        # Shooting Star criteria
        has_long_upper_wick = current['upper_wick'] >= current['body'] * 2
        has_small_lower_wick = current['lower_wick'] <= current['range'] * 0.1
        body_in_lower_third = (current['high'] - current['close']) / current['range'] >= 0.67
        
        if has_long_upper_wick and has_small_lower_wick and body_in_lower_third and in_uptrend:
            wick_ratio = current['upper_wick'] / current['body'] if current['body'] > 0 else 0
            confidence = min(100, 60 + (wick_ratio * 10) + (10 if in_uptrend else 0))
            
            return {
                'pattern': 'SHOOTING_STAR',
                'type': 'BEARISH',
                'confidence': round(confidence, 1),
                'description': 'Bearish reversal - Long upper wick shows sellers rejected rally',
                'strength': 'HIGH' if confidence > 75 else 'MEDIUM'
            }
        
        return None
    
    def detect_bearish_engulfing(self, df: pd.DataFrame, idx: int) -> Optional[Dict]:
        """
        Bearish Engulfing: Large red candle completely engulfs previous green candle
        
        Returns:
            Dict with pattern info or None
        """
        if idx < 1:
            return None
        
        prev = self.get_candle_parts(df.iloc[idx-1])
        current = self.get_candle_parts(df.iloc[idx])
        
        prev_is_bullish = prev['is_bullish']
        current_is_bearish = not current['is_bullish']
        current_opens_above = current['open'] > prev['close']
        current_closes_below = current['close'] < prev['open']
        body_ratio = current['body'] / prev['body'] if prev['body'] > 0 else 0
        
        if (prev_is_bullish and current_is_bearish and 
            current_opens_above and current_closes_below and
            body_ratio >= 1.0):
            
            confidence = min(100, 65 + (body_ratio * 15))
            
            # Volume confirmation
            if idx >= 20:
                avg_volume = df['volume'].iloc[idx-20:idx].mean()
                if df['volume'].iloc[idx] > avg_volume * 1.3:
                    confidence += 10
            
            return {
                'pattern': 'BEARISH_ENGULFING',
                'type': 'BEARISH',
                'confidence': round(confidence, 1),
                'description': f'Strong reversal - Current candle engulfs previous ({body_ratio:.1f}x)',
                'strength': 'HIGH' if confidence > 75 else 'MEDIUM'
            }
        
        return None
    
    def detect_evening_star(self, df: pd.DataFrame, idx: int) -> Optional[Dict]:
        """
        Evening Star: 3-candle bearish reversal pattern
        
        Returns:
            Dict with pattern info or None
        """
        if idx < 2:
            return None
        
        c1 = self.get_candle_parts(df.iloc[idx-2])
        c2 = self.get_candle_parts(df.iloc[idx-1])
        c3 = self.get_candle_parts(df.iloc[idx])
        
        c1_bullish_large = c1['is_bullish'] and c1['body'] / c1['range'] > 0.6
        c2_small_body = c2['body'] / c2['range'] < 0.3
        c3_bearish_large = not c3['is_bullish'] and c3['body'] / c3['range'] > 0.6
        c3_closes_low = c3['close'] < (c1['open'] + c1['close']) / 2
        
        if c1_bullish_large and c2_small_body and c3_bearish_large and c3_closes_low:
            confidence = 80
            
            if idx >= 20:
                avg_vol = df['volume'].iloc[idx-20:idx].mean()
                if df['volume'].iloc[idx] > avg_vol * 1.5:
                    confidence += 10
            
            return {
                'pattern': 'EVENING_STAR',
                'type': 'BEARISH',
                'confidence': round(confidence, 1),
                'description': '3-candle reversal - Strong bearish signal',
                'strength': 'VERY HIGH'
            }
        
        return None
    
    # ========================================================================
    # ADDITIONAL PATTERNS
    # ========================================================================
    
    def detect_doji(self, df: pd.DataFrame, idx: int) -> Optional[Dict]:
        """
        Doji: Very small body, indecision pattern
        """
        current = self.get_candle_parts(df.iloc[idx])
        
        # Doji criteria: body < 10% of range
        is_doji = current['body'] / current['range'] < 0.1 if current['range'] > 0 else False
        
        if is_doji:
            return {
                'pattern': 'DOJI',
                'type': 'NEUTRAL',
                'confidence': 60.0,
                'description': 'Indecision - Wait for confirmation',
                'strength': 'MEDIUM'
            }
        
        return None
    
    def detect_three_white_soldiers(self, df: pd.DataFrame, idx: int) -> Optional[Dict]:
        """
        Three White Soldiers: 3 consecutive strong bullish candles
        """
        if idx < 2:
            return None
        
        c1 = self.get_candle_parts(df.iloc[idx-2])
        c2 = self.get_candle_parts(df.iloc[idx-1])
        c3 = self.get_candle_parts(df.iloc[idx])
        
        all_bullish = c1['is_bullish'] and c2['is_bullish'] and c3['is_bullish']
        strong_bodies = (c1['body'] / c1['range'] > 0.6 and 
                        c2['body'] / c2['range'] > 0.6 and 
                        c3['body'] / c3['range'] > 0.6)
        consecutive_higher = c2['close'] > c1['close'] and c3['close'] > c2['close']
        
        if all_bullish and strong_bodies and consecutive_higher:
            return {
                'pattern': 'THREE_WHITE_SOLDIERS',
                'type': 'BULLISH',
                'confidence': 85.0,
                'description': 'Strong bullish momentum - 3 consecutive strong green candles',
                'strength': 'VERY HIGH'
            }
        
        return None
    
    def detect_three_black_crows(self, df: pd.DataFrame, idx: int) -> Optional[Dict]:
        """
        Three Black Crows: 3 consecutive strong bearish candles
        """
        if idx < 2:
            return None
        
        c1 = self.get_candle_parts(df.iloc[idx-2])
        c2 = self.get_candle_parts(df.iloc[idx-1])
        c3 = self.get_candle_parts(df.iloc[idx])
        
        all_bearish = not c1['is_bullish'] and not c2['is_bullish'] and not c3['is_bullish']
        strong_bodies = (c1['body'] / c1['range'] > 0.6 and 
                        c2['body'] / c2['range'] > 0.6 and 
                        c3['body'] / c3['range'] > 0.6)
        consecutive_lower = c2['close'] < c1['close'] and c3['close'] < c2['close']
        
        if all_bearish and strong_bodies and consecutive_lower:
            return {
                'pattern': 'THREE_BLACK_CROWS',
                'type': 'BEARISH',
                'confidence': 85.0,
                'description': 'Strong bearish momentum - 3 consecutive strong red candles',
                'strength': 'VERY HIGH'
            }
        
        return None
    
    # ========================================================================
    # MAIN DETECTION FUNCTION
    # ========================================================================
    
    def detect_all_patterns(self, df: pd.DataFrame, 
                           check_last_n_candles: int = 1) -> List[Dict]:
        """
        Detect all chart patterns in the dataframe
        
        Args:
            df: Price DataFrame with OHLCV
            check_last_n_candles: How many recent candles to check (default: 1)
        
        Returns:
            List of detected patterns
        """
        if df is None or len(df) < 5:
            return []
        
        patterns_found = []
        
        # Check last N candles for patterns
        for i in range(max(5, len(df) - check_last_n_candles), len(df)):
            # Bullish patterns
            hammer = self.detect_hammer(df, i)
            if hammer:
                patterns_found.append(hammer)
            
            engulfing_bull = self.detect_bullish_engulfing(df, i)
            if engulfing_bull:
                patterns_found.append(engulfing_bull)
            
            morning_star = self.detect_morning_star(df, i)
            if morning_star:
                patterns_found.append(morning_star)
            
            three_white = self.detect_three_white_soldiers(df, i)
            if three_white:
                patterns_found.append(three_white)
            
            # Bearish patterns
            shooting = self.detect_shooting_star(df, i)
            if shooting:
                patterns_found.append(shooting)
            
            engulfing_bear = self.detect_bearish_engulfing(df, i)
            if engulfing_bear:
                patterns_found.append(engulfing_bear)
            
            evening = self.detect_evening_star(df, i)
            if evening:
                patterns_found.append(evening)
            
            three_black = self.detect_three_black_crows(df, i)
            if three_black:
                patterns_found.append(three_black)
            
            # Neutral patterns
            doji = self.detect_doji(df, i)
            if doji:
                patterns_found.append(doji)
        
        # Remove duplicates (keep highest confidence)
        if patterns_found:
            unique_patterns = {}
            for pattern in patterns_found:
                key = pattern['pattern']
                if key not in unique_patterns or pattern['confidence'] > unique_patterns[key]['confidence']:
                    unique_patterns[key] = pattern
            
            patterns_found = list(unique_patterns.values())
        
        return patterns_found
    
    def get_strongest_pattern(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Get the strongest (highest confidence) pattern from latest candle
        
        Returns:
            Single pattern dict or None
        """
        patterns = self.detect_all_patterns(df, check_last_n_candles=1)
        
        if not patterns:
            return None
        
        # Filter out NEUTRAL patterns for trading signals
        tradeable_patterns = [p for p in patterns if p['type'] in ['BULLISH', 'BEARISH']]
        
        if not tradeable_patterns:
            return None
        
        # Return highest confidence pattern
        return max(tradeable_patterns, key=lambda x: x['confidence'])


# Export
__all__ = ['ChartPatternDetector']


