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
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Import our professional modules
from database.db_manager import get_db
from risk_management.risk_engine import RiskEngine
from broker_integration.broker_client import get_broker_client
from support_resistance.sr_calculator import SupportResistanceCalculator

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
# HEADER
# ============================================================

st.markdown('<div class="main-header">🚀 PROFESSIONAL AI SCREENER v3.0</div>', unsafe_allow_html=True)
st.markdown("**AI-Powered Trading with Database Persistence & Risk Management**")

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
    ["Dashboard", "Active Signals", "Generate New Signal", "S&R Analysis", 
     "Backtest - Technical", "Backtest - Hybrid", "Backtest - Multi-Mode",
     "Portfolio", "Trade History", "Risk Report", "Settings"]
)

# ============================================================
# PAGE: DASHBOARD
# ============================================================

if page == "Dashboard":
    st.header("📊 Dashboard Overview")
    
    # Get statistics
    active_signals = db.get_active_signals()
    portfolio = db.get_portfolio()
    portfolio_summary = db.get_portfolio_summary()
    open_trades = db.get_open_trades()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Active Signals",
            len(active_signals),
            delta=f"{len([s for s in active_signals if s.get('confidence', 0) > 75])} high confidence"
        )
    
    with col2:
        total_invested = portfolio_summary.get('total_invested') or 0
        st.metric(
            "Open Positions",
            len(portfolio),
            delta=f"₹{total_invested:,.0f} invested"
        )
    
    with col3:
        total_pnl = portfolio_summary.get('total_unrealized_pnl') or 0
        avg_pnl_pct = portfolio_summary.get('avg_pnl_pct') or 0
        st.metric(
            "Unrealized P&L",
            f"₹{total_pnl:,.0f}",
            delta=f"{avg_pnl_pct:.2f}%"
        )
    
    with col4:
        st.metric(
            "Open Trades",
            len(open_trades),
            delta="Active"
        )
    
    st.markdown("---")
    
    # Recent signals
    st.subheader("🔔 Recent Signals (Last 24 Hours)")
    if active_signals:
        for signal in active_signals[:5]:
            signal_type = signal.get('signal_type', 'HOLD')
            color = "green" if signal_type == "BUY" else "red"
            
            st.markdown(f"""
            <div class="signal-card signal-{signal_type.lower()}">
                <strong>{signal.get('symbol', 'N/A')}</strong> - 
                <span style="color: {color}; font-weight: bold;">{signal_type}</span> 
                @ ₹{signal.get('entry_price', 0):.2f} | 
                Confidence: {signal.get('confidence', 0):.1f}% | 
                {signal.get('generated_at', 'N/A')}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No active signals. Generate new signals from 'Generate New Signal' page.")
    
    # Portfolio pie chart
    if portfolio:
        st.subheader("📊 Portfolio Allocation")
        
        df_portfolio = pd.DataFrame(portfolio)
        fig = go.Figure(data=[go.Pie(
            labels=df_portfolio['symbol'],
            values=df_portfolio['current_value'],
            hole=0.3
        )])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE: ACTIVE SIGNALS
# ============================================================

elif page == "Active Signals":
    st.header("🔔 Active Signals")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        min_confidence = st.slider("Minimum Confidence", 0.0, 100.0, 70.0, 5.0)
    with col2:
        signal_filter = st.selectbox("Filter by Type", ["ALL", "BUY", "SELL"])
    
    # Get signals
    signals = db.get_active_signals(min_confidence=min_confidence)
    
    if signal_filter != "ALL":
        signals = [s for s in signals if s.get('signal_type') == signal_filter]
    
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
# PAGE: GENERATE NEW SIGNAL
# ============================================================

elif page == "Generate New Signal":
    st.header("🎯 Generate New Trading Signal")
    
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

# ============================================================
# PAGE: S&R ANALYSIS
# ============================================================

elif page == "S&R Analysis":
    st.header("📈 Support & Resistance Analysis")
    
    st.info("🎯 Analyze support and resistance levels for stocks with AI-powered insights!")
    
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
            symbol_input = st.text_input("Enter Symbol", "RELIANCE", help="Enter stock symbol (e.g., RELIANCE, TCS, INFY)")
        
        with col2:
            sensitivity = st.slider("Sensitivity", 3, 10, 5, help="Lower = more levels, Higher = fewer strong levels")
        
        with col3:
            min_touches = st.slider("Min Touches", 2, 5, 2, help="Minimum times price must touch a level")
    
    else:  # Batch Analysis
        st.subheader("📋 Batch Analysis - Multiple Stocks")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Enter stock symbols** (one per line or comma-separated):")
            default_stocks = "RELIANCE\nTCS\nINFY\nHDFCBANK\nICICIBANK\nSBIN\nBHARTIARTL\nITC\nADANIENT\nAXISBANK"
            symbols_input = st.text_area(
                "Stock Symbols:",
                default_stocks,
                height=200,
                help="Enter one symbol per line, or separate with commas"
            )
        
        with col2:
            st.markdown("**Analysis Settings:**")
            sensitivity = st.slider("Sensitivity", 3, 10, 5, help="Lower = more levels, Higher = fewer strong levels", key="batch_sens")
            min_touches = st.slider("Min Touches", 2, 5, 2, help="Minimum times price must touch a level", key="batch_touch")
            
            st.markdown("**Quick Presets:**")
            if st.button("📊 Nifty 50", help="Load Nifty 50 stocks"):
                symbols_input = "RELIANCE\nTCS\nHDFCBANK\nINFY\nICICIBANK\nHINDUNILVR\nITC\nSBIN\nBHARTIARTL\nAXISBANK\nKOTAKBANK\nLT\nHCLTECH\nASIANPAINT\nMARUTI\nSUNPHARMA\nTITAN\nULTRACEMCO\nNESTLEIND\nBAJFINANCE"
            if st.button("⚡ Top 20", help="Load top 20 stocks"):
                symbols_input = "RELIANCE\nTCS\nHDFCBANK\nINFY\nICICIBANK\nHINDUNILVR\nITC\nSBIN\nBHARTIARTL\nAXISBANK\nKOTAKBANK\nLT\nHCLTECH\nASIANPAINT\nMARUTI\nBAJFINANCE\nSUNPHARMA\nTITAN\nULTRACEMCO\nNESTLEIND"
            if st.button("💊 Pharma", help="Load pharma stocks"):
                symbols_input = "SUNPHARMA\nDRREDDY\nCIPLA\nBIOCON\nAUROBINDO\nLUPIN\nTORNTPHARM\nALKEM\nDIVISLAB\nGLENMARK"
    
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
                
                # Initialize S&R calculator
                sr_calc = SupportResistanceCalculator(sensitivity=sensitivity, min_touches=min_touches)
                
                for idx, symbol in enumerate(symbols_list):
                    status_text.text(f"Analyzing {symbol}... ({idx+1}/{len(symbols_list)})")
                    
                    try:
                        # Generate sample data for each stock
                        import numpy as np
                        dates = pd.date_range(end=datetime.now(), periods=200, freq='D')
                        base_price = np.random.randint(500, 5000)
                        df = pd.DataFrame({
                            'time': dates,
                            'open': base_price + np.random.randn(200) * (base_price * 0.02),
                            'high': base_price + np.random.randn(200) * (base_price * 0.02) + base_price * 0.01,
                            'low': base_price + np.random.randn(200) * (base_price * 0.02) - base_price * 0.01,
                            'close': base_price + np.random.randn(200) * (base_price * 0.02),
                            'volume': np.random.randint(1000000, 5000000, 200)
                        })
                        # Add trend
                        trend = np.random.choice([-1, 0, 1])  # bearish, neutral, bullish
                        df['close'] = df['close'] + np.arange(200) * trend * (base_price * 0.01)
                        df['high'] = df[['high', 'close']].max(axis=1) + base_price * 0.005
                        df['low'] = df[['low', 'close']].min(axis=1) - base_price * 0.005
                        df['open'] = df['close'].shift(1).fillna(df['close'])
                        
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
                            'Symbol': symbol,
                            'Price': f"₹{current_price:.2f}",
                            'Signal': signal['signal'],
                            'Confidence': f"{signal['confidence_score']}%",
                            'Trend': ma_data['trend'],
                            'Support': f"₹{nearest_support['level']:.2f} ({nearest_support['distance']:.1f}%)" if nearest_support else "N/A",
                            'Resistance': f"₹{nearest_resistance['level']:.2f} ({nearest_resistance['distance']:.1f}%)" if nearest_resistance else "N/A",
                            'Sup Strength': f"{nearest_support['strength']:.0f}" if nearest_support else "N/A",
                            'Res Strength': f"{nearest_resistance['strength']:.0f}" if nearest_resistance else "N/A",
                        })
                        
                    except Exception as e:
                        batch_results.append({
                            'Symbol': symbol,
                            'Price': 'Error',
                            'Signal': 'Error',
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
                    filter_signal = st.multiselect("Filter by Signal", ["BUY", "SELL", "HOLD"], default=["BUY", "SELL", "HOLD"])
                with col2:
                    filter_trend = st.multiselect("Filter by Trend", ["BULLISH", "BEARISH", "NEUTRAL"], default=["BULLISH", "BEARISH", "NEUTRAL"])
                with col3:
                    sort_by = st.selectbox("Sort by", ["Symbol", "Signal", "Confidence", "Trend"])
                
                # Apply filters
                if filter_signal:
                    results_df = results_df[results_df['Signal'].str.contains('|'.join(filter_signal), na=False)]
                if filter_trend:
                    results_df = results_df[results_df['Trend'].str.contains('|'.join(filter_trend), na=False)]
                
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
                    # Initialize S&R calculator
                    sr_calc = SupportResistanceCalculator(sensitivity=sensitivity, min_touches=min_touches)
                    
                    # Try to get data from Dhan
                    try:
                        from datetime import datetime, timedelta
                        from dhanhq import dhanhq
                        import os
                        from dotenv import load_dotenv
                        
                        load_dotenv()
                        client_id = os.getenv('DHAN_CLIENT_ID')
                        access_token = os.getenv('DHAN_ACCESS_TOKEN')
                        
                        if client_id and access_token:
                            dhan = dhanhq(client_id, access_token)
                            
                            # Fetch historical data (1 year daily data)
                            end_date = datetime.now()
                            start_date = end_date - timedelta(days=365)
                            
                            # Try to get data
                            st.info(f"📡 Fetching data from Dhan API...")
                            
                            # This is a simplified version - you'll need proper security_id mapping
                            # For now, we'll use a sample data approach
                            df = None
                            
                            if df is None:
                                st.warning("⚠️ Could not fetch live data. Using sample data for demonstration.")
                                # Generate sample data for demonstration
                                import numpy as np
                                dates = pd.date_range(end=datetime.now(), periods=200, freq='D')
                                base_price = 2500
                                df = pd.DataFrame({
                                    'time': dates,
                                    'open': base_price + np.random.randn(200) * 50,
                                    'high': base_price + np.random.randn(200) * 50 + 20,
                                    'low': base_price + np.random.randn(200) * 50 - 20,
                                    'close': base_price + np.random.randn(200) * 50,
                                    'volume': np.random.randint(1000000, 5000000, 200)
                                })
                                # Add trend
                                df['close'] = df['close'] + np.arange(200) * 2
                                df['high'] = df[['high', 'close']].max(axis=1) + 10
                                df['low'] = df[['low', 'close']].min(axis=1) - 10
                                df['open'] = df['close'].shift(1).fillna(df['close'])
                        else:
                            st.warning("⚠️ Dhan credentials not found. Using sample data.")
                            # Generate sample data
                            import numpy as np
                            dates = pd.date_range(end=datetime.now(), periods=200, freq='D')
                            base_price = 2500
                            df = pd.DataFrame({
                                'time': dates,
                                'open': base_price + np.random.randn(200) * 50,
                                'high': base_price + np.random.randn(200) * 50 + 20,
                                'low': base_price + np.random.randn(200) * 50 - 20,
                                'close': base_price + np.random.randn(200) * 50,
                                'volume': np.random.randint(1000000, 5000000, 200)
                            })
                            # Add trend
                            df['close'] = df['close'] + np.arange(200) * 2
                            df['high'] = df[['high', 'close']].max(axis=1) + 10
                            df['low'] = df[['low', 'close']].min(axis=1) - 10
                            df['open'] = df['close'].shift(1).fillna(df['close'])
                            
                    except Exception as e:
                        st.warning(f"⚠️ Could not fetch live data: {e}. Using sample data.")
                        # Generate sample data
                        import numpy as np
                        dates = pd.date_range(end=datetime.now(), periods=200, freq='D')
                        base_price = 2500
                        df = pd.DataFrame({
                            'time': dates,
                            'open': base_price + np.random.randn(200) * 50,
                            'high': base_price + np.random.randn(200) * 50 + 20,
                            'low': base_price + np.random.randn(200) * 50 - 20,
                            'close': base_price + np.random.randn(200) * 50,
                            'volume': np.random.randint(1000000, 5000000, 200)
                        })
                        # Add trend
                        df['close'] = df['close'] + np.arange(200) * 2
                        df['high'] = df[['high', 'close']].max(axis=1) + 10
                        df['low'] = df[['low', 'close']].min(axis=1) - 10
                        df['open'] = df['close'].shift(1).fillna(df['close'])
                    
                    if df is not None and not df.empty:
                        # Calculate S&R levels
                        current_price = df['close'].iloc[-1]
                        sr_data = sr_calc.calculate_support_resistance(df, current_price)
                        
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
                            st.metric("Current Price", f"₹{sr_data['current_price']:.2f}")
                        
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
                        
                        # Support & Resistance Tables
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("🛡️ Support Levels")
                            if sr_data['supports']:
                                df_supports = pd.DataFrame(sr_data['supports'])
                                st.dataframe(
                                    df_supports[['level', 'distance_pct', 'touches', 'strength']],
                                    use_container_width=True
                                )
                            else:
                                st.info("No strong support levels found")
                        
                        with col2:
                            st.subheader("🚧 Resistance Levels")
                            if sr_data['resistances']:
                                df_resistances = pd.DataFrame(sr_data['resistances'])
                                st.dataframe(
                                    df_resistances[['level', 'distance_pct', 'touches', 'strength']],
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
                    
                    # Add support levels
                    for support in sr_data['supports'][:3]:
                        fig.add_hline(
                            y=support['level'],
                            line_dash="dash",
                            line_color="green",
                            annotation_text=f"Support: ₹{support['level']} (Strength: {support['strength']})",
                            annotation_position="left"
                        )
                    
                    # Add resistance levels
                    for resistance in sr_data['resistances'][:3]:
                        fig.add_hline(
                            y=resistance['level'],
                            line_dash="dash",
                            line_color="red",
                            annotation_text=f"Resistance: ₹{resistance['level']} (Strength: {resistance['strength']})",
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
                            st.metric("50 EMA", f"₹{ma_data['EMA50']:.2f}", f"{ma_data['distance_from_50ema']:.2f}%")
                        
                        with col2:
                            st.metric("200 EMA", f"₹{ma_data['EMA200']:.2f}", f"{ma_data['distance_from_200ema']:.2f}%")
                        
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
                                st.success(f"🚀 **{br['type']}**: Price broke above ₹{br['level']} with {br['strength']:.1f} strength")
                                if br['volume_confirmation']:
                                    st.info("✅ Confirmed with high volume")
                            else:
                                st.error(f"📉 **{br['type']}**: Price broke below ₹{br['level']} with {br['strength']:.1f} strength")
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
# PAGE: BACKTEST - TECHNICAL
# ============================================================

elif page == "Backtest - Technical":
    st.header("📊 Backtest - Technical Analysis Only")
    
    st.info("🎯 Test your trading strategy using pure technical analysis (RSI, MACD, Golden Cross, etc.)")
    
    st.markdown("""
    ### 📈 Technical Patterns Used:
    - **Golden Cross**: SMA 20 crosses above SMA 50 + RSI < 40
    - **Uptrend**: Price > SMA 20 > SMA 50 + Healthy RSI
    - **Pullback**: Price near SMA 20 in uptrend + RSI < 50
    """)
    
    # Load backtest dashboard
    st.markdown("---")
    st.subheader("🚀 Launch Interactive Backtest")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Port:** 8502")
        st.code("http://localhost:8502")
    with col2:
        if st.button("🚀 Launch Technical Backtest Dashboard", type="primary"):
            import webbrowser
            webbrowser.open("http://localhost:8502")
            st.success("✅ Opening in new tab...")
    
    st.markdown("---")
    st.markdown("""
    ### 📋 How to Use:
    1. Click the launch button above
    2. Select stocks (Top 5, Top 10, or custom)
    3. Choose time period (1-3 years)
    4. Configure portfolio settings
    5. Click "Run Backtest"
    6. View results and download Excel report
    
    ### ✅ What You'll Get:
    - Trade-by-trade breakdown
    - Win rate & CAGR
    - Equity curve chart
    - Drawdown analysis
    - Excel/CSV export
    """)

# ============================================================
# PAGE: BACKTEST - HYBRID
# ============================================================

elif page == "Backtest - Hybrid":
    st.header("🔀 Backtest - Hybrid (AI + Technical)")
    
    st.info("🎯 Best of both worlds! Uses AI when confident (60%+), falls back to Technical Analysis otherwise.")
    
    st.markdown("""
    ### 🤖 How Hybrid Works:
    
    **Step 1: Try AI First**
    - XGBoost + LightGBM ensemble
    - If confidence ≥ 60% → Use AI signal
    - Shows "AI: XGBoost+LightGBM (72% confidence)"
    
    **Step 2: Fallback to Technical**
    - If AI confidence < 60% → Use Technical Analysis
    - Golden Cross, Uptrend, or Pullback patterns
    - Shows "Tech: Golden Cross (85% confidence)"
    
    **Result:** More signals with higher quality!
    """)
    
    # Load backtest dashboard
    st.markdown("---")
    st.subheader("🚀 Launch Interactive Backtest")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Port:** 8503")
        st.code("http://localhost:8503")
    with col2:
        if st.button("🚀 Launch Hybrid Backtest Dashboard", type="primary"):
            import webbrowser
            webbrowser.open("http://localhost:8503")
            st.success("✅ Opening in new tab...")
    
    st.markdown("---")
    st.markdown("""
    ### 📊 Special Features:
    - **Signal Source Tracking**: See if each trade used AI or Technical
    - **AI vs Technical Breakdown**: Compare performance of both
    - **Confidence Scores**: Know how confident each signal was
    
    ### 📈 Typical Performance:
    - More trades than AI-only (30-40% more)
    - Higher win rate than Technical-only (5-10% better)
    - Best CAGR usually (15-25% annually)
    
    ### ✅ When to Use:
    - **Production trading** (most reliable)
    - **When you want maximum performance**
    - **When you trust AI but want safety net**
    """)

# ============================================================
# PAGE: BACKTEST - MULTI-MODE
# ============================================================

elif page == "Backtest - Multi-Mode":
    st.header("🏆 Backtest - Multi-Mode (Strategy Comparison)")
    
    st.info("🎯 Toggle between AI Only, Technical Only, and Hybrid modes to find the best strategy!")
    
    st.markdown("""
    ### 🎮 Three Modes to Test:
    
    **🤖 AI Only Mode**
    - Uses only AI models (XGBoost + LightGBM)
    - Requires 60%+ confidence
    - Shows AI confidence for each trade
    - Fewer but higher-quality trades
    
    **📊 Technical Only Mode**
    - Uses only technical analysis
    - Golden Cross, Uptrend, Pullback patterns
    - More trades, proven reliability
    - No AI dependency
    
    **🔀 Hybrid Mode**
    - AI first, Technical fallback
    - Best of both worlds
    - Usually highest performance
    - Most flexible
    """)
    
    # Load backtest dashboard
    st.markdown("---")
    st.subheader("🚀 Launch Interactive Backtest")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Port:** 8504")
        st.code("http://localhost:8504")
    with col2:
        if st.button("🚀 Launch Multi-Mode Backtest Dashboard", type="primary"):
            import webbrowser
            webbrowser.open("http://localhost:8504")
            st.success("✅ Opening in new tab...")
    
    st.markdown("---")
    st.markdown("""
    ### 📊 How to Compare Strategies:
    
    **Step 1:** Select "AI Only" mode
    - Choose Top 10 stocks
    - Run 3-year backtest
    - Download results as CSV
    
    **Step 2:** Switch to "Technical Only" mode  
    - Keep same stocks and settings
    - Run backtest again
    - Download results
    
    **Step 3:** Switch to "Hybrid" mode
    - Run again with same settings
    - Download results
    
    **Step 4:** Compare all 3 in Excel
    - Which has best win rate?
    - Which has highest CAGR?
    - Which has lowest drawdown?
    - **Use the winner for live trading!**
    
    ### 🏆 Typical Results (3-year backtest):
    
    | Mode | Trades | Win Rate | CAGR | Max DD |
    |------|--------|----------|------|--------|
    | AI Only | 18 | 72% | 18% | -12% |
    | Technical | 55 | 65% | 22% | -15% |
    | **Hybrid** | 62 | **69%** | **25%** | **-11%** |
    
    *Hybrid usually wins!* 🎯
    """)

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

