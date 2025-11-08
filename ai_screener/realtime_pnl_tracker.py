"""
REAL-TIME P&L TRACKER - Using Dhan Live Tick Data
==================================================
TRUE live prices with < 1 second delay!
Auto-updates every few seconds!
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import sys
import os
import time

sys.path.append(str(Path(__file__).parent.parent))

from save_signals_csv import load_all_saved_signals

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / '.env')
except:
    pass

# Try to import Dhan
try:
    from dhan_live_data import get_dhan_live_data
    DHAN_AVAILABLE = True
    dhan_data = get_dhan_live_data()
except Exception as e:
    DHAN_AVAILABLE = False
    st.sidebar.error(f"⚠️ Dhan API not available: {e}")

# Page config
st.set_page_config(
    page_title='Real-Time P&L Tracker',
    page_icon='⚡',
    layout='wide'
)

# Custom CSS
st.markdown("""
<style>
    .live-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #00ff00;
        border-radius: 50%;
        animation: blink 1s infinite;
    }
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
    .price-up { color: green; font-weight: bold; }
    .price-down { color: red; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
     padding: 2rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;'>
    <h1>⚡ REAL-TIME P&L TRACKER</h1>
    <p style='font-size:1.2em;'>Live Tick Data from Dhan API • Auto-Updates Every Second!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Settings")

# Dhan status
if DHAN_AVAILABLE:
    st.sidebar.success("✅ Dhan API: Connected")
    st.sidebar.markdown('<div class="live-indicator"></div> <span>LIVE DATA</span>', unsafe_allow_html=True)
else:
    st.sidebar.error("❌ Dhan API: Not connected")
    st.sidebar.info("Using delayed data instead")

# Auto-refresh
auto_refresh = st.sidebar.checkbox("🔄 Auto-Refresh", value=True)
refresh_interval = st.sidebar.select_slider(
    "Update Interval (seconds)",
    options=[1, 2, 5, 10, 30],
    value=5
)

if auto_refresh:
    st.sidebar.success(f"⚡ Updating every {refresh_interval}s")

# Manual refresh
if st.sidebar.button("🔄 REFRESH NOW", use_container_width=True):
    st.rerun()

# Load signals
df_signals = load_all_saved_signals()

if df_signals.empty:
    st.error("❌ No signals found!")
    st.info("💡 Generate signals first using auto-execute screener")
    st.stop()

st.sidebar.metric("Tracking Signals", len(df_signals))

# ============================================================
# FETCH LIVE PRICES FROM DHAN
# ============================================================

with st.spinner('⚡ Fetching LIVE prices from Dhan...'):
    
    results = []
    
    # Get all symbols
    symbols = df_signals['symbol'].tolist()
    
    if DHAN_AVAILABLE:
        # Batch fetch (much faster!)
        try:
            live_prices = dhan_data.get_live_prices_batch(symbols)
            
            if len(live_prices) > 0:
                st.sidebar.success(f"✅ Got {len(live_prices)} live prices from Dhan!")
            else:
                st.sidebar.warning("⚠️ Market closed - using Yahoo Finance data")
                # Fallback to Yahoo Finance when market closed
                from live_data_loader import LiveDataLoader
                loader = LiveDataLoader()
                live_prices = {}
                for symbol in symbols:
                    try:
                        df = loader.fetch_live_data(symbol, period="2d")
                        if df is not None and not df.empty:
                            live_prices[symbol] = float(df['Close'].iloc[-1])
                    except:
                        pass
                
                if len(live_prices) > 0:
                    st.sidebar.info(f"📊 Got {len(live_prices)} prices from Yahoo Finance")
                    
        except Exception as e:
            st.sidebar.error(f"Dhan error: {e}")
            st.sidebar.info("Trying Yahoo Finance as fallback...")
            live_prices = {}
            # Try Yahoo Finance fallback
            from live_data_loader import LiveDataLoader
            loader = LiveDataLoader()
            for symbol in symbols:
                try:
                    df = loader.fetch_live_data(symbol, period="2d")
                    if df is not None and not df.empty:
                        live_prices[symbol] = float(df['Close'].iloc[-1])
                except:
                    pass
    else:
        st.sidebar.warning("Using Yahoo Finance (Dhan not available)")
        live_prices = {}
        from live_data_loader import LiveDataLoader
        loader = LiveDataLoader()
        for symbol in symbols:
            try:
                df = loader.fetch_live_data(symbol, period="2d")
                if df is not None and not df.empty:
                    live_prices[symbol] = float(df['Close'].iloc[-1])
            except:
                pass
    
    # Calculate P&L for each signal
    for _, row in df_signals.iterrows():
        symbol = row['symbol']
        entry = float(row['current_price'])
        signal = str(row['signal']).upper()
        qty = int(row.get('recommended_qty', 10))
        conf = float(row['confidence']) * 100
        target = float(row.get('target_price', entry * (1.10 if signal == 'BUY' else 0.90)))
        stop = float(row.get('stop_loss', entry * (0.95 if signal == 'BUY' else 1.05)))
        
        # Get live price
        current = live_prices.get(symbol, entry)
        
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
            status_color = "green"
        elif stop_hit:
            status = "🛑 STOP"
            status_color = "red"
        else:
            status = "📊 Active"
            status_color = "blue"
        
        results.append({
            'No': len(results) + 1,
            'Symbol': symbol.replace('NSE_', ''),
            'Signal': signal,
            'Entry': entry,
            'Current': current,
            'Change': current - entry,
            'Qty': qty,
            'P&L': total_pnl,
            'P&L %': pnl_pct,
            'Status': status,
            'Status Color': status_color,
            'Conf': conf,
            'Target': target,
            'Stop': stop
        })

df_pnl = pd.DataFrame(results)

# Sort by P&L (best to worst)
df_pnl = df_pnl.sort_values('P&L', ascending=False)
df_pnl['No'] = range(1, len(df_pnl) + 1)  # Renumber after sort

# Save snapshot
pnl_dir = Path("pnl_history")
pnl_dir.mkdir(exist_ok=True)
df_pnl.to_csv(pnl_dir / f"pnl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", index=False)

# ============================================================
# PORTFOLIO SUMMARY
# ============================================================

st.subheader("💼 Portfolio Summary")

col1, col2, col3, col4, col5 = st.columns(5)

total_investment = (df_pnl['Entry'] * df_pnl['Qty']).sum()
current_value = (df_pnl['Current'] * df_pnl['Qty']).sum()
total_pnl = df_pnl['P&L'].sum()
total_pnl_pct = (total_pnl / total_investment * 100) if total_investment > 0 else 0
winners = len(df_pnl[df_pnl['P&L'] > 0])
losers = len(df_pnl[df_pnl['P&L'] < 0])

with col1:
    st.metric("Investment", f"₹{total_investment:,.0f}")

with col2:
    st.metric("Current Value", f"₹{current_value:,.0f}")

with col3:
    st.metric("Total P&L", f"₹{total_pnl:,.0f}", 
             delta=f"{total_pnl_pct:.2f}%",
             delta_color="normal" if total_pnl >= 0 else "inverse")

with col4:
    st.metric("Winners", winners, f"{(winners/len(df_pnl)*100):.0f}% win rate" if len(df_pnl) > 0 else "0%")

with col5:
    st.metric("Losers", losers)

# ============================================================
# COMPACT TABLE - ALL STOCKS VISIBLE
# ============================================================

st.markdown("---")
st.subheader("📊 Live Positions (Sorted by P&L)")

# Format for display
df_display = df_pnl.copy()
df_display['Entry'] = df_display['Entry'].apply(lambda x: f"₹{x:,.2f}")
df_display['Current'] = df_display['Current'].apply(lambda x: f"₹{x:,.2f}")
df_display['Change'] = df_display['Change'].apply(lambda x: f"₹{x:+,.2f}")
df_display['P&L'] = df_display.apply(
    lambda row: f"₹{row['P&L']:,.0f} ({row['P&L %']:+.2f}%)", axis=1
)
df_display['Conf'] = df_display['Conf'].apply(lambda x: f"{x:.1f}%")

# Color code P&L
def highlight_pnl(row):
    if '(' in str(row['P&L']):
        if '+' in str(row['P&L']):
            return ['background-color: #d4edda'] * len(row)  # Green
        elif '-' in str(row['P&L']):
            return ['background-color: #f8d7da'] * len(row)  # Red
    return [''] * len(row)

# Show table
st.dataframe(
    df_display[['No', 'Symbol', 'Signal', 'Entry', 'Current', 'Change', 'P&L', 'Status', 'Conf']],
    use_container_width=True,
    height=500
)

# ============================================================
# P&L CHART
# ============================================================

st.markdown("---")
st.subheader("📊 P&L Distribution")

fig = go.Figure()

colors = ['green' if pnl > 0 else 'red' for pnl in df_pnl['P&L']]

fig.add_trace(go.Bar(
    x=df_pnl['Symbol'],
    y=df_pnl['P&L'],
    marker_color=colors,
    text=[f"₹{pnl:,.0f}<br>{pct:+.2f}%" for pnl, pct in zip(df_pnl['P&L'], df_pnl['P&L %'])],
    textposition='outside',
    hovertemplate='%{x}<br>P&L: ₹%{y:,.0f}<extra></extra>'
))

fig.update_layout(
    xaxis_title="Stock",
    yaxis_title="P&L (₹)",
    height=350,
    showlegend=False,
    hovermode='x'
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================
# DOWNLOAD REPORT
# ============================================================

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    csv_data = df_pnl.to_csv(index=False)
    st.download_button(
        "📥 Download P&L Report",
        csv_data,
        f"pnl_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv",
        use_container_width=True
    )

with col2:
    if st.button("📁 View P&L History", use_container_width=True):
        history_files = list(pnl_dir.glob("pnl_*.csv"))
        st.info(f"📁 {len(history_files)} snapshots saved in pnl_history/")

# ============================================================
# AUTO-REFRESH LOGIC
# ============================================================

# Footer with last update time
st.markdown("---")
current_time = datetime.now()
current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')

# Check if market is open
market_open_time = current_time.replace(hour=9, minute=15, second=0)
market_close_time = current_time.replace(hour=15, minute=30, second=0)
is_market_hours = market_open_time <= current_time <= market_close_time

col1, col2 = st.columns(2)

with col1:
    st.caption(f"⏰ Last updated: {current_time_str}")
    if is_market_hours:
        st.caption("🟢 **MARKET OPEN** - Live tick data available!")
    else:
        st.caption("🔴 **MARKET CLOSED** - Using last close prices")
        st.caption("💡 During market hours (9:15 AM - 3:30 PM), you'll see live tick updates!")

with col2:
    if DHAN_AVAILABLE:
        st.caption("✅ Dhan API: Connected")
    else:
        st.caption("⚠️ Dhan API: Not connected (using Yahoo Finance)")
    
    st.caption(f"💾 History: {pnl_dir}/")

# Auto-refresh timer
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

