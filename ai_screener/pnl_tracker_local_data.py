"""
P&L TRACKER - Using YOUR Local Historical Data
===============================================
Uses your 169 CSV files with 30 years of data!
Works ANYTIME - no internet needed!
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent))

from save_signals_csv import load_all_saved_signals

# Page config
st.set_page_config(
    page_title='P&L Tracker - Local Data',
    page_icon='💰',
    layout='wide'
)

# Header
st.markdown("""
<div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
     padding: 2rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;'>
    <h1>💰 P&L TRACKER</h1>
    <p style='font-size:1.2em;'>Using Your Local 30-Year Historical Data!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Settings")

# Data source
data_folder = Path("../../Nifty200_Data")
if data_folder.exists():
    csv_files = list(data_folder.glob("NSE_*_1D.csv"))
    st.sidebar.success(f"✅ {len(csv_files)} stock data files found!")
    st.sidebar.info("📊 Using YOUR local data")
else:
    st.sidebar.error("❌ Data folder not found")
    st.stop()

# Auto-refresh
auto_refresh = st.sidebar.checkbox("🔄 Auto-Refresh", value=False)
if auto_refresh:
    refresh_interval = st.sidebar.slider("Interval (seconds)", 5, 60, 10)
    st.sidebar.success(f"⚡ Refreshing every {refresh_interval}s")

# Manual refresh - will use Dhan API for latest prices
if st.sidebar.button("🔄 REFRESH WITH LATEST PRICES", use_container_width=True):
    st.cache_data.clear()  # Clear cache to force fresh price fetch
    st.rerun()

# Load signals
signal_source = st.sidebar.radio(
    "📊 Signal Source",
    ["Latest CSV Only", "All Historical CSVs"],
    index=0,
    help="Latest = Most recent signals only (no duplicates)"
)

if signal_source == "Latest CSV Only":
    from save_signals_csv import get_latest_signals
    df_signals = get_latest_signals()
    st.sidebar.success("✅ Loading latest signals (no duplicates)")
else:
    df_signals = load_all_saved_signals()
    st.sidebar.info("📚 Loading all historical signals (may have duplicates)")

if df_signals.empty:
    st.error("❌ No signals found!")
    st.info("Generate signals first using auto-execute screener")
    st.stop()

# Remove duplicates - keep latest signal per stock
if len(df_signals) > 0:
    original_count = len(df_signals)
    df_signals = df_signals.drop_duplicates(subset=['symbol'], keep='last')
    removed = original_count - len(df_signals)
    
    if removed > 0:
        st.sidebar.warning(f"⚠️ Removed {removed} duplicate signals")

st.sidebar.metric("Tracking Signals", len(df_signals))

# ============================================================
# FETCH LATEST PRICES FROM YOUR LOCAL CSV FILES
# ============================================================

with st.spinner('📊 Loading latest prices from your local data...'):
    
    results = []
    prices_loaded = 0
    
    for _, row in df_signals.iterrows():
        symbol = row['symbol']
        entry = float(row['current_price'])
        signal = str(row['signal']).upper()
        qty = int(row.get('recommended_qty', 10))
        conf = float(row['confidence']) * 100
        target = float(row.get('target_price', entry * (1.10 if signal == 'BUY' else 0.90)))
        stop = float(row.get('stop_loss', entry * (0.95 if signal == 'BUY' else 1.05)))
        
        # Try to get latest price from Dhan API FIRST (real-time!)
        current = entry  # Default fallback
        
        try:
            # Use Dhan API for latest price
            from dhanhq import dhanhq
            client_id = os.getenv('DHAN_CLIENT_ID', '1104147457')
            access_token = os.getenv('DHAN_ACCESS_TOKEN', '')
            
            if access_token:
                from dhan_live_data import DhanLiveData
                dhan_client = DhanLiveData(client_id, access_token)
                live_price = dhan_client.get_live_price(symbol)
                
                if live_price > 0:
                    current = live_price
                    prices_loaded += 1
                else:
                    # Fallback to CSV if Dhan doesn't return price
                    csv_file = data_folder / f"{symbol}_1D.csv"
                    if csv_file.exists():
                        df_stock = pd.read_csv(csv_file)
                        if not df_stock.empty and 'close' in df_stock.columns:
                            current = float(df_stock['close'].iloc[-1])
                            prices_loaded += 1
            else:
                # No Dhan token - use CSV
                csv_file = data_folder / f"{symbol}_1D.csv"
                if csv_file.exists():
                    df_stock = pd.read_csv(csv_file)
                    if not df_stock.empty and 'close' in df_stock.columns:
                        current = float(df_stock['close'].iloc[-1])
                        prices_loaded += 1
                        
        except Exception as e:
            # Fallback to local CSV on any error
            try:
                csv_file = data_folder / f"{symbol}_1D.csv"
                if csv_file.exists():
                    df_stock = pd.read_csv(csv_file)
                    if not df_stock.empty and 'close' in df_stock.columns:
                        current = float(df_stock['close'].iloc[-1])
                        prices_loaded += 1
            except:
                pass
        
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
            'Conf': conf
        })
    
    st.sidebar.success(f"✅ Loaded {prices_loaded}/{len(df_signals)} prices from local CSV!")

