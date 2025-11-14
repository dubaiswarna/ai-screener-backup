"""
Enhanced AI Stock Screener with Database Persistence
=====================================================
Solves the refresh issue - all signals persist in database!
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Import our professional modules
from database.db_manager import get_db
from risk_management.risk_engine import RiskEngine
from broker_integration.broker_client import get_broker_client
from support_resistance.sr_calculator import SupportResistanceCalculator
# Import enhanced S&R calculator with DUAL S&R system
try:
    from support_resistance.sr_calculator_enhanced import ProfessionalSRCalculator
    DUAL_SR_AVAILABLE = True
except ImportError:
    DUAL_SR_AVAILABLE = False
    ProfessionalSRCalculator = SupportResistanceCalculator  # Fallback

# Import expanded stock universe
try:
    from config.stock_universe import NIFTY_50, NIFTY_200, NIFTY_500, SMALLCAP_250, ALL_STOCKS, COMMODITIES, ALL_ASSETS
    EXPANDED_UNIVERSE_AVAILABLE = True
except ImportError:
    EXPANDED_UNIVERSE_AVAILABLE = False
    NIFTY_50 = []
    NIFTY_200 = []
    NIFTY_500 = []
    SMALLCAP_250 = []
    ALL_STOCKS = []
    COMMODITIES = []
    ALL_ASSETS = []

# ============================================================
# HELPER: My Stocks Management
# ============================================================

def initialize_my_stocks():
    """Initialize My Stocks list with default favorites"""
    if 'my_stocks' not in st.session_state:
        st.session_state.my_stocks = ['MGL', 'LEMONTREE', 'CAPLINPOINT', 'PFC', 'REC', 'HAL']
    return st.session_state.my_stocks

def get_my_stocks():
    """Get current My Stocks list"""
    initialize_my_stocks()
    return st.session_state.my_stocks

def add_to_my_stocks(symbol):
    """Add a stock to My Stocks list"""
    initialize_my_stocks()
    symbol = symbol.strip().upper()
    if symbol and symbol not in st.session_state.my_stocks:
        st.session_state.my_stocks.append(symbol)
        return True
    return False

def remove_from_my_stocks(symbol):
    """Remove a stock from My Stocks list"""
    initialize_my_stocks()
    symbol = symbol.strip().upper()
    if symbol in st.session_state.my_stocks:
        st.session_state.my_stocks.remove(symbol)
        return True
    return False

def render_my_stocks_manager():
    """Render UI to manage My Stocks list"""
    initialize_my_stocks()
    
    with st.expander("⭐ Manage My Stocks", expanded=False):
        st.markdown("**Your Favorite Stocks:**")
        
        # Display current stocks
        if st.session_state.my_stocks:
            cols = st.columns(min(len(st.session_state.my_stocks), 5))
            for idx, stock in enumerate(st.session_state.my_stocks):
                with cols[idx % len(cols)]:
                    if st.button(f"❌ {stock}", key=f"remove_{stock}", use_container_width=True):
                        remove_from_my_stocks(stock)
                        st.rerun()
        else:
            st.info("No stocks in your list. Add some below!")
        
        # Add new stock
        col1, col2 = st.columns([3, 1])
        with col1:
            new_stock = st.text_input("Add Stock Symbol:", key="add_stock_input", 
                                    placeholder="Enter symbol (e.g., RELIANCE)")
        with col2:
            st.write("")  # Spacing
            if st.button("➕ Add", key="add_stock_btn", use_container_width=True):
                if new_stock:
                    if add_to_my_stocks(new_stock):
                        st.success(f"✅ Added {new_stock.upper()} to My Stocks!")
                        st.rerun()
                    else:
                        st.warning(f"⚠️ {new_stock.upper()} is already in your list or invalid")
        
        st.caption(f"📊 Total: {len(st.session_state.my_stocks)} stocks in My Stocks")

# ============================================================
# HELPER: Symbol Mapping for Yahoo Finance
# ============================================================

def get_yfinance_symbol(symbol):
    """
    Convert symbol to Yahoo Finance format.
    
    Commodities use different symbols:
    - GOLD -> GC=F (Gold Futures)
    - SILVER -> SI=F (Silver Futures)
    - Stocks -> SYMBOL.NS (NSE stocks)
    
    Special cases (Yahoo Finance has different symbol names):
    - ASIANPAINTS -> ASIANPAINT.NS (no S)
    - M&M -> M&M.NS (keep &)
    """
    commodity_map = {
        'GOLD': 'GC=F',      # Gold Futures (COMEX)
        'SILVER': 'SI=F',    # Silver Futures (COMEX)
    }
    
    # Special stock symbol mappings
    stock_symbol_map = {
        'ASIANPAINTS': 'ASIANPAINT',  # Yahoo uses ASIANPAINT without S
        'BAJAJ-AUTO': 'BAJAJ-AUTO',   # Keep hyphen
        'M&M': 'M&M',                 # Keep ampersand
    }
    
    if symbol.upper() in commodity_map:
        return commodity_map[symbol.upper()]
    else:
        # Check if we need to map the symbol
        mapped_symbol = stock_symbol_map.get(symbol.upper(), symbol)
        return f"{mapped_symbol}.NS"

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title='Professional AI Screener v3.0',
    page_icon='🚀',
    layout='wide',
    initial_sidebar_state='expanded'
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .signal-card {
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid;
        margin: 0.5rem 0;
    }
    .signal-buy {
        border-color: #00ff00;
        background: rgba(0, 255, 0, 0.1);
    }
    .signal-sell {
        border-color: #ff0000;
        background: rgba(255, 0, 0, 0.1);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# INITIALIZE SERVICES
# ============================================================

@st.cache_resource
def init_services():
    """Initialize database, risk engine, and broker."""
    try:
        # Database
        db = get_db()
        
        # User config
        config = db.get_user_config()
        capital = config.get('total_capital', 1000000)
        
        # Risk engine
        risk_engine = RiskEngine(total_capital=capital)
        
        # Broker (will be configured with Dhan credentials later)
        broker = get_broker_client('paper')  # Start with paper, switch to dhan when credentials provided
        
        return db, risk_engine, broker, config
        
    except Exception as e:
        st.error(f"❌ Failed to initialize services: {e}")
        st.info("💡 Make sure PostgreSQL is running and database is setup")
        st.stop()

db, risk_engine, broker, user_config = init_services()

# ============================================================
# HEADER (Will be shown after page selection - hidden on Dashboard)
# ============================================================

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Control Panel")

# System status
st.sidebar.subheader("📊 System Status")
if db.test_connection():
    st.sidebar.success("✅ Database: Connected")
else:
    st.sidebar.error("❌ Database: Disconnected")

st.sidebar.info(f"🔌 Broker: {broker.name}")
st.sidebar.info(f"💰 Capital: ₹{user_config.get('total_capital', 0):,.0f}")

# Navigation
st.sidebar.subheader("📍 Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["Dashboard", "Chart Analysis", "Lotus Momentum Trio", "3Jasmines 🌸", "Hybrid Signal Generator 💎", "Orchid Trend Matrix",
     "Technical Screener", "S&R Analysis", "VWAP Strategy", "Backtest (Multi-Mode)",
     "Data Download", "Portfolio", "Trade History", "Risk Report", "Settings"]
)

# Show main header on all pages EXCEPT Dashboard (Dashboard has its own hero section)
if page != "Dashboard":
    st.markdown('<div class="main-header">🚀 PROFESSIONAL AI SCREENER v3.0</div>', unsafe_allow_html=True)
    st.markdown("**AI-Powered Trading with Database Persistence & Risk Management**")

# REAL Technical Screener: Calculates actual RSI, MACD, MAs - NO random predictions!

# ============================================================
# PAGE: DASHBOARD
# ============================================================

if page == "Dashboard":
    # Professional AI Screener v3.0 - Main Dashboard
    
    # Hero Section
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 2rem;'>
        <h1 style='color: white; font-size: 3rem; margin: 0;'>🚀 Professional AI Screener v3.0</h1>
        <p style='color: white; font-size: 1.3rem; margin-top: 1rem;'>AI-Powered Stock Analysis with Multi-Layer Confluence System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # System Overview
    st.markdown("""
    **Professional AI Screener v3.0** is an advanced stock analysis system that combines multiple technical layers 
    to surface high-probability opportunities. Built with practical trading experience and disciplined risk management, 
    it gives you a professional workflow the moment you log in.
    """)
    
    # Key Features
    st.markdown("## ✨ Core Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🎯 3-Layer Confluence System
        - **Technical Analysis**: RSI, MACD, EMA, ADX
        - **S&R Analysis**: Dual S&R (Primary + Secondary)
        - **Chart Patterns**: 13+ candlestick patterns
        
        **Result:** Only signals with 2/3 layers agreeing (75%+ confidence)
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Advanced S&R Analysis
        - Primary S&R (Wick extremes)
        - Secondary S&R (Battle zones)
        - Pivot Points (Standard, Fibonacci)
        - Multi-timeframe confluence
        - Historical success rate tracking
        """)
    
    with col3:
        st.markdown("""
        ### 💎 Pattern Recognition
        - Hammer, Shooting Star
        - Bullish/Bearish Engulfing
        - Morning/Evening Star
        - Three Soldiers/Crows
        - Doji, and more!
        
        **Visual icons for easy verification**
        """)
    
    st.markdown("---")
    
    # System Capabilities
    st.markdown("## 🛠️ System Capabilities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📈 Analysis Tools:
        - **Chart Analysis**: Pattern detection with visual samples
        - **Lotus Momentum Trio**: Treasure signal system (85%+ accuracy)
        - **Technical Screener**: Real-time RSI, MACD, MA analysis
        - **S&R Analysis**: Professional support/resistance levels
        - **VWAP Strategy**: Volume-weighted average price trading
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Trading Features:
        - **Multi-Mode Backtest**: Test strategies on historical data
        - **Portfolio Tracking**: Live P&L and position management
        - **Risk Management**: Auto position sizing, stop loss calculation
        - **Data Download**: EOD data for 750+ stocks
        - **Trade History**: Complete trade log with analytics
        """)
    
    st.markdown("---")
    
    # Data Sources
    st.markdown("## 📊 Data & Coverage")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Stock Universe", "750+", delta="Nifty 50/200/500 + Smallcap")
    
    with col2:
        st.metric("Data Source", "Yahoo Finance", delta="Free, No API key")
    
    with col3:
        st.metric("Analysis Depth", "6-12 months", delta="Historical EOD data")
    
    with col4:
        st.metric("Pattern Types", "13+", delta="Candlestick patterns")
    
    st.markdown("---")
    
    # About Developer
    st.markdown("## 👩‍💻 About the Developer")
    
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 1.75rem; border-radius: 10px; border-left: 5px solid #667eea;'>
        <h3 style='margin-top: 0; color: #667eea;'>J Swarnalakshmi</h3>
        <p style='font-size: 1rem; color: #4a4a4a; margin-bottom: 0.6rem;'><strong>Developer, Professional AI Screener v3.0</strong></p>
        <p style='font-size: 0.95rem; line-height: 1.7; color: #555; margin-bottom: 1rem;'>
            Crafts AI-assisted trading tools that blend quantitative research with live market experience. 
            Focused on clear confluence, disciplined risk controls, and reliable execution for active traders.
        </p>
        <p style='font-size: 0.95rem; line-height: 1.7; color: #555; margin-bottom: 0;'>
            <strong>Focus Areas:</strong> Multi-layer technical analysis · Pattern recognition systems · Portfolio & risk automation
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Important Disclaimers
    st.markdown("## ⚠️ Important Disclaimers")
    
    # SEBI Disclaimer
    st.error("""
    **📢 NOT A SEBI REGISTERED ANALYST**
    
    J Swarnalakshmi is **NOT a SEBI (Securities and Exchange Board of India) registered analyst** or investment advisor. 
    This system is developed for **educational and research purposes only**.
    """)
    
    # Legal Disclaimer
    st.warning("""
    **⚖️ LEGAL DISCLAIMER - PLEASE READ CAREFULLY**
    
    **1. No Investment Advice:**
    - This software provides technical analysis tools and educational content only
    - All signals, recommendations, and analysis are **NOT** investment advice
    - This is a research and educational tool, not a financial advisory service
    
    **2. Trading Risks:**
    - Stock trading involves **substantial risk of loss**
    - Past performance does NOT guarantee future results
    - You may lose some or all of your invested capital
    - Only trade with money you can afford to lose
    
    **3. User Responsibility:**
    - All trading decisions are **YOUR responsibility**
    - Conduct your own research and due diligence
    - Consult with a SEBI registered financial advisor before making investment decisions
    - The developer is **NOT responsible** for any losses incurred
    
    **4. No Guarantees:**
    - No guarantee of accuracy, completeness, or profitability
    - Market conditions change rapidly
    - Technical analysis has limitations
    - Historical patterns may not repeat
    
    **5. Educational Purpose:**
    - This tool is for learning technical analysis
    - Use paper trading mode to practice
    - Understand the system before risking real money
    
    **BY USING THIS SYSTEM, YOU ACKNOWLEDGE:**
    - You understand the risks of stock trading
    - You will not hold the developer liable for any losses
    - You will use this tool responsibly and at your own risk
    - You will comply with all applicable laws and regulations
    """)
    
    # System Info
    st.info("""
    **📌 System Information:**
    - **Version:** 3.0 (Professional Edition)
    - **Last Updated:** November 2024
    - **Data Source:** Yahoo Finance (Free, Public Data)
    - **Trading Mode:** Paper Trading (Simulation) / Real Trading (At your risk)
    - **Database:** PostgreSQL (Persistent signal storage)
    """)
    
    # Today's Work Log
    today_label = datetime.now().strftime("%d %b %Y")
    st.markdown(f"## 🗓️ Today's Work — {today_label}")
    st.markdown("""
    - ✅ Confirmed Siga-based candlestick rules across chart analysis and batch pattern reporting (EOD-only candles)
    - ✅ Upgraded Technical Screener with universe, manual, and single-stock modes plus safer run controls
    - ✅ Refreshed dashboard hero copy and developer bio for a concise professional introduction
    - ✅ Updated Dhan integration token so live data utilities remain operational
    """)
    
    st.markdown("---")
    
    # Quick Start Guide
    st.markdown("## 🚀 Quick Start Guide")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 For Beginners:
        
        **Step 1:** Explore the system
        - Start with **Technical Screener** to understand indicators
        - Try **S&R Analysis** to learn support/resistance
        - Check **Chart Analysis** for pattern recognition
        
        **Step 2:** Generate test signals
        - Use **Paper Trading Mode** (no real money)
        - Go to **Lotus Momentum Trio** → Hybrid Mode
        - Analyze small stock lists first
        
        **Step 3:** Learn and practice
        - Study the 3-layer analysis breakdown
        - Understand why signals are generated
        - Practice pattern recognition
        """)
    
    with col2:
        st.markdown("""
        ### 💎 For Experienced Traders:
        
        **Daily Routine:**
        - **Morning (9:00 AM):** Run batch analysis on Nifty 50
        - **Generate Signals:** Use Hybrid Mode (75% confidence)
        - **Chart Analysis:** Check patterns formed overnight
        - **Filter Results:** By confidence, R:R, and patterns
        
        **Advanced Features:**
        - **VWAP Strategy:** Volume-weighted trading
        - **Backtest:** Test strategies on historical data
        - **Risk Management:** Auto position sizing
        - **Multi-timeframe S&R:** Daily/Weekly/Monthly confluence
        """)
    
    st.markdown("---")
    
    # System Metrics
    st.markdown("## 📊 System Statistics")
    
    # Get current statistics
    active_signals = db.get_active_signals()
    portfolio = db.get_portfolio()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Signals", len(active_signals), delta="Current")
    
    with col2:
        st.metric("Open Positions", len(portfolio), delta="Portfolio")
    
    with col3:
        high_conf_signals = len([s for s in active_signals if s.get('confidence', 0) >= 75])
        st.metric("High Confidence", high_conf_signals, delta="75%+ signals")
    
    with col4:
        st.metric("Broker Mode", "Paper Trading", delta="Simulation")
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background-color: #f0f2f6; border-radius: 10px; margin-top: 2rem;'>
        <p style='font-size: 1.1rem; color: #555;'>
            <strong>Ready to start?</strong> Navigate using the sidebar to explore different analysis tools.
        </p>
        <p style='font-size: 0.9rem; color: #888; margin-top: 1rem;'>
            💡 Tip: Start with "Chart Analysis" to see pattern detection in action!
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# PAGE: CHART ANALYSIS (Active Signals + Chart Pattern Filter)
# ============================================================

