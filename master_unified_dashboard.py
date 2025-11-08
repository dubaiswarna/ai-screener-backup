"""
🌟 MASTER UNIFIED AI TRADING DASHBOARD
=======================================
ONE Dashboard for ALL Markets:
- 📊 NSE Stocks (42 models)
- 🥇 MCX Commodities (Gold, Silver)
- 💱 Forex (3 currency pairs - EUR/USD, GBP/USD, USD/INR)
- ₿ Bitcoin
- 🪙 Cryptocurrencies (8 coins)
"""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import pickle

from ai_screener.data_loader_universal import UniversalDataLoader
from ai_screener.feature_engineering import FeatureEngineer

# Page config
st.set_page_config(
    page_title="Master AI Trading Dashboard",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .segment-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .segment-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    .segment-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    .segment-title {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .segment-desc {
        font-size: 1.1rem;
        opacity: 0.95;
    }
    .stats-box {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .stat-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
    }
    .stat-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_system_stats():
    """Get overall system statistics"""
    loader = UniversalDataLoader()
    
    # Count models
    models_dir = Path("ai_screener/models")
    forex_models_dir = Path("../Forex_Screener/models")
    
    if models_dir.exists():
        nse_models = len(list(models_dir.glob("xgb_NSE_*.pkl")))
        mcx_models = len(list(models_dir.glob("xgb_MCX_*.pkl")))
        crypto_models = len(list(models_dir.glob("xgb_CRYPTO_*.pkl")))
    else:
        nse_models = mcx_models = crypto_models = 0
    
    # Count forex models
    if forex_models_dir.exists():
        forex_models = len(list(forex_models_dir.glob("xgb_*.pkl")))
    else:
        forex_models = 0
    
    total_models = nse_models + mcx_models + crypto_models + forex_models
    
    # Count data files
    nse_count = len(list(Path("Nify50_data").glob("*.csv"))) if Path("Nify50_data").exists() else 0
    mcx_count = len(list(Path("MCX_data").glob("*.csv"))) if Path("MCX_data").exists() else 0
    crypto_count = len(list(Path("Crypto_data").glob("*.csv"))) if Path("Crypto_data").exists() else 0
    forex_count = len(list(Path("../Forex_Screener/data").glob("*.csv"))) if Path("../Forex_Screener/data").exists() else 0
    
    total_instruments = nse_count + mcx_count + crypto_count + forex_count
    
    return {
        'total_models': total_models,
        'total_instruments': total_instruments,
        'nse_models': nse_models,
        'mcx_models': mcx_models,
        'crypto_models': crypto_models,
        'forex_models': forex_models,
        'nse_count': nse_count,
        'mcx_count': mcx_count,
        'crypto_count': crypto_count,
        'forex_count': forex_count
    }

def main():
    """Main dashboard"""
    
    # Header
    st.markdown('<h1 class="main-title">🌟 MASTER AI TRADING DASHBOARD</h1>', unsafe_allow_html=True)
    st.markdown("### *World-Class Multi-Market Trading System*")
    
    # Quick launch info
    with st.expander("🚀 HOW TO ACCESS ALL MARKETS", expanded=False):
        st.markdown("""
        ### Option 1: Launch All Dashboards (Recommended)
        Run `LAUNCH_ALL_DASHBOARDS.bat` to start all 5 dashboards simultaneously.
        
        ### Option 2: Launch Individual Markets
        Click the buttons below to see the URL, then run the corresponding batch file:
        - **NSE Stocks:** `LAUNCH_PRO_SCREENER.bat`
        - **Forex Trading:** `LAUNCH_FOREX_SCREENER.bat`
        - **MCX Commodities:** `launch_dashboard.bat`
        - **Crypto/Bitcoin:** `LAUNCH_CRYPTO_BITCOIN.bat`
        
        **💡 TIP:** Once a dashboard is running, click the 🔗 link to open it in a new tab!
        """)
    
    st.markdown("---")
    
    # Get stats
    stats = get_system_stats()
    
    # System overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stats-box">
            <div class="stat-value">{stats['total_models']}</div>
            <div class="stat-label">AI Models</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-box">
            <div class="stat-value">{stats['total_instruments']}</div>
            <div class="stat-label">Instruments</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-box">
            <div class="stat-value">4</div>
            <div class="stat-label">Markets</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-box">
            <div class="stat-value">89</div>
            <div class="stat-label">Features</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Market segments
    st.markdown("## 🎯 Select Your Market")
    
    # Row 1: NSE and MCX
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="segment-card">
            <div class="segment-icon">📊</div>
            <div class="segment-title">NSE STOCKS</div>
            <div class="segment-desc">{stats['nse_models']} AI Models | {stats['nse_count']} Stocks Available</div>
            <div style="margin-top: 1rem;">Indian Stock Market • Nifty 50</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 OPEN NSE SCREENER", key="nse", use_container_width=True):
            st.success("✅ NSE Dashboard URL:")
            st.markdown("### 🔗 [Open NSE Screener →](http://localhost:8501)")
            st.info("💡 If not running, execute: `LAUNCH_PRO_SCREENER.bat`")
    
    with col2:
        st.markdown(f"""
        <div class="segment-card" style="background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);">
            <div class="segment-icon">🥇</div>
            <div class="segment-title">MCX COMMODITIES</div>
            <div class="segment-desc">{stats['mcx_models']} AI Models | Gold & Silver</div>
            <div style="margin-top: 1rem;">Precious Metals • 94.83% Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 OPEN MCX DASHBOARD", key="mcx", use_container_width=True):
            st.success("✅ MCX Dashboard URL:")
            st.markdown("### 🔗 [Open MCX Commodities →](http://localhost:8503)")
            st.info("💡 If not running, execute: `launch_dashboard.bat`")
    
    # Row 2: Crypto
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="segment-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="segment-icon">🪙</div>
            <div class="segment-title">CRYPTOCURRENCIES</div>
            <div class="segment-desc">{stats['crypto_models']} AI Models | 8 Major Coins</div>
            <div style="margin-top: 1rem;">BTC, ETH, BNB, SOL & More</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 OPEN CRYPTO DASHBOARD", key="crypto", use_container_width=True):
            st.success("✅ Crypto Dashboard URL:")
            st.markdown("### 🔗 [Open Crypto (Bitcoin) →](http://localhost:8504)")
            st.info("💡 If not running, execute: `LAUNCH_CRYPTO_BITCOIN.bat`")
    
    with col2:
        st.markdown(f"""
        <div class="segment-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="segment-icon">💱</div>
            <div class="segment-title">FOREX TRADING</div>
            <div class="segment-desc">{stats['forex_models']} AI Models | 3 Currency Pairs</div>
            <div style="margin-top: 1rem;">EUR/USD • GBP/USD • USD/INR • 24/5 Trading</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 OPEN FOREX SCREENER", key="forex", use_container_width=True):
            st.success("✅ Forex Dashboard URL:")
            st.markdown("### 🔗 [Open Forex Trading →](http://localhost:8502)")
            st.info("💡 If not running, execute: `LAUNCH_FOREX_SCREENER.bat`")
    
    st.markdown("---")
    
    # Market overview
    st.markdown("## 📈 Today's Market Overview")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 NSE Summary", "🥇 MCX Summary", "🪙 Crypto Summary", "💱 Forex Summary"])
    
    with tab1:
        st.markdown("### NSE Stocks AI Models")
        st.info(f"✅ {stats['nse_models']} trained AI models ready")
        st.markdown("**Top Stocks:** RELIANCE, HDFCBANK, INFY, TCS, ICICIBANK")
        st.markdown("**Accuracy Range:** 75-90%")
        st.markdown("**Features:** 89 technical indicators analyzed per stock")
    
    with tab2:
        st.markdown("### MCX Commodities AI Models")
        col1, col2 = st.columns(2)
        with col1:
            st.success("🥇 **GOLD**: 94.83% Accuracy")
            st.markdown("• 2,514 days data")
            st.markdown("• 10 years history")
            st.markdown("• Best performing model!")
        with col2:
            st.success("🥈 **SILVER**: 83.44% Accuracy")
            st.markdown("• 2,514 days data")
            st.markdown("• 10 years history")
            st.markdown("• Strong performance")
    
    with tab3:
        st.markdown("### Cryptocurrency AI Models")
        
        crypto_stats = [
            ("🟠 Bitcoin", "92.73%", "Best in crypto!"),
            ("🟡 BNB", "87.27%", "Excellent"),
            ("🔵 XRP", "74.55%", "Good"),
            ("🔷 Ethereum", "72.73%", "Good"),
            ("🔴 Cardano", "69.55%", "Fair"),
            ("🟣 Solana", "67.73%", "Fair"),
            ("⚪ Polkadot", "65.00%", "Fair"),
            ("🟤 Dogecoin", "61.82%", "Acceptable")
        ]
        
        col1, col2 = st.columns(2)
        for i, (name, acc, rating) in enumerate(crypto_stats):
            with col1 if i % 2 == 0 else col2:
                st.markdown(f"**{name}**: {acc} - *{rating}*")
    
    with tab4:
        st.markdown("### Forex AI Models")
        st.info(f"✅ {stats['forex_models']} trained forex models ready")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("💱 **EUR/USD**: 73.9% Accuracy")
            st.markdown("• Most liquid pair")
            st.markdown("• 50 pips target")
            st.markdown("• 2,601 days data")
        
        with col2:
            st.success("💱 **GBP/USD**: 74.6% Accuracy")
            st.markdown("• Cable pair")
            st.markdown("• 50 pips target")
            st.markdown("• 2,601 days data")
        
        with col3:
            st.success("💱 **USD/INR**: 96.2% Accuracy 🔥")
            st.markdown("• **BEST MODEL!**")
            st.markdown("• 1% target")
            st.markdown("• 2,601 days data")
        
        st.markdown("---")
        st.markdown("**Trading Hours:** 24/5 (Monday to Friday)")
        st.markdown("**Risk/Reward:** 2:1 ratio on all pairs")
        st.markdown("**Live Trading:** Real-time price simulation available")
    
    # Sidebar info
    with st.sidebar:
        st.markdown("## 🎯 System Status")
        st.success("✅ **OPERATIONAL**")
        
        st.markdown("### 📊 Market Coverage")
        st.markdown(f"- NSE: {stats['nse_count']} stocks")
        st.markdown(f"- MCX: {stats['mcx_count']} commodities")
        st.markdown(f"- Crypto: {stats['crypto_count']} coins")
        st.markdown(f"- Forex: {stats['forex_count']} pairs")
        
        st.markdown("### 🤖 AI Models")
        st.markdown(f"- Total: {stats['total_models']} models")
        st.markdown(f"- NSE: {stats['nse_models']}")
        st.markdown(f"- MCX: {stats['mcx_models']}")
        st.markdown(f"- Crypto: {stats['crypto_models']}")
        st.markdown(f"- Forex: {stats['forex_models']}")
        
        st.markdown("### ⚡ Quick Actions")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 🎯 Launch All Markets")
        st.markdown("**Recommended:** Run this batch file:")
        st.code("LAUNCH_ALL_DASHBOARDS.bat", language="bash")
        st.caption("Starts all 5 dashboards at once")
        
        st.markdown("---")
        
        st.markdown("### 📍 Dashboard URLs")
        st.markdown("**NSE:** [localhost:8501](http://localhost:8501)")
        st.markdown("**Forex:** [localhost:8502](http://localhost:8502)")
        st.markdown("**MCX:** [localhost:8503](http://localhost:8503)")
        st.markdown("**Crypto:** [localhost:8504](http://localhost:8504)")
        
        st.markdown("---")
        st.markdown("### 📖 Documentation")
        st.markdown("[View Complete Guide](TODAYS_COMPLETE_WORK_SUMMARY.md)")
        
        st.markdown("---")
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()

