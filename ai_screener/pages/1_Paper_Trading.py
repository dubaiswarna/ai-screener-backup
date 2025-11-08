"""
Paper Trading Dashboard
=======================
Simulate real trading with AI signals - Risk-free practice!
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
from datetime import datetime
import plotly.graph_objects as go

from data_loader import DataLoader
from feature_engineering import FeatureEngineer
from signal_generator import SignalGenerator
import yaml

# Page config
st.set_page_config(
    page_title='Paper Trading',
    page_icon='📝',
    layout='wide'
)

# Initialize session state for portfolio
if 'paper_portfolio' not in st.session_state:
    st.session_state.paper_portfolio = {
        'initial_capital': 100000,
        'cash': 100000,
        'positions': [],
        'closed_trades': [],
        'trade_id': 1
    }

portfolio = st.session_state.paper_portfolio

# Title
st.title('📝 Paper Trading Dashboard')
st.markdown('**Practice Trading with AI Signals - Zero Risk!**')

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

with st.spinner('Loading data...'):
    loader = load_data()
    featured_data = engineer_features(loader)

# Get current prices (last close)
def get_current_prices():
    prices = {}
    for symbol in loader.stock_data.keys():
        prices[symbol] = loader.stock_data[symbol].iloc[-1]['close']
    return prices

current_prices = get_current_prices()

# Sidebar - Portfolio Summary
st.sidebar.header('💰 Portfolio Summary')
total_value = portfolio['cash']
for pos in portfolio['positions']:
    if pos['symbol'] in current_prices:
        current_price = current_prices[pos['symbol']]
        total_value += current_price * pos['quantity']

total_pnl = total_value - portfolio['initial_capital']
total_pnl_pct = (total_pnl / portfolio['initial_capital']) * 100

st.sidebar.metric('Total Value', f"Rs {total_value:,.0f}", f"{total_pnl_pct:+.2f}%")
st.sidebar.metric('Cash Available', f"Rs {portfolio['cash']:,.0f}")
st.sidebar.metric('Open Positions', len(portfolio['positions']))
st.sidebar.metric('Closed Trades', len(portfolio['closed_trades']))

# Reset button
if st.sidebar.button('🔄 Reset Portfolio', type='secondary'):
    st.session_state.paper_portfolio = {
        'initial_capital': 100000,
        'cash': 100000,
        'positions': [],
        'closed_trades': [],
        'trade_id': 1
    }
    st.rerun()

# Main area - Tabs
tab1, tab2, tab3, tab4 = st.tabs(['📊 Live Signals', '📈 Open Positions', '📜 Trade History', '📊 Performance'])

# TAB 1: Live Signals
with tab1:
    st.header('Live AI Signals')
    st.info('💡 Click "Take Trade" to add signal to your paper trading portfolio')
    
    # Generate signals
    signal_gen = SignalGenerator(config)
    
    # Get top stocks with models
    stocks_with_models = [
        'NSE_BHARTIARTL', 'NSE_AXISBANK', 'NSE_KOTAKBANK',
        'NSE_SBIN', 'NSE_TCS', 'NSE_RELIANCE',
        'NSE_INFY', 'NSE_HDFCBANK', 'NSE_ICICIBANK'
    ]
    
    # Filter to stocks we have
    available_stocks = [s for s in stocks_with_models if s in featured_data]
    X_data = {symbol: featured_data[symbol] for symbol in available_stocks}
    
    # Generate signals
    with st.spinner('Generating signals...'):
        df_signals = signal_gen.generate_signals_for_stocks(available_stocks, X_data)
        
        if not df_signals.empty:
            # Filter high confidence only
            df_signals = df_signals[df_signals['confidence'] >= 0.70]
            df_signals = df_signals[df_signals['signal'].isin(['buy', 'sell'])]
            df_signals = df_signals.sort_values('confidence', ascending=False)
            
            if not df_signals.empty:
                st.success(f'Found {len(df_signals)} high-quality signals!')
                
                # Display signals with action buttons
                for idx, row in df_signals.iterrows():
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                    
                    with col1:
                        signal_emoji = '🟢 BUY' if row['signal'] == 'buy' else '🔴 SELL'
                        st.markdown(f"**{signal_emoji} {row['symbol'].replace('NSE_', '')}**")
                        st.caption(f"Confidence: {row['confidence']*100:.1f}%")
                    
                    with col2:
                        st.metric('Entry', f"Rs {row['current_price']:.2f}")
                    
                    with col3:
                        st.metric('Target', f"Rs {row.get('target_price', 0):.2f}")
                    
                    with col4:
                        st.metric('Stop', f"Rs {row.get('stop_loss_price', 0):.2f}")
                    
                    with col5:
                        # Check if already in portfolio
                        already_in = any(p['symbol'] == row['symbol'] and p['status'] == 'OPEN' 
                                       for p in portfolio['positions'])
                        
                        if not already_in:
                            if st.button(f'Take Trade', key=f"trade_{row['symbol']}"):
                                # Open position
                                pos_val = {
                                    'trade_id': portfolio['trade_id'],
                                    'symbol': row['symbol'],
                                    'signal': row['signal'],
                                    'entry_price': row['current_price'],
                                    'quantity': 100,  # Default
                                    'target_price': row.get('target_price', row['current_price'] * 1.03),
                                    'stop_loss': row.get('stop_loss_price', row['current_price'] * 0.985),
                                    'confidence': row['confidence'],
                                    'entry_date': datetime.now(),
                                    'status': 'OPEN',
                                    'current_price': row['current_price'],
                                    'current_pnl': 0,
                                    'current_pnl_pct': 0
                                }
                                
                                position_value = row['current_price'] * 100
                                if position_value <= portfolio['cash']:
                                    portfolio['positions'].append(pos_val)
                                    portfolio['cash'] -= position_value
                                    portfolio['trade_id'] += 1
                                    st.success(f'Trade taken! {row["symbol"]} x100 @ Rs {row["current_price"]:.2f}')
                                    st.rerun()
                                else:
                                    st.error('Insufficient cash!')
                        else:
                            st.info('In Portfolio')
                    
                    st.divider()
            else:
                st.warning('No signals meet the 70% confidence threshold')
        else:
            st.warning('No BUY/SELL signals found. Try lowering confidence or selecting more stocks.')

# TAB 2: Open Positions
with tab2:
    st.header('Open Positions')
    
    if portfolio['positions']:
        # Update positions with current prices
        for pos in portfolio['positions']:
            if pos['symbol'] in current_prices:
                current_price = current_prices[pos['symbol']]
                pos['current_price'] = current_price
                
                if pos['signal'] == 'buy':
                    pos['current_pnl'] = (current_price - pos['entry_price']) * pos['quantity']
                    pos['current_pnl_pct'] = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
                else:
                    pos['current_pnl'] = (pos['entry_price'] - current_price) * pos['quantity']
                    pos['current_pnl_pct'] = ((pos['entry_price'] - current_price) / pos['entry_price']) * 100
                
                # Check if should exit
                should_exit = False
                exit_reason = ''
                
                if pos['signal'] == 'buy':
                    if current_price >= pos['target_price']:
                        should_exit = True
                        exit_reason = 'TARGET_HIT'
                    elif current_price <= pos['stop_loss']:
                        should_exit = True
                        exit_reason = 'STOP_LOSS'
                elif pos['signal'] == 'sell':
                    if current_price <= pos['target_price']:
                        should_exit = True
                        exit_reason = 'TARGET_HIT'
                    elif current_price >= pos['stop_loss']:
                        should_exit = True
                        exit_reason = 'STOP_LOSS'
                
                pos['should_exit'] = should_exit
                pos['exit_reason_live'] = exit_reason
        
        # Display positions
        for pos in portfolio['positions']:
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                signal_emoji = '🟢' if pos['signal'] == 'buy' else '🔴'
                st.markdown(f"**{signal_emoji} {pos['symbol'].replace('NSE_', '')}** x{pos['quantity']}")
                days_held = (datetime.now() - pos['entry_date']).days
                st.caption(f"Opened {days_held} days ago | Conf: {pos['confidence']*100:.0f}%")
            
            with col2:
                st.metric('Entry', f"Rs {pos['entry_price']:.2f}")
                st.caption(f"Current: Rs {pos['current_price']:.2f}")
            
            with col3:
                pnl_color = 'normal' if pos['current_pnl'] >= 0 else 'inverse'
                st.metric('P&L', f"Rs {pos['current_pnl']:+,.0f}", 
                         f"{pos['current_pnl_pct']:+.2f}%", delta_color=pnl_color)
            
            with col4:
                target_dist = abs((pos['current_price'] - pos['target_price']) / pos['target_price'] * 100)
                st.metric('Target', f"Rs {pos['target_price']:.2f}")
                st.caption(f"{target_dist:.1f}% away")
            
            with col5:
                if pos.get('should_exit', False):
                    st.error(f'⚠️ {pos["exit_reason_live"]}!')
                    if st.button('Close Now', key=f'close_{pos["trade_id"]}'):
                        # Close position
                        closed_trade = pos.copy()
                        closed_trade['status'] = 'CLOSED'
                        closed_trade['exit_price'] = pos['current_price']
                        closed_trade['exit_date'] = datetime.now()
                        closed_trade['exit_reason'] = pos['exit_reason_live']
                        closed_trade['pnl'] = pos['current_pnl']
                        closed_trade['pnl_pct'] = pos['current_pnl_pct']
                        closed_trade['result'] = 'WIN' if pos['current_pnl'] > 0 else 'LOSS'
                        
                        portfolio['cash'] += pos['current_price'] * pos['quantity']
                        portfolio['closed_trades'].append(closed_trade)
                        portfolio['positions'].remove(pos)
                        
                        st.success(f'Position closed! P&L: Rs {pos["current_pnl"]:+,.0f}')
                        st.rerun()
                else:
                    if st.button('Manual Close', key=f'manual_{pos["trade_id"]}', type='secondary'):
                        # Manual close
                        closed_trade = pos.copy()
                        closed_trade['status'] = 'CLOSED'
                        closed_trade['exit_price'] = pos['current_price']
                        closed_trade['exit_date'] = datetime.now()
                        closed_trade['exit_reason'] = 'MANUAL'
                        closed_trade['pnl'] = pos['current_pnl']
                        closed_trade['pnl_pct'] = pos['current_pnl_pct']
                        closed_trade['result'] = 'WIN' if pos['current_pnl'] > 0 else 'LOSS'
                        
                        portfolio['cash'] += pos['current_price'] * pos['quantity']
                        portfolio['closed_trades'].append(closed_trade)
                        portfolio['positions'].remove(pos)
                        
                        st.rerun()
            
            st.divider()
    else:
        st.info('No open positions. Go to "Live Signals" tab to take trades!')

# TAB 3: Trade History
with tab3:
    st.header('Trade History')
    
    if portfolio['closed_trades']:
        trades_df = pd.DataFrame(portfolio['closed_trades'])
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        wins = trades_df[trades_df['result'] == 'WIN']
        losses = trades_df[trades_df['result'] == 'LOSS']
        
        with col1:
            st.metric('Total Trades', len(trades_df))
        with col2:
            win_rate = len(wins) / len(trades_df) * 100 if len(trades_df) > 0 else 0
            st.metric('Win Rate', f"{win_rate:.1f}%")
        with col3:
            total_pnl = trades_df['pnl'].sum()
            st.metric('Total P&L', f"Rs {total_pnl:+,.0f}")
        with col4:
            avg_pnl_pct = trades_df['pnl_pct'].mean()
            st.metric('Avg Return', f"{avg_pnl_pct:+.2f}%")
        
        st.divider()
        
        # Show trades table
        display_df = trades_df[['trade_id', 'symbol', 'signal', 'entry_price', 'exit_price', 
                                'quantity', 'pnl', 'pnl_pct', 'result', 'exit_reason', 'confidence']].copy()
        
        display_df['symbol'] = display_df['symbol'].str.replace('NSE_', '')
        display_df['entry_price'] = display_df['entry_price'].round(2)
        display_df['exit_price'] = display_df['exit_price'].round(2)
        display_df['pnl'] = display_df['pnl'].round(2)
        display_df['pnl_pct'] = display_df['pnl_pct'].round(2)
        display_df['confidence'] = (display_df['confidence'] * 100).round(1)
        
        display_df.columns = ['Trade#', 'Stock', 'Type', 'Entry', 'Exit', 'Qty', 'P&L Rs', 'P&L %', 'Result', 'Exit Reason', 'Conf %']
        
        st.dataframe(display_df.sort_values('Trade#', ascending=False), use_container_width=True, height=400)
        
        # Download button
        csv = trades_df.to_csv(index=False)
        st.download_button(
            label='📥 Download Trade History CSV',
            data=csv,
            file_name=f'paper_trading_history_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv'
        )
    else:
        st.info('No closed trades yet. Take some trades from the "Live Signals" tab!')

# TAB 4: Performance
with tab4:
    st.header('Performance Analytics')
    
    if portfolio['closed_trades']:
        trades_df = pd.DataFrame(portfolio['closed_trades'])
        
        # Performance by stock
        st.subheader('Performance by Stock')
        
        stock_perf = trades_df.groupby('symbol').agg({
            'pnl': ['count', 'sum', 'mean'],
            'result': lambda x: (x == 'WIN').sum()
        }).round(2)
        
        stock_perf.columns = ['Trades', 'Total P&L', 'Avg P&L', 'Wins']
        stock_perf['Win Rate %'] = (stock_perf['Wins'] / stock_perf['Trades'] * 100).round(1)
        stock_perf.index = stock_perf.index.str.replace('NSE_', '')
        stock_perf = stock_perf.sort_values('Win Rate %', ascending=False)
        
        st.dataframe(stock_perf, use_container_width=True)
        
        # Performance by signal type
        st.subheader('Performance by Signal Type')
        
        col1, col2 = st.columns(2)
        
        with col1:
            buy_trades = trades_df[trades_df['signal'] == 'buy']
            if len(buy_trades) > 0:
                buy_wins = len(buy_trades[buy_trades['result'] == 'WIN'])
                buy_wr = buy_wins / len(buy_trades) * 100
                st.metric('BUY Trades', len(buy_trades))
                st.metric('BUY Win Rate', f"{buy_wr:.1f}%")
                st.metric('BUY Total P&L', f"Rs {buy_trades['pnl'].sum():+,.0f}")
        
        with col2:
            sell_trades = trades_df[trades_df['signal'] == 'sell']
            if len(sell_trades) > 0:
                sell_wins = len(sell_trades[sell_trades['result'] == 'WIN'])
                sell_wr = sell_wins / len(sell_trades) * 100
                st.metric('SELL Trades', len(sell_trades))
                st.metric('SELL Win Rate', f"{sell_wr:.1f}%")
                st.metric('SELL Total P&L', f"Rs {sell_trades['pnl'].sum():+,.0f}")
        
        # Equity curve
        st.subheader('Equity Curve')
        
        trades_df_sorted = trades_df.sort_values('entry_date')
        trades_df_sorted['cumulative_pnl'] = trades_df_sorted['pnl'].cumsum()
        trades_df_sorted['portfolio_value'] = portfolio['initial_capital'] + trades_df_sorted['cumulative_pnl']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(trades_df_sorted))),
            y=trades_df_sorted['portfolio_value'],
            mode='lines',
            name='Portfolio Value',
            line=dict(color='green', width=2)
        ))
        
        fig.add_hline(y=portfolio['initial_capital'], line_dash='dash', line_color='gray',
                     annotation_text='Initial Capital')
        
        fig.update_layout(
            title='Portfolio Value Over Time',
            xaxis_title='Trade Number',
            yaxis_title='Portfolio Value (Rs)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info('No trades yet! Take some trades to see performance analytics.')

# Auto-refresh option
st.sidebar.divider()
auto_refresh = st.sidebar.checkbox('🔄 Auto-refresh (10sec)', value=False)
if auto_refresh:
    import time
    time.sleep(10)
    st.rerun()

