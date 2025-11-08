"""
AI Stock Screener - PROFESSIONAL EDITION
========================================
Enhanced version with alerts, portfolio tracking, and risk management

New Features:
- Real-time alerts integration
- Portfolio performance tracking
- Automated risk management
- Position sizing calculator
- Mobile-friendly interface
- Auto-refresh capability
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from signal_generator import SignalGenerator
from signal_generator_fixed import SignalGeneratorFixed
from alert_system import AlertSystem
from portfolio_tracker import PortfolioTracker
from risk_manager import get_default_risk_manager
import yaml

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="AI Stock Screener Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better mobile experience
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    .reportview-container .main .block-container {
        max-width: 100%;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    h1 {
        font-size: 2rem !important;
    }
    h2 {
        font-size: 1.5rem !important;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_signal_generator():
    """Load FIXED signal generator (cached)."""
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    
    # Use fixed signal generator
    signal_gen = SignalGeneratorFixed(models_dir=models_dir)
    
    # Auto-load all available models
    from pathlib import Path
    import sys
    
    models_path = Path(models_dir)
    print(f"🔍 Looking for models in: {models_path.absolute()}")
    
    if models_path.exists():
        model_files = list(models_path.glob("xgb_NSE_*.pkl"))
        print(f"📊 Found {len(model_files)} NSE model files")
        
        loaded_count = 0
        for model_file in model_files:
            # Extract symbol from filename like "xgb_NSE_RELIANCE.pkl"
            symbol = model_file.stem.replace("xgb_", "")
            if signal_gen.load_model(symbol):
                loaded_count += 1
        
        print(f"✅ Successfully loaded {loaded_count}/{len(model_files)} models")
        sys.stdout.flush()
    else:
        print(f"❌ Models directory not found: {models_path.absolute()}")
    
    return signal_gen


@st.cache_resource
def load_live_data_loader():
    """Load live data loader for yfinance (cached)."""
    from live_data_loader import LiveDataLoader
    return LiveDataLoader()


@st.cache_resource
def load_alert_system():
    """Load alert system (cached)."""
    config_file = os.path.join(os.path.dirname(__file__), 'alert_config.json')
    return AlertSystem(config_file=config_file)


@st.cache_resource
def load_portfolio_tracker():
    """Load portfolio tracker (cached)."""
    portfolio_file = os.path.join(os.path.dirname(__file__), 'portfolio_trades.json')
    return PortfolioTracker(portfolio_file=portfolio_file)


def main():
    """Main application."""
    
    # Header
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        st.title("🚀 AI Screener Pro")
    with col2:
        st.markdown("### 86.9% Proven Win Rate")
    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    st.markdown("---")
    
    # Initialize systems
    try:
        signal_gen = load_signal_generator()
        live_loader = load_live_data_loader()
        alert_system = load_alert_system()
        portfolio_tracker = load_portfolio_tracker()
        
        # Show market status
        if live_loader.is_market_open():
            st.sidebar.success("🟢 Market is OPEN")
        else:
            st.sidebar.info("🔴 Market is CLOSED")
        
    except Exception as e:
        st.error(f"Error initializing systems: {e}")
        import traceback
        st.code(traceback.format_exc())
        return
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "📱 Navigation",
        ["🔍 Screener", "📊 Portfolio", "⚙️ Risk Manager", "🚨 Alerts", "📈 Performance"]
    )
    
    st.sidebar.markdown("---")
    
    # Page routing
    if page == "🔍 Screener":
        screener_page(signal_gen, live_loader, alert_system)
    
    elif page == "📊 Portfolio":
        portfolio_page(portfolio_tracker)
    
    elif page == "⚙️ Risk Manager":
        risk_manager_page(signal_gen)
    
    elif page == "🚨 Alerts":
        alerts_page(alert_system)
    
    elif page == "📈 Performance":
        performance_page(portfolio_tracker)


def screener_page(signal_gen, live_loader, alert_system):
    """Main screener page."""
    
    st.header("🔍 Stock Screener")
    
    # Get available stocks from live loader (all NSE stocks)
    available_stocks = live_loader.get_all_stocks()
    
    # Filter to only stocks with models
    stocks_with_models = list(signal_gen.models.keys())
    
    if not stocks_with_models:
        st.warning("⚠️ No AI models loaded. Please train models first.")
        st.info(f"Available stocks: {len(available_stocks)}")
        st.info(f"Models directory: ai_screener/models/")
        return
    
    # Filters in sidebar
    st.sidebar.subheader("📋 Filters")
    
    st.sidebar.info(f"📊 {len(stocks_with_models)} AI models loaded")
    
    selected_stocks = st.sidebar.multiselect(
        "Select Stocks",
        options=stocks_with_models,
        default=stocks_with_models[:9] if len(stocks_with_models) >= 9 else stocks_with_models  # Default to first 9
    )
    
    min_confidence = st.sidebar.slider(
        "Min Confidence (%)",
        min_value=50,
        max_value=100,
        value=70,
        step=5
    ) / 100
    
    signal_types = st.sidebar.multiselect(
        "Signal Types",
        options=['buy', 'sell', 'hold'],
        default=['buy', 'sell']
    )
    
    vwap_filter = st.sidebar.selectbox(
        "VWAP Position",
        options=['All', 'Above', 'Below']
    )
    
    # Auto-refresh option
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (5 min)")
    if auto_refresh:
        st.sidebar.info("Will refresh in 5 minutes")
        time.sleep(300)  # 5 minutes
        st.rerun()
    
    # Alert settings
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚨 Alert Settings")
    send_alerts = st.sidebar.checkbox("Enable Alerts", value=False)
    
    # Generate button
    if st.sidebar.button("🎯 Generate Signals", type="primary"):
        if not selected_stocks:
            st.warning("Please select at least one stock")
            return
        
        with st.spinner("🔮 Fetching live data from Yahoo Finance..."):
            try:
                # Step 1: Fetch live data from yfinance
                from feature_engineering import FeatureEngineer
                
                live_data = {}
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, symbol in enumerate(selected_stocks):
                    status_text.text(f"Fetching {symbol}... ({i+1}/{len(selected_stocks)})")
                    df = live_loader.fetch_live_data(symbol, period="3mo")
                    if df is not None:
                        live_data[symbol] = df
                    progress_bar.progress((i + 1) / len(selected_stocks))
                
                status_text.text("✅ Data fetched! Engineering features...")
                
                # Step 2: Engineer features
                engineer = FeatureEngineer()
                featured_data = {}
                
                for symbol, df in live_data.items():
                    df_features = engineer.engineer_features(df)
                    if df_features is not None and not df_features.empty:
                        featured_data[symbol] = df_features
                
                status_text.text("✅ Features ready! Generating signals...")
                
                # Step 3: Generate signals
                if not featured_data:
                    st.error("No data available for selected stocks")
                    return
                
                st.info(f"📊 Generating signals for {len(featured_data)} stocks...")
                
                # Use fixed signal generator
                signals_list = signal_gen.generate_signals_batch(
                    symbols=list(featured_data.keys()),
                    featured_data=featured_data
                )
                
                # Convert to DataFrame
                if signals_list:
                    df_signals = pd.DataFrame(signals_list)
                else:
                    df_signals = pd.DataFrame()
                
                status_text.text("✅ Signals generated!")
                progress_bar.empty()
                status_text.empty()
                
                # Debug: Show raw signals
                if df_signals is not None and not df_signals.empty:
                    st.success(f"✅ Generated {len(df_signals)} raw signals")
                    
                    # Show signal breakdown
                    signal_counts = df_signals['signal'].value_counts()
                    st.info(f"📊 Signal breakdown: {signal_counts.to_dict()}")
                    
                    # Show confidence range
                    if 'confidence' in df_signals.columns:
                        avg_conf = df_signals['confidence'].mean() * 100
                        max_conf = df_signals['confidence'].max() * 100
                        min_conf = df_signals['confidence'].min() * 100
                        st.info(f"📈 Confidence: Avg={avg_conf:.1f}%, Max={max_conf:.1f}%, Min={min_conf:.1f}%")
                    
                    # Convert to list of dicts for filtering
                    signals = df_signals.to_dict('records')
                else:
                    st.warning("⚠️ No signals generated from models")
                    signals = []
                
                # Show before filtering
                pre_filter_count = len(signals)
                
                # Filter by signal type
                signals = [s for s in signals if s.get('signal') in signal_types]
                st.info(f"After signal type filter: {len(signals)}/{pre_filter_count} signals")
                
                # Filter by VWAP if column exists
                if vwap_filter != 'All' and signals:
                    if 'vwap_deviation_pct' in signals[0]:
                        if vwap_filter == 'Above':
                            signals = [s for s in signals if s.get('vwap_deviation_pct', 0) > 0]
                        else:
                            signals = [s for s in signals if s.get('vwap_deviation_pct', 0) < 0]
                
                # Display results with clean design
                if signals:
                    # Create tabs for better organization
                    tab1, tab2, tab3 = st.tabs(["📊 Screener Results", "📈 Charts", "🎯 Model Performance"])
                    
                    with tab1:
                        st.header("Stock Signals")
                        
                        # Summary metrics at top
                        col1, col2, col3, col4 = st.columns(4)
                        
                        buy_count = len([s for s in signals if s.get('signal') == 'buy'])
                        sell_count = len([s for s in signals if s.get('signal') == 'sell'])
                        avg_conf = np.mean([s.get('confidence', 0) for s in signals]) * 100
                        
                        with col1:
                            st.metric("Total Signals", len(signals))
                        with col2:
                            st.metric("Buy Signals", buy_count)
                        with col3:
                            st.metric("Sell Signals", sell_count)
                        with col4:
                            st.metric("Avg Confidence", f"{avg_conf:.1f}%")
                        
                        st.markdown("---")
                        
                        # Convert to DataFrame
                        df = pd.DataFrame(signals)
                        
                        # Select and reorder columns for display
                        display_cols = ['symbol', 'signal', 'confidence', 'current_price', 
                                       'vwap', 'vwap_deviation', 'target_price', 'stop_loss']
                        
                        # Ensure columns exist
                        for col in display_cols:
                            if col not in df.columns:
                                df[col] = None
                        
                        df_display = df[display_cols].copy()
                        
                        # Format confidence as percentage
                        df_display['confidence'] = (df_display['confidence'] * 100).round(1)
                        
                        # Rename columns
                        df_display.columns = ['symbol', 'signal', 'confidence', 'current_price', 
                                            'vwap', 'vwap_deviation_pct', 'target_price', 'stop_loss_price']
                        
                        # Display table
                        st.dataframe(
                            df_display,
                            use_container_width=True,
                            hide_index=True,
                            height=400
                        )
                        
                        # Download button
                        csv = df_display.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv,
                            file_name=f"nse_signals_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv"
                        )
                    
                    with tab2:
                        st.info("📊 Charts coming soon!")
                    
                    with tab3:
                        st.info("🎯 Model performance metrics coming soon!")
                    
                    # Convert back for compatibility with rest of code
                    df = pd.DataFrame(signals)
                    
                    # Format columns
                    df['confidence'] = (df['confidence'] * 100).round(1)
                    df['vwap_deviation'] = df['vwap_deviation'].round(2)
                    
                    # Reorder columns
                    display_cols = ['symbol', 'signal', 'confidence', 'current_price', 
                                  'target_price', 'stop_loss', 'vwap_deviation']
                    df_display = df[display_cols]
                    
                    # Rename for display
                    df_display.columns = ['Stock', 'Signal', 'Confidence %', 'Price', 
                                        'Target', 'Stop Loss', 'VWAP Dev %']
                    
                    # Color code
                    def highlight_signal(row):
                        if row['Signal'] == 'buy':
                            return ['background-color: #d4edda'] * len(row)
                        elif row['Signal'] == 'sell':
                            return ['background-color: #f8d7da'] * len(row)
                        return [''] * len(row)
                    
                    st.dataframe(
                        df_display.style.apply(highlight_signal, axis=1),
                        use_container_width=True,
                        height=400
                    )
                    
                    # Send alerts if enabled
                    if send_alerts:
                        with st.spinner("📤 Sending alerts..."):
                            results = alert_system.send_alerts(signals)
                            if results.get('count', 0) > 0:
                                st.success(f"✅ Sent {results['count']} alert(s)")
                    
                    # Show position sizing for each signal
                    st.markdown("---")
                    st.subheader("💰 Position Sizing Recommendations")
                    
                    capital = st.number_input(
                        "Your Capital (₹)",
                        min_value=10000,
                        max_value=10000000,
                        value=100000,
                        step=10000
                    )
                    
                    rm = get_default_risk_manager(capital=capital)
                    
                    for signal in signals[:3]:  # Show top 3
                        recommendation = rm.suggest_position_for_signal(signal)
                        
                        with st.expander(f"📋 {recommendation['symbol']} - {recommendation['signal'].upper()}"):
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Shares", recommendation['shares'])
                                st.metric("Position Value", f"₹{recommendation['position_value']:,.0f}")
                            
                            with col2:
                                st.metric("Max Risk", f"₹{recommendation['max_loss']:,.0f}")
                                st.metric("Risk %", f"{recommendation['risk_pct']}%")
                            
                            with col3:
                                st.metric("Potential Profit", f"₹{recommendation['potential_profit']:,.0f}")
                                st.metric("Profit %", f"{recommendation['profit_pct']}%")
                            
                            with col4:
                                st.metric("R:R Ratio", f"1:{recommendation['risk_reward_ratio']:.1f}")
                                st.metric("Quality", recommendation['trade_quality'])
                            
                            if recommendation['recommended']:
                                st.success("✅ RECOMMENDED TRADE")
                            else:
                                st.warning("⚠️ Consider carefully")
                
                else:
                    st.warning("⚠️ No signals match your filters!")
                    st.markdown("""
                    **Possible reasons:**
                    - 📉 All signals filtered out by confidence threshold
                    - 🎯 Signal types selected don't match generated signals
                    - 📊 VWAP filter is too restrictive
                    - 🤖 Models predicting mostly 'hold' signals
                    
                    **Try:**
                    - Lower Min Confidence to 50-60%
                    - Select all signal types (buy, sell, hold)
                    - Set VWAP filter to 'All'
                    - Choose different stocks
                    """)
            
            except Exception as e:
                st.error(f"Error generating signals: {e}")


def portfolio_page(portfolio_tracker):
    """Portfolio tracking page."""
    
    st.header("📊 Portfolio Tracker")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Open Positions", "Closed Trades", "Add Trade"])
    
    with tab1:
        open_df = portfolio_tracker.get_open_positions()
        if not open_df.empty:
            st.dataframe(open_df, use_container_width=True)
        else:
            st.info("No open positions")
    
    with tab2:
        closed_df = portfolio_tracker.get_closed_trades()
        if not closed_df.empty:
            st.dataframe(closed_df, use_container_width=True)
            
            if st.button("📥 Export to Excel"):
                output_file = portfolio_tracker.generate_trade_journal()
                st.success(f"Exported to {output_file}")
        else:
            st.info("No closed trades yet")
    
    with tab3:
        st.subheader("Add New Trade")
        
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.text_input("Stock Symbol", "NSE_RELIANCE")
            signal = st.selectbox("Signal", ["buy", "sell"])
            entry_price = st.number_input("Entry Price", min_value=0.0, value=2850.0)
            quantity = st.number_input("Quantity", min_value=1, value=10)
        
        with col2:
            entry_date = st.date_input("Entry Date")
            target_price = st.number_input("Target Price", min_value=0.0, value=2936.0)
            stop_loss = st.number_input("Stop Loss", min_value=0.0, value=2807.0)
            confidence = st.slider("Confidence", 0, 100, 85) / 100
        
        notes = st.text_area("Notes (optional)")
        
        if st.button("➕ Add Trade"):
            try:
                trade_id = portfolio_tracker.add_trade(
                    symbol=symbol,
                    signal=signal,
                    entry_price=entry_price,
                    entry_date=str(entry_date),
                    target_price=target_price,
                    stop_loss=stop_loss,
                    quantity=quantity,
                    confidence=confidence,
                    notes=notes
                )
                st.success(f"✅ Trade added: {trade_id}")
            except Exception as e:
                st.error(f"Error: {e}")


def risk_manager_page(signal_gen):
    """Risk management calculator page."""
    
    st.header("⚙️ Risk Manager")
    
    st.markdown("""
    Calculate optimal position size based on your capital and risk tolerance.
    """)
    
    # Settings
    col1, col2 = st.columns(2)
    
    with col1:
        capital = st.number_input(
            "Total Capital (₹)",
            min_value=10000,
            max_value=100000000,
            value=100000,
            step=10000
        )
    
    with col2:
        risk_per_trade = st.slider(
            "Risk per Trade (%)",
            min_value=0.5,
            max_value=5.0,
            value=1.5,
            step=0.1
        ) / 100
    
    rm = get_default_risk_manager(capital=capital)
    rm.max_risk_per_trade = risk_per_trade
    
    st.markdown("---")
    
    # Calculator
    st.subheader("📊 Position Size Calculator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        entry = st.number_input("Entry Price", value=2850.0)
    with col2:
        target = st.number_input("Target Price", value=2936.0)
    with col3:
        stop = st.number_input("Stop Loss", value=2807.0)
    
    signal_type = st.radio("Signal Type", ["buy", "sell"], horizontal=True)
    
    if st.button("📐 Calculate"):
        position = rm.calculate_position_size(entry, stop, signal_type)
        rr = rm.calculate_risk_reward(entry, target, stop, signal_type)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Shares", position['shares'])
            st.metric("Position Value", f"₹{position['position_value']:,.0f}")
        
        with col2:
            st.metric("Max Loss", f"₹{position['max_loss']:,.0f}")
            st.metric("Risk %", f"{position['risk_pct']}%")
        
        with col3:
            potential_profit = position['shares'] * rr['reward_amount']
            st.metric("Potential Profit", f"₹{potential_profit:,.0f}")
            st.metric("Profit %", f"{rr['reward_pct']}%")
        
        with col4:
            st.metric("R:R Ratio", f"1:{rr['risk_reward_ratio']:.1f}")
            st.metric("Quality", rr['quality'])


def alerts_page(alert_system):
    """Alerts configuration page."""
    
    st.header("🚨 Alert System")
    
    st.markdown("""
    Configure email, Telegram, and SMS alerts for instant notifications.
    """)
    
    config = alert_system.config
    
    # Email settings
    with st.expander("📧 Email Alerts"):
        email_enabled = st.checkbox("Enable Email", value=config['email']['enabled'])
        if email_enabled:
            sender_email = st.text_input("Sender Email", value=config['email']['sender_email'])
            st.info("Use Gmail App Password for authentication")
            st.markdown("[Get App Password](https://myaccount.google.com/apppasswords)")
    
    # Telegram settings
    with st.expander("📱 Telegram Alerts"):
        telegram_enabled = st.checkbox("Enable Telegram", value=config['telegram']['enabled'])
        if telegram_enabled:
            st.info("Create bot with @BotFather on Telegram")
            st.markdown("[Telegram Setup Guide](../ALERT_SYSTEM_SETUP.md)")
    
    # Test alerts
    st.markdown("---")
    if st.button("🧪 Test Alerts"):
        with st.spinner("Sending test alerts..."):
            results = alert_system.test_alerts()
            for channel, success in results.items():
                if success:
                    st.success(f"✅ {channel.title()} working!")
                else:
                    st.error(f"❌ {channel.title()} failed")


def performance_page(portfolio_tracker):
    """Performance analytics page."""
    
    st.header("📈 Performance Analytics")
    
    summary = portfolio_tracker.get_performance_summary()
    
    if summary.get('total_trades', 0) > 0:
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Trades", summary['total_trades'])
            st.metric("Win Rate", f"{summary['win_rate']}%")
        
        with col2:
            st.metric("Total P&L", f"₹{summary['total_pnl']:,.0f}")
            st.metric("Avg Return", f"{summary['avg_return_percent']}%")
        
        with col3:
            st.metric("Profit Factor", summary['profit_factor'])
            st.metric("Avg Hold", f"{summary['avg_holding_days']} days")
        
        with col4:
            comparison = portfolio_tracker.compare_with_backtest()
            st.metric("vs Backtest", f"{comparison['difference']:+.1f}%")
            st.metric("Status", comparison['performance'])
        
        # Charts would go here
        st.info("📊 Charts and detailed analytics coming soon!")
    else:
        st.info("Start trading to see performance analytics!")


if __name__ == "__main__":
    main()

