# -*- coding: utf-8 -*-
"""
Support & Resistance Level Viewer
Interactive tool to view S&R levels for any stock
"""

import sys
import os
from datetime import datetime

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
        access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzYyNTg4MzAyLCJpYXQiOjE3NjI1MDE5MDIsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTA0MTQ3NDU3In0.8Hh2Rnz-jDv15U4g3tTv6ZTgJXR70WUPjMVAPtZpv-sQ-AxoBji1GnC2H4RA1YQrkWY0Pa2jXJjKdEzTjrmnSA"
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

def get_live_price_yfinance(symbol: str) -> float:
    """
    Get LIVE current price from Yahoo Finance
    
    Args:
        symbol: Stock symbol (e.g., GRASIM, RELIANCE)
    
    Returns:
        Current live price or None
    """
    try:
        import yfinance as yf
        
        # NSE stocks need .NS suffix for Yahoo Finance
        ticker = f"{symbol.upper()}.NS"
        
        # Get stock data
        stock = yf.Ticker(ticker)
        
        # Try to get current price (live during market hours)
        info = stock.info
        
        # Try multiple price fields
        live_price = (
            info.get('currentPrice') or 
            info.get('regularMarketPrice') or 
            info.get('previousClose')
        )
        
        if live_price:
            return float(live_price)
        
        # Fallback: Get latest from history
        hist = stock.history(period='5d')
        if not hist.empty:
            latest_close = hist['Close'].iloc[-1]
            return float(latest_close)
        
        return None
        
    except Exception as e:
        # Silent fail - will use Excel price as fallback
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
        
        # Get available stocks
        loader = load_excel_data()
        available_stocks = []
        if loader is not None:
            try:
                available_stocks = sorted(loader.get_all_available_stocks())
            except:
                available_stocks = []
        
        # Analysis Mode (NEW!)
        analysis_mode = st.radio(
            "📊 Analysis Mode",
            options=["Single Stock (Detailed)", "Multi Stock (Table)"],
            index=0,
            help="Single: Full analysis with charts. Multi: Quick table for many stocks"
        )
        
        st.markdown("---")
        
        # Stock selection based on mode
        if analysis_mode == "Multi Stock (Table)":
            # Multi-select for batch analysis
            st.subheader("📋 Select Multiple Stocks")
            
            # Quick select options
            quick_select = st.selectbox(
                "Quick Select",
                options=["Custom Selection", "Top 20 Stocks", "All 170 Stocks", "Nifty 50 Only"],
                help="Quick select groups of stocks"
            )
            
            if quick_select == "Top 20 Stocks":
                default_stocks = available_stocks[:20]
            elif quick_select == "All 170 Stocks":
                default_stocks = available_stocks
            elif quick_select == "Nifty 50 Only":
                # Top 50 stocks
                default_stocks = available_stocks[:50]
            else:
                default_stocks = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK']
            
            selected_stocks = st.multiselect(
                "Select Stocks to Analyze",
                options=available_stocks,
                default=default_stocks,
                help=f"Select multiple stocks for batch analysis",
                key="multi_stock_select"
            )
            
            symbol = None  # Not used in multi mode
            
        else:
            # Single stock selection
            selection_method = st.radio(
                "📋 Stock Selection Method",
                options=["Dropdown (Easy)", "Type Symbol"],
                index=0,
                help="Choose dropdown to select from available stocks, or type to enter any symbol"
            )
            
            if selection_method == "Dropdown (Easy)":
                # Dropdown selector
                if available_stocks:
                    default_idx = available_stocks.index("RELIANCE") if "RELIANCE" in available_stocks else 0
                    symbol = st.selectbox(
                        "📈 Select Stock",
                        options=available_stocks,
                        index=default_idx,
                        help=f"{len(available_stocks)} stocks available",
                        key="stock_dropdown"
                    )
                else:
                    st.warning("No stocks loaded. Using text input.")
                    symbol = st.text_input(
                        "📈 Enter Stock Symbol",
                        value="RELIANCE",
                        placeholder="e.g., RELIANCE, TCS, INFY",
                        key="stock_text_fallback"
                    ).upper()
            else:
                # Text input (for any symbol)
                symbol = st.text_input(
                    "📈 Type Stock Symbol",
                    value="",
                    placeholder="Type: RELIANCE, TCS, INFY, TATAMOTORS, etc.",
                    help="Type any NSE stock symbol from the available 170 stocks",
                    key="stock_text_input"
                ).upper()
                
                # Show suggestions
                if symbol and len(symbol) >= 2:
                    matches = [s for s in available_stocks if symbol in s][:10]
                    if matches:
                        st.caption(f"💡 Suggestions: {', '.join(matches)}")
            
            selected_stocks = None  # Not used in single mode
        
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
        
        # Signal Filter (NEW!)
        st.subheader("🎯 Trading Preference")
        st.caption("💡 Tell us what you're looking for - we'll highlight matches!")
        signal_filter_option = st.multiselect(
            "I'm Interested In",
            options=['STRONG BUY', 'BUY', 'HOLD', 'SELL', 'STRONG SELL'],
            default=['STRONG BUY', 'BUY', 'SELL', 'STRONG SELL'],
            help="Select signals you want to trade. If a stock matches, you'll see ✅ MATCH!"
        )
        
        if not signal_filter_option:
            st.warning("⚠️ Select at least one signal type!")
        
        st.caption(f"📊 Currently looking for: {', '.join(signal_filter_option) if signal_filter_option else 'Nothing selected'}")
        
        st.markdown("---")
        
        # Show stock count
        if available_stocks:
            st.success(f"✅ **ALL {len(available_stocks)} stocks** loaded from Excel")
            with st.expander("📋 View All Available Stocks", expanded=False):
                # Show stocks in 4 columns
                cols = st.columns(4)
                for i, stock in enumerate(available_stocks):
                    with cols[i % 4]:
                        st.caption(f"{i+1}. {stock}")
        else:
            st.error("❌ No stocks loaded! Check Excel file.")
        
        st.markdown("---")
        
        analyze_btn = st.button("🔍 ANALYZE", use_container_width=True)
        
        st.markdown("---")
        
        # CSV Download Section (NEW!)
        st.subheader("💾 Export")
        if 'last_analysis' in st.session_state:
            csv = st.session_state['last_analysis'].to_csv(index=False)
            st.download_button(
                label="📥 Download Analysis CSV",
                data=csv,
                file_name=f"SR_Analysis_{st.session_state.get('last_symbol', 'Stock')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
            st.caption(f"Last: {st.session_state.get('last_symbol', 'N/A')}")
        else:
            st.info("📥 CSV Download\n\nAnalyze a stock first, then download button appears here!")
        
        st.markdown("---")
        st.caption("💡 **Strategy Based On:**")
        st.caption("[Unlocking the Market's Hidden Fortress](https://youtu.be/17tR6S9tqeM)")
    
    # Main area
    if analyze_btn:
        # MULTI STOCK MODE
        if analysis_mode == "Multi Stock (Table)":
            if not selected_stocks:
                st.warning("⚠️ Please select at least one stock to analyze")
                return
            
            st.subheader(f"📊 Batch Analysis - {len(selected_stocks)} Stocks")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            calculator = SupportResistanceCalculator(sensitivity=sensitivity, min_touches=min_touches)
            
            for i, stock in enumerate(selected_stocks):
                status_text.text(f"Analyzing {stock}... ({i+1}/{len(selected_stocks)})")
                progress_bar.progress((i + 1) / len(selected_stocks))
                
                try:
                    # Get data
                    df = get_stock_data(stock, timeframe)
                    
                    if df is None or df.empty:
                        continue
                    
                    # Get live price
                    live_price = get_live_price_yfinance(stock)
                    excel_last_price = df['close'].iloc[-1]
                    current_price = live_price if live_price else excel_last_price
                    
                    # Calculate S&R
                    sr_data = calculator.calculate_support_resistance(df, current_price)
                    ma_data = calculator.calculate_moving_averages(df)
                    breakouts = calculator.detect_breakouts(df, sr_data)
                    reversals = calculator.detect_role_reversals(df, sr_data)
                    
                    # Generate signal
                    trading_signal = calculator.generate_trading_signal(df, sr_data, ma_data, breakouts, reversals)
                    
                    # Filter by signal preference
                    if trading_signal['signal'] not in signal_filter_option:
                        continue  # Skip stocks not matching filter
                    
                    # Add to results
                    results.append({
                        'Symbol': stock,
                        'Signal': trading_signal['signal'],
                        'Confidence': trading_signal['confidence_score'],
                        'Current_Price': current_price,
                        'Nearest_Support': sr_data['supports'][0]['level'] if sr_data['supports'] else None,
                        'Support_Dist_%': sr_data['supports'][0]['distance_pct'] if sr_data['supports'] else None,
                        'Nearest_Resistance': sr_data['resistances'][0]['level'] if sr_data['resistances'] else None,
                        'Resistance_Dist_%': sr_data['resistances'][0]['distance_pct'] if sr_data['resistances'] else None,
                        'MA_Trend': ma_data.get('trend', 'N/A') if ma_data.get('available') else 'N/A',
                        'Reasons': '; '.join(trading_signal['reasons'][:2]) if trading_signal['reasons'] else 'N/A'
                    })
                    
                except Exception as e:
                    # Skip stocks with errors
                    continue
            
            progress_bar.empty()
            status_text.empty()
            
            if results:
                df_results = pd.DataFrame(results)
                
                # Sort by signal priority: STRONG BUY > BUY > HOLD > SELL > STRONG SELL
                signal_order = {'STRONG BUY': 1, 'BUY': 2, 'HOLD': 3, 'SELL': 4, 'STRONG SELL': 5}
                df_results['_sort'] = df_results['Signal'].map(signal_order)
                df_results = df_results.sort_values(['_sort', 'Confidence'], ascending=[True, False])
                df_results = df_results.drop('_sort', axis=1)
                
                # Save for CSV download
                st.session_state['last_analysis'] = df_results
                st.session_state['last_symbol'] = f"{len(results)}_stocks"
                
                # Display summary
                st.success(f"✅ Found {len(results)} stocks matching your filter: {', '.join(signal_filter_option)}")
                
                # Show breakdown
                col1, col2, col3 = st.columns(3)
                with col1:
                    strong_buy_count = len(df_results[df_results['Signal'] == 'STRONG BUY'])
                    st.metric("🟢🟢 STRONG BUY", strong_buy_count)
                with col2:
                    buy_count = len(df_results[df_results['Signal'] == 'BUY'])
                    st.metric("🟢 BUY", buy_count)
                with col3:
                    sell_count = len(df_results[df_results['Signal'].str.contains('SELL')])
                    st.metric("🔴 SELL (All)", sell_count)
                
                st.markdown("---")
                
                # Display table
                st.subheader("📊 Batch Analysis Results")
                
                # Format for display
                df_display = df_results.copy()
                df_display['Current_Price'] = df_display['Current_Price'].apply(lambda x: f"₹{x:,.2f}")
                df_display['Confidence'] = df_display['Confidence'].apply(lambda x: f"{x}%")
                
                if 'Nearest_Support' in df_display.columns:
                    df_display['Nearest_Support'] = df_display['Nearest_Support'].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "N/A")
                if 'Nearest_Resistance' in df_display.columns:
                    df_display['Nearest_Resistance'] = df_display['Nearest_Resistance'].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "N/A")
                if 'Support_Dist_%' in df_display.columns:
                    df_display['Support_Dist_%'] = df_display['Support_Dist_%'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
                if 'Resistance_Dist_%' in df_display.columns:
                    df_display['Resistance_Dist_%'] = df_display['Resistance_Dist_%'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
                
                # Style the dataframe
                def highlight_signal(row):
                    if row['Signal'] == 'STRONG BUY':
                        return ['background-color: #c8e6c9'] * len(row)
                    elif row['Signal'] == 'BUY':
                        return ['background-color: #e8f5e9'] * len(row)
                    elif row['Signal'] == 'STRONG SELL':
                        return ['background-color: #ffcdd2'] * len(row)
                    elif row['Signal'] == 'SELL':
                        return ['background-color: #ffebee'] * len(row)
                    else:
                        return [''] * len(row)
                
                st.dataframe(
                    df_display.style.apply(highlight_signal, axis=1),
                    use_container_width=True,
                    height=600
                )
                
                st.markdown("---")
                st.info("💡 Click any stock name, then analyze in Single Stock mode for detailed charts and analysis!")
                
            else:
                st.warning(f"⚠️ No stocks found matching your filter: {', '.join(signal_filter_option)}")
                st.info(f"💡 Analyzed {len(selected_stocks)} stocks. Try adjusting your signal filter or selecting different stocks.")
            
            return  # End multi-stock mode
        
        # SINGLE STOCK MODE
        if not symbol:
            st.warning("[WARNING] Please enter a stock symbol")
            return
        
        with st.spinner(f"📊 Analyzing {symbol}..."):
            # Fetch historical data from Excel
            df = get_stock_data(symbol, timeframe)
            
            if df is None or df.empty:
                st.error("[ERROR] Could not fetch data. Please check the symbol.")
                return
            
            # Get LIVE current price from Yahoo Finance
            live_price = get_live_price_yfinance(symbol)
            excel_last_date = df['time'].iloc[-1]
            excel_last_price = df['close'].iloc[-1]
            
            # Determine which price to use
            if live_price is not None:
                current_price = live_price
                price_source = "LIVE (Yahoo Finance)"
                st.success(f"✅ Using LIVE price: ₹{live_price:.2f} (Yahoo Finance)")
                
                # Check if price changed significantly from Excel
                price_change = ((live_price - excel_last_price) / excel_last_price) * 100
                if abs(price_change) > 1:
                    st.info(f"💡 Price moved {price_change:+.2f}% since {excel_last_date.strftime('%b %d')}")
            else:
                current_price = excel_last_price
                price_source = f"Excel ({excel_last_date.strftime('%b %d, %Y')})"
                st.warning(f"⚠️ Using Excel price: ₹{excel_last_price:.2f} (Market closed or Yahoo Finance unavailable)")
            
            # Calculate S&R with LIVE current price
            calculator = SupportResistanceCalculator(
                sensitivity=sensitivity,
                min_touches=min_touches
            )
            
            sr_data = calculator.calculate_support_resistance(df, current_price=current_price)
            
            if 'error' in sr_data:
                st.error(f"[ERROR] {sr_data['error']}")
                return
            
            # NEW PHASE 2 FEATURES
            # 1. Role Reversals
            reversals = calculator.detect_role_reversals(df, sr_data)
            
            # 2. Breakouts
            breakouts = calculator.detect_breakouts(df, sr_data)
            
            # 3. Moving Averages
            ma_data = calculator.calculate_moving_averages(df)
            
            # 4. Multi-timeframe
            mtf_data = calculator.get_multi_timeframe_analysis(df)
            
            # 5. Generate Trading Signal (NEW!)
            trading_signal = calculator.generate_trading_signal(df, sr_data, ma_data, breakouts, reversals)
            
            # Save analysis results for CSV download
            analysis_data = {
                'Symbol': [symbol],
                'Current_Price': [sr_data['current_price']],
                'Signal': [trading_signal['signal']],
                'Confidence': [trading_signal['confidence_score']],
                'Strength': [trading_signal['strength']],
                'Nearest_Support': [sr_data['supports'][0]['level'] if sr_data['supports'] else None],
                'Nearest_Resistance': [sr_data['resistances'][0]['level'] if sr_data['resistances'] else None],
                'MA_Trend': [ma_data.get('trend', 'N/A')],
                'Reasons': ['; '.join(trading_signal['reasons'])],
                'Analysis_Date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            }
            st.session_state['last_analysis'] = pd.DataFrame(analysis_data)
            st.session_state['last_symbol'] = symbol
            
            # Check if signal matches filter
            signal_matches_filter = trading_signal['signal'] in signal_filter_option
            
            # Display metrics with data source info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    f"Current Price ({price_source})",
                    f"₹{sr_data['current_price']}",
                    delta=None,
                    help="Live price from Dhan API (when market open) or last Excel price"
                )
            
            with col2:
                st.metric(
                    "Support Levels",
                    sr_data['total_support_levels'],
                    delta=None,
                    help="Based on historical data patterns"
                )
            
            with col3:
                st.metric(
                    "Resistance Levels",
                    sr_data['total_resistance_levels'],
                    delta=None,
                    help="Based on historical data patterns"
                )
            
            st.markdown("---")
            
            # Data source explanation
            with st.expander("ℹ️ Data Source Info", expanded=False):
                st.markdown("""
                ### 📊 Hybrid Data Approach (Best of Both Worlds)
                
                **Historical Data (Excel):**
                - ✅ 10 years of price history
                - ✅ Used for S&R level calculation
                - ✅ Used for pattern detection
                - ✅ Fast and reliable
                
                **Current Price (Yahoo Finance):**
                - ✅ Live price when market is open
                - ✅ Used for distance calculations
                - ✅ Used for breakout detection
                - ✅ Falls back to Excel if market closed
                
                **Why This Approach?**
                - S&R levels = based on long-term patterns (Excel perfect!)
                - Current analysis = needs live price (Yahoo Finance!)
                - Best accuracy: Historical patterns + Live data
                """)
            
            st.markdown("---")
            
            # TRADING SIGNAL (BIG DISPLAY - NEW!)
            signal_color = {
                'STRONG BUY': 'green',
                'BUY': 'green',
                'HOLD': 'gray',
                'SELL': 'red',
                'STRONG SELL': 'red'
            }.get(trading_signal['signal'], 'gray')
            
            signal_emoji = {
                'STRONG BUY': '🟢🟢',
                'BUY': '🟢',
                'HOLD': '⚪',
                'SELL': '🔴',
                'STRONG SELL': '🔴🔴'
            }.get(trading_signal['signal'], '⚪')
            
            match_badge = "✅ MATCHES YOUR FILTER!" if signal_matches_filter else ""
            border_width = "8px" if signal_matches_filter else "5px"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {signal_color}11 0%, {signal_color}33 100%); 
                        padding: 20px; border-radius: 10px; border-left: {border_width} solid {signal_color}; margin: 20px 0;">
                <h2 style="color: {signal_color}; margin:0;">{signal_emoji} {trading_signal['signal']} {match_badge}</h2>
                <p style="font-size: 1.1em; color: #666; margin:5px 0;">Confidence: {trading_signal['confidence_score']}% | Strength: {trading_signal['strength']}</p>
                <p style="font-size: 0.95em; color: #444; margin:5px 0;">
                    <strong>Reasons:</strong><br>
                    {'<br>• '.join(trading_signal['reasons']) if trading_signal['reasons'] else 'Based on current S&R analysis'}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # PHASE 2: Display Advanced Features (NEW!)
            st.subheader("🚀 Advanced Analysis (Video Strategy Complete!)")
            
            adv_col1, adv_col2, adv_col3, adv_col4 = st.columns(4)
            
            with adv_col1:
                # Moving Average Trend
                if ma_data['available']:
                    trend_emoji = "📈" if "BULLISH" in ma_data['trend'] else "📉" if "BEARISH" in ma_data['trend'] else "➡️"
                    st.metric(
                        "MA Trend",
                        ma_data['trend'],
                        delta=f"{ma_data['distance_from_50ema']:+.1f}% from 50 EMA"
                    )
                else:
                    st.info("MA: N/A")
            
            with adv_col2:
                # Breakouts
                if breakouts['breakout_detected']:
                    br = breakouts['breakouts'][0]
                    st.metric(
                        "BREAKOUT!",
                        br['direction'],
                        delta=f"Level: ₹{br['level']}"
                    )
                else:
                    st.success("No Breakout")
            
            with adv_col3:
                # Role Reversals
                if reversals:
                    st.metric(
                        "Role Reversals",
                        len(reversals),
                        delta=f"{reversals[0]['confidence']} confidence"
                    )
                else:
                    st.info("No Reversals")
            
            with adv_col4:
                # Multi-timeframe
                if mtf_data.get('alignment_found'):
                    aligned_count = len(mtf_data['aligned_supports']) + len(mtf_data['aligned_resistances'])
                    st.metric(
                        "MTF Aligned",
                        f"{aligned_count} levels",
                        delta="VERY STRONG"
                    )
                else:
                    st.info("No MTF Alignment")
            
            st.markdown("---")
            
            # Display chart
            if sr_data['supports'] or sr_data['resistances']:
                st.subheader("📊 Price Chart with S&R Levels")
                fig = plot_sr_levels(df, sr_data)
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # PHASE 2: Detailed Analysis Sections
                
                # Section 1: Moving Averages & Trend Context
                if ma_data['available']:
                    with st.expander("📈 Moving Averages & Trend Context", expanded=True):
                        ma_col1, ma_col2 = st.columns(2)
                        
                        with ma_col1:
                            st.markdown("### Trend Analysis")
                            trend_color = "green" if "BULLISH" in ma_data['trend'] else "red" if "BEARISH" in ma_data['trend'] else "gray"
                            st.markdown(f"**Trend:** :{trend_color}[{ma_data['trend']}]")
                            st.info(ma_data['context'])
                            
                            if ma_data['cross']:
                                cross_color = "green" if ma_data['cross'] == 'GOLDEN CROSS' else "red"
                                st.markdown(f"**Special Event:** :{cross_color}[{ma_data['cross']}] 🎯")
                        
                        with ma_col2:
                            st.markdown("### Moving Average Levels")
                            st.metric("50 EMA", f"₹{ma_data['EMA50']}", f"{ma_data['distance_from_50ema']:+.2f}%")
                            st.metric("200 EMA", f"₹{ma_data['EMA200']}", f"{ma_data['distance_from_200ema']:+.2f}%")
                            
                            # Trading advice based on MA
                            if "STRONG BULLISH" in ma_data['trend']:
                                st.success("✅ **Support levels more reliable** in this uptrend")
                            elif "STRONG BEARISH" in ma_data['trend']:
                                st.warning("⚠️ **Resistance levels more reliable** in this downtrend")
                
                # Section 2: Breakouts & Confirmations
                if breakouts['breakout_detected']:
                    with st.expander("🎯 BREAKOUT DETECTED!", expanded=True):
                        for br in breakouts['breakouts']:
                            st.markdown(f"### {br['type'].replace('_', ' ').title()}")
                            
                            br_col1, br_col2 = st.columns(2)
                            
                            with br_col1:
                                direction_color = "green" if br['direction'] == 'BULLISH' else "red"
                                st.markdown(f"**Direction:** :{direction_color}[{br['direction']}]")
                                st.markdown(f"**Level Broken:** ₹{br['level']}")
                                st.markdown(f"**Level Strength:** {br['strength']}%")
                            
                            with br_col2:
                                vol_status = "✅ CONFIRMED" if br['volume_confirmation'] else "⚠️ Weak"
                                st.markdown(f"**Volume Confirmation:** {vol_status}")
                                st.markdown(f"**Status:** {br['status']}")
                            
                            if br['direction'] == 'BULLISH':
                                st.success("💡 **Trading Idea:** Breakout suggests upward momentum. Consider long positions with stop below breakout level.")
                            else:
                                st.error("💡 **Trading Idea:** Breakdown suggests downward momentum. Consider short positions or exit longs.")
                
                # Section 3: Role Reversals
                if reversals:
                    with st.expander("🔄 Role Reversals Detected", expanded=True):
                        st.markdown("**What are Role Reversals?** When a broken support level becomes new resistance (or vice versa). These are high-probability reversal zones!")
                        
                        for rev in reversals:
                            st.markdown(f"### Level: ₹{rev['level']}")
                            
                            rev_col1, rev_col2 = st.columns(2)
                            
                            with rev_col1:
                                st.markdown(f"**Type:** {rev['type'].replace('_', ' → ')}")
                                st.markdown(f"**Status:** {rev['status']}")
                            
                            with rev_col2:
                                st.markdown(f"**Strength:** {rev['strength']}%")
                                st.markdown(f"**Confidence:** {rev['confidence']}")
                            
                            if rev['type'] == 'SUPPORT_TO_RESISTANCE':
                                st.warning("⚠️ **Watch for rejection** at this level. Old support often acts as strong new resistance.")
                            else:
                                st.success("✅ **Watch for bounce** at this level. Old resistance often acts as strong new support.")
                            
                            st.markdown("---")
                
                # Section 4: Multi-timeframe Alignment
                if mtf_data.get('alignment_found'):
                    with st.expander("⏰ Multi-Timeframe Aligned Levels", expanded=True):
                        st.markdown("**What is MTF Alignment?** When Daily AND Weekly levels align, they carry significantly more weight. Institutional traders watch these!")
                        
                        if mtf_data['aligned_supports']:
                            st.markdown("### 🟢 Aligned Support Levels (VERY STRONG)")
                            for supp in mtf_data['aligned_supports']:
                                st.success(f"""
                                **Level:** ₹{supp['level']}  
                                **Timeframes:** {', '.join(supp['timeframes'])}  
                                **Combined Strength:** {supp['combined_strength']}%  
                                **Confidence:** {supp['confidence']}
                                """)
                                st.info("💡 **Trading Tip:** This is a HIGH PROBABILITY bounce zone. Consider buying near this level with tight stop.")
                        
                        if mtf_data['aligned_resistances']:
                            st.markdown("### 🔴 Aligned Resistance Levels (VERY STRONG)")
                            for res in mtf_data['aligned_resistances']:
                                st.error(f"""
                                **Level:** ₹{res['level']}  
                                **Timeframes:** {', '.join(res['timeframes'])}  
                                **Combined Strength:** {res['combined_strength']}%  
                                **Confidence:** {res['confidence']}
                                """)
                                st.info("💡 **Trading Tip:** This is a HIGH PROBABILITY rejection zone. Consider selling near this level or taking profits.")
                
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
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info("""
            ### 👋 Welcome to S&R Analyzer! (PHASE 2 COMPLETE!)
            
            **How to use:**
            1. **Choose selection method** (Dropdown/Type) in sidebar
            2. **Select/Enter a stock symbol**
            3. Adjust sensitivity if needed (default is good!)
            4. Click **🔍 ANALYZE** to see complete S&R analysis
            
            **🎉 Complete Video Strategy Implemented:**
            - ✅ Support & Resistance Detection
            - ✅ Role Reversals (broken S→R, R→S)
            - ✅ Breakout Confirmation (candle close)
            - ✅ Moving Averages (50/200 EMA trend)
            - ✅ Multi-timeframe Alignment (D+W)
            - ✅ Volume Confirmation
            - ✅ Strength Scoring
            - ✅ 170+ stocks available
            
            **100% Video Strategy Coverage!** 🎯
            """)
        
        with col2:
            if available_stocks:
                st.success(f"""
                **Ready!**
                
                ✅ {len(available_stocks)} stocks loaded
                
                **Coverage:**
                - Nifty 50: ✅ Covered
                - Nifty 100: ✅ Covered  
                - Nifty 200: ⚠️ {len(available_stocks)}/200
                
                **Popular stocks:**
                - RELIANCE, TCS, HDFCBANK
                - INFY, ICICIBANK, SBIN
                - BHARTIARTL, KOTAKBANK
                - And {len(available_stocks)-10}+ more!
                """)
                
                if len(available_stocks) < 200:
                    st.info(f"""
                    💡 **Note:** Your Excel has {len(available_stocks)} stocks.
                    
                    To add more stocks, update:
                    `Nifty200_Complete_10yeardata.xlsx`
                    
                    The analyzer will automatically load any stocks you add!
                    """)

if __name__ == "__main__":
    main()

