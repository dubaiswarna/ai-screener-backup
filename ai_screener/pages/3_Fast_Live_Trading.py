"""
FAST Live Paper Trading - Optimized for Speed
==============================================
Ultra-fast updates with minimal overhead!
"""

import streamlit as st
import sys
from pathlib import Path
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)

import pandas as pd
import numpy as np
from datetime import datetime
import time

from data_loader import DataLoader
from signal_generator import SignalGenerator
from live_price_simulator import LivePriceSimulator
import yaml

st.set_page_config(page_title='Fast Live Trading', page_icon='⚡', layout='wide')

# Lightweight session state
if 'fast_portfolio' not in st.session_state:
    st.session_state.fast_portfolio = {
        'cash': 100000,
        'positions': [],
        'trades': 0,
        'wins': 0,
        'total_pnl': 0
    }

if 'fast_simulator' not in st.session_state:
    loader = DataLoader(data_dir=str(Path(parent_dir).parent / 'Nify50_data'))
    loader.load_all_stocks()
    st.session_state.fast_simulator = LivePriceSimulator(loader.stock_data)
    st.session_state.loader = loader

pf = st.session_state.fast_portfolio
sim = st.session_state.fast_simulator

# Update prices
sim.update_prices()
prices = sim.get_all_current_prices()

# Quick P&L calculation
for pos in pf['positions']:
    if pos['sym'] in prices:
        cp = prices[pos['sym']]
        pos['cp'] = cp
        pos['pnl'] = (cp - pos['ep']) * pos['qty'] if pos['dir'] == 'B' else (pos['ep'] - cp) * pos['qty']

# Auto-exits
for pos in pf['positions'][:]:
    if pos['sym'] not in prices:
        continue
    cp = prices[pos['sym']]
    
    if (pos['dir'] == 'B' and (cp >= pos['tgt'] or cp <= pos['stp'])) or \
       (pos['dir'] == 'S' and (cp <= pos['tgt'] or cp >= pos['stp'])):
        pf['cash'] += cp * pos['qty']
        pf['trades'] += 1
        pf['total_pnl'] += pos['pnl']
        if pos['pnl'] > 0:
            pf['wins'] += 1
        pf['positions'].remove(pos)
        st.toast(f"Exit: {pos['sym'].replace('NSE_', '')} P&L: Rs {pos['pnl']:+,.0f}")

# Display
st.title('⚡ Fast Live Trading')

# Compact metrics
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric('Cash', f"Rs {pf['cash']/1000:.0f}K")
c2.metric('Positions', len(pf['positions']))
c3.metric('Trades', pf['trades'])
c4.metric('Win%', f"{pf['wins']/pf['trades']*100:.0f}%" if pf['trades'] > 0 else "0%")
c5.metric('P&L', f"Rs {pf['total_pnl']/1000:+.1f}K")

st.divider()

# Top stocks quick select
stocks = ['NSE_BHARTIARTL', 'NSE_AXISBANK', 'NSE_KOTAKBANK', 'NSE_TCS', 'NSE_RELIANCE']

st.subheader('💹 Live Market')
for sym in stocks:
    if sym in prices:
        cp = prices[sym]
        chg = sim.get_price_change(sym)
        
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        col1.write(f"**{sym.replace('NSE_', '')}**")
        col2.metric('Price', f"Rs {cp:.2f}", f"{chg:+.2f}%")
        
        in_portfolio = any(p['sym'] == sym for p in pf['positions'])
        
        with col3:
            if not in_portfolio and st.button('BUY', key=f'b_{sym}', type='primary'):
                tgt = cp * 1.03
                stp = cp * 0.985
                val = cp * 10  # 10 shares only
                if val <= pf['cash']:
                    pf['positions'].append({
                        'sym': sym, 'dir': 'B', 'ep': cp, 'qty': 10,
                        'tgt': tgt, 'stp': stp, 'cp': cp, 'pnl': 0
                    })
                    pf['cash'] -= val
                    st.rerun()
        
        with col4:
            if not in_portfolio and st.button('SELL', key=f's_{sym}', type='secondary'):
                tgt = cp * 0.97
                stp = cp * 1.015
                val = cp * 10
                if val <= pf['cash']:
                    pf['positions'].append({
                        'sym': sym, 'dir': 'S', 'ep': cp, 'qty': 10,
                        'tgt': tgt, 'stp': stp, 'cp': cp, 'pnl': 0
                    })
                    pf['cash'] -= val
                    st.rerun()

if pf['positions']:
    st.divider()
    st.subheader('📊 Positions')
    for pos in pf['positions']:
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
        c1.write(f"{'🟢' if pos['dir']=='B' else '🔴'} {pos['sym'].replace('NSE_', '')}")
        c2.write(f"Entry: Rs {pos['ep']:.2f}")
        c3.write(f"Now: Rs {pos['cp']:.2f}")
        c4.metric('P&L', f"Rs {pos['pnl']:+,.0f}")
        if c5.button('×', key=f'x_{pos["sym"]}'):
            pf['cash'] += pos['cp'] * pos['qty']
            pf['trades'] += 1
            pf['total_pnl'] += pos['pnl']
            if pos['pnl'] > 0:
                pf['wins'] += 1
            pf['positions'].remove(pos)
            st.rerun()

# Fast auto-refresh (1 second)
time.sleep(1)
st.rerun()

