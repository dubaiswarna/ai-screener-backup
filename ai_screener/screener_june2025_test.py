"""
AI Stock Screener - JUNE 2025 BACKTEST
========================================
Generate signals using data UP TO June 2025
Perfect for testing AI accuracy!
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
from excel_data_loader import ExcelDataLoader

try:
    from database.db_manager import get_db
    from risk_management.risk_engine import RiskEngine
    DATABASE_AVAILABLE = True
except:
    DATABASE_AVAILABLE = False

# ============================================================
# CONFIGURATION
# ============================================================

CUTOFF_DATE = "2025-06-30"  # Use data only up to June 30, 2025
BACKTEST_NAME = "JUNE_2025_TEST"

# Page config
st.set_page_config(
    page_title='AI Screener - June 2025 Test',
    page_icon='🧪',
    layout='wide'
)

# CSS
st.markdown("""
<style>
    .test-header {
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
        padding: 1rem 2rem;
        font-size: 1.2em;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
def init_system():
    """Initialize system"""
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

# Load Excel loader
@st.cache_resource
def load_excel_loader():
    """Load Excel file handle"""
    try:
        excel_path = r"C:\python\MG AI\Nifty200_MASTER_10yeardata.xlsx"
        excel_loader = ExcelDataLoader(excel_path)
        all_stocks = excel_loader.get_all_available_stocks()
        return all_stocks, excel_loader
    except Exception as e:
        st.sidebar.error(f"⚠️ Excel error: {e}")
        return [], None

# Load AI models
signal_gen = load_ai_models()
services = init_system()
all_stocks, excel_loader = load_excel_loader()

# Header
st.markdown(f'''
<div class="test-header">
    <h1>🧪 AI SCREENER - JUNE 2025 BACKTEST</h1>
    <p style="font-size:1.2em;">Testing AI Predictions from June 2025</p>
    <p style="font-size:0.9em;">📅 Using data up to: {CUTOFF_DATE}</p>
    <p style="font-size:0.9em;">🎯 Purpose: Verify AI accuracy with known outcomes</p>
</div>
''', unsafe_allow_html=True)

# Sidebar
st.sidebar.title('🧪 Test Configuration')

st.sidebar.subheader('📊 System Status')
st.sidebar.success(f"✅ {len(signal_gen.models)} AI Models Loaded")
st.sidebar.info(f"📅 Data Cutoff: {CUTOFF_DATE}")
st.sidebar.info(f"📊 Available Stocks: {len(all_stocks)}")

# Settings
st.sidebar.subheader('⚙️ Test Settings')
min_confidence = st.sidebar.slider('Min Confidence for Signals (%)', 50, 100, 75, 5)

# Stock selection - default to trained models
trained_stocks = sorted(signal_gen.models.keys())
st.sidebar.subheader('🎯 Stocks to Test')
st.sidebar.info(f"Testing {len(trained_stocks)} trained models")

selection_mode = st.sidebar.radio(
    "Selection",
    ["All Trained Models", "Custom Select"],
    help="All trained models or custom selection"
)

if selection_mode == "All Trained Models":
    selected_stocks = trained_stocks
    st.sidebar.success(f"✅ Testing: {len(selected_stocks)} stocks")
else:
    selected_stocks = st.sidebar.multiselect(
        'Select Stocks',
        options=trained_stocks,
        default=trained_stocks[:10],
        help='Select stocks to test'
    )

# Info box
st.info("""
🧪 **BACKTEST MODE**: This will generate signals as if it were June 2025.
- Data used: Up to June 30, 2025
- You can compare these signals with actual outcomes (June to Nov 2025)
- Perfect for validating AI accuracy!
""")

# Cache function OUTSIDE button for speed
@st.cache_data(ttl=3600, show_spinner=False)
def load_june_data_for_stock(symbol, cutoff_date):
    """Load and prepare June 2025 data (cached)"""
    if not excel_loader:
        return None
    
    df = excel_loader.get_stock_data(symbol)
    if df is None or df.empty or 'close' not in df.columns:
        return None
    
    # Filter to cutoff date
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['date'] <= cutoff_date]
    elif 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'])
        df = df[df['time'] <= cutoff_date]
    
    if len(df) == 0:
        return None
    
    # Add required columns quickly
    if 'vwap' not in df.columns and 'high' in df.columns:
        df['vwap'] = (df['high'] + df['low'] + df['close']) / 3
    if 'volume' not in df.columns:
        df['volume'] = df['close'] * 1000
    if 'time' not in df.columns and 'date' in df.columns:
        df['time'] = pd.to_datetime(df['date'])
    elif 'time' not in df.columns:
        df['time'] = pd.date_range(end=pd.Timestamp(cutoff_date), periods=len(df), freq='D')
    
    # Engineer features
    engineer = FeatureEngineer()
    return engineer.engineer_features(df)

