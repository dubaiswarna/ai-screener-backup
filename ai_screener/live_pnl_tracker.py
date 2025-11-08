"""
Live P&L Tracker
================
Track profit/loss for your AI-generated signals in real-time
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent))

from save_signals_csv import load_all_saved_signals, get_latest_signals
from live_data_loader import LiveDataLoader

# Page config
st.set_page_config(
    page_title='Live P&L Tracker',
    page_icon='📈',
    layout='wide'
)

# CSS
st.markdown("""
<style>
    .pnl-header {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .profit { color: green; font-weight: bold; }
    .loss { color: red; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('''
<div class="pnl-header">
    <h1>📈 LIVE P&L TRACKER</h1>
    <p style="font-size:1.2em;">Track Your AI Signals in Real-Time</p>
</div>
''', unsafe_allow_html=True)

# Load saved signals
st.sidebar.title('📊 P&L Settings')

signal_source = st.sidebar.radio(
    "Load Signals From:",
    ["Latest CSV", "All CSV Files"],
    help="Choose which signals to track"
)

if signal_source == "Latest CSV":
    df_signals = get_latest_signals()
    st.sidebar.success("📄 Loading latest signals")
else:
    df_signals = load_all_saved_signals()
    st.sidebar.success("📄 Loading all historical signals")

if df_signals.empty:
    st.warning("⚠️ No saved signals found!")
    st.info("💡 Run AUTO SCREEN & EXECUTE first to generate signals!")
    st.stop()

st.sidebar.metric("Total Signals", len(df_signals))

# Filter signals
signal_filter = st.sidebar.multiselect(
    "Show Signal Types",
    ['BUY', 'SELL'],
    default=['BUY', 'SELL']
)

df_signals = df_signals[df_signals['signal'].str.upper().isin([s.upper() for s in signal_filter])]

# Auto-refresh settings
st.sidebar.subheader("🔄 Auto-Refresh")
auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=True,
    help="Automatically update prices every X seconds")

refresh_interval = st.sidebar.selectbox(
    "Refresh Interval",
    [5, 10, 30, 60],
    index=1,
    help="Seconds between price updates"
)

if auto_refresh:
    import time
    st.sidebar.success(f"✅ Auto-refreshing every {refresh_interval}s")
    
if st.sidebar.button("🔄 REFRESH NOW", use_container_width=True):
    st.rerun()

# Main content
st.subheader(f"📊 Tracking {len(df_signals)} Signals")

if len(df_signals) > 0:
    
    # Fetch live prices
    with st.spinner('📡 Fetching live prices...'):
        live_loader = LiveDataLoader()
        
        pnl_data = []
        
        for idx, row in df_signals.iterrows():
            symbol = row['symbol']
            signal_type = str(row['signal']).upper()
            entry_price = float(row['current_price'])
            target = float(row.get('target_price', entry_price * 1.10))
            stop_loss = float(row.get('stop_loss', entry_price * 0.95))
            recommended_qty = int(row.get('recommended_qty', 10))
            
            # Get current live price
            try:
                df_live = live_loader.fetch_live_data(symbol, period="1d")
                if df_live is not None and not df_live.empty:
                    current_price = float(df_live['Close'].iloc[-1])
                else:
                    current_price = entry_price
            except:
                current_price = entry_price
            
            # Calculate P&L
            if signal_type == 'BUY':
                pnl_per_share = current_price - entry_price
            else:  # SELL
                pnl_per_share = entry_price - current_price
            
            total_pnl = pnl_per_share * recommended_qty
            pnl_pct = (pnl_per_share / entry_price) * 100
            
            # Position value
            position_value = recommended_qty * entry_price
            current_value = recommended_qty * current_price
            
            # Risk/Reward status
            if signal_type == 'BUY':
                target_hit = current_price >= target
                stop_hit = current_price <= stop_loss
            else:  # SELL
                target_hit = current_price <= target
                stop_hit = current_price >= stop_loss
            
            pnl_data.append({
                'Symbol': symbol,
                'Signal': signal_type,
                'Entry': entry_price,
                'Current': current_price,
                'Target': target,
                'Stop Loss': stop_loss,
                'Qty': recommended_qty,
                'Position Value': position_value,
                'Current Value': current_value,
                'P&L': total_pnl,
                'P&L %': pnl_pct,
                'Confidence': float(row['confidence']) * 100,
                'Target Hit': target_hit,
                'Stop Hit': stop_hit
            })
        
        df_pnl = pd.DataFrame(pnl_data)
    
    # Summary metrics
    st.markdown("---")
    st.subheader("💰 Portfolio Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_position_value = df_pnl['Position Value'].sum()
    total_current_value = df_pnl['Current Value'].sum()
    total_pnl = df_pnl['P&L'].sum()
    total_pnl_pct = (total_pnl / total_position_value * 100) if total_position_value > 0 else 0
    
    with col1:
        st.metric("Total Investment", f"₹{total_position_value:,.0f}")
    
    with col2:
        st.metric("Current Value", f"₹{total_current_value:,.0f}")
    
    with col3:
        pnl_class = "profit" if total_pnl > 0 else "loss"
        st.metric("Total P&L", f"₹{total_pnl:,.0f}", 
                 delta=f"{total_pnl_pct:.2f}%",
                 delta_color="normal" if total_pnl >= 0 else "inverse")
    
    with col4:
        winners = len(df_pnl[df_pnl['P&L'] > 0])
        win_rate = (winners / len(df_pnl) * 100) if len(df_pnl) > 0 else 0
        st.metric("Win Rate", f"{win_rate:.1f}%", f"{winners}/{len(df_pnl)}")
    
    # Individual positions - COMPACT TABLE VIEW
    st.markdown("---")
    st.subheader("📊 All Positions (Sortable Table)")
    
    # Sort by P&L
    df_pnl_sorted = df_pnl.sort_values('P&L', ascending=False)
    
    # Format for display
    df_display = df_pnl_sorted.copy()
    df_display['Entry'] = df_display['Entry'].apply(lambda x: f"₹{x:,.2f}")
    df_display['Current'] = df_display['Current'].apply(lambda x: f"₹{x:,.2f}")
    df_display['Target'] = df_display['Target'].apply(lambda x: f"₹{x:,.2f}")
    df_display['Stop Loss'] = df_display['Stop Loss'].apply(lambda x: f"₹{x:,.2f}")
    df_display['P&L'] = df_display.apply(
        lambda row: f"₹{row['P&L']:,.0f} ({row['P&L %']:.2f}%)", axis=1
    )
    df_display['Confidence'] = df_display['Confidence'].apply(lambda x: f"{x:.1f}%")
    
    # Status column
    def get_status(row):
        if row['Target Hit']:
            return "🎯 TARGET"
        elif row['Stop Hit']:
            return "🛑 STOP"
        else:
            return "📊 Running"
    
    df_display['Status'] = df_pnl_sorted.apply(get_status, axis=1)
    
    # Show compact table
    st.dataframe(
        df_display[['Symbol', 'Signal', 'Entry', 'Current', 'P&L', 'Status', 'Confidence']],
        use_container_width=True,
        height=600  # Scrollable table
    )
    
    # P&L Chart
    st.markdown("---")
    st.subheader("📈 P&L Distribution")
    
    fig = go.Figure()
    
    colors = ['green' if pnl > 0 else 'red' for pnl in df_pnl_sorted['P&L']]
    
    fig.add_trace(go.Bar(
        x=df_pnl_sorted['Symbol'],
        y=df_pnl_sorted['P&L'],
        marker_color=colors,
        text=[f"₹{pnl:,.0f}" for pnl in df_pnl_sorted['P&L']],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Profit/Loss by Stock",
        xaxis_title="Stock",
        yaxis_title="P&L (₹)",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Export
    st.markdown("---")
    csv_pnl = df_pnl.to_csv(index=False)
    st.download_button(
        "📥 Download P&L Report",
        csv_pnl,
        f"pnl_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv",
        use_container_width=True
    )

else:
    st.info("No signals to track. Generate signals first!")

# Auto-refresh timer
if auto_refresh:
    import time
    time.sleep(refresh_interval)
    st.rerun()

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("""
<div style='text-align:center;color:gray;'>
    <strong>📈 Live P&L Tracker</strong> | 
    {refresh_text} | 
    Based on your AI signals
</div>
""".format(
    refresh_text=f"🔄 Auto-refresh: {refresh_interval}s" if auto_refresh else "Manual refresh only"
), unsafe_allow_html=True)

