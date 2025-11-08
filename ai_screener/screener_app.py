"""
AI Stock Screener - Streamlit UI
=================================

Interactive dashboard for screening stocks using AI models.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yaml
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import our modules
from data_loader import DataLoader
from feature_engineering import FeatureEngineer
from signal_generator import SignalGenerator
from signal_generator_fixed import SignalGeneratorFixed
from live_data_loader import LiveDataLoader


# Page config
st.set_page_config(
    page_title='AI Stock Screener',
    page_icon='📈',
    layout='wide',
    initial_sidebar_state='expanded'
)


# Load configuration
@st.cache_resource
def load_config():
    """Load configuration file."""
    try:
        # Try current directory first
        config_path = Path('config.yaml')
        if not config_path.exists():
            # Try in ai_screener directory
            config_path = Path(__file__).parent / 'config.yaml'
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config if config else {}
    except FileNotFoundError:
        st.error("Config file not found. Using default settings.")
        return {}


@st.cache_resource
def load_data():
    """Load live data loader."""
    return LiveDataLoader()


@st.cache_resource  
def load_models():
    """Load all AI models."""
    import os
    from pathlib import Path
    
    models_dir = Path(__file__).parent / 'models'
    signal_gen = SignalGeneratorFixed(models_dir=str(models_dir))
    
    # Auto-load all NSE models
    if models_dir.exists():
        model_files = list(models_dir.glob("xgb_NSE_*.pkl"))
        for model_file in model_files:
            symbol = model_file.stem.replace("xgb_", "")
            signal_gen.load_model(symbol)
    
    return signal_gen


def main():
    """Main application."""
    # Title
    st.title('🎯 AI Stock Screener')
    st.markdown('**AI-Powered Trading Signals using CNN-LSTM + XGBoost Ensemble Models**')
    st.info('💡 **AI-Driven Screening**: Signals generated purely from ML models (no manual filters applied to AI predictions)')
    
    # Load configuration
    config = load_config()
    
    # Sidebar
    st.sidebar.header('⚙️ Filters')
    
    # Stock selection
    live_loader = load_data()
    signal_gen = load_models()
    
    stocks = sorted(signal_gen.models.keys())
    
    st.sidebar.success(f"✅ {len(stocks)} AI models loaded")
    
    selected_stocks = st.sidebar.multiselect(
        'Select Stocks',
        options=stocks,
        default=stocks[:min(9, len(stocks))]
    )
    
    if not selected_stocks:
        st.warning("Please select at least one stock.")
        return
    
    # AI Signal Display Filters
    st.sidebar.subheader('🎯 AI Signal Display')
    st.sidebar.markdown('_Only shows signals from AI models_')
    
    min_confidence = st.sidebar.slider(
        'Min Confidence (%)',
        min_value=0,
        max_value=100,
        value=50,
        step=5,
        help='Minimum AI model confidence to display (AI models provide this)'
    )
    
    signal_types = st.sidebar.multiselect(
        'Signal Types',
        options=['buy', 'sell', 'hold'],
        default=['buy', 'sell', 'hold'],
        help='Which AI-generated signals to display'
    )
    
    # Additional Display Filters (optional)
    st.sidebar.markdown('---')
    st.sidebar.subheader('📊 Display Filters (Optional)')
    st.sidebar.markdown('_These filters only affect what you see, not AI predictions_')
    
    # VWAP filter (optional - for display only)
    vwap_filter = st.sidebar.selectbox(
        'VWAP Position Filter',
        options=['All', 'Above VWAP', 'Below VWAP'],
        help='⚠️ FOR DISPLAY ONLY: Filter results by VWAP position. AI signals are NOT affected by this.'
    )
    
    # Main content
    tabs = st.tabs(['📊 Screener Results', '📈 Charts', '📉 Model Performance'])
    
    # Tab 1: Screener Results
    with tabs[0]:
        st.subheader('Stock Signals')
        
        # Fetch live data and engineer features
        progress = st.progress(0)
        status = st.empty()
        
        status.text("Fetching live data from Yahoo Finance...")
        
        # Fetch live data
        engineer = FeatureEngineer()
        featured_data = {}
        
        for i, symbol in enumerate(selected_stocks):
            status.text(f"Fetching {symbol}... ({i+1}/{len(selected_stocks)})")
            df = live_loader.fetch_live_data(symbol, period="3mo")
            if df is not None:
                df_features = engineer.engineer_features(df)
                if df_features is not None and not df_features.empty:
                    featured_data[symbol] = df_features
            progress.progress((i + 1) / len(selected_stocks))
        
        # Generate signals
        status.text("Generating AI signals...")
        
        if featured_data:
            # Generate signals using fixed generator
            signals_list = signal_gen.generate_signals_batch(
                symbols=list(featured_data.keys()),
                featured_data=featured_data
            )
            
            df_signals = pd.DataFrame(signals_list)
            
            progress.progress(100)
            status.empty()
            
            # Apply filters
            df_filtered = df_signals.copy()
            
            # Confidence filter
            df_filtered = df_filtered[df_filtered['confidence'] >= min_confidence / 100]
            
            # Signal type filter
            df_filtered = df_filtered[df_filtered['signal'].isin(signal_types)]
            
            # VWAP filter
            if vwap_filter == 'Above VWAP':
                df_filtered = df_filtered[df_filtered['vwap_deviation_pct'] > 0]
            elif vwap_filter == 'Below VWAP':
                df_filtered = df_filtered[df_filtered['vwap_deviation_pct'] < 0]
            
            # Display results
            if not df_filtered.empty:
                # Summary stats
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric('Total Signals', len(df_filtered))
                with col2:
                    buy_count = len(df_filtered[df_filtered['signal'] == 'buy'])
                    st.metric('Buy Signals', buy_count)
                with col3:
                    sell_count = len(df_filtered[df_filtered['signal'] == 'sell'])
                    st.metric('Sell Signals', sell_count)
                with col4:
                    avg_confidence = df_filtered['confidence'].mean()
                    st.metric('Avg Confidence', f"{avg_confidence:.1%}")
                
                # Results table
                st.markdown("---")
                
                # Format table for display
                df_display = df_filtered.copy()
                df_display['confidence'] = df_display['confidence'].apply(lambda x: f"{x:.1%}")
                df_display['current_price'] = df_display['current_price'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
                df_display['vwap_deviation_pct'] = df_display['vwap_deviation_pct'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # Download button
                st.download_button(
                    label='📥 Download Results as CSV',
                    data=df_filtered.to_csv(index=False),
                    file_name=f'screener_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    mime='text/csv'
                )
                
            else:
                st.info("No stocks match the selected filters. Try adjusting your criteria.")
        
        else:
            st.error("Could not load data for selected stocks.")
    
    # Tab 2: Charts
    with tabs[1]:
        st.subheader('Price Charts with VWAP')
        
        if not selected_stocks:
            st.warning("Select stocks to view charts.")
        else:
            chart_stock = st.selectbox('Select Stock for Chart', selected_stocks)
            
            if chart_stock in featured_data:
                df_chart = featured_data[chart_stock]
                
                # Candlestick chart
                fig = go.Figure()
                
                # Candlesticks
                fig.add_trace(go.Candlestick(
                    x=df_chart['time'],
                    open=df_chart['open'],
                    high=df_chart['high'],
                    low=df_chart['low'],
                    close=df_chart['close'],
                    name='Price'
                ))
                
                # VWAP
                if 'vwap' in df_chart.columns:
                    fig.add_trace(go.Scatter(
                        x=df_chart['time'],
                        y=df_chart['vwap'],
                        mode='lines',
                        name='VWAP',
                        line=dict(color='blue', width=2)
                    ))
                
                # Update layout
                fig.update_layout(
                    title=f'{chart_stock} - Price & VWAP',
                    xaxis_title='Date',
                    yaxis_title='Price',
                    height=600,
                    xaxis_rangeslider_visible=False,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    # Tab 3: Model Performance
    with tabs[2]:
        st.subheader('Model Performance Metrics')
        
        st.info("Model performance metrics will be displayed here after training models.")
        st.markdown("""
        **How to view performance:**
        1. Train models using `train_models.py`
        2. Performance metrics will be saved during training
        3. View accuracy, F1 scores, and confusion matrices here
        """)


if __name__ == '__main__':
    main()

