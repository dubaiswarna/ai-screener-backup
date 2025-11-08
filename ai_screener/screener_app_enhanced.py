"""
Enhanced AI Stock Screener - WITH DATABASE & RISK MANAGEMENT
=============================================================
Uses your existing 50+ AI models + adds professional features
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yaml
import sys
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import existing modules (YOUR AI models!)
from data_loader import DataLoader
from feature_engineering import FeatureEngineer
from signal_generator_fixed import SignalGeneratorFixed
from live_data_loader import LiveDataLoader

# Import NEW professional modules
try:
    from database.db_manager import get_db
    from risk_management.risk_engine import RiskEngine
    DATABASE_AVAILABLE = True
except Exception as e:
    DATABASE_AVAILABLE = False
    st.warning(f"⚠️ Database features disabled: {e}")

# Page config
st.set_page_config(
    page_title='Professional AI Stock Screener',
    page_icon='🚀',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .signal-card {
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid;
        margin: 0.5rem 0;
    }
    .signal-buy { border-color: #00ff00; background: rgba(0,255,0,0.1); }
    .signal-sell { border-color: #ff0000; background: rgba(255,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# ============================================================
# INITIALIZE SERVICES
# ============================================================

@st.cache_resource
def init_services():
    """Initialize all services."""
    services = {
        'database': None,
        'risk_engine': None,
        'models_loaded': 0
    }
    
    # Initialize database
    if DATABASE_AVAILABLE:
        try:
            db = get_db()
            services['database'] = db
            
            # Get user config
            config = db.get_user_config()
            capital = config.get('total_capital', 1000000)
            
            # Initialize risk engine
            services['risk_engine'] = RiskEngine(total_capital=capital)
            st.sidebar.success("✅ Database & Risk Engine: Connected")
        except Exception as e:
            st.sidebar.warning(f"⚠️ Database: {e}")
    
    return services

# Initialize
services = init_services()

# Load YOUR AI models
@st.cache_resource  
def load_models():
    """Load all YOUR trained AI models."""
    models_dir = Path(__file__).parent / 'models'
    signal_gen = SignalGeneratorFixed(models_dir=str(models_dir))
    
    # Auto-load all NSE models
    if models_dir.exists():
        model_files = list(models_dir.glob("xgb_NSE_*.pkl"))
        for model_file in model_files:
            symbol = model_file.stem.replace("xgb_", "")
            signal_gen.load_model(symbol)
    
    return signal_gen

signal_gen = load_models()

# ============================================================
# HEADER
# ============================================================

st.markdown('<div class="main-header"><h1>🚀 PROFESSIONAL AI STOCK SCREENER v3.0</h1><p>Your 50+ AI Models + Database Persistence + Risk Management</p></div>', unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title('⚙️ Control Panel')

# System Status
st.sidebar.subheader('📊 System Status')
st.sidebar.success(f"✅ AI Models: {len(signal_gen.models)} loaded")

if DATABASE_AVAILABLE and services['database']:
    if services['database'].test_connection():
        st.sidebar.success("✅ Database: Connected")
        st.sidebar.info("📝 Signals will PERSIST!")
    else:
        st.sidebar.warning("⚠️ Database: Not connected")
else:
    st.sidebar.info("ℹ️ Running without database")

if services['risk_engine']:
    st.sidebar.success("✅ Risk Engine: Active")
    capital = services['risk_engine'].total_capital
    st.sidebar.info(f"💰 Capital: ₹{capital:,.0f}")

# Stock selection
st.sidebar.subheader('🎯 Stock Selection')
stocks = sorted(signal_gen.models.keys())

selected_stocks = st.sidebar.multiselect(
    'Select Stocks',
    options=stocks,
    default=stocks[:min(10, len(stocks))],
    help='Select stocks to screen with AI models'
)

# Filters
st.sidebar.subheader('📊 Signal Filters')
min_confidence = st.sidebar.slider(
    'Min Confidence (%)',
    0, 100, 70, 5,
    help='Minimum AI confidence to show'
)

signal_types = st.sidebar.multiselect(
    'Signal Types',
    ['BUY', 'SELL', 'HOLD'],
    default=['BUY', 'SELL']
)

# ============================================================
# MAIN SCREEN
# ============================================================

if not selected_stocks:
    st.warning("⚠️ Please select at least one stock from the sidebar")
    st.stop()

# Run Screening Button
if st.button('🎯 RUN AI SCREENING', type='primary', use_container_width=True):
    
    with st.spinner('🤖 Running AI analysis on selected stocks...'):
        
        # Fetch live data & engineer features
        live_loader = LiveDataLoader()
        engineer = FeatureEngineer()
        featured_data = {}
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, symbol in enumerate(selected_stocks):
            status_text.text(f"📊 Processing {symbol}... ({i+1}/{len(selected_stocks)})")
            
            # Fetch data
            df = live_loader.fetch_live_data(symbol, period="3mo")
            if df is not None and not df.empty:
                # Engineer features (YOUR feature engineering!)
                df_features = engineer.engineer_features(df)
                if df_features is not None and not df_features.empty:
                    featured_data[symbol] = df_features
            
            progress_bar.progress((i + 1) / len(selected_stocks))
        
        status_text.text("🤖 Generating AI signals...")
        
        # Generate signals using YOUR AI models!
        signals_list = signal_gen.generate_signals_batch(
            symbols=list(featured_data.keys()),
            featured_data=featured_data
        )
        
        if signals_list:
            df_signals = pd.DataFrame(signals_list)
            
            # ============================================================
            # NEW: ADD RISK MANAGEMENT TO EACH SIGNAL
            # ============================================================
            
            if services['risk_engine']:
                risk_data = []
                for idx, row in df_signals.iterrows():
                    # Calculate position size with risk management
                    entry_price = row.get('current_price', 0)
                    
                    # Estimate stop loss (5% below for BUY, 5% above for SELL)
                    if row['signal'] == 'BUY':
                        stop_loss = entry_price * 0.95
                        target = entry_price * 1.10
                    elif row['signal'] == 'SELL':
                        stop_loss = entry_price * 1.05
                        target = entry_price * 0.90
                    else:
                        stop_loss = entry_price
                        target = entry_price
                    
                    # Calculate optimal position size
                    position = services['risk_engine'].calculate_position_size(
                        entry_price=entry_price,
                        stop_loss=stop_loss,
                        confidence=row['confidence']
                    )
                    
                    risk_data.append({
                        'recommended_qty': position.get('quantity', 0),
                        'position_size': position.get('position_size', 0),
                        'risk_amount': position.get('risk_amount', 0),
                        'risk_pct': position.get('risk_pct', 2.0),
                        'stop_loss': stop_loss,
                        'target': target
                    })
                
                df_risk = pd.DataFrame(risk_data)
                df_signals = pd.concat([df_signals, df_risk], axis=1)
                
                st.success("✅ Risk management calculated for all signals!")
            
            # ============================================================
            # NEW: SAVE SIGNALS TO DATABASE
            # ============================================================
            
            if DATABASE_AVAILABLE and services['database']:
                saved_count = 0
                
                # Convert DataFrame to dict records for easier handling
                signals_dict = df_signals.to_dict('records')
                
                for signal in signals_dict:
                    try:
                        # Get values as scalars
                        entry = float(signal.get('current_price', 0))
                        target = float(signal.get('target', 0))
                        sl = float(signal.get('stop_loss', 0))
                        conf = float(signal.get('confidence', 0))
                        
                        # Calculate risk/reward
                        if sl > 0 and entry > 0 and abs(entry - sl) > 0:
                            rr_ratio = abs((target - entry) / (entry - sl))
                        else:
                            rr_ratio = 0
                        
                        signal_data = {
                            'symbol': str(signal.get('symbol', '')),
                            'signal_type': str(signal.get('signal', 'HOLD')).upper(),
                            'confidence': conf * 100,
                            'entry_price': entry,
                            'target_price': target,
                            'stop_loss': sl,
                            'model_name': f"xgb_{signal.get('symbol', '')}",
                            'signal_strength': 'STRONG' if conf > 0.8 else 'MEDIUM' if conf > 0.7 else 'WEAK',
                            'volume': int(signal.get('volume', 0)),
                            'risk_reward_ratio': rr_ratio,
                            'position_size': float(signal.get('position_size', 0)),
                            'max_risk_amount': float(signal.get('risk_amount', 0)),
                            'valid_until': datetime.now() + timedelta(days=1)
                        }
                        
                        signal_id = services['database'].save_signal(signal_data)
                        if signal_id:
                            saved_count += 1
                    except Exception as e:
                        logger.error(f"Could not save {signal.get('symbol')}: {e}")
                        continue
                
                if saved_count > 0:
                    st.success(f"✅ Saved {saved_count} signals to database! (Will persist after refresh!)")
            
            # Apply filters
            df_filtered = df_signals[df_signals['confidence'] >= min_confidence / 100]
            df_filtered = df_filtered[df_filtered['signal'].str.upper().isin([s.upper() for s in signal_types])]
            
            # Clear progress
            progress_bar.empty()
            status_text.empty()
            
            # ============================================================
            # DISPLAY RESULTS
            # ============================================================
            
            st.markdown("---")
            st.subheader('🎯 AI Screening Results')
            
            if not df_filtered.empty:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric('Total Signals', len(df_filtered))
                with col2:
                    buy_count = len(df_filtered[df_filtered['signal'].str.upper() == 'BUY'])
                    st.metric('Buy Signals', buy_count)
                with col3:
                    sell_count = len(df_filtered[df_filtered['signal'].str.upper() == 'SELL'])
                    st.metric('Sell Signals', sell_count)
                with col4:
                    avg_conf = df_filtered['confidence'].mean()
                    st.metric('Avg Confidence', f"{avg_conf:.1%}")
                
                st.markdown("---")
                
                # Display each signal as card
                for idx, row in df_filtered.iterrows():
                    signal_type = row['signal'].upper()
                    color = 'green' if signal_type == 'BUY' else 'red' if signal_type == 'SELL' else 'gray'
                    
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                        
                        with col1:
                            st.markdown(f"### {row['symbol']}")
                            st.markdown(f"**Signal:** <span style='color:{color};font-size:1.2em;font-weight:bold'>{signal_type}</span>", unsafe_allow_html=True)
                        
                        with col2:
                            try:
                                price_val = float(row['current_price']) if 'current_price' in row else 0
                                conf_val = float(row['confidence'])
                                st.metric("Price", f"₹{price_val:,.2f}")
                                st.caption(f"Confidence: {conf_val:.1%}")
                            except:
                                st.metric("Price", "N/A")
                        
                        with col3:
                            try:
                                if 'recommended_qty' in row:
                                    qty_val = int(row['recommended_qty'])
                                    size_val = float(row['position_size']) if 'position_size' in row else 0
                                    st.metric("Qty", qty_val)
                                    st.caption(f"Size: ₹{size_val:,.0f}")
                            except:
                                pass
                        
                        with col4:
                            try:
                                if 'risk_amount' in row:
                                    risk_val = float(row['risk_amount'])
                                    risk_pct_val = float(row['risk_pct']) if 'risk_pct' in row else 0
                                    st.metric("Max Risk", f"₹{risk_val:,.0f}")
                                    st.caption(f"({risk_pct_val:.2f}% of capital)")
                            except:
                                pass
                        
                        # Expandable details
                        with st.expander("📊 View Details"):
                            detail_col1, detail_col2 = st.columns(2)
                            with detail_col1:
                                try:
                                    entry_val = float(row['current_price']) if 'current_price' in row else 0
                                    target_val = float(row['target']) if 'target' in row else 0  
                                    sl_val = float(row['stop_loss']) if 'stop_loss' in row else 0
                                except:
                                    entry_val = target_val = sl_val = 0
                                st.write(f"**Entry:** ₹{entry_val:,.2f}")
                                st.write(f"**Target:** ₹{target_val:,.2f}")
                                st.write(f"**Stop Loss:** ₹{sl_val:,.2f}")
                            with detail_col2:
                                try:
                                    vol_val = int(row['volume']) if 'volume' in row else 0
                                    vwap_val = float(row.get('vwap_deviation_pct', 0)) if 'vwap_deviation_pct' in row else 0
                                except:
                                    vol_val = 0
                                    vwap_val = 0
                                st.write(f"**Volume:** {vol_val:,.0f}")
                                st.write(f"**VWAP Dev:** {vwap_val:.2f}%")
                                st.write(f"**Model:** xgb_{row['symbol']}")
                        
                        st.markdown("---")
                
                # Download option
                st.download_button(
                    label='📥 Download All Signals as CSV',
                    data=df_filtered.to_csv(index=False),
                    file_name=f'ai_signals_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    mime='text/csv',
                    use_container_width=True
                )
                
            else:
                st.info("ℹ️ No signals match your filters. Try adjusting criteria.")
        else:
            st.error("❌ Could not generate signals. Check if data is available.")

# ============================================================
# SIDEBAR: VIEW SAVED SIGNALS
# ============================================================

if DATABASE_AVAILABLE and services['database']:
    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 Saved Signals")
    
    if st.sidebar.button("📋 View All Saved Signals"):
        saved_signals = services['database'].get_active_signals(min_confidence=50)
        
        if saved_signals:
            st.sidebar.success(f"Found {len(saved_signals)} saved signals")
            st.sidebar.info("These persist even after refresh!")
            
            # Show in expandable
            with st.sidebar.expander(f"View {len(saved_signals)} Signals"):
                for sig in saved_signals[:10]:  # Show last 10
                    st.write(f"**{sig['symbol']}** - {sig['signal_type']}")
                    st.caption(f"{sig['confidence']:.1f}% conf | {sig['generated_at']}")
        else:
            st.sidebar.info("No saved signals yet. Run screening to generate!")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div style='text-align:center;color:gray;padding:1rem;'>
    <strong>Professional AI Screener v3.0</strong> | 
    {models} AI Models Loaded | 
    Database: {db_status} | 
    Risk Management: {risk_status}
</div>
""".format(
    models=len(signal_gen.models),
    db_status="✅ Active" if DATABASE_AVAILABLE else "⚠️ Disabled",
    risk_status="✅ Active" if services['risk_engine'] else "⚠️ Disabled"
), unsafe_allow_html=True)

