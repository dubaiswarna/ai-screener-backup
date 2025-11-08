"""
AI Stock Screener - FINAL VERSION
==================================
Your 42 AI Models + Database Persistence + Risk Management
CLEAN & SIMPLE - Everything in one place!
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

# Import YOUR existing modules
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

# Page config
st.set_page_config(
    page_title='AI Stock Screener - Professional',
    page_icon='🚀',
    layout='wide'
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        border: none;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# INITIALIZE
# ============================================================

@st.cache_resource
def init_system():
    """Initialize database and risk engine."""
    services = {'database': None, 'risk_engine': None}
    
    if DATABASE_AVAILABLE:
        try:
            db = get_db()
            config = db.get_user_config()
            capital = config.get('total_capital', 1000000)
            services['database'] = db
            services['risk_engine'] = RiskEngine(total_capital=capital)
        except:
            pass
    
    return services

@st.cache_resource  
def load_ai_models():
    """Load YOUR trained AI models."""
    models_dir = Path(__file__).parent / 'models'
    signal_gen = SignalGeneratorFixed(models_dir=str(models_dir))
    
    if models_dir.exists():
        for model_file in models_dir.glob("xgb_NSE_*.pkl"):
            symbol = model_file.stem.replace("xgb_", "")
            signal_gen.load_model(symbol)
    
    return signal_gen

services = init_system()
signal_gen = load_ai_models()

# ============================================================
# HEADER
# ============================================================

st.markdown('''
<div class="main-header">
    <h1>🚀 AI STOCK SCREENER - PROFESSIONAL</h1>
    <p style="font-size:1.2em;">Your 42 Trained AI Models + Database + Risk Management</p>
</div>
''', unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title('⚙️ Controls')

# System status
st.sidebar.subheader('📊 System Status')
st.sidebar.success(f"✅ {len(signal_gen.models)} AI Models Loaded")

if DATABASE_AVAILABLE and services['database']:
    st.sidebar.success("✅ Database: Signals Persist Forever!")
    st.sidebar.success("✅ Risk Engine: Active")
    if services['risk_engine']:
        st.sidebar.info(f"💰 Capital: ₹{services['risk_engine'].total_capital:,.0f}")

# Stock selection
st.sidebar.subheader('🎯 Select Stocks')
stocks = sorted(signal_gen.models.keys())

selected_stocks = st.sidebar.multiselect(
    'Stocks to Screen',
    options=stocks,
    default=stocks[:10],
    help='Select stocks to analyze with AI'
)

# Filters
st.sidebar.subheader('📊 Filters')
min_confidence = st.sidebar.slider('Min Confidence (%)', 0, 100, 70, 5)
signal_filter = st.sidebar.multiselect('Show Signals', ['BUY', 'SELL', 'HOLD'], default=['BUY', 'SELL'])

# View saved signals
if DATABASE_AVAILABLE and services['database']:
    st.sidebar.markdown("---")
    if st.sidebar.button("📋 View Saved Signals"):
        saved = services['database'].get_active_signals(min_confidence=50)
        st.sidebar.info(f"💾 {len(saved)} signals in database")

# ============================================================
# MAIN SCREEN
# ============================================================

if not selected_stocks:
    st.warning("⚠️ Please select stocks from sidebar")
    st.stop()

# RUN SCREENING BUTTON
if st.button('🎯 RUN AI SCREENING', use_container_width=True, type='primary'):
    
    with st.spinner('🤖 Your AI models are analyzing stocks...'):
        # Fetch data & engineer features
        live_loader = LiveDataLoader()
        engineer = FeatureEngineer()
        featured_data = {}
        
        progress = st.progress(0)
        status = st.empty()
        
        for i, symbol in enumerate(selected_stocks):
            status.text(f"📊 Processing {symbol}... ({i+1}/{len(selected_stocks)})")
            df = live_loader.fetch_live_data(symbol, period="3mo")
            if df is not None and not df.empty:
                df_features = engineer.engineer_features(df)
                if df_features is not None and not df_features.empty:
                    featured_data[symbol] = df_features
            progress.progress((i + 1) / len(selected_stocks))
        
        status.text("🤖 Generating AI signals...")
        
        # Generate signals with YOUR AI models!
        signals_list = signal_gen.generate_signals_batch(
            symbols=list(featured_data.keys()),
            featured_data=featured_data
        )
        
        if signals_list:
            df_signals = pd.DataFrame(signals_list)
            
            # Add risk management
            if services['risk_engine']:
                for idx in range(len(df_signals)):
                    row = df_signals.iloc[idx]
                    entry = float(row.get('current_price', 0))
                    
                    # Calculate stop loss & target
                    if row['signal'] == 'buy':
                        sl = entry * 0.95
                        target = entry * 1.10
                    else:
                        sl = entry * 1.05
                        target = entry * 0.90
                    
                    # Get position size
                    pos = services['risk_engine'].calculate_position_size(
                        entry_price=entry,
                        stop_loss=sl,
                        confidence=float(row['confidence'])
                    )
                    
                    df_signals.at[idx, 'recommended_qty'] = pos.get('quantity', 0)
                    df_signals.at[idx, 'position_size'] = pos.get('position_size', 0)
                    df_signals.at[idx, 'risk_amount'] = pos.get('risk_amount', 0)
                    df_signals.at[idx, 'risk_pct'] = pos.get('risk_pct', 0)
                    df_signals.at[idx, 'stop_loss'] = sl
                    df_signals.at[idx, 'target'] = target
            
            # Save to database
            if DATABASE_AVAILABLE and services['database']:
                saved_count = 0
                for signal in df_signals.to_dict('records'):
                    try:
                        signal_data = {
                            'symbol': str(signal['symbol']),
                            'signal_type': str(signal['signal']).upper(),
                            'confidence': float(signal['confidence']) * 100,
                            'entry_price': float(signal.get('current_price', 0)),
                            'target_price': float(signal.get('target', 0)),
                            'stop_loss': float(signal.get('stop_loss', 0)),
                            'model_name': f"xgb_{signal['symbol']}",
                            'signal_strength': 'STRONG',
                            'volume': int(signal.get('volume', 0)),
                            'risk_reward_ratio': 2.0,
                            'position_size': float(signal.get('position_size', 0)),
                            'max_risk_amount': float(signal.get('risk_amount', 0)),
                            'valid_until': datetime.now() + timedelta(days=1)
                        }
                        if services['database'].save_signal(signal_data):
                            saved_count += 1
                    except:
                        pass
                
                if saved_count > 0:
                    st.success(f"✅ Saved {saved_count} signals to database!")
            
            # Filter signals
            df_filtered = df_signals[df_signals['confidence'] >= min_confidence / 100]
            df_filtered = df_filtered[df_filtered['signal'].str.upper().isin(signal_filter)]
            
            progress.empty()
            status.empty()
            
            # DISPLAY RESULTS
            st.markdown("---")
            st.subheader('🎯 AI Signals Generated')
            
            if not df_filtered.empty:
                # Summary
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
                
                # Show signals
                for _, row in df_filtered.iterrows():
                    signal_type = str(row['signal']).upper()
                    color = 'green' if signal_type == 'BUY' else 'red'
                    
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                    
                    with col1:
                        st.markdown(f"### {row['symbol']}")
                        st.markdown(f"**Signal:** <span style='color:{color};font-size:1.2em;font-weight:bold'>{signal_type}</span>", unsafe_allow_html=True)
                    
                    with col2:
                        st.metric("Price", f"₹{float(row['current_price']):,.2f}")
                        st.caption(f"Confidence: {float(row['confidence']):.1%}")
                    
                    with col3:
                        if 'recommended_qty' in row:
                            st.metric("Qty", int(row['recommended_qty']))
                            st.caption(f"Size: ₹{float(row.get('position_size', 0)):,.0f}")
                    
                    with col4:
                        if 'risk_amount' in row:
                            st.metric("Max Risk", f"₹{float(row['risk_amount']):,.0f}")
                            st.caption(f"({float(row.get('risk_pct', 0)):.2f}% of capital)")
                    
                    st.markdown("---")
                
                # Download
                st.download_button(
                    '📥 Download Signals CSV',
                    df_filtered.to_csv(index=False),
                    f'ai_signals_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    'text/csv',
                    use_container_width=True
                )
            else:
                st.info("No signals match your filters")
        else:
            st.warning("Could not generate signals")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align:center;color:gray;'>
    <strong>Professional AI Screener v3.0</strong> | 
    {len(signal_gen.models)} AI Models | 
    Database: {'✅ Active' if DATABASE_AVAILABLE else '⚠️ Disabled'} | 
    Risk Management: {'✅ Active' if services.get('risk_engine') else '⚠️ Disabled'}
</div>
""", unsafe_allow_html=True)

