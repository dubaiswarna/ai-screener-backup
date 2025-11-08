"""
ALL-IN-ONE AI SCREENER + P&L TRACKER
=====================================
Everything in one simple page!
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

sys.path.append(str(Path(__file__).parent.parent))

from feature_engineering import FeatureEngineer
from signal_generator_fixed import SignalGeneratorFixed
from live_data_loader import LiveDataLoader
from save_signals_csv import save_signals_to_csv, load_all_saved_signals

try:
    from risk_management.risk_engine import RiskEngine
    RISK_AVAILABLE = True
except:
    RISK_AVAILABLE = False

# Page config
st.set_page_config(
    page_title='AI Screener All-in-One',
    page_icon='🎯',
    layout='wide'
)

# Load AI models
@st.cache_resource  
def load_ai_models():
    models_dir = Path(__file__).parent / 'models'
    signal_gen = SignalGeneratorFixed(models_dir=str(models_dir))
    if models_dir.exists():
        for model_file in models_dir.glob("xgb_NSE_*.pkl"):
            symbol = model_file.stem.replace("xgb_", "")
            signal_gen.load_model(symbol)
    return signal_gen

signal_gen = load_ai_models()

# Header
st.title("🎯 AI STOCK SCREENER - ALL IN ONE")
st.markdown("**Screen Stocks + Track P&L + Everything in One Place!**")

# Tabs
tab1, tab2 = st.tabs(["⚡ SCREEN STOCKS", "📈 TRACK P&L"])

# ============================================================
# TAB 1: SCREEN STOCKS
# ============================================================

with tab1:
    st.subheader("⚡ Auto Screen & Save")
    
    # Settings
    col1, col2, col3 = st.columns(3)
    
    with col1:
        stocks = sorted(signal_gen.models.keys())
        num_stocks = st.number_input("Number of stocks to screen", 5, len(stocks), 15)
        selected_stocks = stocks[:num_stocks]
    
    with col2:
        min_conf = st.slider("Min Confidence %", 50, 100, 60)
    
    with col3:
        st.metric("AI Models Loaded", len(signal_gen.models))
    
    # Screen button
    if st.button("⚡ RUN AI SCREENING", type="primary", use_container_width=True):
        
        with st.spinner(f'🤖 Screening {len(selected_stocks)} stocks...'):
            
            live_loader = LiveDataLoader()
            engineer = FeatureEngineer()
            featured_data = {}
            
            progress = st.progress(0)
            
            for i, symbol in enumerate(selected_stocks):
                df = live_loader.fetch_live_data(symbol, period="3mo")
                if df is not None and not df.empty:
                    df_features = engineer.engineer_features(df)
                    if df_features is not None and not df_features.empty:
                        featured_data[symbol] = df_features
                progress.progress((i + 1) / len(selected_stocks))
            
            # Generate signals
            signals_list = signal_gen.generate_signals_batch(
                symbols=list(featured_data.keys()),
                featured_data=featured_data
            )
            
            if signals_list:
                df_signals = pd.DataFrame(signals_list)
                
                # Filter
                df_filtered = df_signals[df_signals['confidence'] >= min_conf / 100]
                df_filtered = df_filtered[df_filtered['signal'].str.upper().isin(['BUY', 'SELL'])]
                
                progress.empty()
                
                # Save to CSV
                if not df_filtered.empty:
                    csv_path = save_signals_to_csv(df_filtered)
                    st.success(f"✅ Saved {len(df_filtered)} signals to CSV!")
                    st.info(f"📄 File: {csv_path}")
                    
                    # Show summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("BUY", len(df_filtered[df_filtered['signal'].str.upper() == 'BUY']))
                    with col2:
                        st.metric("SELL", len(df_filtered[df_filtered['signal'].str.upper() == 'SELL']))
                    with col3:
                        st.metric("Avg Confidence", f"{df_filtered['confidence'].mean():.1%}")
                    
                    # Show signals
                    st.dataframe(
                        df_filtered[['symbol', 'signal', 'confidence', 'current_price']],
                        use_container_width=True
                    )
                else:
                    st.warning("No signals met criteria")
            else:
                st.error("Could not generate signals")

# ============================================================
# TAB 2: TRACK P&L
# ============================================================

with tab2:
    st.subheader("📈 Live P&L Tracker")
    
    # Load signals
    df_saved = load_all_saved_signals()
    
    if df_saved.empty:
        st.info("💡 No signals to track. Generate signals in 'SCREEN STOCKS' tab first!")
    else:
        st.success(f"📊 Tracking {len(df_saved)} signals")
        
        # Fetch live prices
        if st.button("🔄 UPDATE PRICES", use_container_width=True):
            
            with st.spinner('📡 Updating prices...'):
                live_loader = LiveDataLoader()
                pnl_data = []
                
                for _, row in df_saved.iterrows():
                    symbol = row['symbol']
                    entry = float(row['current_price'])
                    signal_type = str(row['signal']).upper()
                    qty = int(row.get('recommended_qty', 10))
                    
                    # Get current price
                    try:
                        df_live = live_loader.fetch_live_data(symbol, period="1d")
                        if df_live is not None and not df_live.empty:
                            current = float(df_live['Close'].iloc[-1])
                        else:
                            current = entry
                    except:
                        current = entry
                    
                    # Calculate P&L
                    if signal_type == 'SELL':
                        pnl = (entry - current) * qty
                    else:
                        pnl = (current - entry) * qty
                    
                    pnl_pct = (pnl / (entry * qty)) * 100
                    
                    pnl_data.append({
                        'Symbol': symbol,
                        'Signal': signal_type,
                        'Entry': f"₹{entry:,.2f}",
                        'Current': f"₹{current:,.2f}",
                        'Qty': qty,
                        'P&L': f"₹{pnl:,.0f}",
                        'P&L %': f"{pnl_pct:.2f}%",
                        'Confidence': f"{float(row['confidence'])*100:.1f}%"
                    })
                
                df_pnl = pd.DataFrame(pnl_data)
                
                # Summary
                total_pnl = sum([float(str(x).replace('₹','').replace(',','')) for x in df_pnl['P&L']])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Signals", len(df_pnl))
                with col2:
                    st.metric("Total P&L", f"₹{total_pnl:,.0f}")
                with col3:
                    winners = len([x for x in df_pnl['P&L %'] if float(x.replace('%','')) > 0])
                    st.metric("Winners", f"{winners}/{len(df_pnl)}")
                
                # Table
                st.dataframe(df_pnl, use_container_width=True, height=600)
                
                st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# Footer
st.markdown("---")
st.caption(f"🚀 AI Screener All-in-One | {len(signal_gen.models)} Models Loaded")

