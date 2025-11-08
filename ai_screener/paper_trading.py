"""
Paper Trading System - Simulate Real Trading with AI Signals
============================================================
Track virtual trades, monitor P&L, and test strategies risk-free!
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

class PaperTradingPortfolio:
    """Manage paper trading portfolio."""
    
    def __init__(self, initial_capital=100000):
        """Initialize portfolio."""
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = []
        self.closed_trades = []
        self.trade_id = 1
    
    def open_position(self, symbol, signal, entry_price, target_price, stop_loss, confidence, quantity=None):
        """Open a new paper trade position."""
        if quantity is None:
            # Auto calculate quantity based on available capital and risk
            risk_amount = self.capital * 0.015  # Risk 1.5% of capital
            risk_per_share = abs(entry_price - stop_loss)
            quantity = int(risk_amount / risk_per_share) if risk_per_share > 0 else 100
        
        position_value = entry_price * quantity
        
        if position_value > self.capital:
            return False, "Insufficient capital"
        
        position = {
            'trade_id': self.trade_id,
            'symbol': symbol,
            'signal': signal,
            'entry_price': entry_price,
            'quantity': quantity,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'confidence': confidence,
            'entry_date': datetime.now(),
            'status': 'OPEN',
            'current_price': entry_price,
            'current_pnl': 0,
            'current_pnl_pct': 0
        }
        
        self.positions.append(position)
        self.capital -= position_value
        self.trade_id += 1
        
        return True, f"Position opened: {symbol} x{quantity} @ Rs {entry_price:.2f}"
    
    def update_positions(self, current_prices):
        """Update all open positions with current prices."""
        for pos in self.positions:
            if pos['status'] == 'OPEN' and pos['symbol'] in current_prices:
                current_price = current_prices[pos['symbol']]
                pos['current_price'] = current_price
                
                if pos['signal'] == 'buy':
                    pos['current_pnl'] = (current_price - pos['entry_price']) * pos['quantity']
                    pos['current_pnl_pct'] = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
                else:  # sell
                    pos['current_pnl'] = (pos['entry_price'] - current_price) * pos['quantity']
                    pos['current_pnl_pct'] = ((pos['entry_price'] - current_price) / pos['entry_price']) * 100
    
    def check_exits(self, current_prices):
        """Check if any positions should be exited."""
        exits = []
        
        for pos in self.positions:
            if pos['status'] != 'OPEN' or pos['symbol'] not in current_prices:
                continue
            
            current_price = current_prices[pos['symbol']]
            
            # Check BUY position exits
            if pos['signal'] == 'buy':
                if current_price >= pos['target_price']:
                    exit_reason = 'TARGET_HIT'
                    pnl = (current_price - pos['entry_price']) * pos['quantity']
                    pnl_pct = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
                    exits.append((pos, current_price, exit_reason, pnl, pnl_pct))
                elif current_price <= pos['stop_loss']:
                    exit_reason = 'STOP_LOSS'
                    pnl = (current_price - pos['entry_price']) * pos['quantity']
                    pnl_pct = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
                    exits.append((pos, current_price, exit_reason, pnl, pnl_pct))
            
            # Check SELL position exits
            elif pos['signal'] == 'sell':
                if current_price <= pos['target_price']:
                    exit_reason = 'TARGET_HIT'
                    pnl = (pos['entry_price'] - current_price) * pos['quantity']
                    pnl_pct = ((pos['entry_price'] - current_price) / pos['entry_price']) * 100
                    exits.append((pos, current_price, exit_reason, pnl, pnl_pct))
                elif current_price >= pos['stop_loss']:
                    exit_reason = 'STOP_LOSS'
                    pnl = (pos['entry_price'] - current_price) * pos['quantity']
                    pnl_pct = ((pos['entry_price'] - current_price) / pos['entry_price']) * 100
                    exits.append((pos, current_price, exit_reason, pnl, pnl_pct))
        
        # Process exits
        for pos, exit_price, exit_reason, pnl, pnl_pct in exits:
            self.close_position(pos, exit_price, exit_reason, pnl, pnl_pct)
        
        return exits
    
    def close_position(self, position, exit_price, exit_reason, pnl, pnl_pct):
        """Close a position."""
        position['status'] = 'CLOSED'
        position['exit_price'] = exit_price
        position['exit_date'] = datetime.now()
        position['exit_reason'] = exit_reason
        position['pnl'] = pnl
        position['pnl_pct'] = pnl_pct
        position['result'] = 'WIN' if pnl > 0 else 'LOSS'
        
        # Return capital + pnl
        self.capital += (exit_price * position['quantity'])
        
        # Move to closed trades
        self.closed_trades.append(position.copy())
        self.positions.remove(position)
    
    def get_portfolio_value(self, current_prices):
        """Calculate total portfolio value."""
        self.update_positions(current_prices)
        
        open_positions_value = sum(
            pos['current_price'] * pos['quantity'] 
            for pos in self.positions 
            if pos['status'] == 'OPEN'
        )
        
        return self.capital + open_positions_value
    
    def get_total_pnl(self):
        """Get total P&L from closed and open positions."""
        closed_pnl = sum(trade['pnl'] for trade in self.closed_trades)
        open_pnl = sum(pos['current_pnl'] for pos in self.positions if pos['status'] == 'OPEN')
        return closed_pnl + open_pnl
    
    def save_to_file(self, filepath='paper_trading_portfolio.json'):
        """Save portfolio to file."""
        data = {
            'initial_capital': self.initial_capital,
            'capital': self.capital,
            'positions': self.positions,
            'closed_trades': self.closed_trades,
            'trade_id': self.trade_id
        }
        
        # Convert datetime to string
        for pos in data['positions']:
            if 'entry_date' in pos and isinstance(pos['entry_date'], datetime):
                pos['entry_date'] = pos['entry_date'].isoformat()
        
        for trade in data['closed_trades']:
            if 'entry_date' in trade and isinstance(trade['entry_date'], datetime):
                trade['entry_date'] = trade['entry_date'].isoformat()
            if 'exit_date' in trade and isinstance(trade['exit_date'], datetime):
                trade['exit_date'] = trade['exit_date'].isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filepath='paper_trading_portfolio.json'):
        """Load portfolio from file."""
        if not os.path.exists(filepath):
            return False
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.initial_capital = data.get('initial_capital', 100000)
        self.capital = data.get('capital', 100000)
        self.positions = data.get('positions', [])
        self.closed_trades = data.get('closed_trades', [])
        self.trade_id = data.get('trade_id', 1)
        
        # Convert string back to datetime
        for pos in self.positions:
            if 'entry_date' in pos and isinstance(pos['entry_date'], str):
                pos['entry_date'] = datetime.fromisoformat(pos['entry_date'])
        
        for trade in self.closed_trades:
            if 'entry_date' in trade and isinstance(trade['entry_date'], str):
                trade['entry_date'] = datetime.fromisoformat(trade['entry_date'])
            if 'exit_date' in trade and isinstance(trade['exit_date'], str):
                trade['exit_date'] = datetime.fromisoformat(trade['exit_date'])
        
        return True


def get_current_prices(symbols, loader):
    """Get latest prices for symbols."""
    prices = {}
    for symbol in symbols:
        if symbol in loader.stock_data:
            prices[symbol] = loader.stock_data[symbol].iloc[-1]['close']
    return prices


# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = PaperTradingPortfolio(initial_capital=100000)
    # Try to load existing portfolio
    st.session_state.portfolio.load_from_file('paper_trading_portfolio.json')

if 'auto_trade_enabled' not in st.session_state:
    st.session_state.auto_trade_enabled = False

portfolio = st.session_state.portfolio

