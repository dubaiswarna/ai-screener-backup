"""
AI Stock Screener - AUTO EXECUTE MODE
======================================
Automatically executes all AI signals for testing
Perfect for backtesting and automated trading!
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import modules
from data_loader import DataLoader
from feature_engineering import FeatureEngineer
from signal_generator_fixed import SignalGeneratorFixed
from live_data_loader import LiveDataLoader
from save_signals_csv import save_signals_to_csv, load_all_saved_signals

# Import S&R Calculator
sys.path.insert(0, str(Path(__file__).parent.parent / 'support_resistance'))
try:
    from sr_calculator import SupportResistanceCalculator
    SR_AVAILABLE = True
except:
    SR_AVAILABLE = False

try:
    from database.db_manager import get_db
    from risk_management.risk_engine import RiskEngine
    DATABASE_AVAILABLE = True
except:
    DATABASE_AVAILABLE = False

# Page config
st.set_page_config(
    page_title='AI Screener - Auto Execute',
    page_icon='⚡',
    layout='wide'
)

# CSS
st.markdown("""
<style>
    .auto-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        font-weight: bold;
        padding: 1rem 2rem;
        font-size: 1.2em;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
def init_system():
    """Initialize system - NO CACHING to avoid stale database connections."""
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
    models_dir = Path(__file__).parent / 'models'
    signal_gen = SignalGeneratorFixed(models_dir=str(models_dir))
    if models_dir.exists():
        for model_file in models_dir.glob("xgb_NSE_*.pkl"):
            symbol = model_file.stem.replace("xgb_", "")
            signal_gen.load_model(symbol)
    return signal_gen

# Load AI models once (these can be cached)
signal_gen = load_ai_models()

# Initialize services fresh every time (no caching!)
services = init_system()

# Header
sr_status = "📊 + Support & Resistance Analysis" if SR_AVAILABLE else ""
st.markdown(f'''
<div class="auto-header">
    <h1>⚡ AI SCREENER - AUTO EXECUTE MODE {sr_status}</h1>
    <p style="font-size:1.2em;">Fully Automated Signal Generation + Execution + S&R Confirmation</p>
    <p style="font-size:0.9em;">🧪 TESTING MODE - AI Predictions verified with Support & Resistance Levels!</p>
</div>
''', unsafe_allow_html=True)

# Sidebar
st.sidebar.title('⚙️ Auto-Execute Settings')

st.sidebar.subheader('📊 System Status')
st.sidebar.success(f"✅ {len(signal_gen.models)} AI Models")
if DATABASE_AVAILABLE and services['database']:
    st.sidebar.success("✅ Database Active")
    st.sidebar.success("✅ Risk Engine Active")
    if services['risk_engine']:
        st.sidebar.info(f"💰 Capital: ₹{services['risk_engine'].total_capital:,.0f}")

# Auto-execute settings
st.sidebar.subheader('⚡ Auto-Execute Rules')
min_confidence = st.sidebar.slider('Min Confidence for Auto-Execute (%)', 50, 100, 75, 5,
    help='Only signals above this confidence will be auto-executed')

max_positions = st.sidebar.number_input('Max Auto Positions', 1, 20, 10,
    help='Maximum number of positions to auto-execute')

signal_filter = st.sidebar.multiselect('Auto-Execute Signals', 
    ['BUY', 'SELL'], 
    default=['BUY', 'SELL'],
    help='Which signal types to auto-execute')

# S&R Filter (NEW!)
if SR_AVAILABLE:
    st.sidebar.markdown("---")
    st.sidebar.subheader('📊 S&R Confirmation Filter')
    require_sr_confirmation = st.sidebar.checkbox(
        'Require Strong S&R Confirmation',
        value=False,
        help='Only show signals with strong S&R alignment (near support for BUY, near resistance for SELL)'
    )
else:
    require_sr_confirmation = False

# Stock selection
st.sidebar.subheader('🎯 Stocks to Screen')
trained_stocks = sorted(signal_gen.models.keys())
st.sidebar.info(f"📊 {len(trained_stocks)} trained AI models available")

