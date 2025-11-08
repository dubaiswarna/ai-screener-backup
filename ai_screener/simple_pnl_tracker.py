"""
SIMPLE P&L TRACKER - Track Your AI Calls Anytime
=================================================
Auto-updates, saves history, accessible 24/7
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent))

from save_signals_csv import load_all_saved_signals
from live_data_loader import LiveDataLoader

# Page config
st.set_page_config(
    page_title='P&L Tracker',
    page_icon='💰',
    layout='wide'
)

st.title("💰 LIVE P&L TRACKER - Track Your AI Calls Anytime")
st.markdown("**Auto-updates prices • Saves history • Always accessible**")

# Load your saved signals
df_signals = load_all_saved_signals()

if df_signals.empty:
    st.error("❌ No signals found!")
    st.info("💡 Generate signals first using the auto-execute screener")
    st.stop()

st.success(f"✅ Tracking {len(df_signals)} AI-generated signals")

# Fetch LIVE prices
with st.spinner('📡 Fetching live prices for all stocks...'):
    
    live_loader = LiveDataLoader()
    results = []
    
    progress = st.progress(0)
    
    for i, (_, row) in enumerate(df_signals.iterrows()):
        symbol = row['symbol']
        entry = float(row['current_price'])
        signal = str(row['signal']).upper()
        target = float(row.get('target_price', entry * (1.10 if signal == 'BUY' else 0.90)))
        stop = float(row.get('stop_loss', entry * (0.95 if signal == 'BUY' else 1.05)))
        qty = int(row.get('recommended_qty', 10))
        conf = float(row['confidence']) * 100
        
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
        if signal == 'SELL':
            pnl_per_share = entry - current
            target_hit = current <= target
            stop_hit = current >= stop
        else:  # BUY
            pnl_per_share = current - entry
            target_hit = current >= target
            stop_hit = current <= stop
        
        total_pnl = pnl_per_share * qty
        pnl_pct = (pnl_per_share / entry) * 100
        
        # Status
        if target_hit:
            status = "🎯 TARGET"
        elif stop_hit:
            status = "🛑 STOP"
        else:
            status = "📊 Active"
        
        results.append({
            'Symbol': symbol,
            'Signal': signal,
            'Entry': entry,
            'Current': current,
            'Target': target,
            'Stop': stop,
            'Qty': qty,
            'P&L': total_pnl,
            'P&L %': pnl_pct,
            'Status': status,
            'Conf %': conf
        })
        
        progress.progress((i + 1) / len(df_signals))
    
    progress.empty()

# Create P&L dataframe
df_pnl = pd.DataFrame(results)

# Save P&L snapshot
pnl_dir = Path("pnl_history")
pnl_dir.mkdir(exist_ok=True)
snapshot_file = pnl_dir / f"pnl_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df_pnl.to_csv(snapshot_file, index=False)

# ============================================================
# PORTFOLIO SUMMARY
# ============================================================

st.markdown("---")
st.subheader("💼 Portfolio Summary")

col1, col2, col3, col4 = st.columns(4)

total_investment = (df_pnl['Entry'] * df_pnl['Qty']).sum()
current_value = (df_pnl['Current'] * df_pnl['Qty']).sum()
total_pnl = df_pnl['P&L'].sum()
total_pnl_pct = (total_pnl / total_investment * 100) if total_investment > 0 else 0

with col1:
    st.metric("Total Investment", f"₹{total_investment:,.0f}")

with col2:
    st.metric("Current Value", f"₹{current_value:,.0f}")

with col3:
    st.metric("Total P&L", f"₹{total_pnl:,.0f}", 
             delta=f"{total_pnl_pct:.2f}%",
             delta_color="normal" if total_pnl >= 0 else "inverse")

with col4:
    winners = len(df_pnl[df_pnl['P&L'] > 0])
    win_rate = (winners / len(df_pnl) * 100) if len(df_pnl) > 0 else 0
    st.metric("Winners", f"{winners}/{len(df_pnl)}", f"{win_rate:.0f}% win rate")

# ============================================================
# COMPACT TABLE - ALL STOCKS VISIBLE
# ============================================================

st.markdown("---")
st.subheader("📊 All Positions")

# Format table
df_display = df_pnl.copy()
df_display = df_display.sort_values('P&L', ascending=False)

# Format columns
df_display['Entry'] = df_display['Entry'].apply(lambda x: f"₹{x:,.2f}")
df_display['Current'] = df_display['Current'].apply(lambda x: f"₹{x:,.2f}")
df_display['P&L'] = df_display.apply(
    lambda row: f"₹{row['P&L']:,.0f} ({row['P&L %']:.2f}%)", axis=1
)
df_display['Conf %'] = df_display['Conf %'].apply(lambda x: f"{x:.1f}%")

# Show table
st.dataframe(
    df_display[['Symbol', 'Signal', 'Entry', 'Current', 'P&L', 'Status', 'Conf %']],
    use_container_width=True,
    height=500  # All stocks visible
)

# ============================================================
# P&L CHART
# ============================================================

st.markdown("---")
st.subheader("📊 P&L Distribution")

fig = go.Figure()

df_chart = df_pnl.sort_values('P&L', ascending=False)
colors = ['green' if pnl > 0 else 'red' for pnl in df_chart['P&L']]

fig.add_trace(go.Bar(
    x=df_chart['Symbol'],
    y=df_chart['P&L'],
    marker_color=colors,
    text=[f"₹{pnl:,.0f}" for pnl in df_chart['P&L']],
    textposition='outside'
))

fig.update_layout(
    xaxis_title="Stock",
    yaxis_title="P&L (₹)",
    height=400,
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================
# EXPORT & HISTORY
# ============================================================

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    # Download current P&L
    csv_data = df_pnl.to_csv(index=False)
    st.download_button(
        "📥 Download Current P&L",
        csv_data,
        f"pnl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv",
        use_container_width=True
    )

with col2:
    # View history
    if st.button("📜 View P&L History", use_container_width=True):
        pnl_files = list(pnl_dir.glob("pnl_snapshot_*.csv"))
        if pnl_files:
            st.success(f"📁 {len(pnl_files)} P&L snapshots saved")
            for pnl_file in sorted(pnl_files, reverse=True)[:5]:
                st.caption(f"• {pnl_file.name}")
        else:
            st.info("No history yet")

# Footer
st.markdown("---")
st.caption(f"💡 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("🔄 Click 'UPDATE PRICES' to refresh anytime!")
st.caption(f"📁 P&L history saved in: {pnl_dir}")

