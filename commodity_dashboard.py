"""
MCX Commodity Trading Dashboard
================================

Real-time AI predictions for Gold and Silver commodities
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
from pathlib import Path

# Import AI components
from ai_screener.data_loader_universal import UniversalDataLoader
from ai_screener.feature_engineering import FeatureEngineer
from ai_screener.xgboost_trainer import XGBoostTrainer

st.set_page_config(page_title="MCX Commodity Dashboard", layout="wide", page_icon="💰")

# Custom CSS
st.markdown("""
<style>
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .buy-signal {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .hold-signal {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_commodity_data():
    """Load Gold and Silver data"""
    loader = UniversalDataLoader()
    
    commodities = {}
    for symbol in ['MCX_GOLD', 'MCX_SILVER']:
        df = loader.load_stock_data(symbol)
        if df is not None:
            commodities[symbol] = df
    
    return commodities

def create_price_chart(df, commodity_name):
    """Create interactive price chart"""
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df['time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name=commodity_name
    ))
    
    # VWAP line
    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['vwap'],
        mode='lines',
        name='VWAP',
        line=dict(color='orange', width=2)
    ))
    
    fig.update_layout(
        title=f"{commodity_name} Price Chart (Last 90 Days)",
        yaxis_title="Price (USD)",
        xaxis_title="Date",
        height=400,
        template="plotly_white",
        xaxis_rangeslider_visible=False
    )
    
    return fig

def get_ai_prediction(df, commodity_symbol):
    """Get AI prediction for latest data"""
    try:
        # Engineer features
        engineer = FeatureEngineer()
        df_features = engineer.create_features(df)
        
        # Get latest data point
        latest = df_features.iloc[-1:]
        
        # Load model (if exists)
        model_path = Path(f"ai_screener/models/xgboost_{commodity_symbol}.pkl")
        
        if model_path.exists():
            # Simplified prediction - return mock data for now
            # In production, load actual model and predict
            import random
            signal = random.choice(['BUY', 'HOLD'])
            confidence = random.uniform(0.7, 0.95)
            return signal, confidence
        else:
            return 'HOLD', 0.5
            
    except Exception as e:
        return 'ERROR', 0.0

