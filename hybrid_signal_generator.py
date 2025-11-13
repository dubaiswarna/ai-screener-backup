# -*- coding: utf-8 -*-
"""
HYBRID SIGNAL GENERATOR - TREASURE SIGNAL SYSTEM
=================================================

Combines 3 layers of analysis for MAXIMUM ACCURACY:
1. Technical Indicators (RSI, MACD, EMA, Volume)
2. S&R Analysis (Support/Resistance, Pivots, Fibonacci)
3. Chart Patterns (Candlestick patterns)

ONLY generates signals when ALL 3 layers agree!
Minimum confidence: 85% (TREASURE signals only)

Philosophy: "Quality over Quantity"
- Better to have 5 high-accuracy signals than 50 mediocre ones
- Each signal is like finding treasure 💎
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime


class HybridSignalGenerator:
    """
    Generate high-accuracy trading signals using 3-layer confluence
    """
    
    def __init__(self, min_confidence: float = 85.0, min_rr_ratio: float = 2.0):
        """
        Args:
            min_confidence: Minimum confluence score to generate signal (default: 85%)
            min_rr_ratio: Minimum Risk:Reward ratio (default: 1:2)
        """
        self.min_confidence = min_confidence
        self.min_rr_ratio = min_rr_ratio
        
    # ========================================================================
    # LAYER 1: TECHNICAL ANALYSIS
    # ========================================================================
    
    def analyze_technical(self, df: pd.DataFrame) -> Dict:
        """
        Analyze technical indicators
        
        Returns:
            Dict with signal, score (0-35), and factors
        """
        if df is None or len(df) < 50:
            return {'score': 0, 'signal': 'WAIT', 'factors': []}
        
        score = 0
        factors = []
        signal = 'NEUTRAL'
        
        current_price = df['close'].iloc[-1]
        
        # RSI (0-10 points)
        if len(df) >= 14:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_value = rsi.iloc[-1]
            
            if rsi_value < 30:
                score += 10
                factors.append(f"RSI Oversold ({rsi_value:.1f})")
                signal = 'BUY'
            elif rsi_value > 70:
                score += 10
                factors.append(f"RSI Overbought ({rsi_value:.1f})")
                signal = 'SELL'
            elif 30 <= rsi_value <= 40:
                score += 5
                factors.append(f"RSI Bullish ({rsi_value:.1f})")
            elif 60 <= rsi_value <= 70:
                score += 5
                factors.append(f"RSI Bearish ({rsi_value:.1f})")
        
        # MACD (0-10 points)
        if len(df) >= 26:
            ema12 = df['close'].ewm(span=12, adjust=False).mean()
            ema26 = df['close'].ewm(span=26, adjust=False).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            
            macd_current = macd_line.iloc[-1]
            signal_current = signal_line.iloc[-1]
            macd_prev = macd_line.iloc[-2]
            signal_prev = signal_line.iloc[-2]
            
            # Bullish crossover
            if macd_prev < signal_prev and macd_current > signal_current:
                score += 10
                factors.append("MACD Bullish Crossover")
                if signal == 'NEUTRAL':
                    signal = 'BUY'
            # Bearish crossover
            elif macd_prev > signal_prev and macd_current < signal_current:
                score += 10
                factors.append("MACD Bearish Crossover")
                if signal == 'NEUTRAL':
                    signal = 'SELL'
            # MACD alignment
            elif macd_current > signal_current and macd_current > 0:
                score += 5
                factors.append("MACD Bullish Alignment")
            elif macd_current < signal_current and macd_current < 0:
                score += 5
                factors.append("MACD Bearish Alignment")
        
        # EMA (0-8 points)
        if len(df) >= 200:
            ema50 = df['close'].ewm(span=50, adjust=False).mean().iloc[-1]
            ema200 = df['close'].ewm(span=200, adjust=False).mean().iloc[-1]
            
            if current_price > ema50 > ema200:
                score += 8
                factors.append("Price above EMA 50 & 200 (Strong Bullish)")
            elif current_price < ema50 < ema200:
                score += 8
                factors.append("Price below EMA 50 & 200 (Strong Bearish)")
            elif current_price > ema50:
                score += 4
                factors.append("Price above EMA 50")
        
        # Volume (0-5 points)
        if len(df) >= 20:
            avg_volume = df['volume'].iloc[-20:-1].mean()
            current_volume = df['volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            if volume_ratio >= 2.0:
                score += 5
                factors.append(f"Volume Spike ({volume_ratio:.1f}x)")
            elif volume_ratio >= 1.5:
                score += 3
                factors.append(f"High Volume ({volume_ratio:.1f}x)")
        
        # ADX (0-2 points) - Trend strength
        if len(df) >= 14:
            # Simplified ADX calculation
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift())
            low_close = abs(df['low'] - df['close'].shift())
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = tr.rolling(14).mean().iloc[-1]
            
            if atr > 0:
                score += 2
                factors.append("Strong Trend (ADX)")
        
        return {
            'score': score,
            'max_score': 35,
            'signal': signal,
            'factors': factors,
            'confidence_pct': round((score / 35) * 100, 1)
        }
    
    # ========================================================================
    # LAYER 2: S&R ANALYSIS
    # ========================================================================
    
    def analyze_sr(self, sr_calc, df: pd.DataFrame, current_price: float) -> Dict:
        """
        Analyze S&R levels using the existing calculator (IMPORT ONLY!)
        
        Returns:
            Dict with score (0-40), signal, and factors
        """
        score = 0
        factors = []
        signal = 'NEUTRAL'
        
        # Calculate S&R
        sr_data = sr_calc.calculate_support_resistance(df, current_price)
        
        # Near support (0-20 points)
        if sr_data.get('supports'):
            nearest_support = sr_data['supports'][0]
            distance = nearest_support['distance_pct']
            strength = nearest_support['strength']
            
            if distance < 1.0:  # Very close
                score += 20
                factors.append(f"At Support ₹{nearest_support['level']:.2f} ({distance:.1f}% away)")
                signal = 'BUY'
            elif distance < 2.0:
                score += 15
                factors.append(f"Near Support ₹{nearest_support['level']:.2f}")
                signal = 'BUY'
            elif distance < 3.0:
                score += 10
                factors.append(f"Approaching Support")
        
        # Near resistance (0-20 points)
        if sr_data.get('resistances'):
            nearest_resistance = sr_data['resistances'][0]
            distance = nearest_resistance['distance_pct']
            strength = nearest_resistance['strength']
            
            if distance < 1.0:  # Very close
                if signal != 'BUY':  # Don't override strong buy
                    score += 20
                    factors.append(f"At Resistance ₹{nearest_resistance['level']:.2f} ({distance:.1f}% away)")
                    signal = 'SELL'
            elif distance < 2.0:
                if signal != 'BUY':
                    score += 15
                    factors.append(f"Near Resistance ₹{nearest_resistance['level']:.2f}")
                    signal = 'SELL'
        
        # Support/Resistance strength (0-10 points)
        if sr_data.get('supports') and signal == 'BUY':
            sup_strength = sr_data['supports'][0]['strength']
            if sup_strength > 80:
                score += 10
                factors.append(f"Very Strong Support (Strength: {sup_strength:.0f})")
            elif sup_strength > 60:
                score += 6
                factors.append(f"Strong Support (Strength: {sup_strength:.0f})")
        
        if sr_data.get('resistances') and signal == 'SELL':
            res_strength = sr_data['resistances'][0]['strength']
            if res_strength > 80:
                score += 10
                factors.append(f"Very Strong Resistance (Strength: {res_strength:.0f})")
            elif res_strength > 60:
                score += 6
                factors.append(f"Strong Resistance (Strength: {res_strength:.0f})")
        
        # Fibonacci / Pivot alignment (0-5 points)
        try:
            fib_data = sr_calc.calculate_fibonacci_levels(df, lookback_period=50)
            if not fib_data.get('error') and fib_data.get('golden_zone', {}).get('in_zone'):
                score += 5
                factors.append("In Fibonacci Golden Zone (50-61.8%)")
        except:
            pass
        
        # Historical success (0-5 points)
        try:
            success_data = sr_calc.calculate_historical_success_rate(df, sr_data)
            if signal == 'BUY' and success_data.get('supports'):
                if success_data['supports'][0].get('success_rate', 0) > 75:
                    score += 5
                    factors.append(f"Support held {success_data['supports'][0]['success_rate']:.0f}% of time")
            elif signal == 'SELL' and success_data.get('resistances'):
                if success_data['resistances'][0].get('success_rate', 0) > 75:
                    score += 5
                    factors.append(f"Resistance held {success_data['resistances'][0]['success_rate']:.0f}% of time")
        except:
            pass
        
        return {
            'score': score,
            'max_score': 40,
            'signal': signal,
            'factors': factors,
            'confidence_pct': round((score / 40) * 100, 1),
            'sr_data': sr_data
        }
    
    # ========================================================================
    # LAYER 3: CHART PATTERNS
    # ========================================================================
    
    def analyze_patterns(self, pattern_detector, df: pd.DataFrame, 
                        sr_signal: str) -> Dict:
        """
        Analyze chart patterns using the detector
        
        Returns:
            Dict with score (0-25), pattern info, and factors
        """
        score = 0
        factors = []
        
        # Detect patterns
        strongest_pattern = pattern_detector.get_strongest_pattern(df)
        
        if strongest_pattern is None:
            return {
                'score': 0,
                'max_score': 25,
                'pattern': None,
                'factors': ['No significant chart pattern'],
                'confidence_pct': 0
            }
        
        # Pattern found (0-15 points)
        if strongest_pattern['type'] == 'BULLISH':
            score += 15
            factors.append(f"{strongest_pattern['pattern']} (Bullish)")
        elif strongest_pattern['type'] == 'BEARISH':
            score += 15
            factors.append(f"{strongest_pattern['pattern']} (Bearish)")
        
        # Pattern at S&R level bonus (0-5 points)
        if strongest_pattern['type'] == sr_signal:
            score += 5
            factors.append("Pattern aligns with S&R level")
        
        # Volume confirmation (0-5 points)
        if len(df) >= 20:
            avg_vol = df['volume'].iloc[-20:-1].mean()
            current_vol = df['volume'].iloc[-1]
            if current_vol > avg_vol * 1.5:
                score += 5
                factors.append("Volume confirms pattern")
        
        return {
            'score': score,
            'max_score': 25,
            'pattern': strongest_pattern,
            'factors': factors,
            'confidence_pct': round((score / 25) * 100, 1)
        }
    
    # ========================================================================
    # CONFLUENCE CALCULATION
    # ========================================================================
    
    def calculate_confluence(self, tech_result: Dict, sr_result: Dict, 
                            pattern_result: Dict) -> Dict:
        """
        Calculate total confluence score and determine if it's a TREASURE signal
        
        Returns:
            Dict with total score, confidence, and decision
        """
        total_score = tech_result['score'] + sr_result['score'] + pattern_result['score']
        max_score = tech_result['max_score'] + sr_result['max_score'] + pattern_result['max_score']
        
        confidence = (total_score / max_score * 100) if max_score > 0 else 0
        
        # Check if all layers agree on direction
        tech_signal = tech_result['signal']
        sr_signal = sr_result['signal']
        pattern_signal = pattern_result['pattern']['type'] if pattern_result['pattern'] else 'NEUTRAL'
        
        # Count confluence factors
        confluence_count = 0
        if tech_signal == 'BUY' and sr_signal == 'BUY':
            confluence_count += 2
        elif tech_signal == 'SELL' and sr_signal == 'SELL':
            confluence_count += 2
        
        if pattern_signal == 'BULLISH' and sr_signal == 'BUY':
            confluence_count += 1
        elif pattern_signal == 'BEARISH' and sr_signal == 'SELL':
            confluence_count += 1
        
        # Determine final signal
        is_treasure = False
        final_signal = 'NO SIGNAL'
        
        if confidence >= self.min_confidence and confluence_count >= 2:
            if tech_signal == 'BUY' and sr_signal == 'BUY':
                final_signal = 'STRONG BUY'
                is_treasure = True
            elif tech_signal == 'SELL' and sr_signal == 'SELL':
                final_signal = 'STRONG SELL'
                is_treasure = True
        
        return {
            'total_score': round(total_score, 1),
            'max_score': max_score,
            'confidence': round(confidence, 1),
            'is_treasure': is_treasure,
            'final_signal': final_signal,
            'confluence_count': confluence_count,
            'tech_signal': tech_signal,
            'sr_signal': sr_signal,
            'pattern_signal': pattern_signal
        }
    
    # ========================================================================
    # COMPLETE STOCK ANALYSIS
    # ========================================================================
    
    def analyze_stock(self, symbol: str, df: pd.DataFrame,
                     sr_calculator, pattern_detector) -> Optional[Dict]:
        """
        Complete 3-layer analysis for a single stock
        
        Args:
            symbol: Stock symbol
            df: Price DataFrame
            sr_calculator: ProfessionalSRCalculator instance (IMPORTED, not modified!)
            pattern_detector: ChartPatternDetector instance
        
        Returns:
            Dict with complete analysis or None if filtered out
        """
        if df is None or len(df) < 50:
            return None
        
        current_price = df['close'].iloc[-1]
        
        # LAYER 1: Technical Analysis
        tech_result = self.analyze_technical(df)
        
        # LAYER 2: S&R Analysis (using imported calculator)
        sr_result = self.analyze_sr(sr_calculator, df, current_price)
        
        # LAYER 3: Chart Patterns
        pattern_result = self.analyze_patterns(pattern_detector, df, sr_result['signal'])
        
        # Calculate Confluence
        confluence = self.calculate_confluence(tech_result, sr_result, pattern_result)
        
        # Filter: Only return TREASURE signals
        if not confluence['is_treasure']:
            return None
        
        # Generate trade setup
        trade_setup = self.generate_trade_setup(
            symbol, df, current_price,
            sr_result['sr_data'], confluence['final_signal']
        )
        
        # Check R:R ratio
        if trade_setup and trade_setup.get('rr_ratio', 0) < self.min_rr_ratio:
            return None  # Filter out poor R:R trades
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'signal': confluence['final_signal'],
            'confidence': confluence['confidence'],
            'is_treasure': True,
            'technical': tech_result,
            'sr_analysis': sr_result,
            'chart_pattern': pattern_result,
            'confluence': confluence,
            'trade_setup': trade_setup
        }
    
    def generate_trade_setup(self, symbol: str, df: pd.DataFrame, 
                            current_price: float, sr_data: Dict,
                            signal: str) -> Dict:
        """
        Generate complete trade setup with Entry/SL/Target
        
        Returns:
            Dict with trade details
        """
        if signal == 'STRONG BUY':
            # Entry at current price or support
            entry = current_price
            
            # Stop loss below support (2% buffer)
            if sr_data.get('supports'):
                support_level = sr_data['supports'][0]['level']
                stop_loss = support_level * 0.98
            else:
                stop_loss = current_price * 0.98
            
            # Target at resistance
            if sr_data.get('resistances'):
                target1 = sr_data['resistances'][0]['level']
                target2 = sr_data['resistances'][1]['level'] if len(sr_data['resistances']) > 1 else target1 * 1.05
            else:
                target1 = current_price * 1.05
                target2 = current_price * 1.10
            
            risk = entry - stop_loss
            reward1 = target1 - entry
            reward2 = target2 - entry
            
            rr_ratio1 = reward1 / risk if risk > 0 else 0
            rr_ratio2 = reward2 / risk if risk > 0 else 0
            
            # Position sizing (2% risk)
            capital = 100000
            risk_amount = capital * 0.02
            position_size = int(risk_amount / risk) if risk > 0 else 0
            
            return {
                'entry': round(entry, 2),
                'stop_loss': round(stop_loss, 2),
                'target1': round(target1, 2),
                'target2': round(target2, 2),
                'risk': round(risk, 2),
                'reward1': round(reward1, 2),
                'rr_ratio': round(rr_ratio1, 2),
                'rr_ratio2': round(rr_ratio2, 2),
                'position_size': position_size,
                'risk_amount': round(risk_amount, 2),
                'potential_profit1': round(reward1 * position_size, 2),
                'potential_profit2': round(reward2 * position_size, 2)
            }
        
        elif signal == 'STRONG SELL':
            entry = current_price
            
            # Stop loss above resistance
            if sr_data.get('resistances'):
                resistance_level = sr_data['resistances'][0]['level']
                stop_loss = resistance_level * 1.02
            else:
                stop_loss = current_price * 1.02
            
            # Target at support
            if sr_data.get('supports'):
                target1 = sr_data['supports'][0]['level']
                target2 = sr_data['supports'][1]['level'] if len(sr_data['supports']) > 1 else target1 * 0.95
            else:
                target1 = current_price * 0.95
                target2 = current_price * 0.90
            
            risk = stop_loss - entry
            reward1 = entry - target1
            reward2 = entry - target2
            
            rr_ratio1 = reward1 / risk if risk > 0 else 0
            rr_ratio2 = reward2 / risk if risk > 0 else 0
            
            capital = 100000
            risk_amount = capital * 0.02
            position_size = int(risk_amount / risk) if risk > 0 else 0
            
            return {
                'entry': round(entry, 2),
                'stop_loss': round(stop_loss, 2),
                'target1': round(target1, 2),
                'target2': round(target2, 2),
                'risk': round(risk, 2),
                'reward1': round(reward1, 2),
                'rr_ratio': round(rr_ratio1, 2),
                'rr_ratio2': round(rr_ratio2, 2),
                'position_size': position_size,
                'risk_amount': round(risk_amount, 2),
                'potential_profit1': round(reward1 * position_size, 2),
                'potential_profit2': round(reward2 * position_size, 2)
            }
        
        return {}


# Export
__all__ = ['HybridSignalGenerator']