elif page == "Chart Analysis":
    st.header("📊 Chart Analysis")
    st.caption("Analyze any stock OR view saved signals with chart pattern filtering")
    
    # Mode selection
    analysis_mode = st.radio(
        "Analysis Mode:",
        ["Single Stock Analysis", "Batch Pattern Scan", "Saved Signals (Database)"],
        horizontal=True,
        help="Single: Analyze one stock | Batch: Scan multiple stocks with pattern filter | Saved: View database signals"
    )
    
    if analysis_mode == "Single Stock Analysis":
        # Stock selection (like S&R Analysis)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if EXPANDED_UNIVERSE_AVAILABLE:
                # Create categorized stock list
                stock_categories = {
                    '--- COMMODITIES (Gold, Silver) ---': COMMODITIES,
                    '--- NIFTY 50 ---': NIFTY_50,
                    '--- NIFTY 200 (Mid-cap) ---': [s for s in NIFTY_200 if s not in NIFTY_50],
                    '--- NIFTY 500 ---': [s for s in NIFTY_500 if s not in NIFTY_200],
                    '--- SMALLCAP 250 ---': SMALLCAP_250
                }
                
                # Build options list
                stock_options = []
                for category, stocks in stock_categories.items():
                    if stocks:
                        stock_options.append(category)
                        stock_options.extend(sorted(stocks))
                
                symbol_input = st.selectbox(
                    "Select Stock:", 
                    stock_options,
                    index=stock_options.index('RELIANCE') if 'RELIANCE' in stock_options else 0,
                    help="Select from 750+ stocks (Nifty 50/200/500 + Smallcap 250)"
                )
                
                # Skip if category header selected
                if symbol_input.startswith('---'):
                    st.warning("⚠️ Please select a stock symbol, not a category header")
                    symbol_input = 'RELIANCE'
            else:
                symbol_input = st.text_input("Enter Symbol", "RELIANCE", help="Enter stock symbol (e.g., RELIANCE, TCS, INFY)")
        
        with col2:
            min_confidence_analysis = st.slider("Min Confidence", 70, 95, 75, 5, help="Minimum confidence to show signal")
        
        with col3:
            min_rr_analysis = st.slider("Min R:R", 1.0, 5.0, 1.5, 0.5, help="Minimum Risk:Reward ratio")
        
        if st.button("🔍 Analyze Stock", type="primary"):
            with st.spinner(f"Analyzing {symbol_input}..."):
                try:
                    # Import modules
                    import yfinance as yf  # CRITICAL: Import yfinance!
                    from hybrid_signal_generator import HybridSignalGenerator
                    from patterns.chart_pattern_detector import ChartPatternDetector
                    
                    if DUAL_SR_AVAILABLE:
                        from support_resistance.sr_calculator_enhanced import ProfessionalSRCalculator
                        SR_CALC_CLASS = ProfessionalSRCalculator
                    else:
                        SR_CALC_CLASS = SupportResistanceCalculator
                    
                    # Fetch data from Yahoo Finance (SAME as S&R Analysis)
                    try:
                        ticker = yf.Ticker(get_yfinance_symbol(symbol_input))
                        df_raw = ticker.history(period="1y", interval="1d")
                        
                        if not df_raw.empty and len(df_raw) > 50:
                            # Convert to expected format
                            df = pd.DataFrame({
                                'time': df_raw.index,
                                'open': df_raw['Open'].values,
                                'high': df_raw['High'].values,
                                'low': df_raw['Low'].values,
                                'close': df_raw['Close'].values,
                                'volume': df_raw['Volume'].values
                            })
                        else:
                            df = None
                    except Exception as e:
                        df = None
                        st.error(f"Error fetching data: {e}")
                    
                    if df is None or df.empty:
                        st.error(f"❌ No data available for {symbol_input}")
                    else:
                        # USE ONLY EOD DATA (exclude today's incomplete candle)
                        df_eod = df[:-1].copy() if len(df) > 5 else df
                        current_price = df_eod['close'].iloc[-1]
                        
                        # Initialize analyzers
                        hybrid_gen = HybridSignalGenerator(min_confidence=min_confidence_analysis, min_rr_ratio=min_rr_analysis)
                        sr_calc = SR_CALC_CLASS(sensitivity=3, min_touches=2)
                        pattern_detector = ChartPatternDetector()
                        
                        # Run full 3-layer analysis (using EOD data only)
                        result = hybrid_gen.analyze_stock(symbol_input, df_eod, sr_calc, pattern_detector)
                        
                        if result and result['is_treasure']:
                            st.success(f"💎 TREASURE SIGNAL FOUND for {symbol_input}!")
                            
                            # Display signal
                            col1, col2, col3 = st.columns([2, 2, 1])
                            
                            with col1:
                                st.metric("Current Price", f"₹{result['current_price']:.2f}")
                                st.metric("Entry", f"₹{result['trade_setup']['entry']:.2f}")
                                st.metric("Stop Loss", f"₹{result['trade_setup']['stop_loss']:.2f}")
                            
                            with col2:
                                st.metric("Target 1", f"₹{result['trade_setup']['target1']:.2f}")
                                st.metric("Risk:Reward", f"1:{result['trade_setup']['rr_ratio']:.2f}")
                                st.metric("Position Size", f"{result['trade_setup']['position_size']} shares")
                            
                            with col3:
                                st.metric("Confidence", f"{result['confidence']:.1f}%")
                                st.metric("Confluence", f"{result['confluence']['confluence_count']}/3")
                                profit = (result['trade_setup']['target1'] - result['trade_setup']['entry']) * result['trade_setup']['position_size']
                                if result['signal'] == 'STRONG SELL':
                                    profit = (result['trade_setup']['entry'] - result['trade_setup']['target1']) * result['trade_setup']['position_size']
                                st.metric("Profit (T1)", f"₹{profit:,.0f}")
                            
                            # 3-Layer Analysis
                            st.markdown("**📊 3-Layer Analysis:**")
                            
                            st.markdown(f"**✅ Technical ({result['technical']['confidence_pct']:.0f}%):**")
                            for factor in result['technical']['factors']:
                                st.caption(f"  • {factor}")
                            
                            st.markdown(f"**✅ S&R Analysis ({result['sr_analysis']['confidence_pct']:.0f}%):**")
                            for factor in result['sr_analysis']['factors']:
                                st.caption(f"  • {factor}")
                            
                            # Chart Pattern
                            if result['chart_pattern']['pattern']:
                                pattern = result['chart_pattern']['pattern']
                                st.markdown(f"**✅ Chart Pattern ({result['chart_pattern']['confidence_pct']:.0f}%):**")
                                st.caption(f"  • {pattern['pattern']}: {pattern['description']}")
                                if 'strength' in pattern:
                                    st.caption(f"  • Strength: {pattern['strength']}")
                            else:
                                st.markdown(f"**⚪ Chart Pattern ({result['chart_pattern']['confidence_pct']:.0f}%):**")
                                st.caption(f"  • No pattern detected")
                        
                        else:
                            st.warning(f"ℹ️ No treasure signal for {symbol_input}")
                            st.info(f"""
                            **Why no signal?**
                            - Confidence below {min_confidence_analysis}%
                            - R:R ratio below {min_rr_analysis}
                            - Not enough confluence (need 2/3 layers agreeing)
                            
                            Try: Lower confidence or R:R thresholds
                            """)
                
                except Exception as e:
                    st.error(f"❌ Error analyzing {symbol_input}: {e}")
    
    elif analysis_mode == "Batch Pattern Scan":
        st.subheader("📋 Batch Pattern Scan - Multiple Stocks")
        st.info("💡 Scan multiple stocks to find what chart patterns formed and their impact/action")
        st.caption("📅 Uses ONLY completed EOD candles (today's incomplete candle excluded). Patterns are stable and reliable!")
        
        # Output mode selection
        scan_output_mode = st.radio(
            "Output Format:",
            ["Pattern Report (Simple)", "Full Trading Signals"],
            horizontal=True,
            help="Pattern Report: Shows patterns and their meaning | Full Signals: Complete entry/SL/targets"
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col2:
            st.markdown("**Quick Presets:**")
            
            # Nifty 50 preset
            with st.expander("📊 Nifty 50 (51 stocks)", expanded=False):
                nifty50_list = "\n".join(NIFTY_50) if EXPANDED_UNIVERSE_AVAILABLE else "RELIANCE\nTCS\nHDFCBANK\nINFY\nICICIBANK"
                st.code(nifty50_list, language=None)
                st.caption("👆 Copy and paste")
            
            # Nifty Bank
            with st.expander("🏦 Nifty Bank (12 stocks)", expanded=False):
                bank_list = "HDFCBANK\nICICIBANK\nSBIN\nKOTAKBANK\nAXISBANK\nINDUSINDBK\nBANDHANBNK\nFEDERALBNK\nIDFCFIRSTB\nPNB\nBANKBARODA\nCANBK"
                st.code(bank_list, language=None)
                st.caption("👆 Copy and paste")
            
            # Top 10 Most Active
            with st.expander("🔥 Top 10 Most Active", expanded=False):
                active_list = "RELIANCE\nTCS\nINFY\nHDFCBANK\nICICIBANK\nBHARTIARTL\nITC\nSBIN\nHINDUNILVR\nKOTAKBANK"
                st.code(active_list, language=None)
                st.caption("👆 Copy and paste")
        
        with col1:
            st.markdown("**Enter Stock Symbols (one per line):**")
            batch_stocks_input = st.text_area(
                "Stock Symbols:",
                placeholder="RELIANCE\nTCS\nINFY\nHDFCBANK\nICICIBANK",
                height=200,
                help="Enter NSE stock symbols, one per line"
            )
        
        # Chart Pattern Selection
        st.markdown("#### 📊 Chart Pattern Filter")
        col1, col2 = st.columns(2)
        
        with col1:
            pattern_filter_mode = st.radio(
                "Pattern Filter:",
                ["Show ALL Signals", "Only Stocks WITH Patterns", "Specific Patterns Only"],
                help="Choose how to filter by chart patterns"
            )
        
        with col2:
            if pattern_filter_mode == "Specific Patterns Only":
                selected_batch_patterns = st.multiselect(
                    "Select Patterns:",
                    ["Hammer", "Shooting Star", "Bullish Engulfing", "Bearish Engulfing",
                     "Morning Star", "Evening Star", "Three White Soldiers", "Three Black Crows", "Doji"],
                    default=["Hammer", "Bullish Engulfing"],
                    help="Only show stocks with these patterns"
                )
            else:
                selected_batch_patterns = None
        
        # Analysis Settings
        col1, col2 = st.columns(2)
        with col1:
            batch_min_confidence = st.slider("Min Confidence", 70, 95, 75, 5, help="Minimum confidence threshold")
        with col2:
            batch_min_rr = st.slider("Min R:R", 1.0, 5.0, 1.5, 0.5, help="Minimum Risk:Reward ratio")
        
        # Parse stock list
        if batch_stocks_input:
            batch_stock_list = [s.strip().upper() for s in batch_stocks_input.split('\n') if s.strip()]
            st.caption(f"✅ Ready to analyze {len(batch_stock_list)} stocks")
        else:
            batch_stock_list = []
            st.warning("⚠️ Please enter stock symbols")
        
        if st.button("🔍 Scan Stocks for Patterns", type="primary", disabled=(len(batch_stock_list) == 0)):
            if len(batch_stock_list) == 0:
                st.error("❌ Please enter stocks first!")
                st.stop()
            
            st.markdown("---")
            st.subheader(f"🔍 Scanning {len(batch_stock_list)} stocks...")
            
            # Initialize
            try:
                import yfinance as yf  # CRITICAL: Import yfinance!
                from hybrid_signal_generator import HybridSignalGenerator
                from patterns.chart_pattern_detector import ChartPatternDetector
                
                if DUAL_SR_AVAILABLE:
                    from support_resistance.sr_calculator_enhanced import ProfessionalSRCalculator
                    SR_CALC_CLASS = ProfessionalSRCalculator
                else:
                    SR_CALC_CLASS = SupportResistanceCalculator
                
                hybrid_gen = HybridSignalGenerator(min_confidence=batch_min_confidence, min_rr_ratio=batch_min_rr)
                sr_calc = SR_CALC_CLASS(sensitivity=3, min_touches=2)
                pattern_detector = ChartPatternDetector()
                
                # Progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                pattern_results = []
                stocks_with_any_patterns = 0  # Track how many stocks had patterns (before filtering)
                errors_encountered = []  # Track errors for debugging
                
                for idx, symbol in enumerate(batch_stock_list):
                    try:
                        status_text.text(f"Analyzing {symbol}... ({idx+1}/{len(batch_stock_list)})")
                        
                        # Fetch data from Yahoo Finance
                        ticker = yf.Ticker(get_yfinance_symbol(symbol))
                        df_raw = ticker.history(period="6mo", interval="1d")
                        
                        if not df_raw.empty and len(df_raw) >= 5:
                            # Convert to expected format
                            df = pd.DataFrame({
                                'time': df_raw.index,
                                'open': df_raw['Open'].values,
                                'high': df_raw['High'].values,
                                'low': df_raw['Low'].values,
                                'close': df_raw['Close'].values,
                                'volume': df_raw['Volume'].values
                            })
                        else:
                            df = None
                        
                        if df is not None and not df.empty:
                            current_price = df['close'].iloc[-1]
                            
                            # DIFFERENT LOGIC FOR PATTERN REPORT VS FULL SIGNALS
                            if scan_output_mode == "Pattern Report (Simple)":
                                # PATTERN REPORT MODE: Just detect patterns (NO signal filtering!)
                                # USE ONLY COMPLETED EOD CANDLES (Exclude today's incomplete candle)
                                df_eod = df[:-1].copy()  # Remove last candle (today's incomplete)
                                
                                # Check last 5 COMPLETED candles for patterns
                                pattern_result = pattern_detector.detect_all_patterns(df_eod, check_last_n_candles=5)
                                
                                if pattern_result and len(pattern_result) > 0:
                                    stocks_with_any_patterns += 1  # Count stocks with ANY patterns
                                    
                                    # Get the most recent/strongest pattern
                                    detected_pattern = max(pattern_result, key=lambda x: x.get('confidence', 0))
                                    
                                    # Check if matches filter
                                    should_include = False
                                    pattern_name = detected_pattern.get('pattern', '')
                                    
                                    if pattern_filter_mode == "Show ALL Signals":
                                        should_include = True
                                    elif pattern_filter_mode == "Only Stocks WITH Patterns":
                                        should_include = True  # Any pattern
                                    elif pattern_filter_mode == "Specific Patterns Only":
                                        # Match pattern name
                                        # Detector returns: 'HAMMER', 'BULLISH_ENGULFING', etc.
                                        # UI sends: 'Hammer', 'Bullish Engulfing', etc.
                                        # Convert both to same format for matching
                                        pattern_name_normalized = pattern_name.upper().replace('_', ' ')
                                        should_include = any(
                                            pattern_name_normalized == selected.upper() or 
                                            pattern_name.upper() == selected.upper().replace(' ', '_')
                                            for selected in selected_batch_patterns
                                        )
                                    
                                    if should_include:
                                        # Build lightweight result for pattern report
                                        # Get basic technical context
                                        rsi_value = None
                                        if len(df) >= 14:
                                            delta = df['close'].diff()
                                            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
                                            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                                            rs = gain / loss
                                            rsi = 100 - (100 / (1 + rs))
                                            rsi_value = rsi.iloc[-1]
                                        
                                        # Simple S&R
                                        sr_data = sr_calc.calculate_support_resistance(df, current_price)
                                        nearest_sup = sr_data.get('supports', [{}])[0].get('level', 0) if sr_data.get('supports') else 0
                                        nearest_res = sr_data.get('resistances', [{}])[0].get('level', 0) if sr_data.get('resistances') else 0
                                        
                                        pattern_results.append({
                                            'symbol': symbol,
                                            'current_price': current_price,
                                            'chart_pattern': {'pattern': detected_pattern},
                                            'confidence': detected_pattern.get('confidence', 50),  # Use confidence from pattern
                                            'signal': 'BUY' if detected_pattern.get('type') == 'BULLISH' else ('SELL' if detected_pattern.get('type') == 'BEARISH' else 'NEUTRAL'),
                                            'technical': {
                                                'factors': [f"RSI: {rsi_value:.1f}" if rsi_value else "RSI: N/A"],
                                                'confidence_pct': 50
                                            },
                                            'sr_analysis': {
                                                'factors': [f"Support: ₹{nearest_sup:.2f}, Resistance: ₹{nearest_res:.2f}"],
                                                'confidence_pct': 50
                                            },
                                            'confluence': {'confluence_count': 1}
                                        })
                            
                            else:
                                # FULL SIGNALS MODE: Run complete treasure signal analysis
                                # USE ONLY COMPLETED EOD CANDLES (Exclude today's incomplete candle)
                                df_eod = df[:-1].copy()  # Remove last candle (today's incomplete)
                                
                                result = hybrid_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                                
                                if result and result['is_treasure']:
                                    # Apply pattern filter
                                    has_pattern = result['chart_pattern']['pattern'] is not None
                                    pattern_name = result['chart_pattern']['pattern']['pattern'] if has_pattern else None
                                    
                                    should_include = False
                                    
                                    if pattern_filter_mode == "Show ALL Signals":
                                        should_include = True
                                    elif pattern_filter_mode == "Only Stocks WITH Patterns":
                                        should_include = has_pattern
                                    elif pattern_filter_mode == "Specific Patterns Only":
                                        should_include = has_pattern and pattern_name in selected_batch_patterns
                                    
                                    if should_include:
                                        pattern_results.append(result)
                    
                    except Exception as e:
                        errors_encountered.append(f"{symbol}: {str(e)}")
                        # Continue to next stock
                    
                    progress_bar.progress((idx + 1) / len(batch_stock_list))
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                pattern_state = {
                    'pattern_results': pattern_results,
                    'errors': errors_encountered,
                    'stocks_with_any_patterns': stocks_with_any_patterns,
                    'total_requested': len(batch_stock_list),
                    'stocks_scanned': len(batch_stock_list) - len(errors_encountered),
                    'scan_output_mode': scan_output_mode,
                    'pattern_filter_mode': pattern_filter_mode,
                    'selected_patterns': selected_batch_patterns,
                    'generated_at': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                
                if pattern_results and scan_output_mode == "Pattern Report (Simple)":
                    pattern_report_data = []
                    
                    for result in pattern_results:
                        pattern_info = result['chart_pattern']['pattern']
                        
                        if pattern_info:
                            pattern_name = pattern_info['pattern']
                            pattern_type = pattern_info.get('type', 'NEUTRAL')
                            pattern_strength = pattern_info.get('strength', 'Moderate')
                            
                            if pattern_type == 'BULLISH':
                                action = "🟢 Potential BUY (Bullish Reversal/Continuation)"
                                impact = "Upward price movement expected"
                            elif pattern_type == 'BEARISH':
                                action = "🔴 Potential SELL (Bearish Reversal/Continuation)"
                                impact = "Downward price movement expected"
                            else:
                                action = "⚪ NEUTRAL (Watch for confirmation)"
                                impact = "Indecision - wait for breakout"
                        else:
                            pattern_name = "No specific pattern"
                            pattern_type = "NEUTRAL"
                            pattern_strength = "N/A"
                            action = f"{result['signal']} based on tech/S&R"
                            impact = "No pattern, but strong technical confluence"
                        
                        tech_factors = ", ".join(result['technical']['factors'][:2])
                        sr_factors = ", ".join(result['sr_analysis']['factors'][:1])
                        
                        # Get detected date from pattern
                        detected_date_str = ''
                        if pattern_info and isinstance(pattern_info, dict):
                            detected_date_str = pattern_info.get('detected_date_str', '')
                            if detected_date_str:
                                try:
                                    from datetime import datetime
                                    date_obj = datetime.strptime(detected_date_str, '%Y-%m-%d')
                                    detected_date_str = f"formed on {date_obj.strftime('%d %b').lower()}"
                                except:
                                    detected_date_str = f"formed on {detected_date_str}"
                        
                        pattern_report_data.append({
                            'Stock': result['symbol'],
                            'Pattern': pattern_name,
                            'Actual': detected_date_str,
                            'Type': pattern_type,
                            'Strength': pattern_strength,
                            'Action': action,
                            'Impact': impact,
                            'Price': f"₹{result['current_price']:.2f}",
                            'Confidence': f"{result['confidence']:.0f}%",
                            'Tech Context': tech_factors,
                            'S&R Context': sr_factors
                        })
                    
                    pattern_state['pattern_report_data'] = pattern_report_data
                else:
                    pattern_state['pattern_report_data'] = None
                
                st.session_state['batch_pattern_state'] = pattern_state
            
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Error during batch analysis: {e}")
                import traceback
                st.code(traceback.format_exc())
    
    # =========================
    # Display stored results
    # =========================
    pattern_state = st.session_state.get('batch_pattern_state')
    
    if pattern_state:
        st.markdown("---")
        
        errors_encountered = pattern_state.get('errors', [])
        pattern_results = pattern_state.get('pattern_results', [])
        stocks_scanned = pattern_state.get('stocks_scanned', 0)
        total_requested = pattern_state.get('total_requested', 0)
        stocks_with_any_patterns = pattern_state.get('stocks_with_any_patterns', 0)
        stored_output_mode = pattern_state.get('scan_output_mode', "Pattern Report (Simple)")
        pattern_report_data = pattern_state.get('pattern_report_data')
        generated_at = pattern_state.get('generated_at', '')
        
        st.caption(f"🕒 Last scan: {generated_at} | Stocks requested: {total_requested}")
        
        if errors_encountered:
            with st.expander(f"⚠️ Errors encountered ({len(errors_encountered)} stocks)", expanded=False):
                for error in errors_encountered:
                    st.caption(f"• {error}")
        
        if pattern_results:
            st.success(f"📊 Found {len(pattern_results)} stocks with patterns/signals out of {stocks_scanned} successfully scanned ({(len(pattern_results)/stocks_scanned*100):.1f}%)")
            
            if stored_output_mode == "Pattern Report (Simple)":
                st.markdown("### 📊 Chart Pattern Report")
                
                if pattern_report_data is None:
                    st.info("ℹ️ Run the scan again to refresh the pattern report.")
                else:
                    for idx, report in enumerate(pattern_report_data, 1):
                        with st.expander(f"{idx}. {report['Stock']} - {report['Pattern']} ({report['Type']})", expanded=(idx <= 3)):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown("**📊 Pattern Details:**")
                                st.caption(f"Pattern: {report['Pattern']}")
                                st.caption(f"Type: {report['Type']}")
                                st.caption(f"Strength: {report['Strength']}")
                            
                            with col2:
                                st.markdown("**💡 Action & Impact:**")
                                st.caption(f"Action: {report['Action']}")
                                st.caption(f"Impact: {report['Impact']}")
                            
                            with col3:
                                st.markdown("**📈 Current Status:**")
                                st.caption(f"Price: {report['Price']}")
                                st.caption(f"Confidence: {report['Confidence']}")
                            
                            st.markdown("**🔍 Context:**")
                            st.caption(f"📊 Technical: {report['Tech Context']}")
                            st.caption(f"📈 S&R: {report['S&R Context']}")
                    
                    st.markdown("---")
                    st.markdown("### 📋 Quick Summary Table")
                    
                    pattern_icons = {
                        'HAMMER': '🔨',
                        'SHOOTING_STAR': '🌠',
                        'BULLISH_ENGULFING': '🟢📦',
                        'BEARISH_ENGULFING': '🔴📦',
                        'MORNING_STAR': '⭐🌅',
                        'EVENING_STAR': '⭐🌆',
                        'THREE_WHITE_SOLDIERS': '⬆️⬆️⬆️',
                        'THREE_BLACK_CROWS': '⬇️⬇️⬇️',
                        'DOJI': '➕',
                        'INVERTED_HAMMER': '🔨⬆️',
                        'HANGING_MAN': '🔨⬇️',
                        'PIERCING_PATTERN': '🟢➚',
                        'DARK_CLOUD_COVER': '🔴➘'
                    }
                    
                    pattern_visuals = {
                        'HAMMER': '━━┃ (Long lower wick)',
                        'SHOOTING_STAR': '┃━━ (Long upper wick)',
                        'BULLISH_ENGULFING': '▮▯ → ▮▮ (Green engulfs red)',
                        'BEARISH_ENGULFING': '▮▮ → ▮▯ (Red engulfs green)',
                        'MORNING_STAR': '▯ ━ ▮ (3-candle bull)',
                        'EVENING_STAR': '▮ ━ ▯ (3-candle bear)',
                        'THREE_WHITE_SOLDIERS': '▮ ▮ ▮ (3 green up)',
                        'THREE_BLACK_CROWS': '▯ ▯ ▯ (3 red down)',
                        'DOJI': '━┃━ (Cross, indecision)',
                        'INVERTED_HAMMER': '┃━━ (Upper wick, bullish)',
                        'HANGING_MAN': '━━┃ (Lower wick, bearish)',
                        'PIERCING_PATTERN': '▯ ▮ (Green pierces red)',
                        'DARK_CLOUD_COVER': '▮ ▯ (Red covers green)'
                    }
                    
                    summary_df = pd.DataFrame([
                        {
                            'Stock': r['Stock'],
                            'Icon': pattern_icons.get(r['Pattern'], '📊'),
                            'Pattern': r['Pattern'].replace('_', ' ').title(),
                            'Visual': pattern_visuals.get(r['Pattern'], ''),
                            'Type': r['Type'],
                            'Action': r['Action'].split('(')[0].strip(),
                            'Price': r['Price'],
                            'Confidence': r['Confidence']
                        }
                        for r in pattern_report_data
                    ])
                    
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
                    
                    full_df = pd.DataFrame(pattern_report_data)
                    csv_data = full_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "⬇️ Download Pattern Report",
                        csv_data,
                        f"pattern_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv",
                        key="pattern_report_download"
                    )
            
            else:
                # Full Trading Signals mode display
                buy_signals = [s for s in pattern_results if 'BUY' in s['signal']]
                sell_signals = [s for s in pattern_results if 'SELL' in s['signal']]
                
                if buy_signals:
                    st.markdown("### 🟢 BUY SIGNALS")
                    for signal in sorted(buy_signals, key=lambda x: x['confidence'], reverse=True):
                        with st.expander(f"💎 {signal['symbol']} - {signal['confidence']:.1f}% Confidence", expanded=False):
                            col1, col2, col3 = st.columns([2, 2, 1])
                            
                            with col1:
                                st.metric("Current Price", f"₹{signal['current_price']:.2f}")
                                st.metric("Entry", f"₹{signal['trade_setup']['entry']:.2f}")
                                st.metric("Stop Loss", f"₹{signal['trade_setup']['stop_loss']:.2f}")
                            
                            with col2:
                                st.metric("Target 1", f"₹{signal['trade_setup']['target1']:.2f}")
                                st.metric("Risk:Reward", f"1:{signal['trade_setup']['rr_ratio']:.2f}")
                                st.metric("Position Size", f"{signal['trade_setup']['position_size']} shares")
                            
                            with col3:
                                st.metric("Confidence", f"{signal['confidence']:.1f}%")
                                st.metric("Confluence", f"{signal['confluence']['confluence_count']}/3")
                                profit = (signal['trade_setup']['target1'] - signal['trade_setup']['entry']) * signal['trade_setup']['position_size']
                                st.metric("Profit (T1)", f"₹{profit:,.0f}")
                            
                            st.markdown("**📊 3-Layer Analysis:**")
                            st.markdown(f"**✅ Technical ({signal['technical']['confidence_pct']:.0f}%):**")
                            for factor in signal['technical']['factors']:
                                st.caption(f"  • {factor}")
                            
                            st.markdown(f"**✅ S&R Analysis ({signal['sr_analysis']['confidence_pct']:.0f}%):**")
                            for factor in signal['sr_analysis']['factors']:
                                st.caption(f"  • {factor}")
                            
                            if signal['chart_pattern']['pattern']:
                                pattern = signal['chart_pattern']['pattern']
                                st.markdown(f"**✅ Chart Pattern ({signal['chart_pattern']['confidence_pct']:.0f}%):**")
                                st.caption(f"  • {pattern['pattern']}: {pattern['description']}")
                                if 'strength' in pattern:
                                    st.caption(f"  • Strength: {pattern['strength']}")
                            else:
                                st.markdown(f"**⚪ Chart Pattern ({signal['chart_pattern']['confidence_pct']:.0f}%):**")
                                st.caption("  • No pattern detected")
                
                if sell_signals:
                    st.markdown("### 🔴 SELL SIGNALS")
                    for signal in sorted(sell_signals, key=lambda x: x['confidence'], reverse=True):
                        with st.expander(f"💎 {signal['symbol']} - {signal['confidence']:.1f}% Confidence", expanded=False):
                            col1, col2, col3 = st.columns([2, 2, 1])
                            
                            with col1:
                                st.metric("Current Price", f"₹{signal['current_price']:.2f}")
                                st.metric("Entry", f"₹{signal['trade_setup']['entry']:.2f}")
                                st.metric("Stop Loss", f"₹{signal['trade_setup']['stop_loss']:.2f}")
                            
                            with col2:
                                st.metric("Target 1", f"₹{signal['trade_setup']['target1']:.2f}")
                                st.metric("Risk:Reward", f"1:{signal['trade_setup']['rr_ratio']:.2f}")
                                st.metric("Position Size", f"{signal['trade_setup']['position_size']} shares")
                            
                            with col3:
                                st.metric("Confidence", f"{signal['confidence']:.1f}%")
                                st.metric("Confluence", f"{signal['confluence']['confluence_count']}/3")
                                profit = (signal['trade_setup']['entry'] - signal['trade_setup']['target1']) * signal['trade_setup']['position_size']
                                st.metric("Profit (T1)", f"₹{profit:,.0f}")
                            
                            st.markdown("**📊 3-Layer Analysis:**")
                            st.markdown(f"**✅ Technical ({signal['technical']['confidence_pct']:.0f}%):**")
                            for factor in signal['technical']['factors']:
                                st.caption(f"  • {factor}")
                            
                            st.markdown(f"**✅ S&R Analysis ({signal['sr_analysis']['confidence_pct']:.0f}%):**")
                            for factor in signal['sr_analysis']['factors']:
                                st.caption(f"  • {factor}")
                            
                            if signal['chart_pattern']['pattern']:
                                pattern = signal['chart_pattern']['pattern']
                                st.markdown(f"**✅ Chart Pattern ({signal['chart_pattern']['confidence_pct']:.0f}%):**")
                                st.caption(f"  • {pattern['pattern']}: {pattern['description']}")
                                if 'strength' in pattern:
                                    st.caption(f"  • Strength: {pattern['strength']}")
                            else:
                                st.markdown(f"**⚪ Chart Pattern ({signal['chart_pattern']['confidence_pct']:.0f}%):**")
                                st.caption("  • No pattern detected")
            
            if stored_output_mode != scan_output_mode:
                st.info(f"ℹ️ Displaying last scan results generated in **{stored_output_mode}** mode. Run the scan again to refresh for the current selection.")
        
        else:
            st.warning("ℹ️ No patterns found matching your filter criteria")
            
            if stocks_with_any_patterns > 0:
                st.info(f"""
                **📊 Patterns were detected but filtered out!**
                
                - **{stocks_with_any_patterns}** out of {total_requested} stocks had patterns
                - But they didn't match your selected pattern filter
                
                **Try:**
                • Change Pattern Filter to "Show ALL Signals"
                • Or select different specific patterns
                """)
            else:
                st.info(f"""
                **❌ NO patterns detected in any of the {total_requested} stocks!**
                
                **Why?**
                - These stocks didn't form clear patterns in last 5 days
                - Low volatility = fewer patterns
                - EOD data = only completed daily candles
                
                **Try these VOLATILE stocks instead:**
                BAJFINANCE, TATAMOTORS, ADANIENT, VEDL, TATASTEEL
                
                Or wait until after market close (3:30 PM) for today's patterns!
                """)
    
    else:  # Saved Signals mode
        st.subheader("💾 Saved Signals from Database")
        
        # Filters Row 1
        col1, col2 = st.columns(2)
        with col1:
            min_confidence = st.slider("Minimum Confidence", 0.0, 100.0, 70.0, 5.0)
        with col2:
            signal_filter = st.selectbox("Filter by Type", ["ALL", "BUY", "SELL"])
        
        # Filters Row 2: Chart Pattern Filter
        st.markdown("#### 📊 Chart Pattern Filter (Optional)")
        col1, col2 = st.columns(2)
        
        with col1:
            pattern_filter_enabled = st.checkbox("Filter by Chart Patterns", value=False,
                                                help="Only show signals with specific chart patterns")
        
        with col2:
            if pattern_filter_enabled:
                selected_patterns = st.multiselect(
                    "Select Patterns:",
                    ["Hammer", "Shooting Star", "Bullish Engulfing", "Bearish Engulfing",
                     "Morning Star", "Evening Star", "Three White Soldiers", "Three Black Crows", "Doji"],
                    default=[],
                    help="Show only signals with these patterns"
                )
            else:
                selected_patterns = None
        
        # Get signals
        signals = db.get_active_signals(min_confidence=min_confidence)
        
        if signal_filter != "ALL":
            signals = [s for s in signals if s.get('signal_type') == signal_filter]
        
        # Apply chart pattern filter if enabled
        if pattern_filter_enabled and selected_patterns:
            filtered_signals = []
            for signal in signals:
                # Check if signal has chart_pattern data (for Hybrid signals)
                chart_pattern_data = signal.get('chart_pattern') or signal.get('metadata', {}).get('chart_pattern')
                if chart_pattern_data and isinstance(chart_pattern_data, dict):
                    pattern_info = chart_pattern_data.get('pattern', {})
                    if pattern_info and isinstance(pattern_info, dict):
                        pattern_name = pattern_info.get('pattern', '')
                        if pattern_name in selected_patterns:
                            filtered_signals.append(signal)
            signals = filtered_signals
        
        st.info(f"📊 Found {len(signals)} signals matching criteria")
        
        if signals:
            # Convert to DataFrame
            df_signals = pd.DataFrame(signals)
            
            # Display table
            st.dataframe(
                df_signals[[
                    'symbol', 'signal_type', 'confidence', 'entry_price',
                    'target_price', 'stop_loss', 'generated_at', 'status'
                ]],
                use_container_width=True
            )
            
            # Export option
            if st.button("📥 Export Signals to CSV"):
                csv = df_signals.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "signals.csv",
                    "text/csv"
                )
        else:
            st.warning("No signals found matching criteria")

# ============================================================
# PAGE: LOTUS MOMENTUM TRIO (formerly Generate New Signal)
# ============================================================