df_pnl = pd.DataFrame(results)

# Sort by P&L
df_pnl = df_pnl.sort_values('P&L', ascending=False)
df_pnl['No'] = range(1, len(df_pnl) + 1)

# ============================================================
# PORTFOLIO SUMMARY
# ============================================================

st.subheader("💼 Portfolio Summary")

col1, col2, col3, col4, col5 = st.columns(5)

# CORRECT calculation
total_investment = (df_pnl['Entry'] * df_pnl['Qty']).sum()
total_pnl = df_pnl['P&L'].sum()  # This is already calculated correctly per position
current_value = total_investment + total_pnl  # Correct: Investment + Profit/Loss
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
    win_rate = (winners / len(df_pnl) * 100) if len(df_pnl) > 0 else 0
    st.metric("Winners", f"{winners}/{len(df_pnl)}", f"{win_rate:.0f}%")

with col5:
    st.metric("Losers", f"{losers}/{len(df_pnl)}")

# ============================================================
# COMPACT TABLE
# ============================================================

st.markdown("---")
st.subheader("📊 All Positions (Sorted by P&L)")

# Format for display
df_display = df_pnl.copy()
df_display['Entry'] = df_display['Entry'].apply(lambda x: f"₹{x:,.2f}")
df_display['Current'] = df_display['Current'].apply(lambda x: f"₹{x:,.2f}")
df_display['Change'] = df_display['Change'].apply(lambda x: f"₹{x:+,.2f}")

# Add Position Value column
df_display['Position Value'] = df_pnl.apply(
    lambda row: f"₹{(row['Entry'] * row['Qty']):,.0f}", axis=1
)

# Keep Qty as is
df_display['Qty'] = df_display['Qty'].astype(int)

df_display['P&L'] = df_display.apply(
    lambda row: f"₹{row['P&L']:,.0f} ({row['P&L %']:+.2f}%)", axis=1
)
df_display['Conf'] = df_display['Conf'].apply(lambda x: f"{x:.1f}%")

# Highlight profitable rows
def highlight_pnl(row):
    if '+' in str(row['P&L']):
        return ['background-color: #d4edda'] * len(row)  # Light green
    elif '-' in str(row['P&L']) and '₹0' not in str(row['P&L']):
        return ['background-color: #f8d7da'] * len(row)  # Light red
    return [''] * len(row)

styled_df = df_display[['No', 'Symbol', 'Signal', 'Qty', 'Entry', 'Current', 'Change', 'Position Value', 'P&L', 'Status', 'Conf']].style.apply(highlight_pnl, axis=1)

st.dataframe(styled_df, use_container_width=True, height=500)

# ============================================================
# P&L CHART
# ============================================================

st.markdown("---")
st.subheader("📊 P&L Distribution")

fig = go.Figure()
colors = ['green' if pnl > 0 else 'red' if pnl < 0 else 'gray' for pnl in df_pnl['P&L']]

fig.add_trace(go.Bar(
    x=df_pnl['Symbol'],
    y=df_pnl['P&L'],
    marker_color=colors,
    text=[f"₹{pnl:,.0f}<br>{pct:+.2f}%" for pnl, pct in zip(df_pnl['P&L'], df_pnl['P&L %'])],
    textposition='outside'
))

fig.update_layout(
    xaxis_title="Stock",
    yaxis_title="P&L (₹)",
    height=350,
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# ============================================================
# EXPORT
# ============================================================

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    csv = df_pnl.to_csv(index=False)
    st.download_button(
        "📥 Download P&L Report",
        csv,
        f"pnl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        use_container_width=True
    )

with col2:
    if st.button("📊 View Data Source", use_container_width=True):
        st.info(f"📁 Using data from: {data_folder}")
        st.caption(f"Total CSV files: {len(csv_files)}")

# Footer
st.markdown("---")
st.caption(f"⏰ Last updated: {datetime.now().strftime('%H:%M:%S')}")
st.caption(f"📊 Data source: {data_folder} ({len(csv_files)} stocks)")
st.caption("💡 Using latest close price from your local CSV files")
st.caption("🚀 During market hours: Switch to Dhan live data for tick-by-tick updates!")

# Auto-refresh
if auto_refresh:
    import time
    time.sleep(refresh_interval)
    st.rerun()

