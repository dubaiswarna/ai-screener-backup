# -*- coding: utf-8 -*-
"""
Support & Resistance Level Viewer
Interactive tool to view S&R levels for any stock
"""

import sys
import os

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from typing import Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sr_calculator import SupportResistanceCalculator
try:
    from dhanhq import dhanhq
except:
    dhanhq = None

# Try to import Excel loader
ExcelDataLoader = None
try:
    ai_screener_path = Path(__file__).parent.parent / 'ai_screener'
    sys.path.insert(0, str(ai_screener_path))
    from excel_data_loader import ExcelDataLoader
    print(f"[OK] ExcelDataLoader imported from {ai_screener_path}")
except Exception as e:
    print(f"[ERROR] Failed to import ExcelDataLoader: {e}")
    import traceback
    traceback.print_exc()

# Page config
st.set_page_config(
    page_title="Support & Resistance Analyzer",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# STYLING
# ============================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 30px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .support-level {
        background-color: #e8f5e9;
        padding: 10px;
        border-left: 4px solid #4caf50;
        margin: 5px 0;
    }
    .resistance-level {
        background-color: #ffebee;
        padding: 10px;
        border-left: 4px solid #f44336;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DHAN API SETUP
# ============================================================

@st.cache_resource
def init_dhan():
    """Initialize Dhan API client"""
    try:
        client_id = "1104147457"
        access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzYyNDkwMDUxLCJpYXQiOjE3NjI0MDM2NTEsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTA0MTQ3NDU3In0.H91FqXQGRmtfJ229QDO8j_u-l6e79oBjascO9kd7vkmRZEuN0IEKYT6M64pYfZlun2iJJ3Ra8YZyrSLRYreqTg"
        dhan = dhanhq(client_id, access_token)
        return dhan
    except Exception as e:
        st.error(f"Dhan API initialization failed: {e}")
        return None

# ============================================================
# DATA FETCHING
# ============================================================

@st.cache_resource(ttl=3600)
def load_excel_data():
    """Load Excel data once"""
    if ExcelDataLoader is None:
        st.error("[ERROR] ExcelDataLoader not imported")
        return None
    try:
        excel_file = r"C:\python\MG AI\Nifty200_Complete_10yeardata.xlsx"
        import os
        if not os.path.exists(excel_file):
            st.error(f"[ERROR] Excel file not found: {excel_file}")
            return None
        loader = ExcelDataLoader(excel_file)
        return loader
    except Exception as e:
        st.error(f"[ERROR] Error loading Excel: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None

def get_stock_data(symbol: str, timeframe: str = "1D") -> pd.DataFrame:
    """
    Fetch stock data from Excel file (faster and more reliable)
    
    Args:
        symbol: Stock symbol (e.g., RELIANCE, TCS)
        timeframe: 1D (daily)
    
    Returns:
        DataFrame with OHLCV data
    """
    try:
        # Try Excel first (faster and more reliable)
        loader = load_excel_data()
        
        if loader is None:
            st.error("[ERROR] Excel data loader failed to initialize")
            st.info("Check if file exists: C:\\python\\MG AI\\Nifty200_Complete_10yeardata.xlsx")
            return None
        
        if loader is not None:
            # Use symbol as-is (Excel has symbols without NSE_ prefix)
            df = loader.get_stock_data(symbol.upper())
            
            if df is None:
                st.warning(f"[WARNING] Excel loader returned None for {symbol}")
            
            if df is not None and not df.empty:
                # Ensure required columns
                if 'date' in df.columns:
                    df = df.rename(columns={'date': 'time'})
                
                if 'time' not in df.columns and 'Date' in df.columns:
                    df = df.rename(columns={'Date': 'time'})
                
                # Ensure lowercase column names
                df.columns = [col.lower() for col in df.columns]
                
                # Ensure we have all required columns
                required = ['time', 'open', 'high', 'low', 'close', 'volume']
                missing = [col for col in required if col not in df.columns]
                
                if not missing:
                    df = df[required].copy()
                    df['time'] = pd.to_datetime(df['time'], utc=True).dt.tz_localize(None)
                    df = df.sort_values('time').reset_index(drop=True)
                    
                    # Return last 1 year of data
                    one_year_ago = pd.Timestamp.now() - pd.Timedelta(days=365)
                    df = df[df['time'] >= one_year_ago]
                    
                    if not df.empty:
                        return df
                    else:
                        st.warning(f"[WARNING] {symbol}: No recent data (last year)")
                        return None
                else:
                    st.error(f"[ERROR] Missing columns: {missing}")
                    return None
        
        # Get list of available stocks
        available = []
        if loader is not None:
            available = loader.get_all_available_stocks()[:20]  # First 20
        
        st.error(f"[ERROR] No data found for {symbol}")
        if available:
            st.info(f"Available stocks (first 20): {', '.join(available)}")
        return None
            
    except Exception as e:
        st.error(f"[ERROR] Error fetching data: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None

# ============================================================
# VISUALIZATION
# ============================================================

def plot_sr_levels(df: pd.DataFrame, sr_data: Dict):
    """
    Plot candlestick chart with S&R levels marked
    """
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=('Price with S&R Levels', 'Volume')
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df['time'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price'
        ),
        row=1, col=1
    )
    
    # Add Support levels (green zones)
    for support in sr_data['supports']:
        fig.add_hline(
            y=support['level'],
            line_dash="dash",
            line_color="green",
            annotation_text=f"S: ₹{support['level']} ({support['strength']}%)",
            annotation_position="right",
            row=1, col=1
        )
        
        # Add zone
        fig.add_hrect(
            y0=support['zone_lower'],
            y1=support['zone_upper'],
            fillcolor="green",
            opacity=0.1,
            line_width=0,
            row=1, col=1
        )
    
    # Add Resistance levels (red zones)
    for resistance in sr_data['resistances']:
        fig.add_hline(
            y=resistance['level'],
            line_dash="dash",
            line_color="red",
            annotation_text=f"R: ₹{resistance['level']} ({resistance['strength']}%)",
            annotation_position="right",
            row=1, col=1
        )
        
        # Add zone
        fig.add_hrect(
            y0=resistance['zone_lower'],
            y1=resistance['zone_upper'],
            fillcolor="red",
            opacity=0.1,
            line_width=0,
            row=1, col=1
        )
    
    # Current price line
    fig.add_hline(
        y=sr_data['current_price'],
        line_color="blue",
        line_width=2,
        annotation_text=f"Current: ₹{sr_data['current_price']}",
        annotation_position="left",
        row=1, col=1
    )
    
    # Volume bars
    colors = ['red' if df['close'].iloc[i] < df['open'].iloc[i] else 'green' 
              for i in range(len(df))]
    
    fig.add_trace(
        go.Bar(
            x=df['time'],
            y=df['volume'],
            marker_color=colors,
            name='Volume'
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        title="Support & Resistance Analysis",
        height=800,
        showlegend=False,
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    
    return fig

# ============================================================
# MAIN APP
# ============================================================

def main():
    # Header
    st.markdown('<div class="main-header">📊 Support & Resistance Analyzer</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Identify key price levels based on swing highs/lows and volume</div>', 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Stock input
        symbol = st.text_input(
            "📈 Enter Stock Symbol",
            value="RELIANCE",
            placeholder="e.g., RELIANCE, TCS, INFY, HDFCBANK",
            help="Enter stock symbol (170+ stocks available)"
        ).upper()
        
        # Timeframe
        timeframe = st.selectbox(
            "📅 Timeframe",
            options=["1D"],
            index=0,
            help="Daily candles (1 year of data)"
        )
        
        # Sensitivity
        sensitivity = st.slider(
            "🎯 Sensitivity",
            min_value=3,
            max_value=10,
            value=5,
            help="Lower = more levels, Higher = fewer strong levels"
        )
        
        # Min touches
        min_touches = st.slider(
            "✋ Minimum Touches",
            min_value=2,
            max_value=5,
            value=2,
            help="Minimum times price must touch a level"
        )
        
        st.markdown("---")
        
        analyze_btn = st.button("🔍 ANALYZE", use_container_width=True)
        
        st.markdown("---")
        st.caption("💡 **Strategy Based On:**")
        st.caption("[Unlocking the Market's Hidden Fortress](https://youtu.be/17tR6S9tqeM)")
    
    # Main area
    if analyze_btn:
        if not symbol:
            st.warning("[WARNING] Please enter a stock symbol")
            return
        
        with st.spinner(f"📊 Analyzing {symbol}..."):
            # Fetch data
            df = get_stock_data(symbol, timeframe)
            
            if df is None or df.empty:
                st.error("[ERROR] Could not fetch data. Please check the symbol.")
                return
            
            # Calculate S&R
            calculator = SupportResistanceCalculator(
                sensitivity=sensitivity,
                min_touches=min_touches
            )
            
            sr_data = calculator.calculate_support_resistance(df)
            
            if 'error' in sr_data:
                st.error(f"[ERROR] {sr_data['error']}")
                return
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Current Price",
                    f"₹{sr_data['current_price']}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    "Support Levels",
                    sr_data['total_support_levels'],
                    delta=None
                )
            
            with col3:
                st.metric(
                    "Resistance Levels",
                    sr_data['total_resistance_levels'],
                    delta=None
                )
            
            st.markdown("---")
            
            # Display chart
            if sr_data['supports'] or sr_data['resistances']:
                st.subheader("📊 Price Chart with S&R Levels")
                fig = plot_sr_levels(df, sr_data)
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Display levels in tables
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🟢 Support Levels (Buy Zones)")
                    if sr_data['supports']:
                        df_supports = pd.DataFrame(sr_data['supports'])
                        df_supports = df_supports[[
                            'level', 'distance_pct', 'touches', 
                            'volume_factor', 'strength'
                        ]]
                        df_supports.columns = [
                            'Level (₹)', 'Distance %', 'Touches', 
                            'Volume Factor', 'Strength %'
                        ]
                        st.dataframe(df_supports, use_container_width=True, hide_index=True)
                    else:
                        st.info("No strong support levels found")
                
                with col2:
                    st.subheader("🔴 Resistance Levels (Sell Zones)")
                    if sr_data['resistances']:
                        df_resistances = pd.DataFrame(sr_data['resistances'])
                        df_resistances = df_resistances[[
                            'level', 'distance_pct', 'touches', 
                            'volume_factor', 'strength'
                        ]]
                        df_resistances.columns = [
                            'Level (₹)', 'Distance %', 'Touches', 
                            'Volume Factor', 'Strength %'
                        ]
                        st.dataframe(df_resistances, use_container_width=True, hide_index=True)
                    else:
                        st.info("No strong resistance levels found")
                
                # Nearest levels
                st.markdown("---")
                st.subheader("🎯 Nearest Key Levels")
                
                col1, col2 = st.columns(2)
                
                if sr_data['supports']:
                    nearest_support = sr_data['supports'][0]
                    with col1:
                        st.success(f"""
                        **Nearest Support:**  
                        ₹{nearest_support['level']} ({nearest_support['distance_pct']}% below)  
                        Strength: {nearest_support['strength']}%  
                        Touches: {nearest_support['touches']}
                        """)
                
                if sr_data['resistances']:
                    nearest_resistance = sr_data['resistances'][0]
                    with col2:
                        st.error(f"""
                        **Nearest Resistance:**  
                        ₹{nearest_resistance['level']} ({nearest_resistance['distance_pct']}% above)  
                        Strength: {nearest_resistance['strength']}%  
                        Touches: {nearest_resistance['touches']}
                        """)
            
            else:
                st.warning("[WARNING] No significant S&R levels found. Try adjusting sensitivity.")
    
    else:
        # Welcome screen
        st.info("""
        ### 👋 Welcome to S&R Analyzer!
        
        **How to use:**
        1. Enter a stock symbol in the sidebar
        2. Select your preferred timeframe (Daily/Weekly)
        3. Adjust sensitivity if needed
        4. Click **ANALYZE** to see Support & Resistance levels
        
        **Features:**
        - 📊 Visual chart with S&R zones
        - 🎯 Strength-based level ranking
        - 📈 Volume confirmation
        - 🔄 Multi-timeframe support
        
        **Strategy based on:** Swing high/low detection with volume analysis
        """)

if __name__ == "__main__":
    main()

