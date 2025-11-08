"""
AI Stock Screener - Web Dashboard
==================================

Beautiful web interface for daily stock screening.
Access via: http://localhost:8501

Run: streamlit run web_screener.py
"""

import streamlit as st
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
import plotly.express as px
import plotly.graph_objects as go

# Add path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

from ai_screener.data_loader import DataLoader
from ai_screener.feature_engineering import FeatureEngineer
from ai_screener.xgboost_trainer import XGBoostTrainer


# Stock tiers
TIER_1_STOCKS = [
    'NSE_BAJAJFINSV', 'NSE_REFEX', 'NSE_MAXHEALTH', 'NSE_RELINFRA',
    'NSE_M&M', 'NSE_ETERNAL', 'NSE_ICICIBANK', 'NSE_ONGC',
    'NSE_ADANIENT', 'NSE_SHRIRAMFIN'
]

TIER_2_STOCKS = [
    'NSE_ADANIPORTS', 'NSE_HINDALCO', 'NSE_TATASTEEL', 'NSE_BIOCON',
    'NSE_EICHERMOT', 'NSE_POWERGRID', 'NSE_PTC', 'NSE_HDFCLIFE',
    'NSE_SBILIFE', 'NSE_TMPV', 'NSE_AXISBANK', 'NSE_JSWSTEEL',
    'NSE_KOTAKBANK', 'NSE_HCLTECH', 'NSE_TECHM'
]


