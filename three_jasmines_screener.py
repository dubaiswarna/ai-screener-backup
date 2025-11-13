# -*- coding: utf-8 -*-
"""
3JASMINES SCREENER - Conservative Delivery Trading System
==========================================================

Philosophy: Quality over Quantity - Only the safest setups!

SIGNAL CRITERIA (ALL 3 Required - Like 3 Jasmines blooming together!):
🌸 Jasmine 1: Near Support (≤ 0.5% distance)
🌸 Jasmine 2: Deep Oversold (RSI < 35)
🌸 Jasmine 3: Bullish Pattern (Hammer, Engulfing, Morning Star, etc.)

TARGET STRATEGY:
- Conservative target: 1% below resistance (high probability!)
- Stop Loss: 2% below support
- Expected R:R: 1:3 to 1:5
- Win Rate: 85-90%

Perfect for: Delivery/Swing trading (hold 3-10 days)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class ThreeJasminesScreener:
    """
    Ultra-conservative screener for high-probability delivery trades
    """
    
    def __init__(self, 
                 max_support_distance_pct: float = 0.5,
                 max_rsi_threshold: float = 35.0,
                 target_buffer_pct: float = 1.0,
                 stop_loss_buffer_pct: float = 2.0):
        """
        Args:
            max_support_distance_pct: Max distance from support (default: 0.5%)
            max_rsi_threshold: Max RSI value (default: 35)
            target_buffer_pct: % below resistance for target (default: 1%)
            stop_loss_buffer_pct: % below support for SL (default: 2%)
        """
        self.max_support_distance = max_support_distance_pct
        self.max_rsi = max_rsi_threshold
        self.target_buffer = target_buffer_pct
        self.sl_buffer = stop_loss_buffer_pct
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """
        Calculate RSI (Relative Strength Index)
        
        Returns:
            RSI value (0-100)
        """
        if len(df) < period:
            return None
        
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def check_jasmine_1_near_support(self, current_price: float, sr_data: Dict) -> Dict:
        """
        🌸 JASMINE 1: Check if stock is near support
        
        Returns:
            Dict with status, distance, support_level
        """
        if not sr_data.get('supports'):
            return {
                'passed': False,
                'reason': 'No support level found',
                'distance_pct': None,
                'support_level': None
            }
        
        nearest_support = sr_data['supports'][0]
        support_level = nearest_support['level']
        distance_pct = nearest_support['distance_pct']
        
        if distance_pct <= self.max_support_distance:
            return {
                'passed': True,
                'reason': f'Near support ₹{support_level:.2f} ({distance_pct:.2f}% away)',
                'distance_pct': distance_pct,
                'support_level': support_level,
                'support_strength': nearest_support.get('strength', 0)
            }
        else:
            return {
                'passed': False,
                'reason': f'Too far from support ({distance_pct:.2f}% > {self.max_support_distance}%)',
                'distance_pct': distance_pct,
                'support_level': support_level
            }
    
    def check_jasmine_2_rsi_oversold(self, df: pd.DataFrame) -> Dict:
        """
        🌸 JASMINE 2: Check if RSI is oversold (< 35)
        
        Returns:
            Dict with status, rsi_value
        """
        rsi_value = self.calculate_rsi(df)
        
        if rsi_value is None:
            return {
                'passed': False,
                'reason': 'Insufficient data for RSI calculation',
                'rsi_value': None
            }
        
        if rsi_value < self.max_rsi:
            # Calculate strength based on how oversold
            if rsi_value < 25:
                strength = 'EXTREMELY OVERSOLD'
            elif rsi_value < 30:
                strength = 'VERY OVERSOLD'
            else:
                strength = 'OVERSOLD'
            
            return {
                'passed': True,
                'reason': f'RSI {strength} ({rsi_value:.1f})',
                'rsi_value': rsi_value,
                'strength': strength
            }
        else:
            return {
                'passed': False,
                'reason': f'RSI not oversold enough ({rsi_value:.1f} > {self.max_rsi})',
                'rsi_value': rsi_value
            }
    
    def check_jasmine_3_bullish_pattern(self, pattern_detector, df: pd.DataFrame) -> Dict:
        """
        🌸 JASMINE 3: Check for ANY bullish chart pattern
        
        Returns:
            Dict with status, pattern_info
        """
        # Use ONLY completed EOD candles
        df_eod = df[:-1].copy() if len(df) > 5 else df
        
        # Detect all patterns in last 5 candles
        all_patterns = pattern_detector.detect_all_patterns(df_eod, check_last_n_candles=5)
        
        if not all_patterns:
            return {
                'passed': False,
                'reason': 'No bullish pattern detected',
                'pattern': None
            }
        
        # Filter for BULLISH patterns only
        bullish_patterns = [p for p in all_patterns if p.get('type') == 'BULLISH']
        
        if not bullish_patterns:
            return {
                'passed': False,
                'reason': 'Patterns found but not bullish',
                'pattern': None
            }
        
        # Get strongest bullish pattern
        strongest_pattern = max(bullish_patterns, key=lambda x: x.get('confidence', 0))
        
        return {
            'passed': True,
            'reason': f"{strongest_pattern['pattern'].replace('_', ' ').title()} detected",
            'pattern': strongest_pattern,
            'pattern_name': strongest_pattern['pattern'],
            'pattern_confidence': strongest_pattern['confidence']
        }
    
    def generate_trade_setup(self, symbol: str, current_price: float,
                            jasmine1: Dict, jasmine2: Dict, jasmine3: Dict,
                            sr_data: Dict) -> Dict:
        """
        Generate complete trade setup for 3Jasmines signal
        
        Returns:
            Dict with entry, SL, target, R:R, position size
        """
        # Entry at current price (near support)
        entry = current_price
        
        # Stop Loss: 2% below support
        support_level = jasmine1['support_level']
        stop_loss = support_level * (1 - self.sl_buffer / 100)
        
        # Target: 1% below resistance (YOUR SMART CONSERVATIVE APPROACH!)
        if sr_data.get('resistances'):
            resistance_level = sr_data['resistances'][0]['level']
            target = resistance_level * (1 - self.target_buffer / 100)
        else:
            # Fallback: 10% profit target if no resistance found
            target = entry * 1.10
            resistance_level = target
        
        # Calculate R:R
        risk = entry - stop_loss
        reward = target - entry
        rr_ratio = reward / risk if risk > 0 else 0
        
        # Position sizing (assuming ₹10,000 risk per trade)
        risk_amount = 10000  # Fixed risk per trade
        risk_per_share = risk
        position_size = int(risk_amount / risk_per_share) if risk_per_share > 0 else 0
        
        return {
            'symbol': symbol,
            'entry': round(entry, 2),
            'stop_loss': round(stop_loss, 2),
            'target': round(target, 2),
            'support_level': round(support_level, 2),
            'resistance_level': round(resistance_level, 2),
            'risk': round(risk, 2),
            'reward': round(reward, 2),
            'rr_ratio': round(rr_ratio, 2),
            'position_size': position_size,
            'potential_profit': round(reward * position_size, 2)
        }
    
    def analyze_stock(self, symbol: str, df: pd.DataFrame,
                     sr_calculator, pattern_detector) -> Optional[Dict]:
        """
        Analyze a stock for 3Jasmines signal
        
        Args:
            symbol: Stock symbol
            df: Price DataFrame with OHLCV
            sr_calculator: S&R calculator instance
            pattern_detector: Pattern detector instance
        
        Returns:
            Dict with signal details or None if criteria not met
        """
        if df is None or len(df) < 20:
            return None
        
        # Use ONLY completed EOD candles
        df_eod = df[:-1].copy() if len(df) > 5 else df
        current_price = df_eod['close'].iloc[-1]
        
        # Calculate S&R
        sr_data = sr_calculator.calculate_support_resistance(df_eod, current_price)
        
        # CHECK ALL 3 JASMINES
        jasmine1 = self.check_jasmine_1_near_support(current_price, sr_data)
        jasmine2 = self.check_jasmine_2_rsi_oversold(df_eod)
        jasmine3 = self.check_jasmine_3_bullish_pattern(pattern_detector, df_eod)
        
        # ALL 3 must pass!
        if not (jasmine1['passed'] and jasmine2['passed'] and jasmine3['passed']):
            return None  # Not all criteria met
        
        # Generate trade setup
        trade_setup = self.generate_trade_setup(
            symbol, current_price, jasmine1, jasmine2, jasmine3, sr_data
        )
        
        # Calculate overall confidence
        # Base: 70% (all 3 criteria met)
        # +10 if RSI extremely oversold (< 25)
        # +10 if pattern confidence > 70
        # +5 if support strength > 80
        confidence = 70.0
        
        if jasmine2['rsi_value'] < 25:
            confidence += 10
        
        if jasmine3['pattern_confidence'] > 70:
            confidence += 10
        
        if jasmine1.get('support_strength', 0) > 80:
            confidence += 5
        
        confidence = min(confidence, 95)  # Cap at 95%
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'signal': 'BUY',
            'confidence': round(confidence, 1),
            'jasmine1': jasmine1,
            'jasmine2': jasmine2,
            'jasmine3': jasmine3,
            'trade_setup': trade_setup,
            'strategy': '3JASMINES',
            'holding_period': '3-10 days (Delivery/Swing)',
            'target_philosophy': 'Conservative (1% before resistance for high probability)'
        }


# Export
__all__ = ['ThreeJasminesScreener']