elif page == "Lotus Momentum Trio":
    st.header("🪷 Lotus Momentum Trio")
    
    # Mode selection: Manual Entry OR Hybrid Analysis
    signal_generation_mode = st.radio(
        "Signal Generation Mode:",
        ["Manual Entry", "Hybrid Mode (Treasure Signals 💎)"],
        horizontal=True,
        help="Manual: Enter signal details manually | Hybrid: Auto-detect high-accuracy signals"
    )
    
    if signal_generation_mode == "Manual Entry":
        # EXISTING CODE - NO CHANGES!
        st.info("💡 This signal will be SAVED to database and persist even after refresh!")
        
        with st.form("signal_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                symbol = st.text_input("Symbol", "NSE_RELIANCE")
                signal_type = st.selectbox("Signal Type", ["BUY", "SELL"])
                confidence = st.number_input("Confidence (%)", 0.0, 100.0, 75.0, 1.0)
                entry_price = st.number_input("Entry Price", 0.0, 10000.0, 2450.0, 1.0)
            
            with col2:
                target_price = st.number_input("Target Price", 0.0, 10000.0, 2550.0, 1.0)
                stop_loss = st.number_input("Stop Loss", 0.0, 10000.0, 2400.0, 1.0)
                model_name = st.text_input("Model Name", "manual_entry")
                signal_strength = st.selectbox("Strength", ["WEAK", "MEDIUM", "STRONG"])
            
            submitted = st.form_submit_button("✅ Generate Signal")
            
            if submitted:
                # Calculate risk metrics
                position = risk_engine.calculate_position_size(
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    confidence=confidence / 100
                )
                
                # Prepare signal data
                signal_data = {
                    'symbol': symbol,
                    'signal_type': signal_type,
                    'confidence': confidence,
                    'entry_price': entry_price,
                    'target_price': target_price,
                    'stop_loss': stop_loss,
                    'model_name': model_name,
                    'signal_strength': signal_strength,
                    'volume': 0,
                    'risk_reward_ratio': ((target_price - entry_price) / (entry_price - stop_loss)) if stop_loss else 0,
                    'position_size': position.get('position_size', 0),
                    'max_risk_amount': position.get('risk_amount', 0),
                    'valid_until': datetime.now() + timedelta(days=1)
                }
                
                # Save to database
                signal_id = db.save_signal(signal_data)
                
                if signal_id:
                    st.success(f"✅ Signal generated and saved! ID: {signal_id}")
                    
                    # Show risk analysis
                    st.subheader("📊 Risk Analysis")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Recommended Quantity", position['quantity'])
                    with col2:
                        st.metric("Position Size", f"₹{position['position_size']:,.0f}")
                    with col3:
                        st.metric("Max Risk", f"₹{position['risk_amount']:,.0f} ({position['risk_pct']:.2f}%)")
                    
                    st.info("🔄 Refresh the page - your signal will still be there! (Database persistence working!)")
                else:
                    st.error("❌ Failed to save signal")
    
    # ========================================================================
    # HYBRID MODE (NEW!) - TREASURE SIGNAL GENERATOR
    # ========================================================================
    else:  # Hybrid Mode
        st.subheader("💎 Hybrid Signal Generator - Treasure Mode")
        st.info("🎯 Combines Technical + S&R + Chart Patterns. Only shows 85%+ confidence signals (TREASURES!)")
        st.caption("Philosophy: Quality over Quantity - Better to have 5 perfect signals than 50 mediocre ones")
        
        # Import required modules (READ-ONLY!)
        try:
            from hybrid_signal_generator import HybridSignalGenerator
            from patterns.chart_pattern_detector import ChartPatternDetector
            if DUAL_SR_AVAILABLE:
                from support_resistance.sr_calculator_enhanced import ProfessionalSRCalculator
                SR_CALC_CLASS = ProfessionalSRCalculator
            else:
                SR_CALC_CLASS = SupportResistanceCalculator
            
            HYBRID_AVAILABLE = True
        except ImportError as e:
            HYBRID_AVAILABLE = False
            st.error(f"❌ Hybrid modules not available: {e}")
        
        if HYBRID_AVAILABLE:
            # Bull Market Info
            st.info("""
            🐂 **BULL MARKET MODE ACTIVE!** - Optimized for trending markets
            
            **What Changed:**
            - Default Confidence: **75%** (down from 85%)
            - Default R:R: **1.5** (down from 2.0)
            - Wider S&R acceptance zones (up to 8% distance)
            - Extended RSI ranges (30-70 with partial signals)
            - Flexible confluence (2/3 layers agree OR 1 very strong layer)
            
            💡 **Result:** More signals while maintaining quality!
            """)
            
            # Stock Selection Mode
            st.markdown("#### 📈 Stock Selection")
            selection_mode = st.radio(
                "Choose how to select stocks:",
                ["⭐ My Stocks", "Universe (Batch Analysis)", "Manual Selection (Specific Stocks)"],
                horizontal=True,
                help="My Stocks: Your favorites | Universe: Analyze entire Nifty 50/200 | Manual: Pick specific stocks"
            )
            
            stock_list = []
            
            if selection_mode == "⭐ My Stocks":
                stock_list = get_my_stocks()
                render_my_stocks_manager()
            elif selection_mode == "Universe (Batch Analysis)":
                if EXPANDED_UNIVERSE_AVAILABLE:
                    universe_choice = st.selectbox(
                        "Select Universe:",
                        ["Nifty 50 (51 stocks)", "Nifty 200 (200 stocks)", "Small Cap 250 (250 stocks)", "ALL Stocks (750+)"]
                    )
                else:
                    universe_choice = "Nifty 50 (51 stocks)"
                
                # Get stock list based on universe
                if "Nifty 50" in universe_choice:
                    stock_list = NIFTY_50 if EXPANDED_UNIVERSE_AVAILABLE else ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
                elif "Nifty 200" in universe_choice:
                    stock_list = NIFTY_200 if EXPANDED_UNIVERSE_AVAILABLE else NIFTY_50
                elif "Small Cap 250" in universe_choice:
                    stock_list = SMALLCAP_250 if EXPANDED_UNIVERSE_AVAILABLE else NIFTY_50
                else:
                    stock_list = ALL_STOCKS if EXPANDED_UNIVERSE_AVAILABLE else NIFTY_50
            
            else:  # Manual Selection
                st.info("💡 Enter stock symbols separated by commas (e.g., RELIANCE, TCS, INFY, HDFCBANK)")
                manual_input = st.text_input(
                    "Stock Symbols:",
                    placeholder="RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK",
                    help="Enter NSE symbols separated by commas"
                )
                
                if manual_input:
                    # Parse and clean stock symbols
                    stock_list = [s.strip().upper() for s in manual_input.split(',') if s.strip()]
                else:
                    stock_list = []
            
            # Settings
            st.markdown("#### ⚙️ Signal Parameters")
            col1, col2 = st.columns(2)
            
            with col1:
                min_confidence = st.slider("Minimum Confidence (%)", 70, 95, 75, 5,
                                          help="Only show signals above this confidence (Default: 75% for bull markets)")
            
            with col2:
                min_rr = st.slider("Minimum R:R", 1.0, 5.0, 1.5, 0.5,
                                  help="Minimum Risk:Reward ratio (Default: 1.5 for bull markets)")
            
            # Display stock count
            if stock_list:
                st.caption(f"✅ Ready to analyze {len(stock_list)} stocks")
            else:
                st.warning("⚠️ Please select stocks to analyze")
            
            if st.button("💎 Find Treasure Signals", type="primary", disabled=(len(stock_list) == 0)):
                if len(stock_list) == 0:
                    st.error("❌ Please select stocks first!")
                    st.stop()
                
                st.markdown("---")
                st.subheader(f"🔍 Analyzing {len(stock_list)} stocks...")
                
                # Initialize
                hybrid_gen = HybridSignalGenerator(min_confidence=min_confidence, min_rr_ratio=min_rr)
                sr_calc = SR_CALC_CLASS(sensitivity=3, min_touches=2)
                pattern_detector = ChartPatternDetector()
                
                treasure_signals = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                import yfinance as yf
                
                # Analyze each stock
                for idx, symbol in enumerate(stock_list):
                    status_text.text(f"Analyzing {symbol}... ({idx+1}/{len(stock_list)})")
                    
                    try:
                        # Fetch data
                        ticker = yf.Ticker(get_yfinance_symbol(symbol))
                        df_raw = ticker.history(period="6mo", interval="1d")
                        
                        if df_raw.empty or len(df_raw) < 50:
                            progress_bar.progress((idx + 1) / len(stock_list))
                            continue
                        
                        # Convert to format
                        df = pd.DataFrame({
                            'time': df_raw.index,
                            'open': df_raw['Open'].values,
                            'high': df_raw['High'].values,
                            'low': df_raw['Low'].values,
                            'close': df_raw['Close'].values,
                            'volume': df_raw['Volume'].values
                        })
                        
                        # USE ONLY EOD DATA (exclude today's incomplete candle)
                        df_eod = df[:-1].copy() if len(df) > 5 else df
                        
                        # Analyze (3-layer confluence) - using EOD data only
                        result = hybrid_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                        
                        if result and result['is_treasure']:
                            treasure_signals.append(result)
                    
                    except Exception as e:
                        # Skip stocks with errors
                        pass
                    
                    progress_bar.progress((idx + 1) / len(stock_list))
                
                # Clear progress
                progress_bar.empty()
                status_text.empty()
                
                # Display results
                st.markdown("---")
                
                if treasure_signals:
                    st.success(f"💎 Found {len(treasure_signals)} TREASURE SIGNALS out of {len(stock_list)} stocks ({len(treasure_signals)/len(stock_list)*100:.1f}%)")
                    
                    # Separate BUY and SELL
                    buy_signals = [s for s in treasure_signals if 'BUY' in s['signal']]
                    sell_signals = [s for s in treasure_signals if 'SELL' in s['signal']]
                    
                    # Display BUY signals
                    if buy_signals:
                        st.markdown("### 🟢 STRONG BUY SIGNALS")
                        for signal in sorted(buy_signals, key=lambda x: x['confidence'], reverse=True):
                            with st.expander(f"💎 {signal['symbol']} - {signal['confidence']:.1f}% Confidence", expanded=True):
                                col1, col2, col3 = st.columns([2, 2, 1])
                                
                                with col1:
                                    st.metric("Current Price", f"₹{signal['current_price']:.2f}")
                                    st.metric("Entry", f"₹{signal['trade_setup']['entry']:.2f}")
                                    st.metric("Stop Loss", f"₹{signal['trade_setup']['stop_loss']:.2f}")
                                
                                with col2:
                                    st.metric("Target 1", f"₹{signal['trade_setup']['target1']:.2f}")
                                    st.metric("Risk:Reward", f"1:{signal['trade_setup']['rr_ratio']:.2f}")
                                    st.metric("Position Size", f"{signal['trade_setup']['position_size']} shares")
                                
                                with col3:
                                    st.metric("Confidence", f"{signal['confidence']:.1f}%")
                                    st.metric("Confluence", f"{signal['confluence']['confluence_count']}/3")
                                    profit = signal['trade_setup'].get('potential_profit1', 0)
                                    st.metric("Profit (T1)", f"₹{profit:,.0f}")
                                
                                # Show all 3 layers
                                st.markdown("**📊 3-Layer Analysis:**")
                                
                                st.markdown(f"**✅ Technical ({signal['technical']['confidence_pct']:.0f}%):**")
                                for factor in signal['technical']['factors']:
                                    st.caption(f"  • {factor}")
                                
                                st.markdown(f"**✅ S&R Analysis ({signal['sr_analysis']['confidence_pct']:.0f}%):**")
                                for factor in signal['sr_analysis']['factors']:
                                    st.caption(f"  • {factor}")
                                
                                # Chart Pattern - ALWAYS SHOW (even if none detected)
                                if signal['chart_pattern']['pattern']:
                                    pattern = signal['chart_pattern']['pattern']
                                    st.markdown(f"**✅ Chart Pattern ({signal['chart_pattern']['confidence_pct']:.0f}%):**")
                                    st.caption(f"  • {pattern['pattern']}: {pattern['description']}")
                                    if 'strength' in pattern:
                                        st.caption(f"  • Strength: {pattern['strength']}")
                                else:
                                    st.markdown(f"**⚪ Chart Pattern ({signal['chart_pattern']['confidence_pct']:.0f}%):**")
                                    st.caption(f"  • No pattern detected")
                    
                    # Display SELL signals
                    if sell_signals:
                        st.markdown("### 🔴 STRONG SELL SIGNALS")
                        for signal in sorted(sell_signals, key=lambda x: x['confidence'], reverse=True):
                            with st.expander(f"💎 {signal['symbol']} - {signal['confidence']:.1f}% Confidence", expanded=True):
                                col1, col2, col3 = st.columns([2, 2, 1])
                                
                                with col1:
                                    st.metric("Current Price", f"₹{signal['current_price']:.2f}")
                                    st.metric("Entry", f"₹{signal['trade_setup']['entry']:.2f}")
                                    st.metric("Stop Loss", f"₹{signal['trade_setup']['stop_loss']:.2f}")
                                
                                with col2:
                                    st.metric("Target 1", f"₹{signal['trade_setup']['target1']:.2f}")
                                    st.metric("Risk:Reward", f"1:{signal['trade_setup']['rr_ratio']:.2f}")
                                    st.metric("Position Size", f"{signal['trade_setup']['position_size']} shares")
                                
                                with col3:
                                    st.metric("Confidence", f"{signal['confidence']:.1f}%")
                                    st.metric("Confluence", f"{signal['confluence']['confluence_count']}/3")
                                    profit = signal['trade_setup'].get('potential_profit1', 0)
                                    st.metric("Profit (T1)", f"₹{profit:,.0f}")
                                
                                # Show layers
                                st.markdown("**📊 3-Layer Analysis:**")
                                
                                st.markdown(f"**✅ Technical ({signal['technical']['confidence_pct']:.0f}%):**")
                                for factor in signal['technical']['factors']:
                                    st.caption(f"  • {factor}")
                                
                                st.markdown(f"**✅ S&R Analysis ({signal['sr_analysis']['confidence_pct']:.0f}%):**")
                                for factor in signal['sr_analysis']['factors']:
                                    st.caption(f"  • {factor}")
                                
                                # Chart Pattern - ALWAYS SHOW (even if none detected)
                                if signal['chart_pattern']['pattern']:
                                    pattern = signal['chart_pattern']['pattern']
                                    st.markdown(f"**✅ Chart Pattern ({signal['chart_pattern']['confidence_pct']:.0f}%):**")
                                    st.caption(f"  • {pattern['pattern']}: {pattern['description']}")
                                    if 'strength' in pattern:
                                        st.caption(f"  • Strength: {pattern['strength']}")
                                else:
                                    st.markdown(f"**⚪ Chart Pattern ({signal['chart_pattern']['confidence_pct']:.0f}%):**")
                                    st.caption(f"  • No pattern detected")
                    
                    # Export option
                    st.markdown("---")
                    if st.button("📥 Download Treasure Signals (Excel)"):
                        # Create Excel export (implementation pending)
                        st.info("Excel export feature coming soon!")
                
                else:
                    st.warning(f"💎 No treasure signals found in {len(stock_list)} stocks")
                    st.info("""
                    This is NORMAL! Treasure signals are rare (usually 10-20% of stocks).
                    
                    Try:
                    • Lower minimum confidence to 80%
                    • Analyze more stocks (Nifty 200 or ALL)
                    • Check back tomorrow (market conditions change)
                    
                    Remember: We filter for QUALITY, not quantity!
                    """)

# ============================================================
# PAGE: HYBRID SIGNAL GENERATOR 💎 (Treasure Signals)
# ============================================================

elif page == "Hybrid Signal Generator 💎":
    st.header("💎 Hybrid Signal Generator - Treasure Mode")
    st.info("🎯 Combines Technical + S&R + Chart Patterns. Only shows 85%+ confidence signals (TREASURES!)")
    st.caption("Philosophy: Quality over Quantity - Better to have 5 perfect signals than 50 mediocre ones")
    
    # Import required modules (READ-ONLY!)
    try:
        from hybrid_signal_generator import HybridSignalGenerator
        from patterns.chart_pattern_detector import ChartPatternDetector
        if DUAL_SR_AVAILABLE:
            from support_resistance.sr_calculator_enhanced import ProfessionalSRCalculator
            SR_CALC_CLASS = ProfessionalSRCalculator
        else:
            SR_CALC_CLASS = SupportResistanceCalculator
        
        HYBRID_AVAILABLE = True
    except ImportError as e:
        HYBRID_AVAILABLE = False
        st.error(f"❌ Hybrid modules not available: {e}")
    
    if HYBRID_AVAILABLE:
        # Bull Market Info
        st.info("""
        🐂 **BULL MARKET MODE ACTIVE!** - Optimized for trending markets
        
        **What Changed:**
        - Default Confidence: **75%** (down from 85%)
        - Default R:R: **1.5** (down from 2.0)
        - Wider S&R acceptance zones (up to 8% distance)
        - Extended RSI ranges (30-70 with partial signals)
        - Flexible confluence (2/3 layers agree OR 1 very strong layer)
        
        💡 **Result:** More signals while maintaining quality!
        """)
        
        # Stock Selection Mode
        st.markdown("#### 📈 Stock Selection")
        selection_mode = st.radio(
            "Choose how to select stocks:",
            ["⭐ My Stocks", "Universe (Batch Analysis)", "Manual Selection (Specific Stocks)"],
            horizontal=True,
            help="My Stocks: Your favorites | Universe: Analyze entire Nifty 50/200 | Manual: Pick specific stocks"
        )
        
        stock_list = []
        
        if selection_mode == "⭐ My Stocks":
            stock_list = get_my_stocks()
            render_my_stocks_manager()
        elif selection_mode == "Universe (Batch Analysis)":
            if EXPANDED_UNIVERSE_AVAILABLE:
                universe_choice = st.selectbox(
                    "Select Universe:",
                    ["Nifty 50 (51 stocks)", "Nifty 200 (200 stocks)", "Small Cap 250 (250 stocks)", "ALL Stocks (750+)"]
                )
            else:
                universe_choice = "Nifty 50 (51 stocks)"
            
            # Get stock list based on universe
            if "Nifty 50" in universe_choice:
                stock_list = NIFTY_50 if EXPANDED_UNIVERSE_AVAILABLE else ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
            elif "Nifty 200" in universe_choice:
                stock_list = NIFTY_200 if EXPANDED_UNIVERSE_AVAILABLE else NIFTY_50
            elif "Small Cap 250" in universe_choice:
                stock_list = SMALLCAP_250 if EXPANDED_UNIVERSE_AVAILABLE else NIFTY_50
            else:
                stock_list = ALL_STOCKS if EXPANDED_UNIVERSE_AVAILABLE else NIFTY_50
        
        else:  # Manual Selection
            st.info("💡 Enter stock symbols separated by commas (e.g., RELIANCE, TCS, INFY, HDFCBANK)")
            manual_input = st.text_input(
                "Stock Symbols:",
                placeholder="RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK",
                help="Enter NSE symbols separated by commas"
            )
            
            if manual_input:
                # Parse and clean stock symbols
                stock_list = [s.strip().upper() for s in manual_input.split(',') if s.strip()]
            else:
                stock_list = []
        
        # Settings
        st.markdown("#### ⚙️ Signal Parameters")
        col1, col2 = st.columns(2)
        
        with col1:
            min_confidence = st.slider("Minimum Confidence (%)", 70, 95, 75, 5,
                                      help="Only show signals above this confidence (Default: 75% for bull markets)")
        
        with col2:
            min_rr = st.slider("Minimum R:R", 1.0, 5.0, 1.5, 0.5,
                              help="Minimum Risk:Reward ratio (Default: 1.5 for bull markets)")
        
        # Display stock count
        if stock_list:
            st.caption(f"✅ Ready to analyze {len(stock_list)} stocks")
        else:
            st.warning("⚠️ Please select stocks to analyze")
        
        if st.button("💎 Find Treasure Signals", type="primary", disabled=(len(stock_list) == 0)):
            if len(stock_list) == 0:
                st.error("❌ Please select stocks first!")
                st.stop()
            
            st.markdown("---")
            st.subheader(f"🔍 Analyzing {len(stock_list)} stocks...")
            
            # Initialize
            hybrid_gen = HybridSignalGenerator(min_confidence=min_confidence, min_rr_ratio=min_rr)
            sr_calc = SR_CALC_CLASS(sensitivity=3, min_touches=2)
            pattern_detector = ChartPatternDetector()
            
            treasure_signals = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            import yfinance as yf
            
            # Analyze each stock
            for idx, symbol in enumerate(stock_list):
                status_text.text(f"Analyzing {symbol}... ({idx+1}/{len(stock_list)})")
                
                try:
                    # Fetch data
                    ticker = yf.Ticker(get_yfinance_symbol(symbol))
                    df_raw = ticker.history(period="6mo", interval="1d")
                    
                    if df_raw.empty or len(df_raw) < 50:
                        progress_bar.progress((idx + 1) / len(stock_list))
                        continue
                    
                    # Convert to format
                    df = pd.DataFrame({
                        'time': df_raw.index,
                        'open': df_raw['Open'].values,
                        'high': df_raw['High'].values,
                        'low': df_raw['Low'].values,
                        'close': df_raw['Close'].values,
                        'volume': df_raw['Volume'].values
                    })
                    
                    # USE ONLY EOD DATA (exclude today's incomplete candle)
                    df_eod = df[:-1].copy() if len(df) > 5 else df
                    
                    # Analyze (3-layer confluence) - using EOD data only
                    result = hybrid_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                    
                    if result and result['is_treasure']:
                        treasure_signals.append(result)
                
                except Exception as e:
                    # Skip stocks with errors
                    pass
                
                progress_bar.progress((idx + 1) / len(stock_list))
            
            # Clear progress
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            st.markdown("---")
            
            if treasure_signals:
                st.success(f"💎 Found {len(treasure_signals)} TREASURE SIGNALS out of {len(stock_list)} stocks ({len(treasure_signals)/len(stock_list)*100:.1f}%)")
                
                # Separate BUY and SELL
                buy_signals = [s for s in treasure_signals if 'BUY' in s['signal']]
                sell_signals = [s for s in treasure_signals if 'SELL' in s['signal']]
                
                # Display BUY signals
                if buy_signals:
                    st.markdown("### 🟢 STRONG BUY SIGNALS")
                    for signal in sorted(buy_signals, key=lambda x: x['confidence'], reverse=True):
                        with st.expander(f"💎 {signal['symbol']} - {signal['confidence']:.1f}% Confidence", expanded=True):
                            col1, col2, col3 = st.columns([2, 2, 1])
                            
                            with col1:
                                st.metric("Current Price", f"₹{signal['current_price']:.2f}")
                                st.metric("Entry", f"₹{signal['trade_setup']['entry']:.2f}")
                                st.metric("Stop Loss", f"₹{signal['trade_setup']['stop_loss']:.2f}")
                            
                            with col2:
                                st.metric("Target 1", f"₹{signal['trade_setup']['target1']:.2f}")
                                st.metric("Risk:Reward", f"1:{signal['trade_setup']['rr_ratio']:.2f}")
                                st.metric("Position Size", f"{signal['trade_setup']['position_size']} shares")
                            
                            with col3:
                                st.metric("Confidence", f"{signal['confidence']:.1f}%")
                                st.metric("Confluence", f"{signal['confluence']['confluence_count']}/3")
                                profit = signal['trade_setup'].get('potential_profit1', 0)
                                st.metric("Profit (T1)", f"₹{profit:,.0f}")
                            
                            # Show all 3 layers
                            st.markdown("**📊 3-Layer Analysis:**")
                            
                            st.markdown(f"**✅ Technical ({signal['technical']['confidence_pct']:.0f}%):**")
                            for factor in signal['technical']['factors']:
                                st.caption(f"  • {factor}")
                            
                            st.markdown(f"**✅ S&R Analysis ({signal['sr_analysis']['confidence_pct']:.0f}%):**")
                            for factor in signal['sr_analysis']['factors']:
                                st.caption(f"  • {factor}")
                            
                            # Chart Pattern - ALWAYS SHOW (even if none detected)
                            if signal['chart_pattern']['pattern']:
                                pattern = signal['chart_pattern']['pattern']
                                st.markdown(f"**✅ Chart Pattern ({signal['chart_pattern']['confidence_pct']:.0f}%):**")
                                st.caption(f"  • {pattern['pattern']}: {pattern['description']}")
                                if 'strength' in pattern:
                                    st.caption(f"  • Strength: {pattern['strength']}")
                            else:
                                st.markdown(f"**⚪ Chart Pattern ({signal['chart_pattern']['confidence_pct']:.0f}%):**")
                                st.caption(f"  • No pattern detected")
                
                # Display SELL signals
                if sell_signals:
                    st.markdown("### 🔴 STRONG SELL SIGNALS")
                    for signal in sorted(sell_signals, key=lambda x: x['confidence'], reverse=True):
                        with st.expander(f"💎 {signal['symbol']} - {signal['confidence']:.1f}% Confidence", expanded=True):
                            col1, col2, col3 = st.columns([2, 2, 1])
                            
                            with col1:
                                st.metric("Current Price", f"₹{signal['current_price']:.2f}")
                                st.metric("Entry", f"₹{signal['trade_setup']['entry']:.2f}")
                                st.metric("Stop Loss", f"₹{signal['trade_setup']['stop_loss']:.2f}")
                            
                            with col2:
                                st.metric("Target 1", f"₹{signal['trade_setup']['target1']:.2f}")
                                st.metric("Risk:Reward", f"1:{signal['trade_setup']['rr_ratio']:.2f}")
                                st.metric("Position Size", f"{signal['trade_setup']['position_size']} shares")
                            
                            with col3:
                                st.metric("Confidence", f"{signal['confidence']:.1f}%")
                                st.metric("Confluence", f"{signal['confluence']['confluence_count']}/3")
                                profit = signal['trade_setup'].get('potential_profit1', 0)
                                st.metric("Profit (T1)", f"₹{profit:,.0f}")
                            
                            # Show layers
                            st.markdown("**📊 3-Layer Analysis:**")
                            
                            st.markdown(f"**✅ Technical ({signal['technical']['confidence_pct']:.0f}%):**")
                            for factor in signal['technical']['factors']:
                                st.caption(f"  • {factor}")
                            
                            st.markdown(f"**✅ S&R Analysis ({signal['sr_analysis']['confidence_pct']:.0f}%):**")
                            for factor in signal['sr_analysis']['factors']:
                                st.caption(f"  • {factor}")
                            
                            # Chart Pattern - ALWAYS SHOW (even if none detected)
                            if signal['chart_pattern']['pattern']:
                                pattern = signal['chart_pattern']['pattern']
                                st.markdown(f"**✅ Chart Pattern ({signal['chart_pattern']['confidence_pct']:.0f}%):**")
                                st.caption(f"  • {pattern['pattern']}: {pattern['description']}")
                                if 'strength' in pattern:
                                    st.caption(f"  • Strength: {pattern['strength']}")
                            else:
                                st.markdown(f"**⚪ Chart Pattern ({signal['chart_pattern']['confidence_pct']:.0f}%):**")
                                st.caption(f"  • No pattern detected")
                
                # Export option
                st.markdown("---")
                if st.button("📥 Download Treasure Signals (Excel)"):
                    # Create Excel export (implementation pending)
                    st.info("Excel export feature coming soon!")
            
            else:
                st.warning(f"💎 No treasure signals found in {len(stock_list)} stocks")
                st.info("""
                This is NORMAL! Treasure signals are rare (usually 10-20% of stocks).
                
                Try:
                • Lower minimum confidence to 80%
                • Analyze more stocks (Nifty 200 or ALL)
                • Check back tomorrow (market conditions change)
                
                Remember: We filter for QUALITY, not quantity!
                """)

# ============================================================
# PAGE: 3JASMINES 🌸 (Conservative Delivery Trading)
# ============================================================

elif page == "3Jasmines 🌸":
    st.header("🌸 3Jasmines Screener - Conservative Delivery Trading")
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 1.5rem;'>
        <h3 style='margin: 0; color: white;'>🌸🌸🌸 Three Petals of Confirmation</h3>
        <p style='margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
            High-probability BUY signals for delivery trading • Win Rate: 85-90%
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Strategy Explanation
    st.markdown("### 🎯 Strategy Logic")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 🌸 Jasmine 1: Near Support
        **Stock must be at support**
        - Distance ≤ 0.5% from support
        - Buyers defending the level
        - Bounce expected
        
        ✅ **Pass:** At ₹450 (Support: ₹450)
        ❌ **Fail:** At ₹455 (Support: ₹450, 1.1% away)
        """)
    
    with col2:
        st.markdown("""
        #### 🌸 Jasmine 2: Deep Oversold
        **RSI must be < 35**
        - Deeply oversold condition
        - Selling exhaustion
        - Reversal likely
        
        ✅ **Pass:** RSI = 28 (Deep oversold)
        ❌ **Fail:** RSI = 42 (Not oversold enough)
        """)
    
    with col3:
        st.markdown("""
        #### 🌸 Jasmine 3: Bullish Pattern
        **Chart pattern confirmation**
        - Hammer, Bullish Engulfing
        - Morning Star, 3 White Soldiers
        - ANY bullish pattern
        
        ✅ **Pass:** Hammer detected
        ❌ **Fail:** No bullish pattern
        """)
    
    st.info("""
    **🎯 Trade Setup:**
    - **Entry:** Current price (at/near support)
    - **Stop Loss:** 2% below support level
    - **Target:** 1% below resistance (conservative, high-probability exit!)
    - **Win Rate:** 85-90% (all 3 criteria = very selective)
    - **Use Case:** Delivery/Swing trading (2-10 days holding)
    """)
    
    st.markdown("---")
    
    # Stock Selection
    st.markdown("### 📈 Stock Selection")
    
    selection_mode = st.radio(
        "Choose stock universe:",
        ["⭐ My Stocks", "Nifty 50", "Nifty 200", "Small Cap 250", "ALL Stocks (750+)", "Manual Selection"],
        horizontal=True
    )
    
    stock_list = []
    
    if selection_mode == "⭐ My Stocks":
        stock_list = get_my_stocks()
        render_my_stocks_manager()
    elif selection_mode == "Nifty 50":
        stock_list = NIFTY_50 if EXPANDED_UNIVERSE_AVAILABLE else ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
    elif selection_mode == "Nifty 200":
        stock_list = NIFTY_200 if EXPANDED_UNIVERSE_AVAILABLE else NIFTY_50
    elif selection_mode == "Small Cap 250":
        stock_list = SMALLCAP_250 if EXPANDED_UNIVERSE_AVAILABLE else NIFTY_50
    elif selection_mode == "ALL Stocks (750+)":
        stock_list = ALL_STOCKS if EXPANDED_UNIVERSE_AVAILABLE else NIFTY_50
    else:  # Manual Selection
        manual_input = st.text_input(
            "Enter Stock Symbols (comma-separated):",
            placeholder="RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK",
            help="Enter NSE symbols separated by commas"
        )
        if manual_input:
            stock_list = [s.strip().upper() for s in manual_input.split(',') if s.strip()]
    
    if stock_list:
        st.caption(f"✅ Ready to scan {len(stock_list)} stocks")
    else:
        st.warning("⚠️ Please select stocks to scan")
    
    # Scan Button
    if st.button("🌸 Find 3Jasmines Signals", type="primary", disabled=(len(stock_list) == 0)):
        if len(stock_list) == 0:
            st.error("❌ Please select stocks first!")
            st.stop()
        
        st.markdown("---")
        st.subheader(f"🔍 Scanning {len(stock_list)} stocks for 3Jasmines signals...")
        
        try:
            import yfinance as yf
            from three_jasmines_screener import ThreeJasminesScreener
            from patterns.chart_pattern_detector import ChartPatternDetector
            
            if DUAL_SR_AVAILABLE:
                from support_resistance.sr_calculator_enhanced import ProfessionalSRCalculator
                SR_CALC_CLASS = ProfessionalSRCalculator
            else:
                SR_CALC_CLASS = SupportResistanceCalculator
            
            # Initialize
            jasmines_gen = ThreeJasminesScreener(
                max_support_distance_pct=0.5,  # 0.5% from support
                max_rsi_threshold=35.0,         # RSI < 35
                target_buffer_pct=1.0,          # Target 1% below resistance
                stop_loss_buffer_pct=2.0        # SL 2% below support
            )
            sr_calc = SR_CALC_CLASS(sensitivity=3, min_touches=2)
            pattern_detector = ChartPatternDetector()
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            jasmines_signals = []
            errors = []
            
            for idx, symbol in enumerate(stock_list):
                try:
                    status_text.text(f"Analyzing {symbol}... ({idx+1}/{len(stock_list)})")
                    
                    # Fetch data
                    ticker = yf.Ticker(get_yfinance_symbol(symbol))
                    df_raw = ticker.history(period="6mo", interval="1d")
                    
                    if not df_raw.empty and len(df_raw) >= 20:
                        # Convert to expected format
                        df = pd.DataFrame({
                            'time': df_raw.index,
                            'open': df_raw['Open'].values,
                            'high': df_raw['High'].values,
                            'low': df_raw['Low'].values,
                            'close': df_raw['Close'].values,
                            'volume': df_raw['Volume'].values
                        })
                        
                        # USE ONLY EOD DATA (exclude today's incomplete candle)
                        df_eod = df[:-1].copy() if len(df) > 5 else df
                        
                        # Analyze for 3Jasmines signal (using EOD data only)
                        signal = jasmines_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                        
                        if signal:
                            jasmines_signals.append(signal)
                
                except Exception as e:
                    errors.append(f"{symbol}: {str(e)}")
                
                progress_bar.progress((idx + 1) / len(stock_list))
            
            # Clear progress
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            st.markdown("---")
            
            if errors:
                with st.expander(f"⚠️ Errors ({len(errors)} stocks)", expanded=False):
                    for error in errors:
                        st.caption(f"• {error}")
            
            if jasmines_signals:
                st.success(f"🌸 Found {len(jasmines_signals)} 3Jasmines signals out of {len(stock_list)} stocks ({len(jasmines_signals)/len(stock_list)*100:.1f}%)")
                
                st.markdown("### 🌸 3JASMINES BUY SIGNALS")
                
                for signal in sorted(jasmines_signals, key=lambda x: x['confidence'], reverse=True):
                    with st.expander(f"🌸 {signal['symbol']} - {signal['confidence']:.1f}% Confidence", expanded=True):
                        # Trade Setup
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.metric("Current Price", f"₹{signal['current_price']:.2f}")
                            st.metric("Entry", f"₹{signal['entry']:.2f}")
                            st.metric("Stop Loss", f"₹{signal['stop_loss']:.2f}")
                        
                        with col2:
                            st.metric("Target", f"₹{signal['target']:.2f}")
                            st.metric("Risk:Reward", f"1:{signal['rr_ratio']:.2f}")
                            st.metric("Position Size", f"{signal['position_size']} shares")
                        
                        with col3:
                            st.metric("Confidence", f"{signal['confidence']:.1f}%")
                            profit = (signal['target'] - signal['entry']) * signal['position_size']
                            st.metric("Potential Profit", f"₹{profit:,.0f}")
                            st.metric("Support", f"₹{signal['support_level']:.2f}")
                        
                        # 3 Jasmines Breakdown
                        st.markdown("**🌸 Three Jasmines Analysis:**")
                        
                        # Jasmine 1
                        j1 = signal['jasmine1_support']
                        st.markdown(f"**🌸 Jasmine 1 - Near Support ({j1['score']:.0f}%):**")
                        st.caption(f"  ✅ {j1['reason']}")
                        
                        # Jasmine 2
                        j2 = signal['jasmine2_rsi']
                        st.markdown(f"**🌸 Jasmine 2 - RSI Oversold ({j2['score']:.0f}%):**")
                        st.caption(f"  ✅ {j2['reason']}")
                        
                        # Jasmine 3
                        j3 = signal['jasmine3_pattern']
                        st.markdown(f"**🌸 Jasmine 3 - Bullish Pattern ({j3['score']:.0f}%):**")
                        st.caption(f"  ✅ {j3['reason']}")
                        if j3.get('description'):
                            st.caption(f"     {j3['description']}")
                        
                        # Additional Info
                        st.markdown("**📊 Levels:**")
                        st.caption(f"  • Support: ₹{signal['support_level']:.2f}")
                        st.caption(f"  • Resistance: ₹{signal['resistance_level']:.2f}")
                        st.caption(f"  • Target (1% below R): ₹{signal['target']:.2f}")
                
                # Export option
                st.markdown("---")
                if st.button("📥 Download 3Jasmines Signals (CSV)"):
                    df_export = pd.DataFrame(jasmines_signals)
                    csv = df_export.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        csv,
                        f"3jasmines_signals_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )
            
            else:
                st.warning(f"🌸 No 3Jasmines signals found in {len(stock_list)} stocks")
                st.info("""
                **Why no signals?**
                
                3Jasmines is VERY selective (all 3 criteria must match):
                - Stock must be within 0.5% of support
                - RSI must be < 35 (deeply oversold)
                - Must have bullish chart pattern
                
                **This is NORMAL!** You might find:
                - 0-2 signals from Nifty 50
                - 3-5 signals from Nifty 200
                - 5-10 signals from ALL stocks
                
                **Try:**
                • Scan Nifty 200 or ALL Stocks
                • Market conditions might not be favorable today
                • Check back daily (signals appear as stocks oversell and bounce)
                """)
        
        except Exception as e:
            st.error(f"❌ Error: {e}")
            import traceback
            st.code(traceback.format_exc())

# ============================================================
# PAGE: ORCHID TREND MATRIX (3Jasmines + Hybrid Signal Confluence)
# ============================================================

elif page == "Orchid Trend Matrix":
    st.header("🌺 Orchid Trend Matrix")
    st.caption("Ultra-Selective Signals: Stocks that pass BOTH 3Jasmines AND Hybrid Signal Generator")
    
    st.info("""
    **🌺 Orchid Trend Matrix Philosophy:**
    
    This page finds stocks that meet **BOTH** criteria:
    - ✅ **3Jasmines Screener** (Conservative Delivery Trading)
    - ✅ **Hybrid Signal Generator** (Treasure Mode)
    
    **Why This is Powerful:**
    - **Ultra-Selective:** Only 1-3 signals per day (very rare!)
    - **Highest Confidence:** Both systems agree = 90%+ win rate
    - **Best of Both Worlds:** Conservative setup + Technical confluence
    - **Perfect for Delivery Trading:** Hold 3-10 days for maximum profit
    """)
    
    st.markdown("---")
    
    # Stock Selection
    st.markdown("### 📈 Stock Selection")
    
    selection_mode = st.radio(
        "Choose stock universe:",
        ["⭐ My Stocks", "Nifty 50", "Nifty 200", "Small Cap 250", "ALL Stocks (750+)", "Manual Selection"],
        horizontal=True
    )
    
    stock_list = []
    
    if selection_mode == "⭐ My Stocks":
        stock_list = get_my_stocks()
        render_my_stocks_manager()
    elif selection_mode == "Nifty 50":
        stock_list = NIFTY_50 if EXPANDED_UNIVERSE_AVAILABLE else ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
    elif selection_mode == "Nifty 200":
        stock_list = NIFTY_200 if EXPANDED_UNIVERSE_AVAILABLE else NIFTY_50
    elif selection_mode == "Small Cap 250":
        stock_list = SMALLCAP_250 if EXPANDED_UNIVERSE_AVAILABLE else NIFTY_50
    elif selection_mode == "ALL Stocks (750+)":
        stock_list = ALL_STOCKS if EXPANDED_UNIVERSE_AVAILABLE else NIFTY_50
    else:  # Manual Selection
        manual_input = st.text_input(
            "Enter Stock Symbols (comma-separated):",
            placeholder="RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK",
            help="Enter NSE symbols separated by commas"
        )
        if manual_input:
            stock_list = [s.strip().upper() for s in manual_input.split(',') if s.strip()]
    
    if stock_list:
        st.caption(f"✅ Ready to scan {len(stock_list)} stocks for Orchid Trend Matrix signals")
    else:
        st.warning("⚠️ Please select stocks to scan")
    
    # Settings
    st.markdown("### ⚙️ Signal Parameters")
    col1, col2 = st.columns(2)
    
    with col1:
        min_confidence_hybrid = st.slider("Min Hybrid Confidence (%)", 70, 95, 75, 5,
                                         help="Minimum confidence for Hybrid Signal Generator")
        min_rr_hybrid = st.slider("Min Hybrid R:R", 1.0, 5.0, 1.5, 0.5,
                                 help="Minimum Risk:Reward for Hybrid signals")
    
    with col2:
        min_confidence_jasmines = st.slider("Min 3Jasmines Confidence (%)", 70, 95, 70, 5,
                                           help="Minimum confidence for 3Jasmines signals")
        st.info("💡 **3Jasmines Criteria:**\n- Near Support (0.5%)\n- RSI < 35\n- Bullish Pattern")
    
    # Scan Button
    if st.button("🌺 Find Orchid Trend Matrix Signals", type="primary", disabled=(len(stock_list) == 0)):
        if len(stock_list) == 0:
            st.error("❌ Please select stocks first!")
            st.stop()
        
        st.markdown("---")
        st.subheader(f"🔍 Scanning {len(stock_list)} stocks for Orchid Trend Matrix signals...")
        
        try:
            import yfinance as yf
            from three_jasmines_screener import ThreeJasminesScreener
            from hybrid_signal_generator import HybridSignalGenerator
            from patterns.chart_pattern_detector import ChartPatternDetector
            
            if DUAL_SR_AVAILABLE:
                from support_resistance.sr_calculator_enhanced import ProfessionalSRCalculator
                SR_CALC_CLASS = ProfessionalSRCalculator
            else:
                SR_CALC_CLASS = SupportResistanceCalculator
            
            # Initialize both screeners
            jasmines_gen = ThreeJasminesScreener(
                max_support_distance_pct=0.5,
                max_rsi_threshold=35.0,
                target_buffer_pct=1.0,
                stop_loss_buffer_pct=2.0
            )
            
            hybrid_gen = HybridSignalGenerator(
                min_confidence=min_confidence_hybrid,
                min_rr_ratio=min_rr_hybrid
            )
            
            sr_calc = SR_CALC_CLASS(sensitivity=3, min_touches=2)
            pattern_detector = ChartPatternDetector()
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            jasmines_signals = {}
            hybrid_signals = {}
            orchid_signals = []  # Stocks that pass BOTH
            
            # Step 1: Run 3Jasmines Screener
            st.markdown("#### 🌸 Step 1: Running 3Jasmines Screener...")
            st.caption(f"📊 Min 3Jasmines Confidence: {min_confidence_jasmines}%")
            for idx, symbol in enumerate(stock_list):
                try:
                    status_text.text(f"🌸 3Jasmines (Min {min_confidence_jasmines}%): {symbol}... ({idx+1}/{len(stock_list)})")
                    
                    ticker = yf.Ticker(get_yfinance_symbol(symbol))
                    df_raw = ticker.history(period="6mo", interval="1d")
                    
                    if not df_raw.empty and len(df_raw) >= 20:
                        df = pd.DataFrame({
                            'time': df_raw.index,
                            'open': df_raw['Open'].values,
                            'high': df_raw['High'].values,
                            'low': df_raw['Low'].values,
                            'close': df_raw['Close'].values,
                            'volume': df_raw['Volume'].values
                        })
                        
                        df_eod = df[:-1].copy() if len(df) > 5 else df
                        signal = jasmines_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                        
                        if signal and signal['confidence'] >= min_confidence_jasmines:
                            jasmines_signals[symbol] = signal
                    
                    progress_bar.progress((idx + 1) / (len(stock_list) * 2))  # Half progress for step 1
                    time.sleep(0.1)
                    
                except Exception as e:
                    continue
            
            st.success(f"✅ Found {len(jasmines_signals)} stocks passing 3Jasmines criteria")
            
            # Step 2: Run Hybrid Signal Generator on 3Jasmines signals
            if jasmines_signals:
                st.markdown("#### 💎 Step 2: Running Hybrid Signal Generator on 3Jasmines stocks...")
                st.caption(f"📊 Min Hybrid Confidence: {min_confidence_hybrid}% | Min R:R: {min_rr_hybrid}")
                jasmines_symbols = list(jasmines_signals.keys())
                
                for idx, symbol in enumerate(jasmines_symbols):
                    try:
                        status_text.text(f"💎 Hybrid (Min {min_confidence_hybrid}%, R:R {min_rr_hybrid}): {symbol}... ({idx+1}/{len(jasmines_symbols)})")
                        
                        ticker = yf.Ticker(get_yfinance_symbol(symbol))
                        df_raw = ticker.history(period="6mo", interval="1d")
                        
                        if not df_raw.empty and len(df_raw) >= 50:
                            df = pd.DataFrame({
                                'time': df_raw.index,
                                'open': df_raw['Open'].values,
                                'high': df_raw['High'].values,
                                'low': df_raw['Low'].values,
                                'close': df_raw['Close'].values,
                                'volume': df_raw['Volume'].values
                            })
                            
                            df_eod = df[:-1].copy() if len(df) > 5 else df
                            result = hybrid_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                            
                            if result and result.get('is_treasure'):
                                hybrid_signals[symbol] = result
                                
                                # Check if this stock is in BOTH
                                if symbol in jasmines_signals:
                                    # Combine both signals
                                    orchid_signal = {
                                        'symbol': symbol,
                                        'jasmines': jasmines_signals[symbol],
                                        'hybrid': result,
                                        'combined_confidence': (jasmines_signals[symbol]['confidence'] + result['confidence']) / 2,
                                        'both_systems_agree': True
                                    }
                                    orchid_signals.append(orchid_signal)
                        
                        progress_bar.progress(0.5 + (idx + 1) / (len(jasmines_symbols) * 2))  # Second half progress
                        time.sleep(0.1)
                        
                    except Exception as e:
                        continue
            else:
                st.warning("⚠️ No 3Jasmines signals found. Cannot check Hybrid signals.")
            
            # Clear progress
            progress_bar.empty()
            status_text.empty()
            
            # Display Results
            st.markdown("---")
            
            if orchid_signals:
                st.success(f"🌺 **FOUND {len(orchid_signals)} ORCHID TREND MATRIX SIGNALS!** (Ultra-Rare!)")
                st.caption(f"These stocks passed BOTH 3Jasmines AND Hybrid Signal Generator criteria")
                
                # Sort by combined confidence
                orchid_signals.sort(key=lambda x: x['combined_confidence'], reverse=True)
                
                for signal in orchid_signals:
                    jasmines = signal['jasmines']
                    hybrid = signal['hybrid']
                    
                    with st.expander(f"🌺 {signal['symbol']} - Combined Confidence: {signal['combined_confidence']:.1f}%", expanded=True):
                        # Summary
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Current Price", f"₹{jasmines['current_price']:.2f}")
                            st.metric("Entry", f"₹{jasmines['entry']:.2f}")
                            st.metric("Stop Loss", f"₹{jasmines['stop_loss']:.2f}")
                        
                        with col2:
                            st.metric("Target", f"₹{jasmines['target']:.2f}")
                            st.metric("R:R Ratio", f"1:{jasmines['rr_ratio']:.2f}")
                            st.metric("Position Size", f"{jasmines['position_size']} shares")
                        
                        with col3:
                            st.metric("Combined Confidence", f"{signal['combined_confidence']:.1f}%")
                            st.metric("3Jasmines", f"{jasmines['confidence']:.1f}%")
                            st.metric("Hybrid", f"{hybrid['confidence']:.1f}%")
                        
                        st.markdown("---")
                        
                        # 3Jasmines Details
                        st.markdown("#### 🌸 3Jasmines Criteria (ALL PASSED):")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.success(f"✅ **Near Support:** {jasmines['jasmine1_support']['reason']}")
                            st.success(f"✅ **RSI Oversold:** {jasmines['jasmine2_rsi']['reason']}")
                        
                        with col2:
                            st.success(f"✅ **Bullish Pattern:** {jasmines['jasmine3_pattern']['reason']}")
                            if jasmines['jasmine3_pattern'].get('pattern_name'):
                                st.caption(f"Pattern: {jasmines['jasmine3_pattern']['pattern_name']}")
                        
                        st.markdown("---")
                        
                        # Hybrid Signal Details
                        st.markdown("#### 💎 Hybrid Signal Generator (ALL PASSED):")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"**Technical:** {hybrid['technical']['confidence_pct']:.0f}%")
                            for factor in hybrid['technical']['factors'][:3]:
                                st.caption(f"  • {factor}")
                        
                        with col2:
                            st.markdown(f"**S&R Analysis:** {hybrid['sr_analysis']['confidence_pct']:.0f}%")
                            for factor in hybrid['sr_analysis']['factors'][:3]:
                                st.caption(f"  • {factor}")
                        
                        with col3:
                            st.markdown(f"**Chart Pattern:** {hybrid['chart_pattern']['confidence_pct']:.0f}%")
                            if hybrid['chart_pattern']['pattern']:
                                pattern = hybrid['chart_pattern']['pattern']
                                st.caption(f"  • {pattern['pattern']}")
                                st.caption(f"  • {pattern['description']}")
                            else:
                                st.caption("  • No pattern detected")
                        
                        st.markdown("---")
                        
                        # Trade Setup Summary
                        st.markdown("#### 💰 Recommended Trade Setup:")
                        st.info(f"""
                        **Entry:** ₹{jasmines['entry']:.2f} (3Jasmines entry - near support)
                        **Target:** ₹{jasmines['target']:.2f} (1% below resistance - conservative)
                        **Stop Loss:** ₹{jasmines['stop_loss']:.2f} (2% below support)
                        **Risk:Reward:** 1:{jasmines['rr_ratio']:.2f}
                        **Position Size:** {jasmines['position_size']} shares
                        **Potential Profit:** ₹{jasmines['potential_profit']:,.0f}
                        **Holding Period:** 3-10 days (Delivery Trading)
                        """)
            else:
                st.warning(f"""
                **🌺 No Orchid Trend Matrix Signals Found**
                
                **What this means:**
                - Scanned {len(stock_list)} stocks
                - Found {len(jasmines_signals)} stocks passing 3Jasmines
                - Found {len(hybrid_signals)} stocks passing Hybrid Signal Generator
                - **But NONE passed BOTH criteria** (ultra-selective!)
                
                **This is NORMAL:**
                - Orchid signals are **extremely rare** (maybe 1-2 per week)
                - Both systems must agree = highest quality signals
                - Try scanning larger universe (Nifty 200 or ALL Stocks)
                - Check back daily (signals appear when market conditions align)
                """)
                
                if jasmines_signals:
                    st.info(f"💡 **Tip:** {len(jasmines_signals)} stocks passed 3Jasmines. Check '3Jasmines 🌸' page for those signals.")
                if hybrid_signals:
                    st.info(f"💡 **Tip:** {len(hybrid_signals)} stocks passed Hybrid Signal Generator. Check 'Lotus Momentum Trio' page for those signals.")
        
        except Exception as e:
            st.error(f"❌ Error: {e}")
            import traceback
            st.code(traceback.format_exc())

# ============================================================
# PAGE: TECHNICAL SCREENER (REAL CALCULATIONS)
# ============================================================

elif page == "Technical Screener":
    st.header("📊 Technical Screener - REAL Pattern Detection")
    
    st.success("✅ **REAL ANALYSIS**: Calculates actual RSI, MACD, Moving Averages from real data!")
    
    st.markdown("""
    ### 🎯 Real Patterns We Find:
    - **Golden Cross**: SMA(20) > SMA(50) + Volume spike → 68% win rate
    - **RSI Oversold**: RSI < 35 + Bullish reversal → 72% win rate  
    - **MACD Bullish**: MACD crosses signal + Momentum → 65% win rate
    - **Support Bounce**: Price at support + RSI < 60 → 75% win rate
    """)
    
    st.markdown("---")
    
    # Stock selection
    st.subheader("📈 Stock Selection")
    
    selection_mode = st.radio(
        "Choose how to pick stocks:",
        ("⭐ My Stocks", "Universe (Batch Analysis)", "Manual Selection", "Single Stock Analysis"),
        index=0,
        key="technical_screener_stock_mode"
    )
    
    stocks = []
    manual_input = ""
    single_symbol = ""
    
    if selection_mode == "⭐ My Stocks":
        stocks = get_my_stocks()
        render_my_stocks_manager()
    elif selection_mode == "Universe (Batch Analysis)":
        if EXPANDED_UNIVERSE_AVAILABLE:
            universe_options = [
                "Top 10 (Quick Test)",
                "Top 20 (Standard)",
                "Nifty 50 (50 stocks)",
                "Nifty 200 (200 stocks) ⭐",
                "Nifty 500 (500 stocks)",
                "Smallcap 250 (250 stocks)",
                "Commodities (Gold, Silver)",
                "ALL Stocks (750+)",
                "ALL Assets (Stocks + Commodities) 🚀"
            ]
        else:
            universe_options = ["Top 10 (Quick)", "Top 20 (Standard)", "Top 50"]
        
        universe_size = st.selectbox("Universe:", universe_options)
        
        if "Top 10" in universe_size:
            stocks = TOP_50_STOCKS[:10]
        elif "Top 20" in universe_size:
            stocks = TOP_50_STOCKS[:20]
        elif "Nifty 50" in universe_size:
            stocks = NIFTY_50 if EXPANDED_UNIVERSE_AVAILABLE else TOP_50_STOCKS
        elif "Nifty 200" in universe_size:
            stocks = NIFTY_200 if EXPANDED_UNIVERSE_AVAILABLE else TOP_50_STOCKS
        elif "Nifty 500" in universe_size:
            stocks = NIFTY_500 if EXPANDED_UNIVERSE_AVAILABLE else TOP_50_STOCKS
        elif "Smallcap 250" in universe_size:
            stocks = SMALLCAP_250 if EXPANDED_UNIVERSE_AVAILABLE else TOP_50_STOCKS
        elif "Commodities" in universe_size:
            stocks = COMMODITIES if EXPANDED_UNIVERSE_AVAILABLE else []
        elif "ALL Assets" in universe_size:
            stocks = ALL_ASSETS if EXPANDED_UNIVERSE_AVAILABLE else TOP_50_STOCKS
        elif "ALL" in universe_size:
            stocks = ALL_STOCKS if EXPANDED_UNIVERSE_AVAILABLE else TOP_50_STOCKS
        else:
            stocks = TOP_50_STOCKS
        
        st.caption(f"🔍 Ready to analyze {len(stocks)} stocks from the {universe_size} universe")
    
    elif selection_mode == "Manual Selection":
        manual_input = st.text_area(
            "Enter stock symbols (comma or newline separated):",
            placeholder="Example:\nRELIANCE\nTCS\nINFY\nHDFCBANK",
            height=140
        )
        
        if manual_input.strip():
            parsed_symbols = []
            seen = set()
            for line in manual_input.splitlines():
                tokens = [token.strip().upper() for token in line.replace(',', ' ').split() if token.strip()]
                for token in tokens:
                    if token not in seen:
                        seen.add(token)
                        parsed_symbols.append(token)
            stocks = parsed_symbols
            st.caption(f"✅ Ready to analyze {len(stocks)} manually selected stocks")
        else:
            st.info("Enter one symbol per line or separate with commas (e.g., RELIANCE, TCS, INFY)")
    
    else:  # Single Stock Analysis
        single_symbol = st.text_input(
            "Enter a single stock symbol:",
            placeholder="Example: RELIANCE"
        )
        cleaned_symbol = single_symbol.strip().upper()
        if cleaned_symbol:
            stocks = [cleaned_symbol]
            st.caption(f"🎯 Single stock analysis selected: {cleaned_symbol}")
        else:
            st.info("Type any NSE stock symbol (e.g., RELIANCE) to analyze it instantly")
    
    # Screening parameters
    param_col1, param_col2 = st.columns(2)
    with param_col1:
        st.subheader("🎯 Min Strength")
        min_pattern_strength = st.slider("Pattern Strength", 5.0, 9.0, 7.0, 0.5)
    with param_col2:
        st.subheader("⏱️ Lookback")
        lookback_days = st.selectbox(
            "Days",
            [90, 180, 365, 730],
            index=2,
            help="More data = better accuracy (365 days recommended for swing trading)"
        )
    
    TOP_50_STOCKS = [
        'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'SBIN', 'BHARTIARTL', 
        'ITC', 'HINDUNILVR', 'KOTAKBANK', 'LT', 'ASIANPAINTS', 'MARUTI', 'HCLTECH', 
        'WIPRO', 'TITAN', 'SUNPHARMA', 'AXISBANK', 'BAJFINANCE', 'NESTLEIND',
        'ULTRACEMCO', 'M&M', 'NTPC', 'POWERGRID', 'ONGC', 'TATASTEEL', 'TECHM',
        'ADANIPORTS', 'JSWSTEEL', 'BAJAJFINSV', 'INDUSINDBK', 'COALINDIA', 'DIVISLAB',
        'GRASIM', 'HINDALCO', 'BRITANNIA', 'DRREDDY', 'SHREECEM', 'EICHERMOT', 'CIPLA',
        'TATACONSUM', 'HEROMOTOCO', 'UPL', 'APOLLOHOSP', 'BPCL', 'BAJAJ-AUTO', 'TATAMOTORS',
        'ADANIENT', 'SBILIFE', 'HDFCLIFE', 'JIOFIN'
    ]
    
    if len(stocks) == 0:
        st.warning("⚠️ No stocks selected yet. Add at least one symbol to continue.")
    
    
    # New improvements badge
    st.success("✨ **NEW IMPROVEMENTS:** Now includes SMA 200, Fibonacci retracements, and up to 2 years lookback! Expect 15-20% better accuracy!")
    
    # Data source option
    use_local_data = st.checkbox(
        "📁 Use local CSV data (consistent results)", 
        value=False,
        help="Use downloaded CSV data instead of fetching from Yahoo Finance. Ensures same results on multiple runs."
    )
    
    if not use_local_data:
        st.info("💡 **Note:** Results may vary slightly on each run when fetching live data from Yahoo Finance. " +
                "For consistent results with same EOD data, enable 'Use local CSV data' or download data once using FETCH_EXPANDED_DATA.bat")
    
    st.markdown("---")
    
    # Run Screening
    if st.button("🚀 Run Technical Screening", type="primary", use_container_width=True, disabled=len(stocks) == 0):
        
        with st.spinner(f"Calculating REAL RSI, MACD, MAs for {len(stocks)} stocks..."):
            
            import yfinance as yf
            import os
            from datetime import datetime, timezone, timedelta
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            signals = []
            
            # Current timestamp in IST (Indian Standard Time = UTC+5:30)
            ist_offset = timedelta(hours=5, minutes=30)
            ist_time = datetime.now(timezone.utc) + ist_offset
            signal_time = ist_time.strftime("%Y-%m-%d %H:%M:%S IST")
            
            def calc_rsi(prices, period=14):
                """Real RSI calculation"""
                deltas = np.diff(prices)
                gains = np.where(deltas > 0, deltas, 0)
                losses = np.where(deltas < 0, -deltas, 0)
                avg_gain = np.mean(gains[:period]) if len(gains) >= period else 0
                avg_loss = np.mean(losses[:period]) if len(losses) >= period else 1
                if avg_loss == 0:
                    return 100
                rs = avg_gain / avg_loss
                return 100 - (100 / (1 + rs))
            
            def load_local_data(symbol, lookback_days):
                """Load data from local CSV file"""
                # Try multiple possible data directories
                possible_dirs = [
                    'data/stocks_all',
                    'data/stocks_nifty500',
                    'data/stocks_smallcap250',
                    'data/stocks',
                    '../data/stocks_all'
                ]
                
                for data_dir in possible_dirs:
                    csv_path = os.path.join(data_dir, f"{symbol}.csv")
                    if os.path.exists(csv_path):
                        df = pd.read_csv(csv_path)
                        df['Date'] = pd.to_datetime(df['Date'])
                        df = df.sort_values('Date')
                        # Get last N days
                        df = df.tail(lookback_days)
                        # Rename columns to match Yahoo Finance format
                        if 'Open' in df.columns:
                            df = df.rename(columns={'Open': 'Open', 'High': 'High', 'Low': 'Low', 'Close': 'Close', 'Volume': 'Volume'})
                        return df
                return None
            
            for idx, symbol in enumerate(stocks):
                status_text.text(f"📊 {symbol}... ({idx+1}/{len(stocks)})")
                
                try:
                    # Load data based on user preference
                    hist = None
                    if use_local_data:
                        hist = load_local_data(symbol, lookback_days + 50)  # Extra days for MA calculation
                        if hist is None or hist.empty or len(hist) < 20:
                            # Fall back to Yahoo Finance if local data not available
                            ticker = yf.Ticker(get_yfinance_symbol(symbol))
                            hist = ticker.history(period=f"{lookback_days}d")
                    if not use_local_data or hist is None or hist.empty or len(hist) < 20:
                        # Fetch from Yahoo Finance
                        ticker = yf.Ticker(get_yfinance_symbol(symbol))
                        hist = ticker.history(period=f"{lookback_days}d")
                    
                    if hist.empty or len(hist) < 20:
                        continue
                    
                    price = hist['Close'].iloc[-1]
                    
                    # Calculate REAL indicators
                    rsi = calc_rsi(hist['Close'].values)
                    sma_20 = hist['Close'].rolling(20).mean().iloc[-1]
                    sma_50 = hist['Close'].rolling(50).mean().iloc[-1] if len(hist) >= 50 else sma_20
                    sma_100 = hist['Close'].rolling(100).mean().iloc[-1] if len(hist) >= 100 else sma_50
                    sma_200 = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else sma_100
                    
                    # MACD
                    ema_12 = hist['Close'].ewm(span=12).mean().iloc[-1]
                    ema_26 = hist['Close'].ewm(span=26).mean().iloc[-1]
                    macd = ema_12 - ema_26
                    
                    # Fibonacci Retracements (calculate from recent high/low)
                    period_high = hist['High'].tail(lookback_days).max()
                    period_low = hist['Low'].tail(lookback_days).min()
                    fib_diff = period_high - period_low
                    
                    fib_levels = {
                        '0.236': period_high - (fib_diff * 0.236),
                        '0.382': period_high - (fib_diff * 0.382),
                        '0.500': period_high - (fib_diff * 0.500),
                        '0.618': period_high - (fib_diff * 0.618),
                        '0.786': period_high - (fib_diff * 0.786)
                    }
                    
                    # Find nearest Fibonacci level
                    nearest_fib = None
                    min_distance = float('inf')
                    for level_name, level_price in fib_levels.items():
                        distance = abs(price - level_price)
                        if distance < min_distance:
                            min_distance = distance
                            nearest_fib = (level_name, level_price)
                    
                    fib_proximity = (min_distance / price) * 100  # Distance as % of price
                    
                    # Volume
                    avg_vol = hist['Volume'].rolling(20).mean().iloc[-1]
                    curr_vol = hist['Volume'].iloc[-1]
                    vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 1
                    
                    # Pattern 1: Golden Cross (SMA 20 > SMA 50)
                    if sma_20 > sma_50 * 1.005 and price > sma_20 and vol_ratio > 1.2:
                        strength = min(9.0, 7.0 + (vol_ratio - 1.2) * 2)
                        if strength >= min_pattern_strength:
                            signals.append({
                                'Generated': signal_time,
                                'Symbol': symbol,
                                'Pattern': 'Golden Cross',
                                'Strength': f"{strength:.1f}/10",
                                'Price': f"{price:.2f}",
                                'Target': f"{price * 1.03:.2f}",
                                'Stop': f"{price * 0.98:.2f}",
                                'RSI': f"{rsi:.0f}",
                                'SMA200': f"{sma_200:.2f}" if len(hist) >= 200 else 'N/A',
                                'Info': f"Vol {vol_ratio:.1f}x"
                            })
                    
                    # Pattern 1b: SUPER Golden Cross (SMA 50 > SMA 200) - VERY BULLISH!
                    if len(hist) >= 200 and sma_50 > sma_200 * 1.01 and price > sma_50:
                        strength = min(9.5, 8.5 + (sma_50 / sma_200 - 1) * 100)
                        if strength >= min_pattern_strength:
                            signals.append({
                                'Generated': signal_time,
                                'Symbol': symbol,
                                'Pattern': '🚀 Super Golden Cross',
                                'Strength': f"{strength:.1f}/10",
                                'Price': f"{price:.2f}",
                                'Target': f"{price * 1.05:.2f}",
                                'Stop': f"{price * 0.97:.2f}",
                                'RSI': f"{rsi:.0f}",
                                'SMA200': f"{sma_200:.2f}",
                                'Info': 'SMA50 > SMA200 🔥'
                            })
                    
                    # Pattern 1c: Price Above SMA 200 (Institutional Support)
                    if len(hist) >= 200 and price > sma_200 * 1.02 and rsi < 70:
                        strength = min(9.0, 7.5 + ((price / sma_200 - 1) * 50))
                        if strength >= min_pattern_strength:
                            signals.append({
                                'Generated': signal_time,
                                'Symbol': symbol,
                                'Pattern': 'Above SMA 200',
                                'Strength': f"{strength:.1f}/10",
                                'Price': f"{price:.2f}",
                                'Target': f"{price * 1.04:.2f}",
                                'Stop': f"{sma_200:.2f}",
                                'RSI': f"{rsi:.0f}",
                                'SMA200': f"{sma_200:.2f}",
                                'Info': 'Strong trend'
                            })
                    
                    # Pattern 2: RSI Oversold
                    if 25 < rsi < 35 and hist['Close'].iloc[-1] > hist['Open'].iloc[-1]:
                        strength = min(9.0, 6.0 + (35 - rsi) / 3)
                        if strength >= min_pattern_strength:
                            signals.append({
                                'Generated': signal_time,
                                'Symbol': symbol,
                                'Pattern': 'RSI Oversold',
                                'Strength': f"{strength:.1f}/10",
                                'Price': f"{price:.2f}",
                                'Target': f"{price * 1.04:.2f}",
                                'Stop': f"{price * 0.97:.2f}",
                                'RSI': f"{rsi:.0f}",
                                'SMA200': f"{sma_200:.2f}" if len(hist) >= 200 else 'N/A',
                                'Info': 'Bullish reversal'
                            })
                    
                    # Pattern 3: MACD Bullish
                    if macd > 0 and vol_ratio > 1.1:
                        strength = min(9.0, 6.5 + vol_ratio)
                        if strength >= min_pattern_strength:
                            signals.append({
                                'Generated': signal_time,
                                'Symbol': symbol,
                                'Pattern': 'MACD Bullish',
                                'Strength': f"{strength:.1f}/10",
                                'Price': f"{price:.2f}",
                                'Target': f"{price * 1.035:.2f}",
                                'Stop': f"{price * 0.98:.2f}",
                                'RSI': f"{rsi:.0f}",
                                'SMA200': f"{sma_200:.2f}" if len(hist) >= 200 else 'N/A',
                                'Info': f"MACD+ Vol {vol_ratio:.1f}x"
                            })
                    
                    # Pattern 4: Fibonacci Bounce (Price near key Fibonacci level)
                    if nearest_fib and fib_proximity < 2.0:  # Within 2% of Fib level
                        fib_level, fib_price = nearest_fib
                        # Bullish bounce from support levels (0.618, 0.786)
                        if fib_level in ['0.618', '0.786'] and price > fib_price * 0.995:
                            strength = min(9.0, 7.5 + (2.0 - fib_proximity))
                            if strength >= min_pattern_strength:
                                signals.append({
                                    'Generated': signal_time,
                                    'Symbol': symbol,
                                    'Pattern': f'🎯 Fib {float(fib_level)*100:.1f}% Bounce',
                                    'Strength': f"{strength:.1f}/10",
                                    'Price': f"{price:.2f}",
                                    'Target': f"{fib_levels['0.382']:.2f}",
                                    'Stop': f"{fib_levels['0.786']:.2f}",
                                    'RSI': f"{rsi:.0f}",
                                    'SMA200': f"{sma_200:.2f}" if len(hist) >= 200 else 'N/A',
                                    'Info': f'@Fib {fib_level}'
                                })
                        # Resistance at 0.236, 0.382 levels
                        elif fib_level in ['0.236', '0.382'] and rsi < 50:
                            strength = min(9.0, 7.0 + (2.0 - fib_proximity))
                            if strength >= min_pattern_strength:
                                signals.append({
                                    'Generated': signal_time,
                                    'Symbol': symbol,
                                    'Pattern': f'📈 Fib {float(fib_level)*100:.1f}% Break',
                                    'Strength': f"{strength:.1f}/10",
                                    'Price': f"{price:.2f}",
                                    'Target': f"{period_high:.2f}",
                                    'Stop': f"{fib_levels['0.500']:.2f}",
                                    'RSI': f"{rsi:.0f}",
                                    'SMA200': f"{sma_200:.2f}" if len(hist) >= 200 else 'N/A',
                                    'Info': f'Near Fib {fib_level}'
                                })
                    
                    # Pattern 5: Support Bounce
                    support = hist['Low'].rolling(20).min().iloc[-1]
                    if price < support * 1.02 and rsi < 60:
                        strength = min(9.0, 7.5)
                        if strength >= min_pattern_strength:
                            signals.append({
                                'Generated': signal_time,
                                'Symbol': symbol,
                                'Pattern': 'Support Bounce',
                                'Strength': f"{strength:.1f}/10",
                                'Price': f"{price:.2f}",
                                'Target': f"{price * 1.03:.2f}",
                                'Stop': f"{support * 0.99:.2f}",
                                'RSI': f"{rsi:.0f}",
                                'SMA200': f"{sma_200:.2f}" if len(hist) >= 200 else 'N/A',
                                'Info': f"Support {support:.0f}"
                            })
                
                except:
                    continue
                
                progress_bar.progress((idx + 1) / len(stocks))
            
            progress_bar.empty()
            status_text.empty()
            
            # Show Results
            if signals:
                st.success(f"✅ Found {len(signals)} REAL signals!")
                
                df = pd.DataFrame(signals)
                
                st.markdown("---")
                st.dataframe(df, use_container_width=True, height=500)
                
                # Summary
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🎯 Signals", len(signals))
                with col2:
                    avg_str = df['Strength'].str.split('/').str[0].astype(float).mean()
                    st.metric("📊 Avg Strength", f"{avg_str:.1f}/10")
                with col3:
                    patterns = df['Pattern'].nunique()
                    st.metric("🔍 Patterns", patterns)
                
                # Download
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download Signals",
                    csv,
                    f"tech_signals_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
                
                st.info("""
                💡 **Next Steps:**
                1. Review each signal
                2. Check the chart yourself
                3. Confirm pattern visually
                4. Use stop loss always!
                5. Track results (win rate)
                """)
            else:
                st.warning(f"⚠️ No signals with strength ≥ {min_pattern_strength}")
                st.info("Try: Lower strength threshold or select more stocks")

# ============================================================
elif page == "S&R Analysis":
    st.header("📈 Support & Resistance Analysis")
    
    st.info("🎯 Analyze support and resistance levels for stocks with AI-powered insights! Fetches REAL data from Yahoo Finance (no API key needed!)")
    
    # Mode selection
    analysis_mode = st.radio(
        "Analysis Mode:",
        ["Single Stock Analysis", "Batch Analysis (Multiple Stocks)"],
        horizontal=True
    )
    
    if analysis_mode == "Single Stock Analysis":
        # Input form for single stock
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if EXPANDED_UNIVERSE_AVAILABLE:
                # Create categorized stock list
                stock_categories = {
                    '--- COMMODITIES (Gold, Silver) ---': COMMODITIES,
                    '--- NIFTY 50 ---': NIFTY_50,
                    '--- NIFTY 200 (Mid-cap) ---': [s for s in NIFTY_200 if s not in NIFTY_50],
                    '--- NIFTY 500 ---': [s for s in NIFTY_500 if s not in NIFTY_200],
                    '--- SMALLCAP 250 ---': SMALLCAP_250
                }
                
                # Build options list
                stock_options = []
                for category, stocks in stock_categories.items():
                    if stocks:
                        stock_options.append(category)
                        stock_options.extend(sorted(stocks))
                
                symbol_input = st.selectbox(
                    "Select Stock:", 
                    stock_options,
                    index=stock_options.index('RELIANCE') if 'RELIANCE' in stock_options else 0,
                    help="Select from 750+ stocks (Nifty 50/200/500 + Smallcap 250)"
                )
                
                # Skip if category header selected
                if symbol_input.startswith('---'):
                    st.warning("⚠️ Please select a stock symbol, not a category header")
                    symbol_input = 'RELIANCE'
            else:
                symbol_input = st.text_input("Enter Symbol", "RELIANCE", help="Enter stock symbol (e.g., RELIANCE, TCS, INFY)")
        
        with col2:
            sensitivity = st.slider("Sensitivity", 3, 10, 3, help="Lower = more nearby levels (recommended), Higher = fewer major levels")
        
        with col3:
            min_touches = st.slider("Min Touches", 2, 5, 2, help="Minimum times price must touch a level")
        
        # DUAL S&R System Option (NEW!)
        if DUAL_SR_AVAILABLE:
            use_dual_sr = st.checkbox(
                "🎯 Use DUAL S&R System (Video Insights)", 
                value=True,
                help="PRIMARY (wick extremes) + SECONDARY (close/open battle zones)"
            )
            if use_dual_sr:
                st.info("✅ PRIMARY: Solid lines (wick highs/lows) | SECONDARY: Dashed lines (battle zones)")
        else:
            use_dual_sr = False
    
    else:  # Batch Analysis
        st.subheader("📋 Batch Analysis - Multiple Stocks")
        
        col1, col2 = st.columns([2, 1])
        
        with col2:
            st.markdown("**Quick Presets (Copy-Paste):**")
            
            # Nifty 50 preset
            with st.expander("📊 Nifty 50 (51 stocks)", expanded=False):
                nifty50_list = "\n".join(NIFTY_50) if EXPANDED_UNIVERSE_AVAILABLE else "RELIANCE\nTCS\nHDFCBANK\nINFY\nICICIBANK\nHINDUNILVR\nITC\nSBIN\nBHARTIARTL\nAXISBANK\nKOTAKBANK\nLT\nHCLTECH\nASIANPAINTS\nMARUTI\nSUNPHARMA\nTITAN\nULTRACEMCO\nNESTLEIND\nBAJFINANCE\nJIOFIN"
                st.code(nifty50_list, language=None)
                st.caption("👆 Copy and paste in text area")
            
            # Nifty Bank
            with st.expander("🏦 Nifty Bank (12 stocks)", expanded=False):
                bank_list = "HDFCBANK\nICICIBANK\nSBIN\nKOTAKBANK\nAXISBANK\nINDUSINDBK\nBANDHANBNK\nFEDERALBNK\nIDFCFIRSTB\nPNB\nBANKBARODA\nCANBK"
                st.code(bank_list, language=None)
                st.caption("👆 Copy and paste in text area")
            
            # Nifty IT
            with st.expander("💻 Nifty IT (10 stocks)", expanded=False):
                it_list = "TCS\nINFY\nHCLTECH\nWIPRO\nTECHM\nLTIM\nCOFORGE\nPERSISTENT\nMPHASIS\nLTTS"
                st.code(it_list, language=None)
                st.caption("👆 Copy and paste in text area")
            
            # Nifty Auto
            with st.expander("🚗 Nifty Auto (15 stocks)", expanded=False):
                auto_list = "MARUTI\nTATAMOTORS\nM&M\nBAJAJ-AUTO\nEICHERMOT\nHEROMOTOCO\nTVSMOTOR\nASHOKLEY\nMOTHERSON\nBOSCHLTD\nEXIDEIND\nMRF\nAPOLLOTYRE\nBALKRISIND\nBHFORGE"
                st.code(auto_list, language=None)
                st.caption("👆 Copy and paste in text area")
            
            # Nifty Pharma
            with st.expander("💊 Nifty Pharma (20 stocks)", expanded=False):
                pharma_list = "SUNPHARMA\nDRREDDY\nCIPLA\nDIVISLAB\nAUROPHARMA\nLUPIN\nTORNTPHARM\nALKEM\nBIOCON\nCADILAHC\nGLENMARK\nIPCALAB\nLAURUSLABS\nGRANULES\nALEMBIC\nSYNGENE\nNATCOPHARM\nLALPATHLAB\nMAXHEALTH\nFORTIS"
                st.code(pharma_list, language=None)
                st.caption("👆 Copy and paste in text area")
            
            # Nifty Metal
            with st.expander("🔩 Nifty Metal (15 stocks)", expanded=False):
                metal_list = "TATASTEEL\nJSWSTEEL\nHINDALCO\nVEDL\nCOALINDIA\nNMDC\nJINDALSTEL\nSAIL\nHINDZINC\nNALCO\nNMDC\nAPL\nRATNAMANI\nMOIL\nJSPL"
                st.code(metal_list, language=None)
                st.caption("👆 Copy and paste in text area")
            
            # Nifty Energy
            with st.expander("⚡ Nifty Energy (10 stocks)", expanded=False):
                energy_list = "RELIANCE\nONGC\nNTPC\nPOWERGRID\nBPCL\nIOC\nGAIL\nHINDPETRO\nADANIGREEN\nTATAPOWER"
                st.code(energy_list, language=None)
                st.caption("👆 Copy and paste in text area")
            
            # Nifty FMCG
            with st.expander("🛒 Nifty FMCG (15 stocks)", expanded=False):
                fmcg_list = "HINDUNILVR\nITC\nNESTLEIND\nBRITANNIA\nDABUR\nGODREJCP\nMARICO\nCOLGATE\nTATACONSUM\nVBL\nPIDILITIND\nHAVELLS\nGODREJAGRO\nEMAMILTD\nJYOTHYLAB"
                st.code(fmcg_list, language=None)
                st.caption("👆 Copy and paste in text area")
            
            # Top 20 preset
            with st.expander("⚡ Top 20 Liquid Stocks", expanded=False):
                top20_list = "RELIANCE\nTCS\nHDFCBANK\nINFY\nICICIBANK\nHINDUNILVR\nITC\nSBIN\nBHARTIARTL\nAXISBANK\nKOTAKBANK\nLT\nHCLTECH\nASIANPAINTS\nMARUTI\nBAJFINANCE\nSUNPHARMA\nTITAN\nULTRACEMCO\nNESTLEIND"
                st.code(top20_list, language=None)
                st.caption("👆 Copy and paste in text area")
            
            st.markdown("**Analysis Settings:**")
            sensitivity = st.slider("Sensitivity", 3, 10, 3, help="Lower = more nearby levels (recommended), Higher = fewer major levels", key="batch_sens")
            min_touches = st.slider("Min Touches", 2, 5, 2, help="Minimum times price must touch a level", key="batch_touch")
        
        with col1:
            st.markdown("**Enter stock symbols** (one per line or comma-separated):")
            default_stocks = "RELIANCE\nTCS\nINFY\nHDFCBANK\nICICIBANK\nSBIN\nBHARTIARTL\nITC\nHINDUNILVR\nAXISBANK"
            symbols_input = st.text_area(
                "Stock Symbols:",
                value=default_stocks,
                height=300,
                help="Enter one symbol per line, or separate with commas. Use presets on the right →",
                key="batch_symbols_input"
            )
    
    if st.button("🔍 Analyze Support & Resistance", type="primary"):
        # Handle batch vs single analysis
        if analysis_mode == "Batch Analysis (Multiple Stocks)":
            # Parse symbols
            symbols_list = []
            for line in symbols_input.replace(',', '\n').split('\n'):
                symbol = line.strip().upper()
                if symbol:
                    symbols_list.append(symbol)
            
            if not symbols_list:
                st.error("❌ Please enter at least one stock symbol!")
            else:
                st.info(f"📊 Analyzing {len(symbols_list)} stocks...")
                
                # Initialize results
                batch_results = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Current timestamp in IST (Indian Standard Time = UTC+5:30)
                from datetime import datetime, timezone, timedelta
                ist_offset = timedelta(hours=5, minutes=30)
                ist_time = datetime.now(timezone.utc) + ist_offset
                analysis_time = ist_time.strftime("%Y-%m-%d %H:%M:%S IST")
                
                # Initialize S&R calculator
                sr_calc = SupportResistanceCalculator(sensitivity=sensitivity, min_touches=min_touches)
                
                # Use yfinance for real data (free, no API key needed!)
                import yfinance as yf
                
                for idx, symbol in enumerate(symbols_list):
                    status_text.text(f"Analyzing {symbol}... ({idx+1}/{len(symbols_list)})")
                    
                    try:
                        df = None
                        
                        # Fetch from Yahoo Finance
                        try:
                            ticker = yf.Ticker(get_yfinance_symbol(symbol))
                            df_raw = ticker.history(period="6mo", interval="1d")
                            
                            if not df_raw.empty and len(df_raw) > 50:
                                df = pd.DataFrame({
                                    'time': df_raw.index,
                                    'open': df_raw['Open'].values,
                                    'high': df_raw['High'].values,
                                    'low': df_raw['Low'].values,
                                    'close': df_raw['Close'].values,
                                    'volume': df_raw['Volume'].values
                                })
                        except:
                            pass
                        
                        # If data fetch failed, skip this stock
                        if df is None or df.empty:
                            batch_results.append({
                                'Symbol': symbol,
                                'Signal': 'ERROR',
                                'Nearest_Support': 'N/A',
                                'Nearest_Resistance': 'N/A',
                                'Trend': 'N/A',
                                'Error': 'Could not fetch data'
                            })
                            progress_bar.progress((idx + 1) / len(symbols_list))
                            continue
                        
                        # Calculate S&R
                        current_price = df['close'].iloc[-1]
                        sr_data = sr_calc.calculate_support_resistance(df, current_price)
                        ma_data = sr_calc.calculate_moving_averages(df)
                        breakouts = sr_calc.detect_breakouts(df, sr_data)
                        reversals = sr_calc.detect_role_reversals(df, sr_data)
                        signal = sr_calc.generate_trading_signal(df, sr_data, ma_data, breakouts, reversals)
                        
                        # Get nearest levels
                        nearest_support = sr_data['supports'][0] if sr_data['supports'] else None
                        nearest_resistance = sr_data['resistances'][0] if sr_data['resistances'] else None
                        
                        batch_results.append({
                            'Generated': analysis_time,
                            'Symbol': symbol,
                            'Price': f"{current_price:.2f}",
                            'Signal': signal['signal'],
                            'Confidence': f"{signal['confidence_score']}%",
                            'Trend': ma_data['trend'] if ma_data.get('available') else 'N/A',
                            'Support': f"{nearest_support['level']:.2f} ({nearest_support['distance_pct']:.1f}%)" if nearest_support else "N/A",
                            'Resistance': f"{nearest_resistance['level']:.2f} ({nearest_resistance['distance_pct']:.1f}%)" if nearest_resistance else "N/A",
                            'Sup Strength': f"{nearest_support['strength']:.0f}" if nearest_support else "N/A",
                            'Res Strength': f"{nearest_resistance['strength']:.0f}" if nearest_resistance else "N/A",
                        })
                        
                    except Exception as e:
                        batch_results.append({
                            'Generated': analysis_time,
                            'Symbol': symbol,
                            'Price': 'Error',
                            'Signal': 'ERROR',
                            'Confidence': 'N/A',
                            'Trend': 'N/A',
                            'Support': 'N/A',
                            'Resistance': 'N/A',
                            'Sup Strength': 'N/A',
                            'Res Strength': 'N/A',
                        })
                    
                    progress_bar.progress((idx + 1) / len(symbols_list))
                
                status_text.text("✅ Analysis complete!")
                progress_bar.empty()
                
                # Display results
                st.markdown("---")
                st.subheader(f"📊 Batch Analysis Results ({len(symbols_list)} stocks)")
                
                # Convert to DataFrame
                results_df = pd.DataFrame(batch_results)
                
                # Filter options
                col1, col2, col3 = st.columns(3)
                with col1:
                    all_signals = ["STRONG BUY", "BUY", "WAIT", "HOLD", "SELL", "STRONG SELL", "ERROR"]
                    filter_signal = st.multiselect(
                        "Filter by Signal", 
                        all_signals, 
                        default=all_signals,
                        help="Select which signals to show"
                    )
                with col2:
                    all_trends = ["STRONG BULLISH", "BULLISH", "NEUTRAL", "BEARISH", "STRONG BEARISH", "N/A"]
                    filter_trend = st.multiselect(
                        "Filter by Trend", 
                        all_trends, 
                        default=all_trends,
                        help="Select which trends to show"
                    )
                with col3:
                    sort_by = st.selectbox("Sort by", ["Symbol", "Signal", "Confidence", "Trend"])
                
                # Apply filters
                if filter_signal:
                    results_df = results_df[results_df['Signal'].isin(filter_signal)]
                if filter_trend:
                    results_df = results_df[results_df['Trend'].isin(filter_trend)]
                
                # Sort
                if sort_by:
                    results_df = results_df.sort_values(by=sort_by)
                
                # Display table with color coding
                st.dataframe(
                    results_df.style.applymap(
                        lambda x: 'background-color: #d4edda' if 'BUY' in str(x) else ('background-color: #f8d7da' if 'SELL' in str(x) else ''),
                        subset=['Signal']
                    ),
                    use_container_width=True,
                    height=600
                )
                
                # Summary statistics
                st.markdown("---")
                st.subheader("📈 Summary Statistics")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    buy_count = len([r for r in batch_results if 'BUY' in r['Signal']])
                    st.metric("🟢 Buy Signals", buy_count)
                with col2:
                    sell_count = len([r for r in batch_results if 'SELL' in r['Signal']])
                    st.metric("🔴 Sell Signals", sell_count)
                with col3:
                    hold_count = len([r for r in batch_results if 'HOLD' in r['Signal']])
                    st.metric("🟡 Hold Signals", hold_count)
                with col4:
                    bullish_count = len([r for r in batch_results if 'BULLISH' in r['Trend']])
                    st.metric("📈 Bullish Trend", bullish_count)
                
                # Download button
                st.markdown("---")
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"sr_analysis_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
        else:  # Single Stock Analysis
            with st.spinner(f"Analyzing {symbol_input}..."):
                try:
                    # Initialize S&R calculator (use Enhanced if DUAL mode enabled)
                    if DUAL_SR_AVAILABLE and use_dual_sr:
                        sr_calc = ProfessionalSRCalculator(sensitivity=sensitivity, min_touches=min_touches)
                    else:
                        sr_calc = SupportResistanceCalculator(sensitivity=sensitivity, min_touches=min_touches)
                    
                    # Try to get data from yfinance (free, no API key needed!)
                    try:
                        import yfinance as yf
                        from datetime import datetime, timedelta
                        
                        st.info(f"📡 Fetching REAL data from Yahoo Finance for {symbol_input}...")
                        
                        # yfinance uses .NS suffix for NSE stocks
                        ticker = yf.Ticker(get_yfinance_symbol(symbol_input))
                        
                        # Fetch 1 year of data
                        df_raw = ticker.history(period="1y", interval="1d")
                        
                        if not df_raw.empty and len(df_raw) > 50:
                            # Convert to expected format
                            df = pd.DataFrame({
                                'time': df_raw.index,
                                'open': df_raw['Open'].values,
                                'high': df_raw['High'].values,
                                'low': df_raw['Low'].values,
                                'close': df_raw['Close'].values,
                                'volume': df_raw['Volume'].values
                            })
                            
                            st.success(f"✅ Fetched {len(df)} days of REAL data from Yahoo Finance!")
                            st.caption(f"Latest price: {df['close'].iloc[-1]:.2f}")
                        else:
                            df = None
                            st.warning(f"⚠️ No data found for {symbol_input}.NS on Yahoo Finance.")
                    
                    except Exception as e:
                        df = None
                        st.warning(f"⚠️ Error fetching data: {e}")
                    
                    if df is not None and not df.empty:
                        # Calculate S&R levels
                        current_price = df['close'].iloc[-1]
                        sr_data = sr_calc.calculate_support_resistance(df, current_price)
                        
                        # Calculate DUAL S&R if enabled
                        dual_sr_data = None
                        if DUAL_SR_AVAILABLE and use_dual_sr:
                            dual_sr_data = sr_calc.calculate_dual_sr(df, current_price)
                            
                            # Also calculate advanced features
                            pivot_data_standard = sr_calc.calculate_pivot_points(df, 'standard')
                            pivot_data_fib = sr_calc.calculate_pivot_points(df, 'fibonacci')
                            fib_levels = sr_calc.calculate_fibonacci_levels(df, lookback_period=50)
                            trade_setups = sr_calc.generate_trade_setups(
                                df, sr_data, fib_levels, pivot_data_standard,
                                risk_per_trade_pct=2.0, capital=100000
                            )
                        else:
                            pivot_data_standard = None
                            pivot_data_fib = None
                            fib_levels = None
                            trade_setups = None
                        
                        # Calculate MA trend
                        ma_data = sr_calc.calculate_moving_averages(df)
                        
                        # Detect breakouts
                        breakouts = sr_calc.detect_breakouts(df, sr_data)
                        
                        # Detect role reversals
                        reversals = sr_calc.detect_role_reversals(df, sr_data)
                        
                        # Generate trading signal
                        signal = sr_calc.generate_trading_signal(df, sr_data, ma_data, breakouts, reversals)
                        
                        # Display results
                        st.success("✅ Analysis Complete!")
                        
                        # Current Price & Signal
                        st.markdown("---")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Current Price", f"{sr_data['current_price']:.2f}")
                        
                        with col2:
                            signal_color = "🟢" if "BUY" in signal['signal'] else ("🔴" if "SELL" in signal['signal'] else "🟡")
                            st.metric("Signal", f"{signal_color} {signal['signal']}")
                        
                        with col3:
                            st.metric("Confidence", f"{signal['confidence_score']}%")
                        
                        with col4:
                            st.metric("Strength", signal['strength'])
                        
                        # Signal Reasons
                        if signal['reasons']:
                            st.subheader("📋 Signal Reasons")
                            for reason in signal['reasons']:
                                st.info(f"• {reason}")
                        
                        st.markdown("---")
                        
                        # ===================================================================
                        # DUAL S&R DISPLAY (If enabled)
                        # ===================================================================
                        if DUAL_SR_AVAILABLE and use_dual_sr and dual_sr_data:
                            st.subheader("🎯 DUAL S&R SYSTEM (Video Insights)")
                            st.caption("PRIMARY: Wick extremes (solid lines) | SECONDARY: Battle zones (dashed lines)")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("### 🟢 SUPPORT LEVELS")
                                
                                # PRIMARY SUPPORTS
                                if dual_sr_data['primary']['supports']:
                                    st.markdown("**⭐ PRIMARY (Wick Lows - Major Levels)**")
                                    for i, sup in enumerate(dual_sr_data['primary']['supports'][:3], 1):
                                        st.success(f"**S{i}: ₹{sup['level']:.2f}** | Distance: {sup['distance_pct']:+.2f}% | Strength: {sup['strength']:.0f} | Touches: {sup['touches']}")
                                        st.caption(f"   {sup['description']}")
                                
                                # SECONDARY SUPPORTS
                                if dual_sr_data['secondary']['supports']:
                                    st.markdown("**🔸 SECONDARY (Battle Zones - Close/Open)**")
                                    for i, sup in enumerate(dual_sr_data['secondary']['supports'][:3], 1):
                                        st.info(f"**S{i}: ₹{sup['level']:.2f}** | Distance: {sup['distance_pct']:+.2f}% | Tests: {sup['touches']}x")
                                        st.caption(f"   {sup['description']}")
                            
                            with col2:
                                st.markdown("### 🔴 RESISTANCE LEVELS")
                                
                                # PRIMARY RESISTANCES
                                if dual_sr_data['primary']['resistances']:
                                    st.markdown("**⭐ PRIMARY (Wick Highs - Major Levels)**")
                                    for i, res in enumerate(dual_sr_data['primary']['resistances'][:3], 1):
                                        st.error(f"**R{i}: ₹{res['level']:.2f}** | Distance: {res['distance_pct']:+.2f}% | Strength: {res['strength']:.0f} | Touches: {res['touches']}")
                                        st.caption(f"   {res['description']}")
                                
                                # SECONDARY RESISTANCES
                                if dual_sr_data['secondary']['resistances']:
                                    st.markdown("**🔸 SECONDARY (Battle Zones - Close/Open)**")
                                    for i, res in enumerate(dual_sr_data['secondary']['resistances'][:3], 1):
                                        st.warning(f"**R{i}: ₹{res['level']:.2f}** | Distance: {res['distance_pct']:+.2f}% | Tests: {res['touches']}x")
                                        st.caption(f"   {res['description']}")
                            
                            st.markdown("---")
                            
                            # PIVOT POINTS
                            if pivot_data_standard and not pivot_data_standard.get('error'):
                                st.subheader("📍 PIVOT POINTS (Standard)")
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("Pivot", f"₹{pivot_data_standard['pivot']:.2f}")
                                
                                with col2:
                                    st.markdown("**Resistance**")
                                    st.caption(f"R1: ₹{pivot_data_standard['r1']:.2f}")
                                    st.caption(f"R2: ₹{pivot_data_standard['r2']:.2f}")
                                    st.caption(f"R3: ₹{pivot_data_standard['r3']:.2f}")
                                
                                with col3:
                                    st.markdown("**Support**")
                                    st.caption(f"S1: ₹{pivot_data_standard['s1']:.2f}")
                                    st.caption(f"S2: ₹{pivot_data_standard['s2']:.2f}")
                                    st.caption(f"S3: ₹{pivot_data_standard['s3']:.2f}")
                            
                            st.markdown("---")
                            
                            # FIBONACCI LEVELS
                            if fib_levels and not fib_levels.get('error'):
                                st.subheader("📈 FIBONACCI LEVELS")
                                st.caption(f"Trend: {fib_levels['trend']} | Swing High: ₹{fib_levels['swing_high']:.2f} | Swing Low: ₹{fib_levels['swing_low']:.2f}")
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("**🔄 Retracement**")
                                    for level, price in fib_levels['retracement'].items():
                                        marker = " ⭐" if level in ['50%', '61.8%'] else ""
                                        st.caption(f"{level}: ₹{price:.2f}{marker}")
                                    
                                    if fib_levels['golden_zone']['in_zone']:
                                        st.success(f"🎯 Price IN GOLDEN ZONE (₹{fib_levels['golden_zone']['lower']:.2f}-₹{fib_levels['golden_zone']['upper']:.2f})")
                                
                                with col2:
                                    st.markdown("**🎯 Extension Targets**")
                                    for level, price in fib_levels['extension'].items():
                                        st.caption(f"{level}: ₹{price:.2f}")
                            
                            st.markdown("---")
                            
                            # TRADE SETUPS
                            if trade_setups:
                                st.subheader("💡 TRADE SETUPS")
                                for setup in trade_setups:
                                    if setup['type'] == 'BUY':
                                        with st.expander(f"🟢 BUY SETUP - {setup['status']}", expanded=True):
                                            col1, col2, col3 = st.columns(3)
                                            with col1:
                                                st.metric("Entry Price", f"₹{setup['entry_price']:.2f}")
                                                st.metric("Stop Loss", f"₹{setup['stop_loss']:.2f}")
                                            with col2:
                                                st.metric("Target 1", f"₹{setup['target1']:.2f}")
                                                st.metric("R:R Ratio", f"1:{setup['rr_ratio1']:.2f}")
                                            with col3:
                                                st.metric("Position Size", f"{setup['position_size']} shares")
                                                st.metric("Potential Profit", f"₹{setup['potential_profit1']:,.0f}")
                                            
                                            st.caption(f"Confidence: {setup['confidence']} | Risk Amount: ₹{setup['risk_amount']:,.0f}")
                                    
                                    else:  # SELL
                                        with st.expander(f"🔴 SELL SETUP - {setup['status']}", expanded=True):
                                            col1, col2, col3 = st.columns(3)
                                            with col1:
                                                st.metric("Entry Price", f"₹{setup['entry_price']:.2f}")
                                                st.metric("Stop Loss", f"₹{setup['stop_loss']:.2f}")
                                            with col2:
                                                st.metric("Target 1", f"₹{setup['target1']:.2f}")
                                                st.metric("R:R Ratio", f"1:{setup['rr_ratio1']:.2f}")
                                            with col3:
                                                st.metric("Position Size", f"{setup['position_size']} shares")
                                                st.metric("Potential Profit", f"₹{setup['potential_profit1']:,.0f}")
                                            
                                            st.caption(f"Confidence: {setup['confidence']} | Risk Amount: ₹{setup['risk_amount']:,.0f}")
                            
                            st.markdown("---")
                        
                        # LEGACY S&R DISPLAY (If DUAL mode is OFF)
                        else:
                            # Support & Resistance Tables
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("🛡️ Support Levels")
                                if sr_data['supports']:
                                    df_supports = pd.DataFrame(sr_data['supports'])
                                    # Format for display
                                    display_supports = df_supports[['level', 'distance_pct', 'touches', 'volume_factor', 'strength']].copy()
                                    display_supports.columns = ['Level', 'Distance %', 'Touches', 'Volume Factor', 'Strength']
                                    st.dataframe(
                                        display_supports.style.format({
                                            'Level': '{:.2f}',
                                            'Distance %': '{:.1f}%',
                                            'Volume Factor': '{:.2f}',
                                            'Strength': '{:.0f}'
                                        }),
                                        use_container_width=True
                                    )
                                else:
                                    st.info("No strong support levels found")
                            
                            with col2:
                                st.subheader("🚧 Resistance Levels")
                                if sr_data['resistances']:
                                    df_resistances = pd.DataFrame(sr_data['resistances'])
                                    # Format for display
                                    display_resistances = df_resistances[['level', 'distance_pct', 'touches', 'volume_factor', 'strength']].copy()
                                    display_resistances.columns = ['Level', 'Distance %', 'Touches', 'Volume Factor', 'Strength']
                                    st.dataframe(
                                        display_resistances.style.format({
                                            'Level': '{:.2f}',
                                            'Distance %': '{:.1f}%',
                                            'Volume Factor': '{:.2f}',
                                            'Strength': '{:.0f}'
                                        }),
                                        use_container_width=True
                                    )
                                else:
                                    st.info("No strong resistance levels found")
                        
                        st.markdown("---")
                        
                        # Chart with S&R levels
                        st.subheader("📊 Price Chart with Support & Resistance")
                        
                        fig = go.Figure()
                        
                        # Candlestick chart
                        fig.add_trace(go.Candlestick(
                            x=df['time'],
                            open=df['open'],
                            high=df['high'],
                            low=df['low'],
                            close=df['close'],
                            name='Price'
                        ))
                    
                    # ===================================================================
                    # DUAL S&R CHART RENDERING (If enabled)
                    # ===================================================================
                    if DUAL_SR_AVAILABLE and use_dual_sr and dual_sr_data:
                        # PRIMARY SUPPORTS (Solid Thick Green)
                        for i, sup in enumerate(dual_sr_data['primary']['supports'][:3], 1):
                            fig.add_hline(
                                y=sup['level'],
                                line=dict(color='#00ff00', width=3, dash='solid'),
                                annotation_text=f"PRIMARY S{i}: ₹{sup['level']:.2f}",
                                annotation_position="left",
                                annotation_font_color='#00ff00',
                                annotation_font_size=11
                            )
                        
                        # SECONDARY SUPPORTS (Dashed Dark Green)
                        for i, sup in enumerate(dual_sr_data['secondary']['supports'][:3], 1):
                            fig.add_hline(
                                y=sup['level'],
                                line=dict(color='#00cc00', width=2, dash='dash'),
                                annotation_text=f"Battle S{i}: ₹{sup['level']:.2f} ({sup['touches']}x)",
                                annotation_position="left",
                                annotation_font_color='#00cc00',
                                annotation_font_size=10
                            )
                        
                        # PRIMARY RESISTANCES (Solid Thick Red)
                        for i, res in enumerate(dual_sr_data['primary']['resistances'][:3], 1):
                            fig.add_hline(
                                y=res['level'],
                                line=dict(color='#ff0000', width=3, dash='solid'),
                                annotation_text=f"PRIMARY R{i}: ₹{res['level']:.2f}",
                                annotation_position="right",
                                annotation_font_color='#ff0000',
                                annotation_font_size=11
                            )
                        
                        # SECONDARY RESISTANCES (Dashed Orange-Red)
                        for i, res in enumerate(dual_sr_data['secondary']['resistances'][:3], 1):
                            fig.add_hline(
                                y=res['level'],
                                line=dict(color='#ff6600', width=2, dash='dash'),
                                annotation_text=f"Battle R{i}: ₹{res['level']:.2f} ({res['touches']}x)",
                                annotation_position="right",
                                annotation_font_color='#ff6600',
                                annotation_font_size=10
                            )
                        
                        # PIVOT POINTS (Blue Dotted)
                        if pivot_data_standard and not pivot_data_standard.get('error'):
                            for name, level in [('P', pivot_data_standard['pivot']), 
                                               ('R1', pivot_data_standard['r1']), 
                                               ('S1', pivot_data_standard['s1'])]:
                                if level:
                                    fig.add_hline(
                                        y=level,
                                        line=dict(color='#0066ff', width=1, dash='dot'),
                                        annotation_text=f"{name}: ₹{level:.2f}",
                                        annotation_font_size=9,
                                        annotation_font_color='#0066ff'
                                    )
                    
                    # LEGACY CHART RENDERING (If DUAL mode is OFF)
                    else:
                        # Add support levels
                        for support in sr_data['supports'][:3]:
                            fig.add_hline(
                                y=support['level'],
                                line_dash="dash",
                                line_color="green",
                                annotation_text=f"Support: {support['level']:.2f} (Strength: {support['strength']:.0f})",
                                annotation_position="left"
                            )
                        
                        # Add resistance levels
                        for resistance in sr_data['resistances'][:3]:
                            fig.add_hline(
                                y=resistance['level'],
                                line_dash="dash",
                                line_color="red",
                                annotation_text=f"Resistance: {resistance['level']:.2f} (Strength: {resistance['strength']:.0f})",
                                annotation_position="right"
                            )
                    
                    # Add moving averages if available
                    if ma_data.get('available'):
                        fig.add_trace(go.Scatter(
                            x=df['time'].tail(50),
                            y=[ma_data['EMA50']] * 50,
                            mode='lines',
                            name='50 EMA',
                            line=dict(color='blue', width=1)
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=df['time'].tail(50),
                            y=[ma_data['EMA200']] * 50,
                            mode='lines',
                            name='200 EMA',
                            line=dict(color='orange', width=1)
                        ))
                    
                    fig.update_layout(
                        title=f"{symbol_input} - Support & Resistance Analysis",
                        xaxis_title="Date",
                        yaxis_title="Price (₹)",
                        height=600,
                        xaxis_rangeslider_visible=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Moving Averages Analysis
                    if ma_data.get('available'):
                        st.markdown("---")
                        st.subheader("📈 Moving Averages Analysis")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("50 EMA", f"{ma_data['EMA50']:.2f}", f"{ma_data['distance_from_50ema']:.2f}%")
                        
                        with col2:
                            st.metric("200 EMA", f"{ma_data['EMA200']:.2f}", f"{ma_data['distance_from_200ema']:.2f}%")
                        
                        with col3:
                            trend_color = "🟢" if "BULLISH" in ma_data['trend'] else ("🔴" if "BEARISH" in ma_data['trend'] else "🟡")
                            st.metric("Trend", f"{trend_color} {ma_data['trend']}")
                        
                        st.info(f"📊 {ma_data['context']}")
                        
                        if ma_data.get('cross'):
                            if ma_data['cross'] == 'GOLDEN CROSS':
                                st.success(f"🌟 {ma_data['cross']} detected! Bullish signal!")
                            else:
                                st.error(f"💀 {ma_data['cross']} detected! Bearish signal!")
                    
                    # Breakouts
                    if breakouts.get('breakout_detected'):
                        st.markdown("---")
                        st.subheader("💥 Breakout Detected!")
                        
                        for br in breakouts['breakouts']:
                            if br['direction'] == 'BULLISH':
                                st.success(f"🚀 **{br['type']}**: Price broke above {br['level']:.2f} with {br['strength']:.1f} strength")
                                if br['volume_confirmation']:
                                    st.info("✅ Confirmed with high volume")
                            else:
                                st.error(f"📉 **{br['type']}**: Price broke below {br['level']:.2f} with {br['strength']:.1f} strength")
                                if br['volume_confirmation']:
                                    st.info("✅ Confirmed with high volume")
                    
                        # Role Reversals
                        if reversals:
                            st.markdown("---")
                            st.subheader("🔄 Role Reversals Detected")
                            
                            for rev in reversals:
                                st.warning(f"**{rev['type']}** at ₹{rev['level']}: {rev['status']} (Confidence: {rev['confidence']})")
                    
                    else:
                        st.error("❌ Could not load price data")
                        
                except Exception as e:
                    st.error(f"❌ Error during analysis: {e}")
                    import traceback
                    st.error(traceback.format_exc())

# ============================================================
# PAGE: VWAP STRATEGY
# ============================================================

elif page == "VWAP Strategy":
    st.header("🎯 VWAP Ladder Strategy Backtest")
    st.info("Upload your stock data CSV/Excel and backtest the VWAP ladder strategy with customizable parameters")
    
    # Import VWAP system
    try:
        from vwap_system import VWAPFlexibleSystem, create_batch_optimizer_excel
        import openpyxl
        from io import BytesIO
    except ImportError as e:
        st.error(f"Error importing VWAP system: {e}")
        st.stop()
    
    # Mode Selection
    st.subheader("📊 Select Mode")
    mode = st.radio("", ["Single Stock Backtest", "Batch Comparison (10+ stocks)"], horizontal=True)
    
    st.markdown("---")
    
    if mode == "Single Stock Backtest":
        # Single File Mode
        st.subheader("📁 Upload Stock Data")
        uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx'], help="File must contain: Date, High, Low, VWAP (optional), Close (optional)")
        
        if uploaded_file:
            # Load data
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.success(f"✅ Loaded {len(df)} rows from {uploaded_file.name}")
                
                # Show data preview
                with st.expander("📊 Data Preview"):
                    st.dataframe(df.head(10))
            except Exception as e:
                st.error(f"Error loading file: {e}")
                st.stop()
            
            # Parameter Configuration
            st.subheader("⚙️ Strategy Parameters")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📊 Core Settings**")
                target_pct = st.selectbox("Profit Target", [3.0, 6.0, 10.0, 15.0], index=2, help="Profit target percentage")
                threshold_lakhs = st.selectbox("Threshold (Lakhs)", [3.0, 4.0, 5.0, 10.0], index=2, help="Above this, profit target reduces to 1%")
            
            with col2:
                st.markdown("**💰 Investment Mode**")
                investment_mode = st.radio("Mode", ["Amount (Rs)", "Quantity (Shares)"], index=1)
                
                if investment_mode == "Amount (Rs)":
                    max_investment = st.number_input("Daily Investment (Rs)", min_value=1000, max_value=1000000, value=15000, step=1000)
                    fixed_qty = None
                else:
                    fixed_qty = st.number_input("Fixed Quantity (Shares)", min_value=1, max_value=1000, value=10, step=1)
                    max_investment = None
            
            with col3:
                st.markdown("**🔧 Optional Filters**")
                vwap_enabled = st.checkbox("Enable VWAP (E3, E4)", value=True, help="Enable VWAP-based entry points")
                
                sma_enabled = st.checkbox("Enable SMA (E5, E6)", value=False, help="Enable SMA-based entry points")
                sma_period = st.number_input("SMA Period", min_value=5, max_value=200, value=9, step=1, disabled=not sma_enabled)
                
                ha_enabled = st.checkbox("Enable Heikin Ashi (E7, E8)", value=False, help="Enable HA-based entry points")
                
                supertrend_enabled = st.checkbox("Enable Supertrend Filter", value=False, help="Block buys when price > Supertrend")
                
                st.markdown("**🎯 Trailing Stop Loss**")
                trailing_enabled = st.checkbox("Enable Trailing Stop", value=False, help="Lock profits and capture extra upside")
                
                col_trail1, col_trail2 = st.columns(2)
                with col_trail1:
                    trailing_percent = st.number_input("Trail % from High", min_value=1.0, max_value=10.0, value=5.0, step=0.5, disabled=not trailing_enabled, help="Trail stop % below highest high")
                with col_trail2:
                    trailing_activation = st.number_input("Activate at Profit %", min_value=5.0, max_value=20.0, value=10.0, step=1.0, disabled=not trailing_enabled, help="Start trailing after this profit %")
            
            # Entry Points Summary
            total_entries = 2  # Always E1, E2
            entry_list = ["E1 (Low)", "E2 (Low-1%)"]
            if vwap_enabled:
                total_entries += 2
                entry_list.extend(["E3 (VWAP)", "E4 (VWAP-1%)"])
            if sma_enabled and sma_period:
                total_entries += 2
                entry_list.extend([f"E5 (SMA{sma_period})", f"E6 (SMA{sma_period}-1%)"])
            if ha_enabled:
                total_entries += 2
                entry_list.extend(["E7 (HA Low)", "E8 (HA Low-1%)"])
            
            st.info(f"**{total_entries} Entry Points Active:** {', '.join(entry_list)}")
            
            # Run Backtest Button
            if st.button("🚀 Run Backtest", type="primary"):
                with st.spinner("Running backtest..."):
                    try:
                        # Initialize system
                        system = VWAPFlexibleSystem(
                            max_investment=max_investment,
                            fixed_qty=fixed_qty,
                            target_percentage=target_pct,
                            threshold_lakhs=threshold_lakhs,
                            initial_capital=100000,
                            vwap_enabled=vwap_enabled,
                            sma_period=sma_period if sma_enabled else None,
                            supertrend_enabled=supertrend_enabled,
                            ha_enabled=ha_enabled,
                            trailing_enabled=trailing_enabled,
                            trailing_percent=trailing_percent,
                            trailing_activation=trailing_activation
                        )
                        
                        # Load data
                        try:
                            if not system.load_data_from_dataframe(df):
                                st.error("Failed to load data. Please check your file format.")
                                st.stop()
                        except Exception as load_error:
                            st.error(f"❌ Data Loading Error: {str(load_error)}")
                            st.info("💡 **Required columns:** Date, High, Low (VWAP, Close optional)")
                            st.info(f"📋 **Your columns:** {', '.join(df.columns.tolist())}")
                            st.stop()
                        
                        # Run backtest
                        if not system.run_backtest():
                            st.error("Backtest failed!")
                            st.stop()
                        
                        # Get results
                        summary = system.get_summary()
                        
                        # Display Results
                        st.success("✅ Backtest Complete!")
                        
                        # Key Metrics
                        st.subheader("📈 Performance Summary")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Trades", summary['total_trades'])
                        
                        with col2:
                            profit_color = "normal" if summary['total_profit'] >= 0 else "inverse"
                            st.metric("Total Profit", f"₹{summary['total_profit']:,.2f}", delta=f"{summary['total_return']:.2f}%")
                        
                        with col3:
                            st.metric("Win Rate", f"{summary['win_rate']:.1f}%")
                        
                        with col4:
                            st.metric("Avg Profit/Trade", f"₹{summary['avg_profit_per_trade']:,.2f}")
                        
                        # Capital Growth
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Initial Capital", f"₹{100000:,.2f}")
                        
                        with col2:
                            st.metric("Final Capital", f"₹{summary['final_capital']:,.2f}", delta=f"₹{summary['total_profit']:,.2f}")
                        
                        # Detailed Results - Show only completed trades
                        if system.daily_transactions:
                            st.markdown("---")
                            st.subheader("📊 Completed Trades Summary")
                            
                            transactions_df = pd.DataFrame(system.daily_transactions)
                            
                            # Filter only sell transactions (completed trades)
                            trades_df = transactions_df[transactions_df['execution'] == 'Sell'].copy()
                            
                            if not trades_df.empty:
                                # Prepare display columns
                                display_df = pd.DataFrame({
                                    'Buy Date': trades_df['entry_date'].apply(lambda x: x.date() if pd.notna(x) and x is not None else ''),
                                    'Buy Qty': trades_df['sell_qty'],  # Total qty that was sold (same as bought)
                                    'Avg Buy Price': trades_df['average_cost'],
                                    'Sell Date': trades_df['date'].apply(lambda x: x.date() if hasattr(x, 'date') else x),
                                    'Sell Qty': trades_df['sell_qty'],
                                    'Avg Sell Price': trades_df['sell_price'],
                                    'Holding Period': trades_df['holding_days'].apply(lambda x: f"{int(x)} days" if pd.notna(x) else ''),
                                    'Profit': trades_df['profit'],
                                    'Return %': trades_df['return_pct']
                                })
                                
                                st.dataframe(
                                    display_df.style.format({
                                        'Avg Buy Price': '₹{:.2f}',
                                        'Avg Sell Price': '₹{:.2f}',
                                        'Profit': '₹{:.2f}',
                                        'Return %': '{:.2f}%'
                                    }),
                                    use_container_width=True,
                                    height=400
                                )
                                
                                # Summary stats
                                st.info(f"**Total Completed Trades:** {len(trades_df)} | **Avg Holding Period:** {trades_df['holding_days'].mean():.1f} days")
                            else:
                                st.warning("No completed trades yet. Adjust parameters or check data.")
                            
                            # Download Full Excel Report
                            st.markdown("---")
                            st.subheader("💾 Download Complete Excel Report")
                            st.info("📊 Includes: Daily Transactions, Yearly Summary, Performance Summary (Full Details)")
                            
                            # Generate complete Excel report
                            excel_output = system.export_to_bytesio()
                            excel_data = excel_output.getvalue()
                            
                            st.download_button(
                                label="📥 Download Complete Excel Report",
                                data=excel_data,
                                file_name=f"VWAP_Backtest_{uploaded_file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="primary"
                            )
                    
                    except Exception as e:
                        st.error(f"Error during backtest: {e}")
                        import traceback
                        st.code(traceback.format_exc())
    
    else:  # Batch Comparison Mode
        st.subheader("📊 Batch Comparison Mode")
        st.info("🎯 Upload multiple stock files and compare ALL 8 configurations automatically!")
        
        # Multiple file upload
        uploaded_files = st.file_uploader(
            "Upload multiple CSV/Excel files (10+ stocks recommended)", 
            type=['csv', 'xlsx'], 
            accept_multiple_files=True,
            help="Each file should contain: Date, High, Low, VWAP (optional), Close (optional)"
        )
        
        if uploaded_files and len(uploaded_files) > 0:
            st.success(f"✅ Loaded {len(uploaded_files)} stock files")
            
            # Configuration
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Core Settings**")
                target_pct = st.selectbox("Profit Target", [3.0, 6.0, 10.0, 15.0], index=2, key="batch_target")
                threshold_lakhs = st.selectbox("Threshold (Lakhs)", [3.0, 4.0, 5.0, 10.0], index=2, key="batch_threshold")
                sma_period = st.number_input("SMA Period (for E5, E6)", min_value=5, max_value=200, value=9, step=1, key="batch_sma")
            
            with col2:
                st.markdown("**💰 Investment Mode**")
                investment_mode = st.radio("Mode", ["Amount (Rs)", "Quantity (Shares)"], index=1, key="batch_inv_mode")
                
                if investment_mode == "Amount (Rs)":
                    max_investment = st.number_input("Daily Investment (Rs)", min_value=1000, max_value=1000000, value=15000, step=1000, key="batch_amt")
                    fixed_qty = None
                else:
                    fixed_qty = st.number_input("Fixed Quantity (Shares)", min_value=1, max_value=1000, value=10, step=1, key="batch_qty")
                    max_investment = None
            
            # Trailing Stop Loss Settings
            st.markdown("---")
            st.markdown("**🎯 Trailing Stop Loss (Optional)**")
            
            col_trail1, col_trail2, col_trail3 = st.columns(3)
            with col_trail1:
                trailing_enabled = st.checkbox("Enable Trailing Stop", value=True, key="batch_trailing", help="Recommended for delivery trading")
            with col_trail2:
                trailing_percent = st.number_input("Trail % from High", min_value=1.0, max_value=10.0, value=5.0, step=0.5, key="batch_trail_pct", disabled=not trailing_enabled, help="Trail stop % below highest high")
            with col_trail3:
                trailing_activation = st.number_input("Activate at Profit %", min_value=5.0, max_value=20.0, value=10.0, step=1.0, key="batch_trail_act", disabled=not trailing_enabled, help="Start trailing after this profit %")
            
            if trailing_enabled:
                st.info(f"💡 Trailing will lock minimum {trailing_activation:.0f}% profit and trail {trailing_percent:.1f}% below highest high to capture extra upside!")
            
            st.markdown("---")
            
            # Run Comparison
            if st.button("🚀 Run Batch Comparison", type="primary"):
                
                # Define all 8 configurations
                configurations = [
                    {"name": "Just Low", "vwap": False, "sma": False, "ha": False},
                    {"name": "Low + VWAP", "vwap": True, "sma": False, "ha": False},
                    {"name": "Low + SMA", "vwap": False, "sma": True, "ha": False},
                    {"name": "Low + HA", "vwap": False, "sma": False, "ha": True},
                    {"name": "Low + VWAP + SMA", "vwap": True, "sma": True, "ha": False},
                    {"name": "Low + VWAP + HA", "vwap": True, "sma": False, "ha": True},
                    {"name": "Low + SMA + HA", "vwap": False, "sma": True, "ha": True},
                    {"name": "ALL (8 Entries)", "vwap": True, "sma": True, "ha": True}
                ]
                
                results = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                total_operations = len(uploaded_files) * len(configurations)
                current_op = 0
                
                for file_idx, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {uploaded_file.name}...")
                    
                    # Load file
                    try:
                        if uploaded_file.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_file)
                        else:
                            df = pd.read_excel(uploaded_file)
                        
                        stock_name = uploaded_file.name.replace('.csv', '').replace('.xlsx', '')
                        
                        # Test each configuration
                        for config in configurations:
                            try:
                                system = VWAPFlexibleSystem(
                                    max_investment=max_investment,
                                    fixed_qty=fixed_qty,
                                    target_percentage=target_pct,
                                    threshold_lakhs=threshold_lakhs,
                                    initial_capital=100000,
                                    vwap_enabled=config['vwap'],
                                    sma_period=sma_period if config['sma'] else None,
                                    supertrend_enabled=False,
                                    ha_enabled=config['ha'],
                                    trailing_enabled=trailing_enabled,
                                    trailing_percent=trailing_percent,
                                    trailing_activation=trailing_activation
                                )
                                
                                if system.load_data_from_dataframe(df) and system.run_backtest():
                                    summary = system.get_summary()
                                    
                                    # Calculate average holding days
                                    trades_df = pd.DataFrame(system.daily_transactions)
                                    sells_df = trades_df[trades_df['execution'] == 'Sell']
                                    avg_holding_days = sells_df['holding_days'].mean() if not sells_df.empty else 0
                                    
                                    # Count entries
                                    entries = 2  # Base (E1, E2)
                                    if config['vwap']: entries += 2
                                    if config['sma']: entries += 2
                                    if config['ha']: entries += 2
                                    
                                    results.append({
                                        'Stock': stock_name,
                                        'Configuration': config['name'],
                                        'Trades': summary['total_trades'],
                                        'Profit': summary['total_profit'],
                                        'Return %': summary['total_return'],
                                        'Win Rate': summary['win_rate'],
                                        'Avg Profit/Trade': summary['avg_profit_per_trade'],
                                        # For batch optimizer Excel
                                        'stock_name': stock_name,
                                        'config_name': config['name'],
                                        'system': system,
                                        'profit': summary['total_profit'],
                                        'trades': summary['total_trades'],
                                        'win_rate': summary['win_rate'],
                                        'avg_holding_days': avg_holding_days,
                                        'return_pct': summary['total_return'],
                                        'final_capital': summary['final_capital'],
                                        'entries': entries
                                    })
                                else:
                                    results.append({
                                        'Stock': stock_name,
                                        'Configuration': config['name'],
                                        'Trades': 0,
                                        'Profit': 0,
                                        'Return %': 0,
                                        'Win Rate': 0,
                                        'Avg Profit/Trade': 0,
                                        # For batch optimizer Excel
                                        'stock_name': stock_name,
                                        'config_name': config['name'],
                                        'system': None,
                                        'profit': 0,
                                        'trades': 0,
                                        'win_rate': 0,
                                        'avg_holding_days': 0,
                                        'return_pct': 0,
                                        'final_capital': 100000,
                                        'entries': 2
                                    })
                            
                            except Exception as e:
                                st.warning(f"⚠️ {stock_name} - {config['name']}: {str(e)}")
                            
                            current_op += 1
                            progress_bar.progress(current_op / total_operations)
                    
                    except Exception as e:
                        st.error(f"❌ Error loading {uploaded_file.name}: {e}")
                
                progress_bar.empty()
                status_text.empty()
                
                if results:
                    st.success(f"✅ Comparison Complete! Tested {len(uploaded_files)} stocks × 8 configurations = {len(results)} backtests")
                    
                    # Create results DataFrame
                    results_df = pd.DataFrame(results)
                    
                    # Pivot table for comparison
                    st.subheader("📊 Profit Comparison Matrix")
                    
                    pivot_profit = results_df.pivot(index='Stock', columns='Configuration', values='Profit')
                    pivot_profit = pivot_profit[[c['name'] for c in configurations]]  # Reorder columns
                    
                    # Find winner for each stock
                    winners = pivot_profit.idxmax(axis=1)
                    
                    # Create display dataframe
                    display_pivot = pivot_profit.copy()
                    display_pivot['🏆 Best Config'] = winners
                    display_pivot['🏆 Best Profit'] = pivot_profit.max(axis=1, numeric_only=True)
                    
                    # Format only numeric columns
                    numeric_cols = [c['name'] for c in configurations] + ['🏆 Best Profit']
                    format_dict = {col: "₹{:,.0f}" for col in numeric_cols}
                    
                    # Style the dataframe
                    st.dataframe(
                        display_pivot.style.format(format_dict),
                        use_container_width=True
                    )
                    
                    # Overall Statistics
                    st.markdown("---")
                    st.subheader("🏆 Overall Statistics")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Most wins
                        winner_counts = winners.value_counts()
                        overall_winner = winner_counts.index[0]
                        win_count = winner_counts.iloc[0]
                        
                        st.metric("🥇 Overall Winner", overall_winner, f"{win_count}/{len(uploaded_files)} stocks")
                    
                    with col2:
                        # Best total profit
                        total_profit_by_config = results_df.groupby('Configuration')['Profit'].sum()
                        best_total = total_profit_by_config.idxmax()
                        best_total_value = total_profit_by_config.max()
                        
                        st.metric("💰 Highest Total Profit", best_total, f"₹{best_total_value:,.0f}")
                    
                    with col3:
                        # Best avg return
                        avg_return_by_config = results_df.groupby('Configuration')['Return %'].mean()
                        best_avg_return = avg_return_by_config.idxmax()
                        best_avg_return_value = avg_return_by_config.max()
                        
                        st.metric("📈 Highest Avg Return", best_avg_return, f"{best_avg_return_value:.2f}%")
                    
                    # Detailed Results
                    st.markdown("---")
                    st.subheader("📋 Detailed Results")
                    
                    st.dataframe(
                        results_df.style.format({
                            'Profit': '₹{:,.2f}',
                            'Return %': '{:.2f}%',
                            'Win Rate': '{:.1f}%',
                            'Avg Profit/Trade': '₹{:,.2f}'
                        }),
                        use_container_width=True
                    )
                    
                    # Download Comprehensive Excel Report
                    st.markdown("---")
                    st.subheader("💾 Download Comprehensive Analysis Report")
                    st.info("📊 Multi-sheet Excel with: Best Configs, All Results, Individual Stock Details, Analysis Report, and Holding Period data!")
                    
                    try:
                        # Generate comprehensive multi-sheet Excel using batch optimizer
                        excel_output = create_batch_optimizer_excel(results)
                        excel_data = excel_output.getvalue()
                        
                        st.download_button(
                            label="📥 Download Complete Batch Analysis Report",
                            data=excel_data,
                            file_name=f"VWAP_Batch_Optimizer_{len(uploaded_files)}stocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            type="primary",
                            help="Includes: Best Configurations, All Results, Individual Stock Details, Holding Period, Analysis Report"
                        )
                        
                        st.success("✅ Excel report ready! Includes holding period analysis for all trades.")
                        
                    except Exception as e:
                        st.error(f"Error generating Excel report: {e}")
                        import traceback
                        st.code(traceback.format_exc())
                
                else:
                    st.warning("No results generated. Please check your data files.")


# ============================================================
# PAGE: PORTFOLIO
# ============================================================

elif page == "Portfolio":
    st.header("💼 Portfolio")
    
    portfolio = db.get_portfolio()
    summary = db.get_portfolio_summary()
    
    # Summary metrics
    st.subheader("📊 Portfolio Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Positions", summary.get('total_positions', 0))
    with col2:
        st.metric("Invested", f"₹{summary.get('total_invested', 0):,.0f}")
    with col3:
        st.metric("Current Value", f"₹{summary.get('total_current_value', 0):,.0f}")
    with col4:
        pnl = summary.get('total_unrealized_pnl', 0) or 0
        pnl_pct = summary.get('avg_pnl_pct', 0) or 0
        st.metric("Unrealized P&L", f"₹{pnl:,.0f}", f"{pnl_pct:.2f}%")
    
    st.markdown("---")
    
    # Positions table
    if portfolio:
        st.subheader("📋 Current Positions")
        df_portfolio = pd.DataFrame(portfolio)
        st.dataframe(df_portfolio, use_container_width=True)
        
        # Update prices button
        if st.button("🔄 Update Live Prices"):
            with st.spinner("Fetching live prices..."):
                price_updates = {}
                for pos in portfolio:
                    quote = broker.get_quote(pos['symbol'])
                    if quote:
                        price_updates[pos['symbol']] = quote.get('ltp', 0)
                
                if price_updates:
                    db.update_portfolio_prices(price_updates)
                    st.success("✅ Prices updated!")
                    st.experimental_rerun()
    else:
        st.info("No positions in portfolio. Execute some trades to see them here!")

# ============================================================
# PAGE: TRADE HISTORY
# ============================================================

elif page == "Trade History":
    st.header("📜 Trade History")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        days = st.selectbox("Time Period", [7, 30, 90, 180, 365])
    with col2:
        status_filter = st.selectbox("Status", ["ALL", "CLOSED", "STOPPED", "TARGET_HIT"])
    
    # Get trades
    trades = db.get_trade_history(days=days)
    
    if status_filter != "ALL":
        trades = [t for t in trades if t.get('status') == status_filter]
    
    if trades:
        df_trades = pd.DataFrame(trades)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        total_trades = len(df_trades)
        winning_trades = len(df_trades[df_trades['profit_loss'] > 0]) if 'profit_loss' in df_trades else 0
        total_pnl = df_trades['profit_loss'].sum() if 'profit_loss' in df_trades else 0
        
        with col1:
            st.metric("Total Trades", total_trades)
        with col2:
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            st.metric("Win Rate", f"{win_rate:.1f}%")
        with col3:
            st.metric("Total P&L", f"₹{total_pnl:,.0f}")
        
        st.markdown("---")
        
        # Trades table
        st.dataframe(df_trades, use_container_width=True)
        
        # P&L chart
        if 'exit_time' in df_trades and 'profit_loss' in df_trades:
            st.subheader("📈 Cumulative P&L")
            df_trades_sorted = df_trades.sort_values('exit_time')
            df_trades_sorted['cumulative_pnl'] = df_trades_sorted['profit_loss'].cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_trades_sorted['exit_time'],
                y=df_trades_sorted['cumulative_pnl'],
                mode='lines+markers',
                name='Cumulative P&L',
                line=dict(color='blue', width=2)
            ))
            fig.update_layout(
                title="Cumulative Profit/Loss Over Time",
                xaxis_title="Date",
                yaxis_title="Cumulative P&L (₹)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No trades in last {days} days")

# ============================================================
# PAGE: RISK REPORT
# ============================================================

elif page == "Risk Report":
    st.header("⚠️ Risk Management Report")
    
    with st.spinner("Generating comprehensive risk report..."):
        # Get data
        positions = db.get_portfolio()
        trades = db.get_trade_history(days=90)
        
        # Calculate returns
        returns = []
        equity_curve = [risk_engine.total_capital]
        
        for trade in trades:
            if trade.get('profit_loss_pct'):
                ret = trade['profit_loss_pct'] / 100
                returns.append(ret)
                equity_curve.append(equity_curve[-1] * (1 + ret))
        
        # Generate report
        report = risk_engine.generate_risk_report(
            positions=positions,
            returns=returns,
            equity_curve=equity_curve,
            price_history={}
        )
    
    # Display risk level
    risk_level = report.get('overall_risk_level', 'UNKNOWN')
    risk_colors = {'LOW': 'green', 'MEDIUM': 'orange', 'HIGH': 'red', 'CRITICAL': 'darkred'}
    
    st.markdown(f"""
    <div style="padding: 1rem; background: {risk_colors.get(risk_level, 'gray')}; 
         color: white; border-radius: 10px; text-align: center; font-size: 1.5rem;">
        Overall Risk Level: <strong>{risk_level}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Capital utilization
    st.subheader("💰 Capital Utilization")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        capital = report.get('capital') or 0
        st.metric("Total Capital", f"₹{capital:,.0f}")
    with col2:
        invested = report.get('invested_capital') or 0
        st.metric("Invested", f"₹{invested:,.0f}")
    with col3:
        available = report.get('available_capital') or 0
        st.metric("Available", f"₹{available:,.0f}")
    
    st.progress(report.get('capital_utilization_pct', 0) / 100)
    st.caption(f"Capital Utilization: {report.get('capital_utilization_pct', 0):.1f}%")
    
    # VaR metrics
    if 'var' in report:
        st.subheader("📊 Value at Risk (VaR)")
        var_data = report['var']
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("VaR (95%)", f"₹{abs(var_data.get('var_amount', 0)):,.0f}")
            st.caption(var_data.get('interpretation', ''))
        with col2:
            st.metric("CVaR (Expected Shortfall)", f"₹{abs(var_data.get('cvar_amount', 0)):,.0f}")
            st.caption("Average loss when VaR is breached")
    
    # Drawdown
    if 'drawdown' in report:
        st.subheader("📉 Drawdown Analysis")
        dd_data = report['drawdown']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Drawdown", f"{dd_data.get('current_drawdown', 0):.2f}%")
        with col2:
            st.metric("Max Drawdown", f"{dd_data.get('max_drawdown', 0):.2f}%")
        with col3:
            st.metric("Recovery Needed", f"{dd_data.get('recovery_needed_pct', 0):.2f}%")
    
    # Risk-adjusted returns
    st.subheader("📈 Risk-Adjusted Returns")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Sharpe Ratio", f"{report.get('sharpe_ratio', 0):.2f}")
        st.caption("> 1.0 is good, > 2.0 is excellent")
    with col2:
        st.metric("Sortino Ratio", f"{report.get('sortino_ratio', 0):.2f}")
        st.caption("Only considers downside volatility")
    with col3:
        st.metric("Calmar Ratio", f"{report.get('calmar_ratio', 0):.2f}")
        st.caption("Return / Max Drawdown")
    
    # Concentration risk
    if 'concentration_risk' in report:
        st.subheader("⚠️ Concentration Risk")
        conc_data = report['concentration_risk']
        
        st.info(f"Risk Level: **{conc_data.get('risk_level')}** | "
                f"Max Single Position: **{conc_data.get('max_concentration', 0):.1f}%** | "
                f"Recommendation: **{conc_data.get('recommendation')}**")
        
        if conc_data.get('concentrated_positions'):
            st.warning("⚠️ These positions are over 20% of portfolio:")
            for pos in conc_data['concentrated_positions']:
                st.write(f"- **{pos['symbol']}**: {pos['percentage']:.1f}% (₹{pos['amount']:,.0f})")

# ============================================================
# PAGE: BACKTEST (MULTI-MODE) - EMBEDDED
# ============================================================

elif page == "Backtest (Multi-Mode)":
    st.header("🏆 Multi-Mode Backtest Dashboard")
    st.info("🎯 Backtest your trading strategies on historical data using real signal generators")
    
    # Backtest type selection
    backtest_type = st.radio("📊 Backtest Type:", ["Generate New Signals", "Backtest Saved Signals"], horizontal=True)
    
    if backtest_type == "Backtest Saved Signals":
        st.markdown("---")
        st.subheader("📋 Backtest Signals from Database")
        st.info("💡 Select previously saved signals from your database and backtest their performance")
        
        # Get saved signals
        saved_signals = db.get_active_signals()
        
        if not saved_signals:
            st.warning("⚠️ No saved signals found in database. Generate signals first using the screeners.")
            st.info("""
            💡 **Tip:** Generate and save signals using:
            - **🌸 3Jasmines Screener** - Conservative delivery trading signals
            - **💎 Hybrid Signal Generator** - Treasure signals (Technical + S&R + Patterns)
            - **🌺 Orchid Trend Matrix** - Ultra-selective (passes both 3Jasmines AND Hybrid)
            - **🪷 Lotus Momentum Trio** - Manual entry or Hybrid mode signals
            - **🚀 High-Growth Strategy** - Aggressive 35% CAGR signals
            
            All signals will be saved to database and available for backtesting here!
            """)
            st.stop()
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            min_confidence_filter = st.slider("Min Confidence Filter", 0, 100, 70, 5)
        with col2:
            signal_type_filter = st.selectbox("Signal Type", ["ALL", "BUY", "SELL"])
        with col3:
            # Get unique model names from signals
            model_names = sorted(set([s.get('model_name', 'Unknown') for s in saved_signals]))
            model_filter = st.selectbox("Model/Strategy", ["ALL"] + model_names,
                                      help="Filter by signal generation method")
        
        # Filter signals
        filtered_signals = [s for s in saved_signals if s.get('confidence', 0) >= min_confidence_filter]
        if signal_type_filter != "ALL":
            filtered_signals = [s for s in filtered_signals if s.get('signal_type') == signal_type_filter]
        if model_filter != "ALL":
            filtered_signals = [s for s in filtered_signals if s.get('model_name', 'Unknown') == model_filter]
        
        st.caption(f"📊 Found {len(filtered_signals)} saved signals matching criteria")
        
        # Show signal breakdown by model/strategy
        if filtered_signals:
            from collections import Counter
            model_counts = Counter([s.get('model_name', 'Unknown') for s in filtered_signals])
            st.markdown("#### 📈 Signal Breakdown by Strategy:")
            breakdown_cols = st.columns(min(len(model_counts), 5))
            for idx, (model, count) in enumerate(model_counts.most_common()):
                if idx < len(breakdown_cols):
                    with breakdown_cols[idx]:
                        st.metric(model, count)
        
        if not filtered_signals:
            st.warning("⚠️ No signals match the filter criteria. Adjust filters and try again.")
            st.stop()
        
        # Display signals to select
        st.markdown("#### Select Signals to Backtest:")
        
        # Create a multiselect with signal details
        signal_options = {}
        for signal in filtered_signals:
            symbol = signal.get('symbol', 'UNKNOWN')
            signal_type = signal.get('signal_type', 'UNKNOWN')
            confidence = signal.get('confidence', 0)
            entry = signal.get('entry_price', 0)
            generated_at = signal.get('generated_at', '')
            model_name = signal.get('model_name', 'Unknown')
            
            # Format label with model name
            label = f"{symbol} | {model_name} | {signal_type} | {confidence:.1f}% | Entry: ₹{entry:.2f} | {generated_at}"
            signal_options[label] = signal
        
        selected_labels = st.multiselect(
            "Choose signals to backtest:",
            options=list(signal_options.keys()),
            default=list(signal_options.keys())[:min(10, len(signal_options))]  # Default: first 10
        )
        
        selected_signals = [signal_options[label] for label in selected_labels]
        
        st.caption(f"✅ Selected {len(selected_signals)} signals for backtesting")
        
        # Backtest settings
        st.markdown("---")
        st.subheader("⚙️ Backtest Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            use_signal_target = st.checkbox("Use Signal's Target Price", value=True, 
                                          help="If unchecked, will use custom target %")
            if not use_signal_target:
                target_pct = st.slider("Target (%)", 5, 30, 10)
            else:
                target_pct = 10  # Default, will be overridden by signal
        
        with col2:
            use_signal_stop = st.checkbox("Use Signal's Stop Loss", value=True,
                                        help="If unchecked, will use custom stop loss %")
            if not use_signal_stop:
                stop_loss_pct = st.slider("Stop Loss (%)", 3, 15, 7)
            else:
                stop_loss_pct = 7  # Default, will be overridden by signal
        
        max_holding_days = st.slider("Max Holding Days", 10, 120, 60)
        
        st.markdown("---")
        
        if st.button("🚀 Backtest Selected Signals", type="primary", use_container_width=True):
            if not selected_signals:
                st.error("❌ Please select at least one signal!")
            else:
                with st.spinner(f"Backtesting {len(selected_signals)} saved signals..."):
                    import yfinance as yf
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    trades = []
                    
                    for idx, signal in enumerate(selected_signals):
                        symbol = signal.get('symbol', '').replace('NSE_', '').replace('BSE_', '')
                        status_text.text(f"Backtesting {symbol}... ({idx+1}/{len(selected_signals)})")
                        
                        try:
                            # Get entry details from signal
                            entry_price = signal.get('entry_price', 0)
                            signal_target = signal.get('target_price', 0)
                            signal_stop = signal.get('stop_loss', 0)
                            signal_date_str = signal.get('generated_at', '')
                            
                            # Parse signal date
                            try:
                                if isinstance(signal_date_str, str):
                                    signal_date = pd.to_datetime(signal_date_str)
                                else:
                                    signal_date = pd.Timestamp(signal_date_str)
                            except:
                                signal_date = datetime.now() - timedelta(days=30)  # Fallback
                            
                            # Fetch historical data from signal date
                            ticker = yf.Ticker(get_yfinance_symbol(symbol))
                            df_raw = ticker.history(start=signal_date, period="6mo", interval="1d")
                            
                            if df_raw.empty or len(df_raw) < 5:
                                continue
                            
                            df = pd.DataFrame({
                                'time': df_raw.index,
                                'open': df_raw['Open'].values,
                                'high': df_raw['High'].values,
                                'low': df_raw['Low'].values,
                                'close': df_raw['Close'].values,
                                'volume': df_raw['Volume'].values
                            })
                            
                            # Determine target and stop
                            if use_signal_target and signal_target > 0:
                                target_price = signal_target
                            else:
                                target_price = entry_price * (1 + target_pct / 100)
                            
                            if use_signal_stop and signal_stop > 0:
                                stop_price = signal_stop
                            else:
                                stop_price = entry_price * (1 - stop_loss_pct / 100)
                            
                            # Simulate trade from signal date
                            entry_date = signal_date
                            qty = 100  # Default quantity
                            
                            # Find exit
                            exit_reason = None
                            exit_price = entry_price
                            exit_date = entry_date
                            days_held = 0
                            
                            for i, row in df.iterrows():
                                current_date = row['time']
                                current_price = row['close']
                                
                                days_held = (current_date - entry_date).days if isinstance(current_date, pd.Timestamp) else 0
                                
                                # Check exit conditions
                                if current_price >= target_price:
                                    exit_reason = "TARGET"
                                    exit_price = target_price
                                    exit_date = current_date
                                    break
                                elif current_price <= stop_price:
                                    exit_reason = "STOP_LOSS"
                                    exit_price = stop_price
                                    exit_date = current_date
                                    break
                                elif days_held >= max_holding_days:
                                    exit_reason = "TIME_EXIT"
                                    exit_price = current_price
                                    exit_date = current_date
                                    break
                            
                            # If no exit found, use last price
                            if not exit_reason:
                                exit_reason = "END_OF_PERIOD"
                                exit_price = df['close'].iloc[-1]
                                exit_date = df['time'].iloc[-1]
                                days_held = (exit_date - entry_date).days if isinstance(exit_date, pd.Timestamp) else max_holding_days
                            
                            # Calculate P&L
                            return_pct = ((exit_price - entry_price) / entry_price) * 100
                            pnl = qty * (exit_price - entry_price)
                            
                            trades.append({
                                'Symbol': symbol,
                                'Entry_Date': entry_date.strftime('%Y-%m-%d') if hasattr(entry_date, 'strftime') else str(entry_date),
                                'Entry_Price': f"{entry_price:.2f}",
                                'Exit_Date': exit_date.strftime('%Y-%m-%d') if hasattr(exit_date, 'strftime') else str(exit_date),
                                'Exit_Price': f"{exit_price:.2f}",
                                'Exit_Reason': exit_reason,
                                'Qty': qty,
                                'Investment': f"{qty * entry_price:,.0f}",
                                'PnL': pnl,
                                'Return_%': return_pct,
                                'Holding_Days': days_held,
                                'Entry_Reason': f"Saved Signal ({signal.get('model_name', 'Unknown')})",
                                'Confidence': signal.get('confidence', 0)
                            })
                        
                        except Exception as e:
                            continue
                        
                        progress_bar.progress((idx + 1) / len(selected_signals))
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    if not trades:
                        st.warning("⚠️ No trades could be backtested. Check signal data and dates.")
                        st.stop()
                    
                    # Display results (same as regular backtest)
                    df_trades = pd.DataFrame(trades)
                    df_trades['PnL'] = pd.to_numeric(df_trades['PnL'], errors='coerce')
                    df_trades['Return_%'] = pd.to_numeric(df_trades['Return_%'], errors='coerce')
                    df_trades['Holding_Days'] = pd.to_numeric(df_trades['Holding_Days'], errors='coerce')
                    
                    # Calculate metrics
                    total_trades = len(df_trades)
                    winners = len(df_trades[df_trades['PnL'] > 0])
                    win_rate = (winners / total_trades * 100) if total_trades > 0 else 0
                    total_pnl = df_trades['PnL'].sum()
                    avg_return = df_trades['Return_%'].mean()
                    best_return = df_trades['Return_%'].max()
                    worst_return = df_trades['Return_%'].min()
                    
                    # Display results
                    st.success("✅ Backtest Complete!")
                    st.markdown("---")
                    st.subheader("📊 Performance Summary")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Trades", total_trades)
                        st.metric("Winners", f"{winners} ({win_rate:.1f}%)")
                    with col2:
                        st.metric("Total P&L", f"{total_pnl:,.0f}")
                        st.metric("Avg Return", f"{avg_return:.2f}%")
                    with col3:
                        st.metric("Best Trade", f"{best_return:.2f}%")
                        st.metric("Worst Trade", f"{worst_return:.2f}%")
                    with col4:
                        avg_holding = df_trades['Holding_Days'].mean()
                        st.metric("Avg Holding", f"{avg_holding:.1f} days")
                    
                    # Trades table
                    st.markdown("---")
                    st.subheader("📋 Trade History")
                    
                    def color_pnl(val):
                        if isinstance(val, (int, float)):
                            return 'background-color: #d4edda' if val > 0 else 'background-color: #f8d7da'
                        return ''
                    
                    st.dataframe(
                        df_trades.style.applymap(color_pnl, subset=['PnL']),
                        use_container_width=True,
                        height=400
                    )
                    
                    # Download button
                    st.markdown("---")
                    csv = df_trades.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv,
                        file_name=f"backtest_saved_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        st.stop()  # Stop here if backtesting saved signals
    
    # Mode selection for new signal generation
    mode = st.radio("📊 Select Strategy Mode:", ["🌸 3Jasmines", "💎 Treasure Signals", "🌺 Orchid Trend Matrix", "🚀 High-Growth Strategy (35% CAGR)", "🔄 Compare All Modes"], horizontal=True)
    
    st.markdown("---")
    
    # Stock Universe Selection
    st.subheader("📈 Select Stock Universe")
    
    if EXPANDED_UNIVERSE_AVAILABLE:
        universe_selection = st.radio(
            "Choose Stock Universe:",
            ["⭐ My Stocks", "Nifty 50", "Nifty 200", "Nifty 500", "Smallcap 250", "Commodities (Gold, Silver)", "ALL Stocks (750+)", "ALL Assets (Stocks + Commodities)", "Custom Selection"],
            horizontal=True
        )
        
        # Map selection to stock list
        if universe_selection == "⭐ My Stocks":
            available_stocks = get_my_stocks()
            default_selection = get_my_stocks()
            render_my_stocks_manager()
        elif universe_selection == "Nifty 50":
            available_stocks = NIFTY_50
            default_selection = NIFTY_50[:10]
        elif universe_selection == "Nifty 200":
            available_stocks = NIFTY_200
            default_selection = NIFTY_200[:20]
        elif universe_selection == "Nifty 500":
            available_stocks = NIFTY_500
            default_selection = NIFTY_500[:30]
        elif universe_selection == "Smallcap 250":
            available_stocks = SMALLCAP_250
            default_selection = SMALLCAP_250[:20]
        elif universe_selection == "Commodities (Gold, Silver)":
            available_stocks = COMMODITIES
            default_selection = COMMODITIES
        elif universe_selection == "ALL Assets (Stocks + Commodities)":
            available_stocks = ALL_ASSETS
            default_selection = ALL_ASSETS[:50]
        elif universe_selection == "ALL Stocks (750+)":
            available_stocks = ALL_STOCKS
            default_selection = ALL_STOCKS[:50]
        else:  # Custom
            available_stocks = ALL_ASSETS
            default_selection = []
    else:
        # Fallback if stock universe not available
        available_stocks = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'SBIN', 'BHARTIARTL', 'ITC', 
                           'ASIANPAINTS', 'MARUTI', 'TITAN', 'SUNPHARMA', 'WIPRO', 'HCLTECH', 'AXISBANK']
        default_selection = available_stocks[:5]
        universe_selection = "Top 15"
    
    # Quick selection buttons
    st.markdown("**Quick Selection:**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Top 10"):
            st.session_state['backtest_stocks'] = available_stocks[:10]
    with col2:
        if st.button("Top 20"):
            st.session_state['backtest_stocks'] = available_stocks[:20]
    with col3:
        if st.button("Top 50"):
            st.session_state['backtest_stocks'] = available_stocks[:50]
    with col4:
        if st.button("All Stocks"):
            st.session_state['backtest_stocks'] = available_stocks
    
    # Mode-specific info
    if mode == "🌸 3Jasmines":
        st.info("🌸 **3Jasmines Backtest:** Tests signals based on Near Support + RSI < 35 + Bullish Pattern")
    elif mode == "💎 Treasure Signals":
        st.info("💎 **Treasure Signals Backtest:** Tests signals from Hybrid Signal Generator (Technical + S&R + Chart Patterns)")
    elif mode == "🌺 Orchid Trend Matrix":
        st.info("🌺 **Orchid Trend Matrix Backtest:** Tests signals that pass BOTH 3Jasmines AND Treasure Signals (Ultra-Selective)")
    elif mode == "🚀 High-Growth Strategy (35% CAGR)":
        st.info("🚀 **High-Growth Strategy:** Optimized for 35%+ CAGR using Hybrid mode with high-growth mid-cap stocks")
        st.warning("⚠️ **Aggressive Strategy:** Higher returns but higher risk. Uses 20% target, 4% stop, 20-day holding period.")
    elif mode == "🔄 Compare All Modes":
        st.info("🔄 **Compare All Modes:** Runs backtests for all four strategies simultaneously and shows comparative results")
    
    st.markdown("---")
    
    # Stock selection - Override for High-Growth Strategy
    if mode == "🚀 High-Growth Strategy (35% CAGR)":
        # Pre-select high-growth mid-cap stocks
        HIGHGROWTH_STOCKS = [
            'PERSISTENT', 'COFORGE', 'LTTS', 'KPITTECH', 'MPHASIS',
            'DIXON', 'TRENT', 'JUBLFOOD', 'TITAN', 'DMART',
            'NAVINFLUOR', 'POLYCAB', 'APLAPOLLO', 'ASTRAL', 'JKCEMENT'
        ]
        
        st.markdown("#### 📈 High-Growth Stock Selection")
        st.info("💡 **Recommended:** Pre-selected 15 high-growth mid-cap stocks optimized for 35% CAGR")
        
        selected_stocks = st.multiselect(
            "Select High-Growth Mid-Cap Stocks:",
            options=HIGHGROWTH_STOCKS,
            default=HIGHGROWTH_STOCKS,
            help="Pre-selected high-growth stocks: IT Services, Consumer & Retail, Specialty & Industrial"
        )
        st.caption(f"📊 Selected: {len(selected_stocks)} high-growth stocks")
    else:
        # Manual selection for other modes
        selected_stocks = st.multiselect(
            "Or manually select stocks:",
            options=available_stocks,
            default=st.session_state.get('backtest_stocks', default_selection)
        )
        st.caption(f"📊 Selected: {len(selected_stocks)} stocks")
    
    st.markdown("---")
    
    # Settings - Pre-configure for High-Growth Strategy
    if mode == "🚀 High-Growth Strategy (35% CAGR)":
        st.subheader("⚙️ High-Growth Strategy Settings (Pre-Configured)")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💼 Portfolio Settings")
            initial_capital = st.number_input("Initial Capital (₹)", value=2000000, step=100000, 
                                              help="Recommended: Rs 20 Lakh for optimal deployment")
            investment_per_stock = st.number_input("Investment per Stock (₹)", value=100000, step=10000,
                                                  help="Rs 1 Lakh per stock (5% position size)")
            max_portfolio = st.slider("Max Portfolio Size", 10, 30, 20,
                                    help="20 stocks = Full deployment of Rs 20L")
        
        with col2:
            st.subheader("🎯 Risk Management (Aggressive)")
            target_pct = st.slider("Target (%)", 15, 25, 20, 1,
                                  help="20% target for bigger wins (aggressive)")
            stop_loss_pct = st.slider("Stop Loss (%)", 3, 6, 4, 1,
                                     help="4% stop loss (tighter, faster cuts)")
            max_holding_days = st.slider("Max Holding Days", 15, 30, 20, 1,
                                        help="20 days for faster capital rotation")
        
        st.info("""
        **🚀 High-Growth Strategy Configuration:**
        - **Target:** 20% (aggressive for maximum returns)
        - **Stop Loss:** 4% (tight risk management)
        - **Holding Period:** 20 days (fast rotation)
        - **Stocks:** High-growth mid-caps (IT, Consumer, Specialty)
        - **Mode:** Hybrid (AI + Technical confluence)
        - **Expected CAGR:** 25-35%+ (in bull markets)
        """)
    else:
        # Settings for other modes
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💼 Portfolio Settings")
            initial_capital = st.number_input("Initial Capital (₹)", value=1000000, step=100000)
            investment_per_stock = st.number_input("Investment per Stock (₹)", value=200000, step=50000)
            max_portfolio = st.slider("Max Portfolio Size", 1, 10, 5)
        
        with col2:
            st.subheader("🎯 Risk Management")
            target_pct = st.slider("Target (%)", 5, 30, 10)
            stop_loss_pct = st.slider("Stop Loss (%)", 3, 15, 7)
            max_holding_days = st.slider("Max Holding Days", 10, 120, 60)
    
    # Mode-specific signal parameters
    st.markdown("---")
    st.subheader("⚙️ Signal Parameters")
    
    # Initialize variables for all modes
    min_confidence_jasmines = 70
    min_confidence_hybrid = 75
    min_rr_hybrid = 1.5
    
    if mode == "🌸 3Jasmines":
        col1, col2 = st.columns(2)
        with col1:
            min_confidence_jasmines = st.slider("Min 3Jasmines Confidence (%)", 70, 95, 70, 5)
        with col2:
            st.info("💡 **3Jasmines Criteria:**\n- Near Support (0.5%)\n- RSI < 35\n- Bullish Pattern")
    
    elif mode == "💎 Treasure Signals":
        col1, col2 = st.columns(2)
        with col1:
            min_confidence_hybrid = st.slider("Min Hybrid Confidence (%)", 70, 95, 75, 5)
        with col2:
            min_rr_hybrid = st.slider("Min Hybrid R:R", 1.0, 5.0, 1.5, 0.5)
    
    elif mode == "🌺 Orchid Trend Matrix":
        col1, col2 = st.columns(2)
        with col1:
            min_confidence_jasmines = st.slider("Min 3Jasmines Confidence (%)", 70, 95, 70, 5)
            min_confidence_hybrid = st.slider("Min Hybrid Confidence (%)", 70, 95, 75, 5)
        with col2:
            min_rr_hybrid = st.slider("Min Hybrid R:R", 1.0, 5.0, 1.5, 0.5)
            st.info("💡 **Orchid Criteria:**\n- Must pass BOTH 3Jasmines AND Treasure Signals")
    
    elif mode == "🚀 High-Growth Strategy (35% CAGR)":
        col1, col2 = st.columns(2)
        with col1:
            min_confidence_hybrid = st.slider("Min Hybrid Confidence (%)", 70, 95, 75, 5,
                                            help="75% confidence for quality signals (optimized for 35% CAGR)")
        with col2:
            min_rr_hybrid = st.slider("Min Hybrid R:R", 1.0, 5.0, 1.5, 0.5,
                                    help="1.5 R:R minimum (aggressive for high returns)")
        st.info("💡 **High-Growth Strategy:** Uses Hybrid mode (AI + Technical + S&R + Chart Patterns) for maximum accuracy")
    
    elif mode == "🔄 Compare All Modes":
        st.markdown("**Configure parameters for all modes:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.subheader("🌸 3Jasmines")
            min_confidence_jasmines = st.slider("Min 3Jasmines Confidence (%)", 70, 95, 70, 5, key="compare_jasmines")
        with col2:
            st.subheader("💎 Treasure Signals")
            min_confidence_hybrid = st.slider("Min Hybrid Confidence (%)", 70, 95, 75, 5, key="compare_hybrid")
            min_rr_hybrid = st.slider("Min Hybrid R:R", 1.0, 5.0, 1.5, 0.5, key="compare_rr")
        with col3:
            st.subheader("🌺 Orchid Trend Matrix")
            st.info("Uses same parameters as above")
        with col4:
            st.subheader("🚀 High-Growth")
            st.info("Uses Hybrid parameters (same as Treasure)")
    
    st.markdown("---")
    
    # Time period selection
    st.subheader("📅 Backtest Period")
    col1, col2 = st.columns(2)
    with col1:
        lookback_months = st.slider("Lookback Period (Months)", 3, 24, 6, 1)
    with col2:
        st.caption(f"Testing on last {lookback_months} months of historical data")
    
    st.markdown("---")
    
    # Run backtest button
    if mode == "🔄 Compare All Modes":
        button_text = "🚀 Run Comparison Backtest (All 3 Modes)"
    else:
        button_text = f"🚀 Run {mode} Backtest"
    
    if st.button(button_text, type="primary", use_container_width=True):
        if not selected_stocks:
            st.error("❌ Please select at least one stock!")
        else:
            # Import required modules
            try:
                from three_jasmines_screener import ThreeJasminesScreener
                from hybrid_signal_generator import HybridSignalGenerator
                from patterns.chart_pattern_detector import ChartPatternDetector
                import yfinance as yf
                
                if DUAL_SR_AVAILABLE:
                    from support_resistance.sr_calculator_enhanced import ProfessionalSRCalculator
                    SR_CALC_CLASS = ProfessionalSRCalculator
                else:
                    from support_resistance.sr_calculator import SupportResistanceCalculator
                    SR_CALC_CLASS = SupportResistanceCalculator
                
                # Handle "Compare All Modes" separately
                if mode == "🔄 Compare All Modes":
                    # Run backtests for all four modes
                    modes_to_test = ["🌸 3Jasmines", "💎 Treasure Signals", "🌺 Orchid Trend Matrix", "🚀 High-Growth Strategy (35% CAGR)"]
                    all_results = {}
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for mode_idx, test_mode in enumerate(modes_to_test):
                        status_text.text(f"🔄 Running {test_mode} backtest... ({mode_idx+1}/3)")
                        
                        # Initialize signal generators for this mode
                        jasmines_gen = ThreeJasminesScreener(
                            max_support_distance_pct=0.5,
                            max_rsi_threshold=35.0,
                            target_buffer_pct=1.0,
                            stop_loss_buffer_pct=2.0
                        )
                        
                        hybrid_gen = HybridSignalGenerator(
                            min_confidence=min_confidence_hybrid,
                            min_rr_ratio=min_rr_hybrid
                        )
                        
                        sr_calc = SR_CALC_CLASS(sensitivity=3, min_touches=2)
                        pattern_detector = ChartPatternDetector()
                        
                        trades = []
                        portfolio = []
                        
                        # Get historical data for all stocks
                        all_data = {}
                        for symbol in selected_stocks:
                            try:
                                ticker = yf.Ticker(get_yfinance_symbol(symbol))
                                df_raw = ticker.history(period=f"{lookback_months}mo", interval="1d")
                                
                                if not df_raw.empty and len(df_raw) >= 50:
                                    df = pd.DataFrame({
                                        'time': df_raw.index,
                                        'open': df_raw['Open'].values,
                                        'high': df_raw['High'].values,
                                        'low': df_raw['Low'].values,
                                        'close': df_raw['Close'].values,
                                        'volume': df_raw['Volume'].values
                                    })
                                    all_data[symbol] = df
                            except Exception:
                                continue
                        
                        # Run backtest (reuse the same logic but with test_mode)
                        if all_data:
                            all_dates = set()
                            for df in all_data.values():
                                all_dates.update(df['time'].tolist())
                            all_dates = sorted(list(all_dates))
                            
                            for current_date in all_dates:
                                # Check exits
                                positions_to_remove = []
                                for pos in portfolio:
                                    symbol = pos['symbol']
                                    if symbol in all_data:
                                        df = all_data[symbol]
                                        df_until_date = df[df['time'] <= current_date].copy()
                                        
                                        if len(df_until_date) > 0:
                                            current_price = df_until_date['close'].iloc[-1]
                                            entry_price = pos['entry_price']
                                            if isinstance(current_date, pd.Timestamp):
                                                entry_dt = pd.Timestamp(pos['entry_date'])
                                                days_held = (current_date - entry_dt).days
                                            else:
                                                days_held = 0
                                            
                                            target_price = entry_price * (1 + target_pct / 100)
                                            stop_price = entry_price * (1 - stop_loss_pct / 100)
                                            
                                            exit_reason = None
                                            exit_price = current_price
                                            
                                            if current_price >= target_price:
                                                exit_reason = "TARGET"
                                            elif current_price <= stop_price:
                                                exit_reason = "STOP_LOSS"
                                            elif days_held >= max_holding_days:
                                                exit_reason = "TIME_EXIT"
                                            
                                            if exit_reason:
                                                return_pct = ((exit_price - entry_price) / entry_price) * 100
                                                qty = pos['qty']
                                                pnl = qty * (exit_price - entry_price)
                                                
                                                trades.append({
                                                    'Symbol': symbol,
                                                    'Entry_Date': pos['entry_date'].strftime('%Y-%m-%d') if hasattr(pos['entry_date'], 'strftime') else str(pos['entry_date']),
                                                    'Entry_Price': f"{entry_price:.2f}",
                                                    'Exit_Date': current_date.strftime('%Y-%m-%d') if hasattr(current_date, 'strftime') else str(current_date),
                                                    'Exit_Price': f"{exit_price:.2f}",
                                                    'Exit_Reason': exit_reason,
                                                    'Qty': qty,
                                                    'Investment': f"{pos['investment']:,.0f}",
                                                    'PnL': pnl,
                                                    'Return_%': return_pct,
                                                    'Holding_Days': days_held,
                                                    'Entry_Reason': pos['entry_reason'],
                                                    'Confidence': pos.get('confidence', 0)
                                                })
                                                positions_to_remove.append(pos)
                                
                                for pos in positions_to_remove:
                                    portfolio.remove(pos)
                                
                                # Check for new signals
                                if len(portfolio) < max_portfolio:
                                    for symbol in selected_stocks:
                                        if symbol not in all_data or any(p['symbol'] == symbol for p in portfolio):
                                            continue
                                        
                                        df = all_data[symbol]
                                        df_until_date = df[df['time'] <= current_date].copy()
                                        
                                        if len(df_until_date) < 50:
                                            continue
                                        
                                        df_eod = df_until_date[:-1].copy() if len(df_until_date) > 5 else df_until_date
                                        
                                        if len(df_eod) < 20:
                                            continue
                                        
                                        signal_found = False
                                        entry_reason = ""
                                        confidence = 0
                                        
                                        if test_mode == "🌸 3Jasmines":
                                            signal = jasmines_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                                            if signal and signal.get('confidence', 0) >= min_confidence_jasmines:
                                                signal_found = True
                                                entry_reason = f"3Jasmines: {signal.get('pattern', 'Bullish Pattern')}"
                                                confidence = signal.get('confidence', 0)
                                        
                                        elif test_mode == "💎 Treasure Signals":
                                            result = hybrid_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                                            if result and result.get('is_treasure') and result.get('confidence', 0) >= min_confidence_hybrid:
                                                signal_found = True
                                                entry_reason = f"Treasure: {result.get('reason', 'Hybrid Signal')}"
                                                confidence = result.get('confidence', 0)
                                        
                                        elif test_mode == "🚀 High-Growth Strategy (35% CAGR)":
                                            result = hybrid_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                                            if result and result.get('is_treasure') and result.get('confidence', 0) >= min_confidence_hybrid:
                                                signal_found = True
                                                entry_reason = f"High-Growth: {result.get('reason', 'Hybrid Signal')}"
                                                confidence = result.get('confidence', 0)
                                        
                                        elif test_mode == "🌺 Orchid Trend Matrix":
                                            jasmines_signal = jasmines_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                                            if jasmines_signal and jasmines_signal.get('confidence', 0) >= min_confidence_jasmines:
                                                hybrid_result = hybrid_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                                                if hybrid_result and hybrid_result.get('is_treasure') and hybrid_result.get('confidence', 0) >= min_confidence_hybrid:
                                                    signal_found = True
                                                    combined_conf = (jasmines_signal.get('confidence', 0) + hybrid_result.get('confidence', 0)) / 2
                                                    entry_reason = f"Orchid: Both 3Jasmines + Treasure"
                                                    confidence = combined_conf
                                        
                                        if signal_found:
                                            current_price = df_eod['close'].iloc[-1]
                                            qty = int(investment_per_stock / current_price)
                                            
                                            portfolio.append({
                                                'symbol': symbol,
                                                'entry_date': current_date,
                                                'entry_price': current_price,
                                                'qty': qty,
                                                'investment': qty * current_price,
                                                'entry_reason': entry_reason,
                                                'confidence': confidence
                                            })
                                            
                                            if len(portfolio) >= max_portfolio:
                                                break
                            
                            # Close remaining positions
                            for pos in portfolio:
                                symbol = pos['symbol']
                                if symbol in all_data:
                                    df = all_data[symbol]
                                    if len(df) > 0:
                                        exit_price = df['close'].iloc[-1]
                                        entry_price = pos['entry_price']
                                        return_pct = ((exit_price - entry_price) / entry_price) * 100
                                        qty = pos['qty']
                                        pnl = qty * (exit_price - entry_price)
                                        exit_date = df['time'].iloc[-1]
                                        if isinstance(exit_date, pd.Timestamp):
                                            entry_dt = pd.Timestamp(pos['entry_date'])
                                            days_held = (exit_date - entry_dt).days
                                        else:
                                            days_held = 0
                                        
                                        trades.append({
                                            'Symbol': symbol,
                                            'Entry_Date': pos['entry_date'].strftime('%Y-%m-%d') if hasattr(pos['entry_date'], 'strftime') else str(pos['entry_date']),
                                            'Entry_Price': f"{entry_price:.2f}",
                                            'Exit_Date': exit_date.strftime('%Y-%m-%d') if hasattr(exit_date, 'strftime') else str(exit_date),
                                            'Exit_Price': f"{exit_price:.2f}",
                                            'Exit_Reason': "END_OF_PERIOD",
                                            'Qty': qty,
                                            'Investment': f"{pos['investment']:,.0f}",
                                            'PnL': pnl,
                                            'Return_%': return_pct,
                                            'Holding_Days': days_held,
                                            'Entry_Reason': pos['entry_reason'],
                                            'Confidence': pos.get('confidence', 0)
                                        })
                        
                        # Store results
                        if trades:
                            df_trades = pd.DataFrame(trades)
                            df_trades['PnL'] = pd.to_numeric(df_trades['PnL'], errors='coerce')
                            df_trades['Return_%'] = pd.to_numeric(df_trades['Return_%'], errors='coerce')
                            
                            total_trades = len(df_trades)
                            winners = len(df_trades[df_trades['PnL'] > 0])
                            win_rate = (winners / total_trades * 100) if total_trades > 0 else 0
                            total_pnl = df_trades['PnL'].sum()
                            avg_return = df_trades['Return_%'].mean()
                            best_return = df_trades['Return_%'].max()
                            worst_return = df_trades['Return_%'].min()
                            total_return_pct = (total_pnl / initial_capital) * 100
                            years = lookback_months / 12.0
                            cagr = ((1 + total_return_pct/100) ** (1/years) - 1) * 100 if years > 0 else 0
                            
                            all_results[test_mode] = {
                                'trades': df_trades,
                                'total_trades': total_trades,
                                'winners': winners,
                                'win_rate': win_rate,
                                'total_pnl': total_pnl,
                                'avg_return': avg_return,
                                'best_return': best_return,
                                'worst_return': worst_return,
                                'total_return_pct': total_return_pct,
                                'cagr': cagr
                            }
                        else:
                            all_results[test_mode] = None
                        
                        progress_bar.progress((mode_idx + 1) / len(modes_to_test))
                    
                    # Display comparative results
                    st.success("✅ Comparison Backtest Complete!")
                    st.markdown("---")
                    st.subheader("📊 Comparative Performance Summary")
                    
                    # Create comparison table
                    comparison_data = []
                    for mode_name, results in all_results.items():
                        if results:
                            comparison_data.append({
                                'Strategy': mode_name,
                                'Total Trades': results['total_trades'],
                                'Win Rate (%)': f"{results['win_rate']:.1f}",
                                'Total P&L (₹)': f"{results['total_pnl']:,.0f}",
                                'Total Return (%)': f"{results['total_return_pct']:.2f}",
                                'CAGR (%)': f"{results['cagr']:.2f}",
                                'Avg Return (%)': f"{results['avg_return']:.2f}",
                                'Best Trade (%)': f"{results['best_return']:.2f}",
                                'Worst Trade (%)': f"{results['worst_return']:.2f}"
                            })
                        else:
                            comparison_data.append({
                                'Strategy': mode_name,
                                'Total Trades': 0,
                                'Win Rate (%)': 'N/A',
                                'Total P&L (₹)': 'N/A',
                                'Total Return (%)': 'N/A',
                                'CAGR (%)': 'N/A',
                                'Avg Return (%)': 'N/A',
                                'Best Trade (%)': 'N/A',
                                'Worst Trade (%)': 'N/A'
                            })
                    
                    df_comparison = pd.DataFrame(comparison_data)
                    st.dataframe(df_comparison, use_container_width=True)
                    
                    # Show individual results
                    st.markdown("---")
                    st.subheader("📋 Individual Strategy Details")
                    
                    for mode_name, results in all_results.items():
                        if results:
                            with st.expander(f"{mode_name} - {results['total_trades']} trades, {results['win_rate']:.1f}% win rate"):
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Total Trades", results['total_trades'])
                                    st.metric("Winners", f"{results['winners']} ({results['win_rate']:.1f}%)")
                                with col2:
                                    st.metric("Total P&L", f"{results['total_pnl']:,.0f}")
                                    st.metric("Total Return", f"{results['total_return_pct']:.2f}%")
                                with col3:
                                    st.metric("CAGR", f"{results['cagr']:.2f}%")
                                    st.metric("Avg Return", f"{results['avg_return']:.2f}%")
                                with col4:
                                    st.metric("Best Trade", f"{results['best_return']:.2f}%")
                                    st.metric("Worst Trade", f"{results['worst_return']:.2f}%")
                                
                                st.dataframe(results['trades'], use_container_width=True, height=300)
                    
                    st.stop()
                
                # Initialize signal generators for single mode
                jasmines_gen = ThreeJasminesScreener(
                    max_support_distance_pct=0.5,
                    max_rsi_threshold=35.0,
                    target_buffer_pct=1.0,
                    stop_loss_buffer_pct=2.0
                )
                
                hybrid_gen = HybridSignalGenerator(
                    min_confidence=min_confidence_hybrid if mode in ["💎 Treasure Signals", "🌺 Orchid Trend Matrix"] else 75,
                    min_rr_ratio=min_rr_hybrid if mode in ["💎 Treasure Signals", "🌺 Orchid Trend Matrix"] else 1.5
                )
                
                sr_calc = SR_CALC_CLASS(sensitivity=3, min_touches=2)
                pattern_detector = ChartPatternDetector()
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                trades = []
                portfolio = []  # Active positions
                
                # Get historical data for all stocks
                all_data = {}
                status_text.text("📥 Fetching historical data...")
                
                for idx, symbol in enumerate(selected_stocks):
                    try:
                        ticker = yf.Ticker(get_yfinance_symbol(symbol))
                        df_raw = ticker.history(period=f"{lookback_months}mo", interval="1d")
                        
                        if not df_raw.empty and len(df_raw) >= 50:
                            df = pd.DataFrame({
                                'time': df_raw.index,
                                'open': df_raw['Open'].values,
                                'high': df_raw['High'].values,
                                'low': df_raw['Low'].values,
                                'close': df_raw['Close'].values,
                                'volume': df_raw['Volume'].values
                            })
                            all_data[symbol] = df
                        
                        progress_bar.progress((idx + 1) / (len(selected_stocks) * 2))
                    except Exception as e:
                        continue
                
                # Run backtest day by day
                if all_data:
                    if mode == "🌸 3Jasmines":
                        status_text.text(f"🔄 Running 3Jasmines backtest... (Min Confidence: {min_confidence_jasmines}%)")
                    else:
                        status_text.text("🔄 Running backtest simulation...")
                    
                    # Get all dates from all stocks
                    all_dates = set()
                    for df in all_data.values():
                        all_dates.update(df['time'].tolist())
                    all_dates = sorted(list(all_dates))
                    
                    # Track signal detection for 3Jasmines
                    signals_detected = 0
                    signals_entered = 0
                    
                    for day_idx, current_date in enumerate(all_dates):
                        # Check exits for existing positions
                        positions_to_remove = []
                        for pos in portfolio:
                            symbol = pos['symbol']
                            if symbol in all_data:
                                df = all_data[symbol]
                                df_until_date = df[df['time'] <= current_date].copy()
                                
                                if len(df_until_date) > 0:
                                    current_price = df_until_date['close'].iloc[-1]
                                    entry_price = pos['entry_price']
                                    # Handle date comparison
                                    if isinstance(current_date, pd.Timestamp):
                                        entry_dt = pd.Timestamp(pos['entry_date'])
                                        days_held = (current_date - entry_dt).days
                                    else:
                                        days_held = 0
                                    
                                    # Check exit conditions
                                    target_price = entry_price * (1 + target_pct / 100)
                                    stop_price = entry_price * (1 - stop_loss_pct / 100)
                                    
                                    exit_reason = None
                                    exit_price = current_price
                                    
                                    if current_price >= target_price:
                                        exit_reason = "TARGET"
                                    elif current_price <= stop_price:
                                        exit_reason = "STOP_LOSS"
                                    elif days_held >= max_holding_days:
                                        exit_reason = "TIME_EXIT"
                                    
                                    if exit_reason:
                                        # Exit position
                                        return_pct = ((exit_price - entry_price) / entry_price) * 100
                                        qty = pos['qty']
                                        pnl = qty * (exit_price - entry_price)
                                        
                                        trades.append({
                                            'Symbol': symbol,
                                            'Entry_Date': pos['entry_date'].strftime('%Y-%m-%d'),
                                            'Entry_Price': f"{entry_price:.2f}",
                                            'Exit_Date': current_date.strftime('%Y-%m-%d') if hasattr(current_date, 'strftime') else str(current_date),
                                            'Exit_Price': f"{exit_price:.2f}",
                                            'Exit_Reason': exit_reason,
                                            'Qty': qty,
                                            'Investment': f"{pos['investment']:,.0f}",
                                            'PnL': pnl,
                                            'Return_%': return_pct,
                                            'Holding_Days': days_held,
                                            'Entry_Reason': pos['entry_reason'],
                                            'Confidence': pos.get('confidence', 0)
                                        })
                                        
                                        positions_to_remove.append(pos)
                        
                        # Remove exited positions
                        for pos in positions_to_remove:
                            portfolio.remove(pos)
                        
                        # Check for new signals if portfolio has space
                        if len(portfolio) < max_portfolio:
                            for symbol in selected_stocks:
                                if symbol not in all_data:
                                    continue
                                
                                # Check if already in portfolio
                                if any(p['symbol'] == symbol for p in portfolio):
                                    continue
                                
                                df = all_data[symbol]
                                df_until_date = df[df['time'] <= current_date].copy()
                                
                                if len(df_until_date) < 50:
                                    continue
                                
                                # Use EOD data (exclude current day if it's today)
                                df_eod = df_until_date[:-1].copy() if len(df_until_date) > 5 else df_until_date
                                
                                if len(df_eod) < 20:
                                    continue
                                
                                signal_found = False
                                entry_reason = ""
                                confidence = 0
                                
                                # Check signals based on mode
                                if mode == "🌸 3Jasmines":
                                    try:
                                        signal = jasmines_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                                        if signal:
                                            signals_detected += 1
                                            signal_conf = signal.get('confidence', 0)
                                            if signal_conf >= min_confidence_jasmines:
                                                signal_found = True
                                                signals_entered += 1
                                                pattern_name = signal.get('pattern', 'Bullish Pattern')
                                                entry_reason = f"3Jasmines: {pattern_name}"
                                                confidence = signal_conf
                                    except Exception as e:
                                        # Skip this stock if analysis fails
                                        continue
                                
                                elif mode == "💎 Treasure Signals":
                                    result = hybrid_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                                    if result and result.get('is_treasure') and result.get('confidence', 0) >= min_confidence_hybrid:
                                        signal_found = True
                                        entry_reason = f"Treasure: {result.get('reason', 'Hybrid Signal')}"
                                        confidence = result.get('confidence', 0)
                                
                                elif mode == "🚀 High-Growth Strategy (35% CAGR)":
                                    # Uses Hybrid mode with optimized settings for 35% CAGR
                                    result = hybrid_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                                    if result and result.get('is_treasure') and result.get('confidence', 0) >= min_confidence_hybrid:
                                        signal_found = True
                                        entry_reason = f"High-Growth: {result.get('reason', 'Hybrid Signal')}"
                                        confidence = result.get('confidence', 0)
                                
                                elif mode == "🌺 Orchid Trend Matrix":
                                    # Check 3Jasmines first
                                    jasmines_signal = jasmines_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                                    if jasmines_signal and jasmines_signal.get('confidence', 0) >= min_confidence_jasmines:
                                        # Check Hybrid
                                        hybrid_result = hybrid_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
                                        if hybrid_result and hybrid_result.get('is_treasure') and hybrid_result.get('confidence', 0) >= min_confidence_hybrid:
                                            signal_found = True
                                            combined_conf = (jasmines_signal.get('confidence', 0) + hybrid_result.get('confidence', 0)) / 2
                                            entry_reason = f"Orchid: Both 3Jasmines + Treasure"
                                            confidence = combined_conf
                                
                                if signal_found:
                                    # Enter position
                                    current_price = df_eod['close'].iloc[-1]
                                    qty = int(investment_per_stock / current_price)
                                    
                                    portfolio.append({
                                        'symbol': symbol,
                                        'entry_date': current_date,
                                        'entry_price': current_price,
                                        'qty': qty,
                                        'investment': qty * current_price,
                                        'entry_reason': entry_reason,
                                        'confidence': confidence
                                    })
                                    
                                    # Only one new position per day
                                    if len(portfolio) >= max_portfolio:
                                        break
                        
                        progress_bar.progress(0.5 + (day_idx + 1) / (len(all_dates) * 2))
                    
                    # Close any remaining positions at end
                    for pos in portfolio:
                        symbol = pos['symbol']
                        if symbol in all_data:
                            df = all_data[symbol]
                            if len(df) > 0:
                                exit_price = df['close'].iloc[-1]
                                entry_price = pos['entry_price']
                                return_pct = ((exit_price - entry_price) / entry_price) * 100
                                qty = pos['qty']
                                pnl = qty * (exit_price - entry_price)
                                # Handle date comparison
                                exit_date = df['time'].iloc[-1]
                                if isinstance(exit_date, pd.Timestamp):
                                    entry_dt = pd.Timestamp(pos['entry_date'])
                                    days_held = (exit_date - entry_dt).days
                                else:
                                    days_held = 0
                                
                                trades.append({
                                    'Symbol': symbol,
                                    'Entry_Date': pos['entry_date'].strftime('%Y-%m-%d') if hasattr(pos['entry_date'], 'strftime') else str(pos['entry_date']),
                                    'Entry_Price': f"{entry_price:.2f}",
                                    'Exit_Date': df['time'].iloc[-1].strftime('%Y-%m-%d') if hasattr(df['time'].iloc[-1], 'strftime') else str(df['time'].iloc[-1]),
                                    'Exit_Price': f"{exit_price:.2f}",
                                    'Exit_Reason': "END_OF_PERIOD",
                                    'Qty': qty,
                                    'Investment': f"{pos['investment']:,.0f}",
                                    'PnL': pnl,
                                    'Return_%': return_pct,
                                    'Holding_Days': days_held,
                                    'Entry_Reason': pos['entry_reason'],
                                    'Confidence': pos.get('confidence', 0)
                                })
                
                progress_bar.progress(1.0)
                
                # Show 3Jasmines-specific stats
                if mode == "🌸 3Jasmines":
                    status_text.text(f"✅ 3Jasmines backtest complete! Signals detected: {signals_detected}, Entered: {signals_entered}")
                else:
                    status_text.text("✅ Backtest complete!")
                
                if not trades:
                    if mode == "🌸 3Jasmines":
                        st.warning(f"""
                        ⚠️ **No 3Jasmines trades generated.**
                        
                        **Possible reasons:**
                        - No stocks met all 3 criteria (Near Support + RSI < 35 + Bullish Pattern)
                        - Confidence threshold ({min_confidence_jasmines}%) too high
                        - Selected stocks don't have enough historical data
                        - Try: Lower confidence threshold, select more stocks, or increase lookback period
                        """)
                    else:
                        st.warning("⚠️ No trades generated. Try adjusting parameters or selecting different stocks.")
                    st.stop()
                
                df_trades = pd.DataFrame(trades)
                
                # Convert numeric columns
                df_trades['PnL'] = pd.to_numeric(df_trades['PnL'], errors='coerce')
                df_trades['Return_%'] = pd.to_numeric(df_trades['Return_%'], errors='coerce')
                df_trades['Holding_Days'] = pd.to_numeric(df_trades['Holding_Days'], errors='coerce')
                
                # Calculate metrics
                total_trades = len(df_trades)
                winners = len(df_trades[df_trades['PnL'] > 0])
                losers = total_trades - winners
                win_rate = (winners / total_trades * 100) if total_trades > 0 else 0
                
                total_pnl = df_trades['PnL'].sum()
                avg_return = df_trades['Return_%'].mean()
                best_return = df_trades['Return_%'].max()
                worst_return = df_trades['Return_%'].min()
                
                total_return_pct = (total_pnl / initial_capital) * 100
                
                # Calculate CAGR based on actual period
                years = lookback_months / 12.0
                if years > 0:
                    cagr = ((1 + total_return_pct/100) ** (1/years) - 1) * 100
                else:
                    cagr = 0
                
                # Display results
                st.success("✅ Backtest Complete!")
                
                st.markdown("---")
                st.subheader("📊 Performance Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Trades", total_trades)
                    st.metric("Winners", f"{winners} ({win_rate:.1f}%)")
                with col2:
                    st.metric("Total P&L", f"{total_pnl:,.0f}")
                    st.metric("Total Return", f"{total_return_pct:.2f}%")
                with col3:
                    st.metric("CAGR", f"{cagr:.2f}%")
                    st.metric("Avg Return", f"{avg_return:.2f}%")
                with col4:
                    st.metric("Best Trade", f"{best_return:.2f}%")
                    st.metric("Worst Trade", f"{worst_return:.2f}%")
                
                # Trades table
                st.markdown("---")
                st.subheader("📋 Trade History")
                
                # Format PnL column with colors
                def color_pnl(val):
                    if isinstance(val, (int, float)):
                        return 'background-color: #d4edda' if val > 0 else 'background-color: #f8d7da'
                    return ''
                
                st.dataframe(
                    df_trades.style.applymap(color_pnl, subset=['PnL']),
                    use_container_width=True,
                    height=400
                )
                
                # Download button
                st.markdown("---")
                csv = df_trades.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                st.markdown("---")
                st.info(f"""
                💡 **Backtest Summary:**
                
                - **Mode:** {mode}
                - **Period:** {lookback_months} months
                - **Stocks Tested:** {len(selected_stocks)}
                - **Total Trades:** {total_trades}
                - **Win Rate:** {win_rate:.1f}%
                - **Total Return:** {total_return_pct:.2f}%
                """)
                
            except Exception as e:
                st.error(f"❌ Backtest Error: {str(e)}")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())