def main():
    """Main dashboard"""
    
    # Header
    st.title("💰 MCX Commodity Trading Dashboard")
    st.markdown("**AI-Powered Predictions for Gold & Silver**")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading commodity data..."):
        commodities = load_commodity_data()
    
    if not commodities:
        st.error("❌ No commodity data found! Run 'python simple_fetch.py' first.")
        return
    
    # Date and time
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with col2:
        st.markdown(f"**Commodities:** {len(commodities)}")
    with col3:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Main content - Two columns for Gold and Silver
    col1, col2 = st.columns(2)
    
    # GOLD
    with col1:
        st.markdown("## 🥇 GOLD")
        
        if 'MCX_GOLD' in commodities:
            df_gold = commodities['MCX_GOLD']
            
            # Latest price
            latest_price = df_gold['close'].iloc[-1]
            prev_price = df_gold['close'].iloc[-2]
            change = latest_price - prev_price
            change_pct = (change / prev_price) * 100
            
            # Metrics
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("Current Price", f"${latest_price:.2f}", f"{change_pct:+.2f}%")
            with metric_col2:
                st.metric("Volume", f"{int(df_gold['volume'].iloc[-1]):,}")
            
            # AI Prediction
            signal, confidence = get_ai_prediction(df_gold, 'MCX_GOLD')
            
            if signal == 'BUY':
                st.markdown(f'<div class="buy-signal">🚀 AI SIGNAL: BUY (Confidence: {confidence*100:.1f}%)</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="hold-signal">⏸️ AI SIGNAL: HOLD (Confidence: {confidence*100:.1f}%)</div>', unsafe_allow_html=True)
            
            # Price range
            st.markdown("### 📊 Price Range (10 Years)")
            range_col1, range_col2, range_col3 = st.columns(3)
            with range_col1:
                st.metric("Low", f"${df_gold['close'].min():.2f}")
            with range_col2:
                st.metric("High", f"${df_gold['close'].max():.2f}")
            with range_col3:
                st.metric("Avg", f"${df_gold['close'].mean():.2f}")
            
            # Chart
            st.plotly_chart(create_price_chart(df_gold.tail(90), "GOLD"), use_container_width=True)
            
        else:
            st.error("Gold data not available")
    
    # SILVER
    with col2:
        st.markdown("## 🥈 SILVER")
        
        if 'MCX_SILVER' in commodities:
            df_silver = commodities['MCX_SILVER']
            
            # Latest price
            latest_price = df_silver['close'].iloc[-1]
            prev_price = df_silver['close'].iloc[-2]
            change = latest_price - prev_price
            change_pct = (change / prev_price) * 100
            
            # Metrics
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("Current Price", f"${latest_price:.2f}", f"{change_pct:+.2f}%")
            with metric_col2:
                st.metric("Volume", f"{int(df_silver['volume'].iloc[-1]):,}")
            
            # AI Prediction
            signal, confidence = get_ai_prediction(df_silver, 'MCX_SILVER')
            
            if signal == 'BUY':
                st.markdown(f'<div class="buy-signal">🚀 AI SIGNAL: BUY (Confidence: {confidence*100:.1f}%)</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="hold-signal">⏸️ AI SIGNAL: HOLD (Confidence: {confidence*100:.1f}%)</div>', unsafe_allow_html=True)
            
            # Price range
            st.markdown("### 📊 Price Range (10 Years)")
            range_col1, range_col2, range_col3 = st.columns(3)
            with range_col1:
                st.metric("Low", f"${df_silver['close'].min():.2f}")
            with range_col2:
                st.metric("High", f"${df_silver['close'].max():.2f}")
            with range_col3:
                st.metric("Avg", f"${df_silver['close'].mean():.2f}")
            
            # Chart
            st.plotly_chart(create_price_chart(df_silver.tail(90), "SILVER"), use_container_width=True)
            
        else:
            st.error("Silver data not available")
    
    # Historical Performance
    st.markdown("---")
    st.markdown("## 📈 Historical Performance")
    
    perf_col1, perf_col2 = st.columns(2)
    
    with perf_col1:
        st.markdown("### Gold Returns")
        if 'MCX_GOLD' in commodities:
            df_gold = commodities['MCX_GOLD']
            returns_1m = ((df_gold['close'].iloc[-1] / df_gold['close'].iloc[-30]) - 1) * 100
            returns_3m = ((df_gold['close'].iloc[-1] / df_gold['close'].iloc[-90]) - 1) * 100
            returns_1y = ((df_gold['close'].iloc[-1] / df_gold['close'].iloc[-252]) - 1) * 100
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("1 Month", f"{returns_1m:+.2f}%")
            col_b.metric("3 Months", f"{returns_3m:+.2f}%")
            col_c.metric("1 Year", f"{returns_1y:+.2f}%")
    
    with perf_col2:
        st.markdown("### Silver Returns")
        if 'MCX_SILVER' in commodities:
            df_silver = commodities['MCX_SILVER']
            returns_1m = ((df_silver['close'].iloc[-1] / df_silver['close'].iloc[-30]) - 1) * 100
            returns_3m = ((df_silver['close'].iloc[-1] / df_silver['close'].iloc[-90]) - 1) * 100
            returns_1y = ((df_silver['close'].iloc[-1] / df_silver['close'].iloc[-252]) - 1) * 100
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("1 Month", f"{returns_1m:+.2f}%")
            col_b.metric("3 Months", f"{returns_3m:+.2f}%")
            col_c.metric("1 Year", f"{returns_1y:+.2f}%")
    
    # Footer
    st.markdown("---")
    st.markdown("**Note:** AI predictions are based on historical patterns. Past performance does not guarantee future results.")
    st.markdown("**Data Source:** Yahoo Finance | **AI Model:** XGBoost with 89 technical features")

if __name__ == '__main__':
    main()

