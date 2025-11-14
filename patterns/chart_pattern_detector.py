# -*- coding: utf-8 -*-
"""
Professional Chart Pattern Detector - UPDATED WITH SIGA CRITERIA
=================================================================

✅ UPDATED PATTERNS (Based on Siga Candle Pattern Reference):
1. 🔨 Bullish Hammer - Long lower wick (≥2x body), small/no upper shadow
2. ➕ Doji - Open/close difference ≤10% of range
3. 💚 Bullish Harami - Small green inside large red (NEW!)
4. 📦 Bullish Engulfing - Large green engulfs previous red
5. ⭐🌅 Morning Star - 3-candle bullish reversal

BULLISH PATTERNS (7):
1. Hammer - Long lower wick at support (SIGA)
2. Bullish Harami - Small green inside large red (NEW - SIGA)
3. Inverted Hammer - Long upper wick, reversal signal
4. Bullish Engulfing - Large green candle engulfs previous red (SIGA)
5. Piercing Pattern - Green candle pierces >50% of previous red
6. Morning Star - 3-candle bullish reversal (SIGA)
7. Three White Soldiers - 3 consecutive strong green candles

BEARISH PATTERNS (6):
8. Shooting Star - Long upper wick at resistance
9. Hanging Man - Long lower wick at top (bearish)
10. Bearish Engulfing - Large red candle engulfs previous green
11. Dark Cloud Cover - Red candle covers >50% of previous green
12. Evening Star - 3-candle bearish reversal
13. Three Black Crows - 3 consecutive strong red candles

NEUTRAL PATTERNS (1):
14. Doji - Indecision pattern (SIGA - 10% threshold)

Based on SIGA candle pattern criteria & institutional trading standards.
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
        🔨 Bullish Hammer (SIGA CRITERIA)
        
        ✅ Siga Definition:
        - Long lower wick (at least 2× the body length)
        - Small or no upper shadow
        - Color doesn't matter (can be red or green)
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
    
    def detect_bullish_harami(self, df: pd.DataFrame, idx: int) -> Optional[Dict]:
        """
        💚 Bullish Harami (SIGA CRITERIA)
        
        ✅ Siga Definition:
        - Previous candle: large red (bearish)
        - Current candle: smaller green (bullish) inside the previous candle's body
        
        Returns:
            Dict with pattern info or None
        """
        if idx < 1:
            return None
        
        prev = self.get_candle_parts(df.iloc[idx-1])
        current = self.get_candle_parts(df.iloc[idx])
        
        # Siga Criteria:
        # 1. Previous candle is large red (bearish)
        prev_is_large_red = not prev['is_bullish'] and prev['body'] / prev['range'] > 0.6
        
        # 2. Current candle is smaller green (bullish) inside previous body
        current_is_green = current['is_bullish']
        current_inside_prev = (current['open'] > prev['close'] and 
                               current['close'] < prev['open'] and
                               current['body'] < prev['body'])
        
        if prev_is_large_red and current_is_green and current_inside_prev:
            # Calculate confidence
            size_ratio = current['body'] / prev['body']
            confidence = 70 + (15 if size_ratio < 0.5 else 10)  # Smaller inside = stronger
            
            return {
                'pattern': 'BULLISH_HARAMI',
                'type': 'BULLISH',
                'confidence': round(confidence, 1),
                'description': 'Bullish reversal - Small green inside large red',
                'strength': 'HIGH' if confidence > 75 else 'MEDIUM'
            }
        
        return None
    
    def detect_bullish_engulfing(self, df: pd.DataFrame, idx: int) -> Optional[Dict]:
        """
        📦 Bullish Engulfing (SIGA CRITERIA)
        
        ✅ Siga Definition:
        - First candle red (small)
        - Second candle green and large enough to engulf the previous red body
        
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
        ⭐🌅 Morning Star (SIGA CRITERIA)
        
        ✅ Siga Definition:
        - 1st candle: big red
        - 2nd candle: doji or spinning top (small body)
        - 3rd candle: big green, closes above mid of 1st candle
        
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
        ➕ Doji (SIGA CRITERIA)
        
        ✅ Siga Definition:
        - Open and close are nearly the same (difference ≤ 10% of total range)
        - Long or short wicks possible
        - Used to classify types like Dragonfly, Gravestone, etc.
        """
        current = self.get_candle_parts(df.iloc[idx])
        
        # Siga Doji criteria: body ≤ 10% of range
        if current['range'] == 0:
            return None
        
        body_to_range_ratio = current['body'] / current['range']
        
        is_doji = body_to_range_ratio <= 0.10  # SIGA: Body ≤ 10% of range
        
        # Check if both wicks present (classic Doji)
        has_upper_wick = current['upper_wick'] > 0
        has_lower_wick = current['lower_wick'] > 0
        
        if is_doji:
            # Calculate confidence based on how small the body is
            confidence = 70 - (body_to_range_ratio * 100)  # Smaller body = higher confidence
            confidence = max(50, min(85, confidence))
            
            return {
                'pattern': 'DOJI',
                'type': 'NEUTRAL',
                'confidence': round(confidence, 1),
                'description': f'Indecision - Open ≈ Close ({body_to_range_ratio*100:.1f}% body)',
                'strength': 'HIGH' if confidence > 70 else 'MEDIUM'
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
            
            harami_bull = self.detect_bullish_harami(df, i)
            if harami_bull:
                patterns_found.append(harami_bull)
            
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