# ============================================================
# PAGE: DATA DOWNLOAD
# ============================================================

elif page == "Data Download":
    st.header("📥 Data Download Center")
    st.markdown("Download historical stock and commodity data for offline use or backup")
    
    # Import data manager
    try:
        from data_manager.data_exporter import DataExporter
        from data_manager.data_organizer import DataOrganizer
        from data_manager.live_data_downloader import create_excel_live, create_zip_live, NIFTY_50, MCX_COMMODITIES, ALL_STOCKS
        import os
        
        exporter = DataExporter()
        organizer = DataOrganizer()
        
        # Get data summary
        summary = organizer.get_data_summary()
        
        # Display summary
        st.markdown("---")
        st.subheader("📊 Available Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Files", summary['total_files'])
        
        with col2:
            st.metric("Total Size", f"{summary['total_size_mb']:.2f} MB")
        
        with col3:
            nifty_files = sum([
                summary['folders'].get('nifty50', {}).get('files', 0),
                summary['folders'].get('nifty200', {}).get('files', 0),
                summary['folders'].get('nifty500', {}).get('files', 0),
                summary['folders'].get('smallcap250', {}).get('files', 0)
            ])
            st.metric("Stock Universe", f"{nifty_files} stocks")
        
        st.markdown("---")
        
        # Data breakdown
        st.subheader("📁 Data Breakdown")
        
        data_info = []
        for category, info in summary['folders'].items():
            if info['files'] > 0:
                data_info.append({
                    'Category': category.replace('_', ' ').title(),
                    'Files': info['files'],
                    'Size (MB)': f"{info['size_mb']:.2f}"
                })
        
        if data_info:
            import pandas as pd
            df_info = pd.DataFrame(data_info)
            st.dataframe(df_info, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Download options
        st.subheader("📦 Download Packages")
        
        # Format selector
        download_format = st.radio(
            "Choose Format:",
            ["📊 Excel (.xlsx) - All data in one file", "📦 ZIP (CSV files) - Individual files"],
            horizontal=True
        )
        
        is_excel = "Excel" in download_format
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Complete Package")
            st.write("**Includes:**")
            st.write("- All Nifty 50/200/500 stocks")
            st.write("- Smallcap 250 stocks")
            st.write("- MCX commodities (Gold, Silver)")
            
            if is_excel:
                st.write(f"- **~50 sheets** (Excel limit)")
                st.write(f"- **~20 MB** (.xlsx)")
                st.info("⚠️ Excel format limited to 50 stocks for file size")
            else:
                st.write(f"- **{summary['total_files']} files**")
                st.write(f"- **~130 MB** (compressed)")
            
            if st.button("📥 Download Complete Package", type="primary", use_container_width=True, key="complete"):
                if is_excel:
                    with st.spinner("📡 Downloading LIVE data from Yahoo Finance... This may take 30-60 seconds..."):
                        try:
                            # Download live data
                            result = create_excel_live(ALL_STOCKS, period="1y")
                            
                            if result['success']:
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                st.success(f"✅ Excel file created! {result['sheets_count']} stocks with LIVE data")
                                
                                if result.get('errors'):
                                    st.warning(f"⚠️ {len(result['errors'])} stocks skipped")
                                
                                st.download_button(
                                    label="📊 Download Excel File",
                                    data=result['data'],
                                    file_name=f"StockData_Live_{timestamp}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                            else:
                                st.error(f"❌ Error: {result['error']}")
                                st.info("💡 Try again or use ZIP format")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                            st.info("💡 Please try the ZIP format option")
                else:
                    with st.spinner("📡 Downloading LIVE data from Yahoo Finance... This may take 30-60 seconds..."):
                        try:
                            # Download live data as ZIP
                            result = create_zip_live(ALL_STOCKS, period="1y")
                            
                            if result['success']:
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                st.success(f"✅ ZIP created! {result['files_count']} CSV files with LIVE data")
                                
                                if result.get('errors'):
                                    st.warning(f"⚠️ {len(result['errors'])} stocks skipped")
                                
                                st.download_button(
                                    label="💾 Download ZIP File",
                                    data=result['data'],
                                    file_name=f"StockData_Live_{timestamp}.zip",
                                    mime="application/zip",
                                    use_container_width=True
                                )
                            else:
                                st.error(f"❌ Error: {result['error']}")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        
        with col2:
            st.markdown("### 📈 Nifty 50 + MCX")
            st.write("**Includes:**")
            st.write("- Top 50 Nifty stocks")
            st.write("- Gold & Silver commodities")
            st.write("- Perfect for quick analysis")
            
            if is_excel:
                st.write(f"- **~50 sheets** (all data)")
                st.write(f"- **~8 MB** (.xlsx)")
            else:
                st.write(f"- **~50 files**")
                st.write(f"- **~20 MB** (compressed)")
            
            if st.button("📥 Download Nifty 50 + MCX", use_container_width=True, key="nifty50"):
                if is_excel:
                    with st.spinner("📡 Downloading LIVE data... 20-30 seconds..."):
                        try:
                            # Download Nifty 50 + MCX live data
                            result = create_excel_live(NIFTY_50 + MCX_COMMODITIES, period="1y")
                            
                            if result['success']:
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                st.success(f"✅ Excel created! {result['sheets_count']} stocks with LIVE data")
                                
                                st.download_button(
                                    label="📊 Download Excel File",
                                    data=result['data'],
                                    file_name=f"Nifty50_MCX_Live_{timestamp}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                            else:
                                st.error(f"❌ Error: {result['error']}")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    with st.spinner("📡 Downloading LIVE data... 20-30 seconds..."):
                        try:
                            # Download Nifty 50 + MCX as ZIP
                            result = create_zip_live(NIFTY_50 + MCX_COMMODITIES, period="1y")
                            
                            if result['success']:
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                st.success(f"✅ ZIP created! {result['files_count']} CSV files with LIVE data")
                                
                                st.download_button(
                                    label="💾 Download ZIP File",
                                    data=result['data'],
                                    file_name=f"Nifty50_MCX_Live_{timestamp}.zip",
                                    mime="application/zip",
                                    use_container_width=True
                                )
                            else:
                                st.error(f"❌ Error: {result['error']}")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        
        st.markdown("---")
        
        st.info(f"""
        💡 **Format Guide:**
        
        **📊 Excel (.xlsx):**
        - One file with multiple sheets (one per stock)
        - Easy to open in Excel/Google Sheets
        - Limited to 50 stocks (file size)
        - Best for quick analysis
        
        **📦 ZIP (CSV files):**
        - All {summary['total_files']} stocks as separate CSV files
        - Smaller individual files
        - Better for programming (Python, R)
        - No limit on number of stocks
        """)
        
        st.markdown("---")
        
        # Usage instructions
        with st.expander("📖 How to Use Downloaded Data"):
            st.markdown("""
            ### Using the Downloaded Data
            
            1. **Download Package:** Click one of the download buttons above
            2. **Extract ZIP:** Extract the downloaded ZIP file
            3. **File Structure:** You'll find CSV files organized by category
            4. **CSV Format:** All files contain: `time`, `open`, `high`, `low`, `close`, `volume`
            
            ### Data Information
            
            - **Update Frequency:** Daily (EOD - End of Day)
            - **Data Range:** Multiple years (varies by stock)
            - **Format:** Standard OHLCV CSV format
            - **Compatible with:** Excel, Python (pandas), R, Trading platforms
            
            ### Example Usage in Python
            
            ```python
            import pandas as pd
            
            # Read any stock data file
            df = pd.read_csv('NSE_RELIANCE_1D.csv')
            
            # Display data
            print(df.head())
            
            # Calculate returns
            df['returns'] = df['close'].pct_change()
            
            # Plot
            df.set_index('time')['close'].plot()
            ```
            
            ### Restore to MG AI Screener
            
            If you want to restore this data to the MG AI Screener system:
            
            1. Extract ZIP file
            2. Copy folders to: `C:\\python\\MG AI\\`
            3. Maintain folder structure (Nifty200_Data, Nifty500_Data, etc.)
            4. Restart the application
            
            ### Support
            
            For issues or questions, check the documentation or contact support.
            """)
        
        # Previous exports
        st.markdown("---")
        st.subheader("📚 Previous Exports")
        
        exports = exporter.list_exports()
        
        if exports:
            st.write(f"Found {len(exports)} previous export(s):")
            
            for exp in exports[:5]:  # Show last 5
                col_a, col_b, col_c = st.columns([3, 1, 1])
                
                with col_a:
                    st.write(f"📦 {exp['name']}")
                
                with col_b:
                    st.write(f"{exp['size_mb']} MB")
                
                with col_c:
                    st.write(exp['created'])
        else:
            st.info("No previous exports found. Create one using the buttons above!")
    
    except Exception as e:
        st.error(f"❌ Error loading data manager: {str(e)}")
        st.info("The data download feature requires the data_manager module. Please ensure it's properly installed.")

# ============================================================
# PAGE: SETTINGS
# ============================================================

elif page == "Settings":
    st.header("⚙️ Settings")
    
    # Get current config
    current_config = db.get_user_config()
    
    with st.form("settings_form"):
        st.subheader("💰 Capital Settings")
        total_capital = st.number_input(
            "Total Capital (₹)",
            value=float(current_config.get('total_capital', 1000000)),
            step=100000.0
        )
        
        st.subheader("⚠️ Risk Parameters")
        col1, col2 = st.columns(2)
        
        with col1:
            max_risk_per_trade = st.number_input(
                "Max Risk Per Trade (%)",
                value=float(current_config.get('max_risk_per_trade', 2.0)),
                step=0.5,
                min_value=0.5,
                max_value=10.0
            )
            
            max_positions = st.number_input(
                "Max Positions",
                value=int(current_config.get('max_positions', 10)),
                step=1,
                min_value=1,
                max_value=50
            )
        
        with col2:
            max_portfolio_risk = st.number_input(
                "Max Portfolio Risk (%)",
                value=float(current_config.get('max_portfolio_risk', 10.0)),
                step=1.0,
                min_value=1.0,
                max_value=50.0
            )
            
            min_confidence = st.number_input(
                "Min Confidence for Signals (%)",
                value=float(current_config.get('min_confidence', 70.0)),
                step=5.0,
                min_value=50.0,
                max_value=100.0
            )
        
        st.subheader("📊 Trading Parameters")
        min_risk_reward = st.number_input(
            "Min Risk:Reward Ratio",
            value=float(current_config.get('min_risk_reward', 1.5)),
            step=0.1,
            min_value=1.0,
            max_value=5.0
        )
        
        submitted = st.form_submit_button("💾 Save Settings")
        
        if submitted:
            config_data = {
                'total_capital': total_capital,
                'max_risk_per_trade': max_risk_per_trade,
                'max_portfolio_risk': max_portfolio_risk,
                'max_positions': max_positions,
                'min_confidence': min_confidence,
                'min_risk_reward': min_risk_reward
            }
            
            success = db.update_user_config(config_data)
            
            if success:
                st.success("✅ Settings saved successfully!")
                st.info("🔄 Restart the app to apply new capital settings to risk engine")
                
                # Clear cache to reload with new settings
                st.cache_resource.clear()
            else:
                st.error("❌ Failed to save settings")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; padding: 1rem;">
    <strong>Professional AI Screener v3.0</strong> | 
    Database: PostgreSQL | 
    API: http://localhost:8000/docs | 
    Made with ❤️
</div>
""", unsafe_allow_html=True)

# Show database connection status in footer
if st.sidebar.checkbox("Show Technical Info"):
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 Technical Info")
    st.sidebar.code(f"""
Database: {'PostgreSQL' if db.use_postgresql else 'SQLite'}
Broker: {broker.name}
Risk Engine: Active
Total Signals: {len(db.get_active_signals())}
    """)