selected_stocks = st.sidebar.multiselect(
    'Select Stocks',
    options=trained_stocks,
    default=trained_stocks,  # All trained models
    help='Select stocks to screen (only trained models work)'
)

# Portfolio summary
if DATABASE_AVAILABLE and services['database']:
    st.sidebar.markdown("---")
    st.sidebar.subheader("💼 Portfolio")
    portfolio = services['database'].get_portfolio()
    saved_signals = services['database'].get_active_signals()
    
    st.sidebar.metric("Saved Signals", len(saved_signals))
    st.sidebar.metric("Open Positions", len(portfolio))

# Main screen
if not selected_stocks:
    st.warning("⚠️ Select stocks from sidebar")
    st.stop()

# AUTO EXECUTE BUTTON
st.info("⚡ **AUTO-EXECUTE MODE**: All high-confidence signals will be automatically saved and tracked!")

if st.button('⚡ AUTO SCREEN & EXECUTE', use_container_width=True, type='primary'):
    
    with st.spinner('🤖 AI Screening + Auto-Executing...'):
        
        # Fetch data
        live_loader = LiveDataLoader()
        engineer = FeatureEngineer()
        featured_data = {}
        
        progress = st.progress(0)
        status = st.empty()
        
        # Fetch data for all stocks
        for i, symbol in enumerate(selected_stocks):
            status.text(f"📊 Fetching {symbol}... ({i+1}/{len(selected_stocks)})")
            df = live_loader.fetch_live_data(symbol, period="3mo")
            if df is not None and not df.empty:
                df_features = engineer.engineer_features(df)
                if df_features is not None and not df_features.empty:
                    featured_data[symbol] = df_features
            progress.progress((i + 1) / len(selected_stocks))
        
        status.text("🤖 Generating AI signals...")
        
        # Generate signals
        signals_list = signal_gen.generate_signals_batch(
            symbols=list(featured_data.keys()),
            featured_data=featured_data
        )
        
        if signals_list:
            df_signals = pd.DataFrame(signals_list)
            
            # ADD S&R ANALYSIS FOR EACH SIGNAL
            if SR_AVAILABLE:
                st.info("📊 Calculating Support & Resistance levels...")
                sr_calculator = SupportResistanceCalculator(sensitivity=5, min_touches=2)
                
                # Add S&R columns
                df_signals['nearest_support'] = None
                df_signals['nearest_resistance'] = None
                df_signals['support_distance'] = None
                df_signals['resistance_distance'] = None
                df_signals['sr_confirmation'] = None
                
                for idx, row in df_signals.iterrows():
                    symbol = row['symbol']
                    # Remove NSE_ prefix if present
                    clean_symbol = symbol.replace('NSE_', '')
                    
                    if clean_symbol in featured_data:
                        try:
                            df_stock = featured_data[clean_symbol]
                            current_price = row['current_price']
                            
                            # Calculate S&R
                            sr_data = sr_calculator.calculate_support_resistance(df_stock, current_price)
                            
                            # Get nearest levels
                            nearest_support = sr_data['supports'][0]['level'] if sr_data['supports'] else None
                            nearest_resistance = sr_data['resistances'][0]['level'] if sr_data['resistances'] else None
                            
                            df_signals.at[idx, 'nearest_support'] = nearest_support
                            df_signals.at[idx, 'nearest_resistance'] = nearest_resistance
                            
                            if nearest_support:
                                df_signals.at[idx, 'support_distance'] = ((current_price - nearest_support) / current_price) * 100
                            if nearest_resistance:
                                df_signals.at[idx, 'resistance_distance'] = ((nearest_resistance - current_price) / current_price) * 100
                            
                            # S&R Confirmation Logic
                            signal = row['signal'].upper()
                            if signal == 'BUY' and nearest_support:
                                # BUY near support = GOOD
                                dist = df_signals.at[idx, 'support_distance']
                                if dist and dist < 3:  # Within 3% of support
                                    df_signals.at[idx, 'sr_confirmation'] = '✅ STRONG (Near Support)'
                                else:
                                    df_signals.at[idx, 'sr_confirmation'] = '⚠️ OK'
                            elif signal == 'SELL' and nearest_resistance:
                                # SELL near resistance = GOOD
                                dist = df_signals.at[idx, 'resistance_distance']
                                if dist and dist < 3:  # Within 3% of resistance
                                    df_signals.at[idx, 'sr_confirmation'] = '✅ STRONG (Near Resistance)'
                                else:
                                    df_signals.at[idx, 'sr_confirmation'] = '⚠️ OK'
                            else:
                                df_signals.at[idx, 'sr_confirmation'] = '➡️ Neutral'
                                
                        except Exception as e:
                            # Silent fail for S&R calculation
                            pass
                
                st.success(f"✅ S&R analysis added to signals!")
            
            # Show ALL signals generated
            st.info(f"🤖 AI Generated {len(df_signals)} total signals")
            
            # Show breakdown by signal type
            col1, col2, col3 = st.columns(3)
            with col1:
                buy_count = len(df_signals[df_signals['signal'].str.lower() == 'buy'])
                st.metric("BUY Signals", buy_count)
            with col2:
                sell_count = len(df_signals[df_signals['signal'].str.lower() == 'sell'])
                st.metric("SELL Signals", sell_count)
            with col3:
                hold_count = len(df_signals[df_signals['signal'].str.lower() == 'hold'])
                st.metric("HOLD Signals", hold_count)
            
            # Show confidence range
            if len(df_signals) > 0:
                min_conf = df_signals['confidence'].min() * 100
                max_conf = df_signals['confidence'].max() * 100
                avg_conf = df_signals['confidence'].mean() * 100
                st.info(f"Confidence range: {min_conf:.1f}% to {max_conf:.1f}% (avg: {avg_conf:.1f}%)")
            
            # Show S&R Confirmation Summary
            if SR_AVAILABLE and 'sr_confirmation' in df_signals.columns:
                strong_sr = len(df_signals[df_signals['sr_confirmation'].str.contains('STRONG', na=False)])
                if strong_sr > 0:
                    st.success(f"🎯 {strong_sr} signals have STRONG S&R confirmation!")
            
            # Filter for auto-execute
            df_auto = df_signals[
                (df_signals['confidence'] >= (min_confidence / 100)) &
                (df_signals['signal'].str.upper().isin([s.upper() for s in signal_filter]))
            ]
            
            # Apply S&R filter if enabled
            if require_sr_confirmation and 'sr_confirmation' in df_auto.columns:
                df_auto = df_auto[df_auto['sr_confirmation'].str.contains('STRONG', na=False)]
                st.info(f"🎯 Filtered to {len(df_auto)} signals with STRONG S&R confirmation")
            
            df_auto = df_auto.head(max_positions)
            
            st.info(f"⚡ {len(df_auto)} signals meet auto-execute criteria (>{min_confidence}% confidence)")
            
            if len(df_auto) > 0:
                # Add risk management calculations
                if services['risk_engine']:
                    risk_engine = services['risk_engine']
                    
                    for idx, row in df_auto.iterrows():
                        try:
                            risk_calc = risk_engine.calculate_position_size(
                                symbol=str(row['symbol']),
                                entry_price=float(row['current_price']),
                                confidence=float(row['confidence']),
                                signal_type=str(row['signal'])
                            )
                            
                            df_auto.at[idx, 'recommended_qty'] = risk_calc.get('recommended_qty', 0)
                            df_auto.at[idx, 'position_size'] = risk_calc.get('position_size', 0)
                            df_auto.at[idx, 'risk_amount'] = risk_calc.get('risk_amount', 0)
                            df_auto.at[idx, 'risk_pct'] = risk_calc.get('risk_pct', 0)
                        except Exception as e:
                            df_auto.at[idx, 'recommended_qty'] = 0
                            df_auto.at[idx, 'position_size'] = 0
                            df_auto.at[idx, 'risk_amount'] = 0
                            df_auto.at[idx, 'risk_pct'] = 0
                
                # Save signals to CSV
                csv_path = save_signals_to_csv(df_auto)
                st.success(f"💾 Saved {len(df_auto)} signals to CSV: {csv_path}")
                
                # Save to database
                db_save_count = 0
                db_errors = []
                
                for idx, row in df_auto.iterrows():
                    try:
                        # Get fresh database instance
                        db = get_db()
                        
                        signal_data = {
                            'symbol': str(row['symbol']),
                            'signal': str(row['signal']),
                            'confidence': float(row['confidence']),
                            'entry_price': float(row['current_price']),
                            'target': float(row.get('target_price', 0)),
                            'stop_loss': float(row.get('stop_loss', 0)),
                            'recommended_qty': int(row.get('recommended_qty', 0)),
                            'position_size': float(row.get('position_size', 0)),
                            'risk_amount': float(row.get('risk_amount', 0)),
                            'risk_pct': float(row.get('risk_pct', 0))
                        }
                        
                        db.save_signal(signal_data)
                        db_save_count += 1
                    except Exception as e:
                        db_errors.append(f"{row['symbol']}: {str(e)}")
                
                if db_save_count > 0:
                    st.success(f"💾 Saved {db_save_count} signals to database")
                
                if db_errors:
                    with st.expander("⚠️ Database save errors (signals still saved to CSV)"):
                        for err in db_errors:
                            st.text(err)
                
                # Display signals
                st.markdown("---")
                st.subheader("⚡ Auto-Executed Signals")
                
                # Format for display
                df_display = df_auto.copy()
                df_display['confidence'] = (df_display['confidence'] * 100).apply(lambda x: f"{x:.1f}%")
                df_display['current_price'] = df_display['current_price'].apply(lambda x: f"₹{x:,.2f}")
                
                if 'target_price' in df_display.columns:
                    df_display['target_price'] = df_display['target_price'].apply(lambda x: f"₹{x:,.2f}")
                if 'stop_loss' in df_display.columns:
                    df_display['stop_loss'] = df_display['stop_loss'].apply(lambda x: f"₹{x:,.2f}")
                if 'recommended_qty' in df_display.columns:
                    df_display['recommended_qty'] = df_display['recommended_qty'].apply(lambda x: int(x) if pd.notna(x) else 0)
                
                # Format S&R columns if available
                if 'nearest_support' in df_display.columns:
                    df_display['nearest_support'] = df_display['nearest_support'].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "N/A")
                if 'nearest_resistance' in df_display.columns:
                    df_display['nearest_resistance'] = df_display['nearest_resistance'].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "N/A")
                if 'support_distance' in df_display.columns:
                    df_display['support_distance'] = df_display['support_distance'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
                if 'resistance_distance' in df_display.columns:
                    df_display['resistance_distance'] = df_display['resistance_distance'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
                
                # Select columns to display
                display_cols = ['symbol', 'signal', 'confidence', 'current_price', 
                               'target_price', 'stop_loss', 'recommended_qty']
                
                # Add S&R columns if available
                if SR_AVAILABLE and 'sr_confirmation' in df_display.columns:
                    display_cols.extend(['sr_confirmation', 'nearest_support', 'nearest_resistance'])
                
                st.dataframe(df_display[display_cols], 
                           use_container_width=True, height=400)
                
                st.success("✅ Auto-execution complete! Signals saved and ready for tracking.")
                
            else:
                st.warning("No signals met auto-execute criteria")
                st.info(f"💡 Try lowering confidence threshold or adjusting filters")
        
        else:
            st.error("❌ No signals generated. Check data availability.")
        
        progress.empty()
        status.empty()

# View saved signals
st.markdown("---")
st.subheader("📊 View Saved Signals")

col1, col2 = st.columns(2)

with col1:
    if st.button("📂 View Database Signals", use_container_width=True):
        if DATABASE_AVAILABLE and services['database']:
            signals = services['database'].get_active_signals()
            if signals:
                st.info(f"Found {len(signals)} signals in database")
                df_db = pd.DataFrame(signals)
                st.dataframe(df_db, use_container_width=True)
            else:
                st.warning("No signals in database")
        else:
            st.error("Database not available")

with col2:
    if st.button("📁 View CSV Signals", use_container_width=True):
        all_signals = load_all_saved_signals()
        if all_signals:
            st.info(f"Found {len(all_signals)} signals in CSV files")
            st.dataframe(all_signals, use_container_width=True)
        else:
            st.warning("No CSV signals found")