# Main button
if st.button('🧪 GENERATE JUNE 2025 SIGNALS', use_container_width=True, type='primary'):
    
    with st.spinner('🤖 Loading June 2025 data...'):
        
        featured_data = {}
        progress = st.progress(0)
        status = st.empty()
        
        # Load features (cached!)
        for i, symbol in enumerate(selected_stocks):
            status.text(f"📊 {symbol}... ({i+1}/{len(selected_stocks)})")
            df_features = load_june_data_for_stock(symbol, CUTOFF_DATE)
            if df_features is not None and not df_features.empty:
                featured_data[symbol] = df_features
            progress.progress((i + 1) / len(selected_stocks))
        
        status.text("🤖 Generating signals...")
        
        # Generate signals
        signals_list = signal_gen.generate_signals_batch(
            symbols=list(featured_data.keys()),
            featured_data=featured_data
        )
        
        progress.empty()
        status.empty()
        
        if signals_list:
            df_signals = pd.DataFrame(signals_list)
            
            # Add risk management
            if services['risk_engine']:
                risk_engine = services['risk_engine']
                for idx, row in df_signals.iterrows():
                    try:
                        risk_calc = risk_engine.calculate_position_size(
                            symbol=str(row['symbol']),
                            entry_price=float(row['current_price']),
                            confidence=float(row['confidence']),
                            signal_type=str(row['signal'])
                        )
                        df_signals.at[idx, 'recommended_qty'] = risk_calc.get('recommended_qty', 0)
                        df_signals.at[idx, 'position_size'] = risk_calc.get('position_size', 0)
                        df_signals.at[idx, 'risk_amount'] = risk_calc.get('risk_amount', 0)
                        df_signals.at[idx, 'risk_pct'] = risk_calc.get('risk_pct', 0)
                    except:
                        df_signals.at[idx, 'recommended_qty'] = 0
                        df_signals.at[idx, 'position_size'] = 0
                        df_signals.at[idx, 'risk_amount'] = 0
                        df_signals.at[idx, 'risk_pct'] = 0
            
            # Add timestamp
            df_signals['generated_date'] = CUTOFF_DATE
            
            st.success(f"✅ Generated {len(df_signals)} signals from June 2025 data!")
            
            # Show breakdown
            st.markdown("---")
            st.subheader("📊 Signal Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                buy_count = len(df_signals[df_signals['signal'].str.upper() == 'BUY'])
                st.metric("BUY Signals", buy_count)
            with col2:
                sell_count = len(df_signals[df_signals['signal'].str.upper() == 'SELL'])
                st.metric("SELL Signals", sell_count)
            with col3:
                hold_count = len(df_signals[df_signals['signal'].str.upper() == 'HOLD'])
                st.metric("HOLD Signals", hold_count)
            with col4:
                avg_conf = df_signals['confidence'].mean() * 100
                st.metric("Avg Confidence", f"{avg_conf:.1f}%")
            
            # Filter by confidence
            df_filtered = df_signals[df_signals['confidence'] >= (min_confidence / 100)]
            
            if len(df_filtered) > 0:
                st.markdown("---")
                st.subheader(f"⚡ Signals Above {min_confidence}% Confidence")
                st.info(f"📊 {len(df_filtered)} signals meet confidence threshold")
                
                # Prepare display
                df_display = df_filtered.copy()
                df_display['confidence'] = (df_display['confidence'] * 100).apply(lambda x: f"{x:.1f}%")
                df_display['current_price'] = df_display['current_price'].apply(lambda x: f"₹{x:,.2f}")
                
                if 'target_price' in df_display.columns:
                    df_display['target_price'] = df_display['target_price'].apply(lambda x: f"₹{x:,.2f}")
                if 'stop_loss' in df_display.columns:
                    df_display['stop_loss'] = df_display['stop_loss'].apply(lambda x: f"₹{x:,.2f}")
                if 'recommended_qty' in df_display.columns:
                    df_display['recommended_qty'] = df_display['recommended_qty'].apply(lambda x: int(x) if pd.notna(x) else 0)
                
                # Display table
                cols_to_show = ['symbol', 'signal', 'confidence', 'current_price']
                if 'target_price' in df_display.columns:
                    cols_to_show.append('target_price')
                if 'stop_loss' in df_display.columns:
                    cols_to_show.append('stop_loss')
                if 'recommended_qty' in df_display.columns:
                    cols_to_show.append('recommended_qty')
                
                st.dataframe(df_display[cols_to_show], use_container_width=True, height=400)
                
                # Save to CSV with special name
                csv_filename = f"ai_signals_JUNE2025_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                csv_path = save_signals_to_csv(df_filtered, filename=csv_filename)
                
                st.success(f"💾 Signals saved to: {csv_path}")
                st.info("""
                📝 **Next Steps:**
                1. Compare these June 2025 signals with actual price movements (June-Nov 2025)
                2. Calculate accuracy: How many signals were correct?
                3. Calculate returns: What profit/loss would these signals have generated?
                4. Use this data to validate your AI models!
                """)
                
                # Download button
                csv_data = df_filtered.to_csv(index=False)
                st.download_button(
                    label="📥 Download June 2025 Signals CSV",
                    data=csv_data,
                    file_name=csv_filename,
                    mime="text/csv"
                )
                
            else:
                st.warning(f"⚠️ No signals above {min_confidence}% confidence threshold")
        
        else:
            st.warning("⚠️ No signals generated. Try adjusting settings.")

# Info section
st.markdown("---")
st.subheader("ℹ️ About This Test")
st.markdown(f"""
**Purpose:** Generate AI signals using data available as of **{CUTOFF_DATE}**

**How to use results:**
1. These signals show what your AI would have predicted in June 2025
2. Compare with actual price movements from July-November 2025
3. Calculate accuracy and profitability
4. Validate your AI model performance

**Why this is useful:**
- ✅ Test AI accuracy with known outcomes
- ✅ Identify which stocks/patterns worked best
- ✅ Improve model based on real results
- ✅ Build confidence before live trading
""")

st.markdown("---")
st.caption(f"🧪 Backtest Mode | Data cutoff: {CUTOFF_DATE} | Port: 8502")

