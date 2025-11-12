# -*- coding: utf-8 -*-
"""
Interactive Chart Generator for S&R Analysis
============================================

Creates beautiful interactive Plotly charts with:
- Candlestick patterns
- Support & Resistance levels
- Pivot Points
- Fibonacci levels
- Moving Averages
- Volume bars
- Trade setup markers

Export as HTML or PNG
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional


class SRChartGenerator:
    """
    Generate professional interactive charts with S&R analysis
    """
    
    def __init__(self):
        """Initialize chart generator with default settings"""
        self.colors = {
            'support': '#00ff00',        # Green
            'resistance': '#ff0000',     # Red
            'pivot': '#0066ff',          # Blue
            'fibonacci': '#ff00ff',      # Magenta
            'ma50': '#ffaa00',          # Orange
            'ma200': '#00aaff',         # Cyan
            'bullish_candle': '#26a69a',  # Teal
            'bearish_candle': '#ef5350',  # Red
            'volume': '#1f77b4'          # Blue
        }
    
    def create_sr_chart(self, 
                        df: pd.DataFrame,
                        symbol: str,
                        sr_data: Dict,
                        dual_sr_data: Optional[Dict] = None,
                        pivot_data: Optional[Dict] = None,
                        fib_data: Optional[Dict] = None,
                        trade_setups: Optional[List[Dict]] = None,
                        show_volume: bool = True,
                        show_ma: bool = True) -> go.Figure:
        """
        Create comprehensive S&R chart with all levels marked
        
        Args:
            df: Price DataFrame with OHLCV data
            symbol: Stock symbol
            sr_data: S&R data dict
            pivot_data: Pivot points dict (optional)
            fib_data: Fibonacci levels dict (optional)
            trade_setups: Trade setups list (optional)
            show_volume: Show volume bars (default: True)
            show_ma: Show moving averages (default: True)
        
        Returns:
            Plotly Figure object
        """
        # Create subplots (price + volume)
        if show_volume:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3],
                subplot_titles=(f'{symbol} - S&R Analysis', 'Volume')
            )
        else:
            fig = go.Figure()
        
        # ===================================================================
        # CANDLESTICK CHART
        # ===================================================================
        candlestick = go.Candlestick(
            x=df.index if 'time' not in df.columns else df['time'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='OHLC',
            increasing_line_color=self.colors['bullish_candle'],
            decreasing_line_color=self.colors['bearish_candle']
        )
        
        if show_volume:
            fig.add_trace(candlestick, row=1, col=1)
        else:
            fig.add_trace(candlestick)
        
        # ===================================================================
        # DUAL S&R SYSTEM (If provided - NEW from Video Insights)
        # ===================================================================
        if dual_sr_data and not dual_sr_data.get('error'):
            # PRIMARY RESISTANCE (Solid Thick Lines - Wick Extremes)
            for res in dual_sr_data['primary']['resistances'][:3]:
                level = res['level']
                strength = res.get('strength', 50)
                
                fig.add_hline(
                    y=level,
                    line=dict(
                        color='#ff0000',  # Red
                        width=3,  # Thick for primary
                        dash='solid'
                    ),
                    annotation_text=f"PRIMARY R: ₹{level:.2f} (Wick High)",
                    annotation_position="right",
                    annotation_font_size=11,
                    annotation_font_color='#ff0000',
                    annotation_bgcolor='rgba(255,255,255,0.8)',
                    row=1 if show_volume else None,
                    col=1 if show_volume else None
                )
            
            # SECONDARY RESISTANCE (Dashed Lines - Battle Zones)
            for res in dual_sr_data['secondary']['resistances'][:3]:
                level = res['level']
                touches = res.get('touches', 0)
                
                fig.add_hline(
                    y=level,
                    line=dict(
                        color='#ff6600',  # Orange-Red
                        width=2,  # Thinner for secondary
                        dash='dash'
                    ),
                    annotation_text=f"Battle Zone R: ₹{level:.2f} ({touches}x)",
                    annotation_position="right",
                    annotation_font_size=10,
                    annotation_font_color='#ff6600',
                    annotation_bgcolor='rgba(255,255,255,0.7)',
                    row=1 if show_volume else None,
                    col=1 if show_volume else None
                )
            
            # PRIMARY SUPPORT (Solid Thick Lines - Wick Extremes)
            for sup in dual_sr_data['primary']['supports'][:3]:
                level = sup['level']
                strength = sup.get('strength', 50)
                
                fig.add_hline(
                    y=level,
                    line=dict(
                        color='#00ff00',  # Green
                        width=3,  # Thick for primary
                        dash='solid'
                    ),
                    annotation_text=f"PRIMARY S: ₹{level:.2f} (Wick Low)",
                    annotation_position="left",
                    annotation_font_size=11,
                    annotation_font_color='#00ff00',
                    annotation_bgcolor='rgba(255,255,255,0.8)',
                    row=1 if show_volume else None,
                    col=1 if show_volume else None
                )
            
            # SECONDARY SUPPORT (Dashed Lines - Battle Zones)
            for sup in dual_sr_data['secondary']['supports'][:3]:
                level = sup['level']
                touches = sup.get('touches', 0)
                
                fig.add_hline(
                    y=level,
                    line=dict(
                        color='#00cc00',  # Dark Green
                        width=2,  # Thinner for secondary
                        dash='dash'
                    ),
                    annotation_text=f"Battle Zone S: ₹{level:.2f} ({touches}x)",
                    annotation_position="left",
                    annotation_font_size=10,
                    annotation_font_color='#00cc00',
                    annotation_bgcolor='rgba(255,255,255,0.7)',
                    row=1 if show_volume else None,
                    col=1 if show_volume else None
                )
        
        # ===================================================================
        # SUPPORT LEVELS (Green Horizontal Lines) - Legacy Format
        # ===================================================================
        elif sr_data.get('supports'):
            for i, support in enumerate(sr_data['supports'][:5]):  # Top 5 supports
                level = support['level']
                strength = support['strength']
                touches = support['touches']
                
                # Line width based on strength
                line_width = 1 + (strength / 50)  # 1-3px width
                
                fig.add_hline(
                    y=level,
                    line=dict(
                        color=self.colors['support'],
                        width=line_width,
                        dash='solid' if strength > 70 else 'dash'
                    ),
                    annotation_text=f"S: ₹{level:.2f} ({touches} touches)",
                    annotation_position="left",
                    row=1 if show_volume else None,
                    col=1 if show_volume else None
                )
                
                # Add zone (shaded area)
                fig.add_hrect(
                    y0=support['zone_lower'],
                    y1=support['zone_upper'],
                    fillcolor=self.colors['support'],
                    opacity=0.1,
                    line_width=0,
                    row=1 if show_volume else None,
                    col=1 if show_volume else None
                )
        
        # ===================================================================
        # RESISTANCE LEVELS (Red Horizontal Lines)
        # ===================================================================
        if sr_data.get('resistances'):
            for i, resistance in enumerate(sr_data['resistances'][:5]):  # Top 5 resistances
                level = resistance['level']
                strength = resistance['strength']
                touches = resistance['touches']
                
                line_width = 1 + (strength / 50)
                
                fig.add_hline(
                    y=level,
                    line=dict(
                        color=self.colors['resistance'],
                        width=line_width,
                        dash='solid' if strength > 70 else 'dash'
                    ),
                    annotation_text=f"R: ₹{level:.2f} ({touches} touches)",
                    annotation_position="right",
                    row=1 if show_volume else None,
                    col=1 if show_volume else None
                )
                
                # Add zone
                fig.add_hrect(
                    y0=resistance['zone_lower'],
                    y1=resistance['zone_upper'],
                    fillcolor=self.colors['resistance'],
                    opacity=0.1,
                    line_width=0,
                    row=1 if show_volume else None,
                    col=1 if show_volume else None
                )
        
        # ===================================================================
        # PIVOT POINTS (Blue Dashed Lines)
        # ===================================================================
        if pivot_data and not pivot_data.get('error'):
            pivot_levels = {
                'Pivot': pivot_data.get('pivot'),
                'R1': pivot_data.get('r1'),
                'R2': pivot_data.get('r2'),
                'R3': pivot_data.get('r3'),
                'S1': pivot_data.get('s1'),
                'S2': pivot_data.get('s2'),
                'S3': pivot_data.get('s3')
            }
            
            for name, level in pivot_levels.items():
                if level:
                    fig.add_hline(
                        y=level,
                        line=dict(
                            color=self.colors['pivot'],
                            width=1,
                            dash='dot'
                        ),
                        annotation_text=f"{name}: ₹{level:.2f}",
                        annotation_position="left",
                        annotation_font_size=10,
                        row=1 if show_volume else None,
                        col=1 if show_volume else None
                    )
        
        # ===================================================================
        # FIBONACCI LEVELS (Magenta Dotted Lines)
        # ===================================================================
        if fib_data and not fib_data.get('error'):
            # Retracement levels
            for level_name, level_value in fib_data['retracement'].items():
                fig.add_hline(
                    y=level_value,
                    line=dict(
                        color=self.colors['fibonacci'],
                        width=1,
                        dash='dot'
                    ),
                    annotation_text=f"Fib {level_name}: ₹{level_value:.2f}",
                    annotation_position="right",
                    annotation_font_size=9,
                    row=1 if show_volume else None,
                    col=1 if show_volume else None
                )
            
            # Golden Zone (50-61.8%) - Highlighted
            golden_zone = fib_data.get('golden_zone', {})
            if golden_zone.get('lower') and golden_zone.get('upper'):
                fig.add_hrect(
                    y0=golden_zone['lower'],
                    y1=golden_zone['upper'],
                    fillcolor='gold',
                    opacity=0.15,
                    line_width=0,
                    annotation_text="Golden Zone",
                    annotation_position="top right",
                    row=1 if show_volume else None,
                    col=1 if show_volume else None
                )
        
        # ===================================================================
        # MOVING AVERAGES
        # ===================================================================
        if show_ma and len(df) >= 50:
            # Calculate EMAs if not already in dataframe
            if 'ema50' not in df.columns:
                df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
            if 'ema200' not in df.columns and len(df) >= 200:
                df['ema200'] = df['close'].ewm(span=200, adjust=False).mean()
            
            # EMA 50
            fig.add_trace(
                go.Scatter(
                    x=df.index if 'time' not in df.columns else df['time'],
                    y=df['ema50'],
                    name='EMA 50',
                    line=dict(color=self.colors['ma50'], width=1),
                    opacity=0.7
                ),
                row=1 if show_volume else None,
                col=1 if show_volume else None
            )
            
            # EMA 200
            if len(df) >= 200:
                fig.add_trace(
                    go.Scatter(
                        x=df.index if 'time' not in df.columns else df['time'],
                        y=df['ema200'],
                        name='EMA 200',
                        line=dict(color=self.colors['ma200'], width=1),
                        opacity=0.7
                    ),
                    row=1 if show_volume else None,
                    col=1 if show_volume else None
                )
        
        # ===================================================================
        # TRADE SETUP MARKERS
        # ===================================================================
        if trade_setups:
            for setup in trade_setups:
                if setup['type'] == 'BUY':
                    # Entry marker (green arrow up)
                    fig.add_annotation(
                        x=df.index[-1] if 'time' not in df.columns else df['time'].iloc[-1],
                        y=setup['entry_price'],
                        text="BUY",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1.5,
                        arrowwidth=2,
                        arrowcolor="green",
                        ax=0,
                        ay=40,
                        font=dict(color="white", size=10),
                        bgcolor="green",
                        bordercolor="white",
                        borderwidth=2,
                        row=1 if show_volume else None,
                        col=1 if show_volume else None
                    )
                    
                    # Stop Loss line
                    fig.add_hline(
                        y=setup['stop_loss'],
                        line=dict(color='red', width=1, dash='dash'),
                        annotation_text=f"SL: ₹{setup['stop_loss']:.2f}",
                        row=1 if show_volume else None,
                        col=1 if show_volume else None
                    )
                    
                    # Target lines
                    fig.add_hline(
                        y=setup['target1'],
                        line=dict(color='green', width=1, dash='dash'),
                        annotation_text=f"T1: ₹{setup['target1']:.2f}",
                        row=1 if show_volume else None,
                        col=1 if show_volume else None
                    )
                    
                elif setup['type'] == 'SELL':
                    # Entry marker (red arrow down)
                    fig.add_annotation(
                        x=df.index[-1] if 'time' not in df.columns else df['time'].iloc[-1],
                        y=setup['entry_price'],
                        text="SELL",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1.5,
                        arrowwidth=2,
                        arrowcolor="red",
                        ax=0,
                        ay=-40,
                        font=dict(color="white", size=10),
                        bgcolor="red",
                        bordercolor="white",
                        borderwidth=2,
                        row=1 if show_volume else None,
                        col=1 if show_volume else None
                    )
                    
                    # Stop Loss and Targets
                    fig.add_hline(
                        y=setup['stop_loss'],
                        line=dict(color='red', width=1, dash='dash'),
                        annotation_text=f"SL: ₹{setup['stop_loss']:.2f}",
                        row=1 if show_volume else None,
                        col=1 if show_volume else None
                    )
                    
                    fig.add_hline(
                        y=setup['target1'],
                        line=dict(color='green', width=1, dash='dash'),
                        annotation_text=f"T1: ₹{setup['target1']:.2f}",
                        row=1 if show_volume else None,
                        col=1 if show_volume else None
                    )
        
        # ===================================================================
        # VOLUME BARS
        # ===================================================================
        if show_volume:
            colors_volume = [self.colors['bullish_candle'] if row['close'] >= row['open'] 
                           else self.colors['bearish_candle'] for _, row in df.iterrows()]
            
            fig.add_trace(
                go.Bar(
                    x=df.index if 'time' not in df.columns else df['time'],
                    y=df['volume'],
                    name='Volume',
                    marker_color=colors_volume,
                    opacity=0.5
                ),
                row=2, col=1
            )
        
        # ===================================================================
        # LAYOUT & STYLING
        # ===================================================================
        fig.update_layout(
            title={
                'text': f"{symbol} - Support & Resistance Analysis",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#1f77b4', 'family': 'Arial Black'}
            },
            xaxis_rangeslider_visible=False,
            template='plotly_white',
            height=800 if show_volume else 600,
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Update axes
        fig.update_xaxes(title_text="Date", row=2 if show_volume else 1, col=1)
        fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
        if show_volume:
            fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return fig
    
    def export_chart(self, fig: go.Figure, filename: str, format: str = 'html'):
        """
        Export chart to file
        
        Args:
            fig: Plotly Figure
            filename: Output filename (without extension)
            format: 'html' or 'png' (default: 'html')
        """
        if format == 'html':
            fig.write_html(f"{filename}.html")
            print(f"✅ Chart saved: {filename}.html")
        elif format == 'png':
            fig.write_image(f"{filename}.png", width=1920, height=1080)
            print(f"✅ Chart saved: {filename}.png")
        else:
            print("❌ Invalid format! Use 'html' or 'png'")


# Export
__all__ = ['SRChartGenerator']

