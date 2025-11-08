"""
Live Paper Trading with Realistic Price Simulation
===================================================
Practice trading with simulated live prices that fluctuate realistically!
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import time

from data_loader import DataLoader
from feature_engineering import FeatureEngineer
from signal_generator import SignalGenerator
from live_price_simulator import LivePriceSimulator
import yaml

# Page config
st.set_page_config(
    page_title='Live Paper Trading',
    page_icon='🔴',
    layout='wide'
)

# Initialize session state
if 'paper_portfolio' not in st.session_state:
    st.session_state.paper_portfolio = {
        'initial_capital': 100000,
        'cash': 100000,
        'positions': [],
        'closed_trades': [],
        'trade_id': 1
    }

if 'price_simulator' not in st.session_state:
    st.session_state.price_simulator = None
    st.session_state.last_price_update = datetime.now()

if 'live_mode' not in st.session_state:
    st.session_state.live_mode = True

portfolio = st.session_state.paper_portfolio

# Title
st.title('🔴 Live Paper Trading Dashboard')
st.markdown('**Real-Time Simulated Trading with Live Price Updates!**')

# Load config
@st.cache_resource
def load_config():
    config_path = Path(parent_dir) / 'config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

# Load data
@st.cache_resource
def load_data():
    loader = DataLoader(data_dir=str(Path(parent_dir).parent / 'Nify50_data'))
    loader.load_all_stocks()
    return loader

@st.cache_resource
def engineer_features(_loader):
    engineer = FeatureEngineer()
    featured_data = {}
    for symbol, df in _loader.stock_data.items():
        df_features = engineer.engineer_features(df)
        featured_data[symbol] = df_features
    return featured_data

# Load data
with st.spinner('Loading market data...'):
    loader = load_data()
    featured_data = engineer_features(loader)

# Initialize price simulator
if st.session_state.price_simulator is None:
    with st.spinner('Initializing live price simulator...'):
        st.session_state.price_simulator = LivePriceSimulator(loader.stock_data)

simulator = st.session_state.price_simulator

# Update prices if live mode enabled (optimized - only update once per page load)
if st.session_state.live_mode:
    simulator.update_prices()
    st.session_state.last_price_update = datetime.now()

# Get current prices
current_prices = simulator.get_all_current_prices()

# Calculate portfolio value
total_value = portfolio['cash']
open_pnl = 0

for pos in portfolio['positions']:
    if pos['symbol'] in current_prices:
        current_price = current_prices[pos['symbol']]
        pos['current_price'] = current_price
        
        # Calculate P&L
        if pos['signal'] == 'buy':
            pnl = (current_price - pos['entry_price']) * pos['quantity']
            pnl_pct = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
        else:  # sell
            pnl = (pos['entry_price'] - current_price) * pos['quantity']
            pnl_pct = ((pos['entry_price'] - current_price) / pos['entry_price']) * 100
        
        pos['current_pnl'] = pnl
        pos['current_pnl_pct'] = pnl_pct
        
        total_value += current_price * pos['quantity']
        open_pnl += pnl

# Check auto-exits
auto_exits = []
for pos in portfolio['positions'][:]:  # Copy list to avoid modification during iteration
    if pos['symbol'] not in current_prices:
        continue
    
    current_price = current_prices[pos['symbol']]
    
    should_exit = False
    exit_reason = ''
    
    if pos['signal'] == 'buy':
        if current_price >= pos['target_price']:
            should_exit = True
            exit_reason = 'TARGET_HIT'
        elif current_price <= pos['stop_loss']:
            should_exit = True
            exit_reason = 'STOP_LOSS'
    else:  # sell
        if current_price <= pos['target_price']:
            should_exit = True
            exit_reason = 'TARGET_HIT'
        elif current_price >= pos['stop_loss']:
            should_exit = True
            exit_reason = 'STOP_LOSS'
    
    if should_exit:
        auto_exits.append((pos, exit_reason))

# Process auto-exits
for pos, exit_reason in auto_exits:
    closed_trade = pos.copy()
    closed_trade['status'] = 'CLOSED'
    closed_trade['exit_price'] = pos['current_price']
    closed_trade['exit_date'] = datetime.now()
    closed_trade['exit_reason'] = exit_reason
    closed_trade['pnl'] = pos['current_pnl']
    closed_trade['pnl_pct'] = pos['current_pnl_pct']
    closed_trade['result'] = 'WIN' if pos['current_pnl'] > 0 else 'LOSS'
    
    portfolio['cash'] += pos['current_price'] * pos['quantity']
    portfolio['closed_trades'].append(closed_trade)
    portfolio['positions'].remove(pos)
    
    st.toast(f"🎯 {exit_reason}! {pos['symbol'].replace('NSE_', '')} exited at Rs {pos['current_price']:.2f}", icon='✅')

# Sidebar - Live Portfolio Summary
st.sidebar.header('💰 Live Portfolio')

total_pnl = total_value - portfolio['initial_capital']
total_pnl_pct = (total_pnl / portfolio['initial_capital']) * 100

col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric('Total Value', f"Rs {total_value:,.0f}")
with col2:
    st.metric('Total P&L', f"Rs {total_pnl:+,.0f}", f"{total_pnl_pct:+.2f}%")

st.sidebar.metric('💵 Cash', f"Rs {portfolio['cash']:,.0f}")
st.sidebar.metric('📊 Open Positions', len(portfolio['positions']))
st.sidebar.metric('📈 Open P&L', f"Rs {open_pnl:+,.0f}")
st.sidebar.metric('✅ Closed Trades', len(portfolio['closed_trades']))

st.sidebar.divider()

# Live mode toggle
st.sidebar.subheader('🔴 Live Mode')
live_enabled = st.sidebar.toggle('Enable Live Prices', value=True, key='live_toggle')
st.session_state.live_mode = live_enabled

if live_enabled:
    st.sidebar.success('🟢 LIVE - Prices updating')
    refresh_rate = st.sidebar.select_slider('Refresh Rate', 
                                            options=[1, 2, 3, 5], 
                                            value=2,
                                            format_func=lambda x: f'{x} sec')
else:
    st.sidebar.warning('⚪ PAUSED - Prices frozen')
    refresh_rate = None

st.sidebar.divider()

# Reset button
if st.sidebar.button('🔄 Reset Portfolio', type='secondary'):
    st.session_state.paper_portfolio = {
        'initial_capital': 100000,
        'cash': 100000,
        'positions': [],
        'closed_trades': [],
        'trade_id': 1
    }
    st.session_state.price_simulator = LivePriceSimulator(loader.stock_data)
    st.success('Portfolio reset!')
    st.rerun()

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    '📊 Live Signals', 
    '📈 Open Positions', 
    '💹 Live Market', 
    '📜 Trade History', 
    '📊 Performance'
])

# TAB 1: Live Signals
with tab1:
    st.header('Live AI Signals')
    st.info('💡 Signals generated from latest data. Prices update in real-time!')
    
    # Generate signals
    signal_gen = SignalGenerator(config)
    
    stocks_with_models = [
        'NSE_BHARTIARTL', 'NSE_AXISBANK', 'NSE_KOTAKBANK',
        'NSE_SBIN', 'NSE_TCS', 'NSE_RELIANCE',
        'NSE_INFY', 'NSE_HDFCBANK', 'NSE_ICICIBANK'
    ]
    
    available_stocks = [s for s in stocks_with_models if s in featured_data]
    X_data = {symbol: featured_data[symbol] for symbol in available_stocks}
    
    with st.spinner('Generating AI signals...'):
        df_signals = signal_gen.generate_signals_for_stocks(available_stocks, X_data)
        
        if not df_signals.empty:
            df_signals = df_signals[df_signals['confidence'] >= 0.70]
            df_signals = df_signals[df_signals['signal'].isin(['buy', 'sell'])]
            df_signals = df_signals.sort_values('confidence', ascending=False)
            
            if not df_signals.empty:
                st.success(f'🎯 Found {len(df_signals)} high-quality signals! (Live prices shown)')
                
                for idx, row in df_signals.iterrows():
                    # Get live price
                    live_price = simulator.get_current_price(row['symbol'])
                    price_change = simulator.get_price_change(row['symbol'])
                    
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
                    
                    with col1:
                        signal_emoji = '🟢 BUY' if row['signal'] == 'buy' else '🔴 SELL'
                        st.markdown(f"**{signal_emoji} {row['symbol'].replace('NSE_', '')}**")
                        st.caption(f"AI Confidence: {row['confidence']*100:.1f}%")
                    
                    with col2:
                        change_color = 'normal' if price_change >= 0 else 'inverse'
                        st.metric('Live Price', f"Rs {live_price:.2f}", f"{price_change:+.2f}%", 
                                 delta_color=change_color)
                    
                    with col3:
                        target = live_price * 1.03 if row['signal'] == 'buy' else live_price * 0.97
                        st.metric('Target', f"Rs {target:.2f}")
                        st.caption('+3.0%')
                    
                    with col4:
                        stop = live_price * 0.985 if row['signal'] == 'buy' else live_price * 1.015
                        st.metric('Stop', f"Rs {stop:.2f}")
                        st.caption('-1.5%')
                    
                    with col5:
                        risk_reward = 3.0 / 1.5
                        st.metric('R:R', f'{risk_reward:.1f}:1')
                    
                    with col6:
                        already_in = any(p['symbol'] == row['symbol'] and p['status'] == 'OPEN' 
                                       for p in portfolio['positions'])
                        
                        if not already_in:
                            if st.button(f'Take Trade', key=f"trade_{row['symbol']}", type='primary'):
                                pos_val = {
                                    'trade_id': portfolio['trade_id'],
                                    'symbol': row['symbol'],
                                    'signal': row['signal'],
                                    'entry_price': live_price,
                                    'quantity': 100,
                                    'target_price': target,
                                    'stop_loss': stop,
                                    'confidence': row['confidence'],
                                    'entry_date': datetime.now(),
                                    'status': 'OPEN',
                                    'current_price': live_price,
                                    'current_pnl': 0,
                                    'current_pnl_pct': 0
                                }
                                
                                position_value = live_price * 100
                                if position_value <= portfolio['cash']:
                                    portfolio['positions'].append(pos_val)
                                    portfolio['cash'] -= position_value
                                    portfolio['trade_id'] += 1
                                    st.success(f'✅ Trade Taken! {row["symbol"].replace("NSE_", "")} x100 @ Rs {live_price:.2f}')
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.error('❌ Insufficient cash!')
                        else:
                            st.info('In Portfolio')
                    
                    st.divider()
            else:
                st.warning('No BUY/SELL signals above 70% confidence')
        else:
            st.warning('No signals found. Markets may be consolidating.')

# TAB 2: Open Positions with LIVE P&L
with tab2:
    st.header('📈 Open Positions (Live P&L)')
    
    if portfolio['positions']:
        st.info(f'🔴 LIVE MODE: P&L updates every {refresh_rate if live_enabled else "refresh"}')
        
        for pos in portfolio['positions']:
            current_price = current_prices.get(pos['symbol'], pos['entry_price'])
            price_change_from_entry = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
            
            # Create expandable card for each position
            with st.expander(f"{'🟢' if pos['signal'] == 'buy' else '🔴'} {pos['symbol'].replace('NSE_', '')} | P&L: Rs {pos['current_pnl']:+,.0f} ({pos['current_pnl_pct']:+.2f}%)", expanded=True):
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric('Entry Price', f"Rs {pos['entry_price']:.2f}")
                    days_held = (datetime.now() - pos['entry_date']).total_seconds() / 3600
                    st.caption(f"Held: {days_held:.1f} hours")
                
                with col2:
                    change_color = 'normal' if price_change_from_entry >= 0 else 'inverse'
                    st.metric('Live Price', f"Rs {current_price:.2f}", 
                             f"{price_change_from_entry:+.2f}%", delta_color=change_color)
                    trend = simulator.get_price_trend(pos['symbol'])
                    st.caption(f"Trend: {trend}")
                
                with col3:
                    target_dist = ((pos['target_price'] - current_price) / current_price) * 100
                    st.metric('Target', f"Rs {pos['target_price']:.2f}")
                    st.caption(f"{target_dist:+.2f}% away")
                
                with col4:
                    stop_dist = ((current_price - pos['stop_loss']) / pos['stop_loss']) * 100
                    st.metric('Stop Loss', f"Rs {pos['stop_loss']:.2f}")
                    st.caption(f"{stop_dist:+.2f}% away")
                
                with col5:
                    pnl_color = 'normal' if pos['current_pnl'] >= 0 else 'inverse'
                    st.metric('Live P&L', f"Rs {pos['current_pnl']:+,.0f}", 
                             f"{pos['current_pnl_pct']:+.2f}%", delta_color=pnl_color)
                
                # Action buttons
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if st.button('Close at Market', key=f'close_market_{pos["trade_id"]}', type='primary'):
                        closed_trade = pos.copy()
                        closed_trade['status'] = 'CLOSED'
                        closed_trade['exit_price'] = current_price
                        closed_trade['exit_date'] = datetime.now()
                        closed_trade['exit_reason'] = 'MANUAL_MARKET'
                        closed_trade['pnl'] = pos['current_pnl']
                        closed_trade['pnl_pct'] = pos['current_pnl_pct']
                        closed_trade['result'] = 'WIN' if pos['current_pnl'] > 0 else 'LOSS'
                        
                        portfolio['cash'] += current_price * pos['quantity']
                        portfolio['closed_trades'].append(closed_trade)
                        portfolio['positions'].remove(pos)
                        
                        st.success(f'✅ Position Closed! P&L: Rs {pos["current_pnl"]:+,.0f}')
                        time.sleep(0.5)
                        st.rerun()
                
                with col_b:
                    if st.button('Close at Target', key=f'close_target_{pos["trade_id"]}', disabled=(current_price < pos['target_price'] if pos['signal'] == 'buy' else current_price > pos['target_price'])):
                        st.info('Target not reached yet')
                
                with col_c:
                    if st.button('Close at Stop', key=f'close_stop_{pos["trade_id"]}', disabled=(current_price > pos['stop_loss'] if pos['signal'] == 'buy' else current_price < pos['stop_loss'])):
                        st.info('Stop not hit yet')
    else:
        st.info('📭 No open positions. Go to "Live Signals" to take trades!')

# TAB 3: Live Market Watch
with tab3:
    st.header('💹 Live Market Watch')
    st.caption(f'Last update: {st.session_state.last_price_update.strftime("%H:%M:%S")}')
    
    # Show live prices for all 9 stocks
    market_data = []
    for symbol in stocks_with_models[:9]:
        if symbol in current_prices:
            live_price = current_prices[symbol]
            price_change = simulator.get_price_change(symbol)
            ohlc = simulator.get_ohlc(symbol)
            trend = simulator.get_price_trend(symbol)
            
            market_data.append({
                'Stock': symbol.replace('NSE_', ''),
                'Live Price': f"Rs {live_price:.2f}",
                'Change %': f"{price_change:+.2f}%",
                'Open': f"Rs {ohlc['open']:.2f}",
                'High': f"Rs {ohlc['high']:.2f}",
                'Low': f"Rs {ohlc['low']:.2f}",
                'Trend': trend
            })
    
    if market_data:
        df_market = pd.DataFrame(market_data)
        
        # Style the dataframe
        def highlight_change(row):
            if '+' in str(row['Change %']):
                return ['background-color: #d4edda'] * len(row)
            elif '-' in str(row['Change %']):
                return ['background-color: #f8d7da'] * len(row)
            return [''] * len(row)
        
        st.dataframe(df_market, use_container_width=True, height=400)

# TAB 4: Trade History
with tab4:
    st.header('📜 Trade History')
    
    if portfolio['closed_trades']:
        trades_df = pd.DataFrame(portfolio['closed_trades'])
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        wins = trades_df[trades_df['result'] == 'WIN']
        losses = trades_df[trades_df['result'] == 'LOSS']
        
        with col1:
            st.metric('Total Trades', len(trades_df))
        with col2:
            win_rate = len(wins) / len(trades_df) * 100
            st.metric('Win Rate', f"{win_rate:.1f}%")
        with col3:
            total_pnl_closed = trades_df['pnl'].sum()
            st.metric('Closed P&L', f"Rs {total_pnl_closed:+,.0f}")
        with col4:
            avg_pnl = trades_df['pnl_pct'].mean()
            st.metric('Avg Return', f"{avg_pnl:+.2f}%")
        with col5:
            best_trade = trades_df['pnl'].max()
            st.metric('Best Trade', f"Rs {best_trade:+,.0f}")
        
        st.divider()
        
        # Detailed trade table
        display_df = trades_df[['trade_id', 'symbol', 'signal', 'entry_price', 'exit_price', 
                                'quantity', 'pnl', 'pnl_pct', 'result', 'exit_reason', 'confidence']].copy()
        
        display_df['symbol'] = display_df['symbol'].str.replace('NSE_', '')
        display_df.columns = ['#', 'Stock', 'Type', 'Entry', 'Exit', 'Qty', 'P&L Rs', 'P&L %', 'Result', 'Exit', 'Conf']
        
        st.dataframe(display_df.sort_values('#', ascending=False), use_container_width=True, height=400)
    else:
        st.info('No trades yet! Take some from "Live Signals"')

# TAB 5: Performance  
with tab5:
    st.header('📊 Performance Analytics')
    
    if portfolio['closed_trades']:
        trades_df = pd.DataFrame(portfolio['closed_trades'])
        
        # Equity curve
        st.subheader('Equity Curve')
        
        trades_sorted = trades_df.sort_values('entry_date')
        trades_sorted['cumulative_pnl'] = trades_sorted['pnl'].cumsum()
        trades_sorted['equity'] = portfolio['initial_capital'] + trades_sorted['cumulative_pnl']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(trades_sorted))),
            y=trades_sorted['equity'],
            mode='lines+markers',
            name='Portfolio Value',
            line=dict(color='green', width=2),
            fill='tonexty'
        ))
        
        fig.add_hline(y=portfolio['initial_capital'], line_dash='dash', 
                     line_color='gray', annotation_text='Initial Capital')
        
        fig.update_layout(
            xaxis_title='Trade Number',
            yaxis_title='Portfolio Value (Rs)',
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance by stock
        st.subheader('Performance by Stock')
        
        stock_perf = trades_df.groupby('symbol').agg({
            'pnl': ['count', 'sum', 'mean'],
            'result': lambda x: (x == 'WIN').sum()
        }).round(2)
        
        stock_perf.columns = ['Trades', 'Total P&L', 'Avg P&L', 'Wins']
        stock_perf['Win %'] = (stock_perf['Wins'] / stock_perf['Trades'] * 100).round(1)
        stock_perf.index = stock_perf.index.str.replace('NSE_', '')
        stock_perf = stock_perf.sort_values('Win %', ascending=False)
        
        st.dataframe(stock_perf, use_container_width=True)
    else:
        st.info('No closed trades yet!')

# Auto-refresh for live mode (optimized)
if st.session_state.live_mode and refresh_rate:
    st_autorefresh = st.empty()
    with st_autorefresh:
        st.caption(f'⏱️ Next update in {refresh_rate} seconds...')
    
    time.sleep(refresh_rate)
    st.rerun()