# Page config
st.set_page_config(
    page_title="AI Stock Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .tier1-signal {
        background-color: #d4edda;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    .tier2-signal {
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
    .tier3-signal {
        background-color: #f8d7da;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_all_models():
    """Load all trained models (cached)."""
    models_dir = 'ai_screener/models'
    loader = DataLoader()
    all_stocks = loader.get_all_stocks()
    
    models = {}
    for stock in all_stocks:
        model_path = os.path.join(models_dir, f'xgb_{stock}.pkl')
        if os.path.exists(model_path):
            try:
                models[stock] = joblib.load(model_path)
            except:
                pass
    
    return models


@st.cache_data(ttl=3600)  # Cache for 1 hour
def scan_all_stocks(models):
    """Scan all stocks and get predictions."""
    loader = DataLoader()
    engineer = FeatureEngineer()
    trainer = XGBoostTrainer()
    
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_stocks = len(models)
    
    for idx, (stock, model) in enumerate(models.items(), 1):
        status_text.text(f"Scanning {stock}... ({idx}/{total_stocks})")
        progress_bar.progress(idx / total_stocks)
        
        try:
            # Load data
            df = loader.load_stock_data(stock)
            if df is None or len(df) < 50:
                continue
            
            # Engineer features
            df_features = engineer.engineer_features(df)
            
            # Get latest data
            latest = df_features.iloc[-1]
            feature_cols = trainer.get_feature_columns(df_features)
            X = df_features[feature_cols].values[-1:]
            
            # Predict
            prediction = model.predict(X)[0]
            proba = model.predict_proba(X)[0]
            
            confidence = proba[prediction] * 100
            buy_proba = proba[1] * 100 if len(proba) > 1 else 0
            
            signal = "BUY" if prediction == 1 else "HOLD"
            
            # Get tier
            if stock in TIER_1_STOCKS:
                tier, tier_label = 1, "HIGH"
            elif stock in TIER_2_STOCKS:
                tier, tier_label = 2, "MEDIUM"
            else:
                tier, tier_label = 3, "LOW"
            
            # Get price info
            latest_price = df.iloc[-1]['close']
            latest_date = df.iloc[-1]['time']
            
            results.append({
                'Stock': stock.replace('NSE_', ''),
                'Signal': signal,
                'Confidence': confidence,
                'Buy_Probability': buy_proba,
                'Tier': tier,
                'Tier_Label': tier_label,
                'Price': latest_price,
                'Date': latest_date
            })
            
        except Exception as e:
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)


def get_stock_tier(stock_name):
    """Get tier for stock."""
    stock_full = f'NSE_{stock_name}'
    if stock_full in TIER_1_STOCKS:
        return 1
    elif stock_full in TIER_2_STOCKS:
        return 2
    return 3


def main():
    """Main dashboard function."""
    
    # Header
    st.markdown('<div class="main-header">📈 AI Stock Screener Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f"**Live Scan** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        min_confidence = st.slider(
            "Minimum Confidence %",
            min_value=0,
            max_value=100,
            value=50,
            step=5,
            help="Filter signals by minimum confidence level"
        )
        
        show_tiers = st.multiselect(
            "Show Tiers",
            options=[1, 2, 3],
            default=[1, 2],
            help="Tier 1 = High accuracy, Tier 3 = Low accuracy"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Model Info")
        st.info("✅ 42 Models Trained\n\n✅ Avg Precision: 28.6%\n\n✅ Top 10: 40-60%")
        
        st.markdown("---")
        st.markdown("### 🎯 Quick Guide")
        st.success("""
**Tier 1 (HIGH):**  
Best for VWAP strategy  
40-60% accurate

**Tier 2 (MEDIUM):**  
Use selectively  
30-40% accurate

**Tier 3 (LOW):**  
Avoid - too stable  
<20% accurate
        """)
        
        if st.button("🔄 Refresh Scan", type="primary"):
            st.cache_data.clear()
            st.rerun()
    
    # Load models
    with st.spinner("Loading AI models..."):
        models = load_all_models()
    
    st.success(f"✓ Loaded {len(models)} trained models")
    
    # Scan stocks
    with st.spinner("Scanning all stocks... This may take 30-60 seconds..."):
        df_results = scan_all_stocks(models)
    
    if df_results.empty:
        st.error("No results found. Check data availability.")
        return
    
    # Summary metrics
    st.markdown("## 📊 Today's Scan Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_stocks = len(df_results)
    buy_signals = len(df_results[df_results['Signal'] == 'BUY'])
    tier1_buys = len(df_results[(df_results['Signal'] == 'BUY') & (df_results['Tier'] == 1)])
    avg_confidence = df_results[df_results['Signal'] == 'BUY']['Confidence'].mean() if buy_signals > 0 else 0
    
    with col1:
        st.metric("Total Stocks Scanned", total_stocks)
    with col2:
        st.metric("BUY Signals", buy_signals, delta=f"{buy_signals} opportunities")
    with col3:
        st.metric("Tier 1 BUY Signals", tier1_buys, delta="High Confidence")
    with col4:
        st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
    
    st.markdown("---")
    
    # Filter results
    buy_signals_df = df_results[
        (df_results['Signal'] == 'BUY') & 
        (df_results['Confidence'] >= min_confidence) &
        (df_results['Tier'].isin(show_tiers))
    ].copy()
    
    # TIER 1 SIGNALS
    tier1_signals = buy_signals_df[buy_signals_df['Tier'] == 1].sort_values('Confidence', ascending=False)
    
    if not tier1_signals.empty:
        st.markdown("## 🌟 TIER 1 - HIGH CONFIDENCE SIGNALS")
        st.markdown("**These are your BEST opportunities!** (40-60% accurate)")
        
        # Display as cards
        for idx, row in tier1_signals.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="tier1-signal">
                    <h3>🎯 {row['Stock']}</h3>
                    <p><strong>Confidence:</strong> {row['Confidence']:.1f}% | 
                    <strong>Price:</strong> Rs {row['Price']:.2f} | 
                    <strong>Buy Probability:</strong> {row['Buy_Probability']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Table view
        st.dataframe(
            tier1_signals[['Stock', 'Confidence', 'Buy_Probability', 'Price', 'Date']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("⚠️ No Tier 1 signals found today")
    
    st.markdown("---")
    
    # TIER 2 SIGNALS
    if 2 in show_tiers:
        tier2_signals = buy_signals_df[buy_signals_df['Tier'] == 2].sort_values('Confidence', ascending=False)
        
        if not tier2_signals.empty:
            st.markdown("## ✓ TIER 2 - MEDIUM CONFIDENCE SIGNALS")
            st.markdown("**Consider these if Tier 1 looks limited** (30-40% accurate)")
            
            st.dataframe(
                tier2_signals[['Stock', 'Confidence', 'Buy_Probability', 'Price', 'Date']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No Tier 2 signals above your confidence threshold")
    
    st.markdown("---")
    
    # TIER 3 SIGNALS
    if 3 in show_tiers:
        tier3_signals = buy_signals_df[buy_signals_df['Tier'] == 3].sort_values('Confidence', ascending=False)
        
        if not tier3_signals.empty:
            with st.expander("⚠️ TIER 3 - LOW CONFIDENCE SIGNALS (Not Recommended)"):
                st.markdown("**Avoid these** - Low volatility stocks (<20% accurate)")
                st.dataframe(
                    tier3_signals[['Stock', 'Confidence', 'Buy_Probability', 'Price', 'Date']],
                    use_container_width=True,
                    hide_index=True
                )
    
    # Visualization
    st.markdown("---")
    st.markdown("## 📊 Signal Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart - Signal distribution
        signal_counts = df_results['Signal'].value_counts()
        fig_pie = px.pie(
            values=signal_counts.values,
            names=signal_counts.index,
            title="Overall Signal Distribution",
            color_discrete_map={'BUY': '#28a745', 'HOLD': '#6c757d'}
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Bar chart - BUY signals by tier
        buy_by_tier = buy_signals_df.groupby('Tier_Label').size().reset_index(name='Count')
        fig_bar = px.bar(
            buy_by_tier,
            x='Tier_Label',
            y='Count',
            title="BUY Signals by Tier",
            color='Tier_Label',
            color_discrete_map={'HIGH': '#28a745', 'MEDIUM': '#ffc107', 'LOW': '#dc3545'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Top confidence signals
    st.markdown("---")
    st.markdown("## 🏆 Top 10 Highest Confidence Signals")
    
    top_10 = buy_signals_df.nlargest(10, 'Confidence')[['Stock', 'Tier_Label', 'Confidence', 'Buy_Probability', 'Price']]
    
    # Color code by tier
    def highlight_tier(row):
        if row['Tier_Label'] == 'HIGH':
            return ['background-color: #d4edda'] * len(row)
        elif row['Tier_Label'] == 'MEDIUM':
            return ['background-color: #fff3cd'] * len(row)
        else:
            return ['background-color: #f8d7da'] * len(row)
    
    if not top_10.empty:
        styled_df = top_10.style.apply(highlight_tier, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No BUY signals found")
    
    # Action plan
    st.markdown("---")
    st.markdown("## 📋 Recommended Action Plan")
    
    if not tier1_signals.empty:
        st.success(f"""
**STEP 1: Focus on {len(tier1_signals)} Tier 1 stocks**
- These have 40-60% accuracy
- Run VWAP Filter backtest on these
- Select best 2-3 based on profit potential
        """)
    
    if not tier2_signals.empty and len(tier1_signals) < 3:
        st.info(f"""
**STEP 2: Consider top 5 from {len(tier2_signals)} Tier 2 stocks**
- Use if Tier 1 has limited signals
- Verify with VWAP Filter
- Trade only if backtest looks strong
        """)
    
    st.warning("""
**STEP 3: Next Steps**
1. Note down Tier 1 + Top Tier 2 stocks
2. Copy their CSV files to separate folder
3. Run: `python RVwapfilter_ssc.py`
4. Compare 3%, 6%, 10% profit targets
5. Select best 2-3 stocks to trade today
    """)
    
    # Download button
    st.markdown("---")
    
    # Create downloadable CSV
    csv = buy_signals_df.to_csv(index=False)
    st.download_button(
        label="📥 Download BUY Signals (CSV)",
        data=csv,
        file_name=f'ai_screener_signals_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv'
    )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>AI Stock Screener | VWAP Ladder Strategy | Models trained on historical data</p>
        <p>⚠️ Use signals as screening tool only. Always verify with VWAP backtest and your analysis.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    # Title
    st.title("🤖 AI Stock Screener")
    st.caption("Nifty 50 Stock Scanner for VWAP Ladder Strategy")
    
    try:
        # Load models
        with st.spinner("Loading trained models..."):
            models = load_all_models()
        
        if not models:
            st.error("❌ No models found! Please train models first.")
            st.info("Run: `python train_all_stocks.py`")
        else:
            st.success(f"✅ Loaded {len(models)} trained AI models")
            
            # Run scanner
            main()
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

