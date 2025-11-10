"""
VWAP Flexible Trading System - Core Logic
==========================================
Reusable class for VWAP ladder strategy backtesting
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class VWAPFlexibleSystem:
    """
    Flexible VWAP Ladder Strategy
    Supports optional VWAP, SMA, and Heikin Ashi entries
    """
    
    def __init__(self, max_investment=None, fixed_qty=None, target_percentage=10, threshold_lakhs=5,
                 initial_capital=100000, vwap_enabled=True, sma_period=None, 
                 supertrend_enabled=False, supertrend_period=10, supertrend_multiplier=3, ha_enabled=False):
        """
        Initialize with user-defined parameters
        
        Parameters:
        - max_investment: Max investment per day (None if using fixed_qty)
        - fixed_qty: Fixed quantity per order (None if using max_investment)
        - target_percentage: Profit target in % (e.g., 3, 6, 10)
        - threshold_lakhs: Threshold in lakhs (e.g., 3, 4, 5)
        - initial_capital: Starting capital for backtest
        - vwap_enabled: Enable VWAP entries (E3, E4)
        - sma_period: SMA period (enables E5 and E6 entries if set)
        - supertrend_enabled: Enable Supertrend filter
        - ha_enabled: Enable Heikin Ashi (enables E7 and E8 entries if set)
        """
        # Validate parameters
        if max_investment is None and fixed_qty is None:
            max_investment = 15000
        
        if fixed_qty is not None:
            fixed_qty = int(fixed_qty)
        
        self.max_investment = max_investment
        self.fixed_qty = fixed_qty
        self.target_percentage = target_percentage
        self.target_price = target_percentage / 100
        self.threshold_lakhs = threshold_lakhs
        self.threshold_amount = threshold_lakhs * 100000
        
        self.initial_capital = initial_capital
        self.position_size = None
        self.profit_target = self.target_price
        
        # Entry configuration
        self.vwap_enabled = vwap_enabled
        self.vwap_entries_enabled = bool(vwap_enabled)
        
        self.sma_period = int(sma_period) if sma_period else None
        self.sma_entries_enabled = bool(self.sma_period)
        
        self.supertrend_enabled = supertrend_enabled
        self.supertrend_period = int(supertrend_period) if supertrend_period else 10
        self.supertrend_multiplier = float(supertrend_multiplier) if supertrend_multiplier else 3
        
        self.ha_enabled = ha_enabled
        self.ha_entries_enabled = bool(ha_enabled)
        
        # Trading parameters
        self.r_low_discount = 0.01
        self.r_vwap_discount = 0.01
        
        # Transaction costs
        self.charges = 0.007
        self.brokerage = 0.003
        self.total_charges = self.charges + self.brokerage
        
        # Above threshold protection
        self.reduced_profit_target = 0.01
        
        # Reset tracking
        self.reset_system()
    
    def reset_system(self):
        """Reset all tracking variables"""
        self.capital = self.initial_capital
        self.data = None
        self.daily_transactions = []
        self.position_summary = []
        self.yearly_summary = []
        
        self.total_shares_held = 0
        self.total_cost = 0
        self.average_cost = 0
        self.target_price_value = 0
    
    def load_data_from_dataframe(self, df):
        """Load data from pandas DataFrame"""
        try:
            # Normalize column names
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # Ensure required columns
            required_cols = ['date', 'high', 'low']
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Missing required column: {col}")
            
            # Parse date
            df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=['date'])
            
            # Clean numeric columns
            for col in ['open', 'high', 'low', 'close', 'vwap', 'volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Set index
            df = df.sort_values('date').set_index('date')
            
            # Calculate reference levels
            df['r_low'] = df['low'] * (1 - self.r_low_discount)
            if 'vwap' in df.columns:
                df['r_vwap'] = df['vwap'] * (1 - self.r_vwap_discount)
            else:
                ref_col = 'close' if 'close' in df.columns else 'high'
                df['r_vwap'] = df[ref_col] * (1 - self.r_vwap_discount)
            
            self.data = df
            
            # Calculate SMA if requested
            if self.sma_period and self.sma_period > 0:
                price_col = 'close' if 'close' in self.data.columns else ('vwap' if 'vwap' in self.data.columns else 'high')
                sma_col = f"SMA_{self.sma_period}"
                self.data[sma_col] = self.data[price_col].rolling(window=self.sma_period, min_periods=self.sma_period).mean()
                self._sma_col = sma_col
            
            # Calculate Supertrend if requested
            if self.supertrend_enabled:
                self.calculate_supertrend()
            
            # Calculate Heikin Ashi if requested
            if self.ha_enabled:
                self.calculate_heikin_ashi()
            
            return True
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
    
    def calculate_supertrend(self):
        """Calculate Supertrend indicator"""
        if 'close' not in self.data.columns:
            close_col = 'vwap' if 'vwap' in self.data.columns else 'high'
            self.data['close'] = self.data[close_col]
        
        self.data['prev_close'] = self.data['close'].shift(1)
        self.data['tr1'] = self.data['high'] - self.data['low']
        self.data['tr2'] = abs(self.data['high'] - self.data['prev_close'])
        self.data['tr3'] = abs(self.data['low'] - self.data['prev_close'])
        self.data['TR'] = self.data[['tr1', 'tr2', 'tr3']].max(axis=1)
        self.data['ATR'] = self.data['TR'].rolling(window=self.supertrend_period).mean()
        self.data['hl_avg'] = (self.data['high'] + self.data['low']) / 2
        self.data['basic_ub'] = self.data['hl_avg'] + (self.supertrend_multiplier * self.data['ATR'])
        self.data['basic_lb'] = self.data['hl_avg'] - (self.supertrend_multiplier * self.data['ATR'])
        
        self.data['final_ub'] = 0.0
        self.data['final_lb'] = 0.0
        self.data['supertrend'] = 0.0
        
        for i in range(self.supertrend_period, len(self.data)):
            if i == self.supertrend_period:
                self.data.iloc[i, self.data.columns.get_loc('final_ub')] = self.data.iloc[i]['basic_ub']
                self.data.iloc[i, self.data.columns.get_loc('final_lb')] = self.data.iloc[i]['basic_lb']
                self.data.iloc[i, self.data.columns.get_loc('supertrend')] = self.data.iloc[i]['final_ub']
            else:
                if self.data.iloc[i]['basic_ub'] < self.data.iloc[i-1]['final_ub'] or self.data.iloc[i-1]['close'] > self.data.iloc[i-1]['final_ub']:
                    self.data.iloc[i, self.data.columns.get_loc('final_ub')] = self.data.iloc[i]['basic_ub']
                else:
                    self.data.iloc[i, self.data.columns.get_loc('final_ub')] = self.data.iloc[i-1]['final_ub']
                
                if self.data.iloc[i]['basic_lb'] > self.data.iloc[i-1]['final_lb'] or self.data.iloc[i-1]['close'] < self.data.iloc[i-1]['final_lb']:
                    self.data.iloc[i, self.data.columns.get_loc('final_lb')] = self.data.iloc[i]['basic_lb']
                else:
                    self.data.iloc[i, self.data.columns.get_loc('final_lb')] = self.data.iloc[i-1]['final_lb']
                
                if self.data.iloc[i-1]['supertrend'] == self.data.iloc[i-1]['final_ub']:
                    if self.data.iloc[i]['close'] <= self.data.iloc[i]['final_ub']:
                        self.data.iloc[i, self.data.columns.get_loc('supertrend')] = self.data.iloc[i]['final_ub']
                    else:
                        self.data.iloc[i, self.data.columns.get_loc('supertrend')] = self.data.iloc[i]['final_lb']
                else:
                    if self.data.iloc[i]['close'] >= self.data.iloc[i]['final_lb']:
                        self.data.iloc[i, self.data.columns.get_loc('supertrend')] = self.data.iloc[i]['final_lb']
                    else:
                        self.data.iloc[i, self.data.columns.get_loc('supertrend')] = self.data.iloc[i]['final_ub']
        
        self.data.drop(['prev_close', 'tr1', 'tr2', 'tr3', 'TR', 'hl_avg', 'basic_ub', 'basic_lb', 'final_ub', 'final_lb'], axis=1, inplace=True)
    
    def calculate_heikin_ashi(self):
        """Calculate Heikin Ashi candles"""
        if 'open' not in self.data.columns:
            self.data['open'] = self.data['close']
        
        self.data['ha_close'] = (self.data['open'] + self.data['high'] + self.data['low'] + self.data['close']) / 4
        self.data['ha_open'] = 0.0
        self.data['ha_high'] = 0.0
        self.data['ha_low'] = 0.0
        
        for i in range(len(self.data)):
            if i == 0:
                self.data.iloc[i, self.data.columns.get_loc('ha_open')] = (self.data.iloc[i]['open'] + self.data.iloc[i]['close']) / 2
            else:
                self.data.iloc[i, self.data.columns.get_loc('ha_open')] = (self.data.iloc[i-1]['ha_open'] + self.data.iloc[i-1]['ha_close']) / 2
            
            self.data.iloc[i, self.data.columns.get_loc('ha_high')] = max(self.data.iloc[i]['high'], self.data.iloc[i]['ha_open'], self.data.iloc[i]['ha_close'])
            self.data.iloc[i, self.data.columns.get_loc('ha_low')] = min(self.data.iloc[i]['low'], self.data.iloc[i]['ha_open'], self.data.iloc[i]['ha_close'])
    
    def run_backtest(self):
        """Run complete backtest"""
        if self.data is None:
            return False
        
        # Reset
        self.capital = self.initial_capital
        self.daily_transactions = []
        self.total_shares_held = 0
        self.total_cost = 0
        self.average_cost = 0
        self.target_price_value = 0
        
        # Process each day
        for date in self.data.index:
            daily_transaction = self.simulate_daily_trading(date)
            if daily_transaction:
                self.daily_transactions.append(daily_transaction)
        
        return True
    
    def simulate_daily_trading(self, date):
        """Simulate daily trading"""
        if date not in self.data.index:
            return None
        
        row = self.data.loc[date]
        high_price = row['high']
        low_price = row['low']
        date_index = self.data.index.get_loc(date)
        
        # Initialize transaction
        daily_transaction = {
            'date': date,
            'high': high_price,
            'low': low_price,
            'vwap': row.get('vwap', 0),
            'total_buy_qty': 0,
            'total_buy_value': 0,
            'avg_buy_price': 0,
            'sell_qty': 0,
            'sell_price': 0,
            'sell_value': 0,
            'profit': 0,
            'return_pct': 0,
            'execution': 'No',
            'total_shares_held': self.total_shares_held,
            'total_cost': self.total_cost,
            'average_cost': self.average_cost,
            'target_price': self.target_price_value
        }
        
        # Filter checks
        block_new_buys_due_to_sma = False
        price_col = 'close' if 'close' in self.data.columns else ('vwap' if 'vwap' in self.data.columns else 'high')
        if hasattr(self, '_sma_col') and self._sma_col in row.index:
            current_sma = row[self._sma_col]
            current_price = row[price_col]
            if pd.isna(current_sma) or current_price < current_sma:
                block_new_buys_due_to_sma = True
        
        block_new_buys_due_to_supertrend = False
        if self.supertrend_enabled and 'supertrend' in row.index:
            current_supertrend = row['supertrend']
            current_price = row[price_col]
            if pd.isna(current_supertrend) or current_price > current_supertrend:
                block_new_buys_due_to_supertrend = True
        
        block_new_buys_due_to_threshold = self.total_cost >= self.threshold_amount
        
        # Process buy orders
        filled_orders = []
        if not block_new_buys_due_to_sma and not block_new_buys_due_to_supertrend and not block_new_buys_due_to_threshold:
            if date_index > 0:
                prev_date = self.data.index[date_index - 1]
                prev_row = self.data.loc[prev_date]
                
                # Calculate entry levels
                e1_price = prev_row['low']
                e2_price = prev_row['low'] * 0.99
                
                entry_levels = {'E1': e1_price, 'E2': e2_price}
                
                # VWAP entries
                if self.vwap_entries_enabled and 'vwap' in prev_row.index:
                    prev_vwap = prev_row['vwap']
                    if pd.notna(prev_vwap) and prev_vwap > 0:
                        entry_levels['E3'] = prev_vwap
                        entry_levels['E4'] = prev_vwap * 0.99
                
                # SMA entries
                if self.sma_entries_enabled and hasattr(self, '_sma_col') and self._sma_col in prev_row.index:
                    prev_sma = prev_row[self._sma_col]
                    if pd.notna(prev_sma) and prev_sma > 0:
                        entry_levels['E5'] = prev_sma
                        entry_levels['E6'] = prev_sma * 0.99
                
                # HA entries
                if self.ha_entries_enabled and 'ha_low' in prev_row.index:
                    prev_ha_low = prev_row['ha_low']
                    if pd.notna(prev_ha_low) and prev_ha_low > 0:
                        entry_levels['E7'] = prev_ha_low
                        entry_levels['E8'] = prev_ha_low * 0.99
                
                # Calculate quantity
                if self.max_investment is not None and self.max_investment > 0:
                    total_entry_price = sum(entry_levels.values())
                    qty_per_order = max(1, int(self.max_investment / total_entry_price))
                elif self.fixed_qty is not None and self.fixed_qty > 0:
                    qty_per_order = int(self.fixed_qty)
                else:
                    qty_per_order = 1
                
                # Check fills
                for level, price in entry_levels.items():
                    if price > 0 and low_price <= price:
                        filled_orders.append({'level': level, 'price': price, 'qty': qty_per_order, 'value': price * qty_per_order})
        
        # Process filled orders
        if filled_orders:
            total_qty = sum(o['qty'] for o in filled_orders)
            total_value = sum(o['value'] for o in filled_orders)
            avg_price = total_value / total_qty
            
            total_charges_amount = total_value * self.total_charges
            total_cost_with_charges = total_value + total_charges_amount
            
            daily_transaction['total_buy_qty'] = total_qty
            daily_transaction['total_buy_value'] = total_value
            daily_transaction['avg_buy_price'] = avg_price
            
            if (self.total_cost + total_cost_with_charges) <= self.threshold_amount:
                self.total_shares_held += total_qty
                self.total_cost += total_cost_with_charges
                self.average_cost = self.total_cost / self.total_shares_held if self.total_shares_held > 0 else 0
                
                if self.total_cost <= self.threshold_amount:
                    self.target_price_value = self.average_cost * (1 + self.profit_target)
                else:
                    self.target_price_value = self.average_cost * (1 + self.reduced_profit_target)
                
                daily_transaction['total_shares_held'] = self.total_shares_held
                daily_transaction['total_cost'] = self.total_cost
                daily_transaction['average_cost'] = self.average_cost
                daily_transaction['target_price'] = self.target_price_value
        
        # Check if we can sell
        if self.total_shares_held > 0 and high_price >= self.target_price_value:
            sell_value_gross = self.target_price_value * self.total_shares_held
            sell_charges_amount = sell_value_gross * self.total_charges
            sell_value_net = sell_value_gross - sell_charges_amount
            
            daily_transaction['sell_qty'] = self.total_shares_held
            daily_transaction['sell_price'] = self.target_price_value
            daily_transaction['sell_value'] = sell_value_gross
            daily_transaction['profit'] = sell_value_net - self.total_cost
            daily_transaction['return_pct'] = (daily_transaction['profit'] / self.total_cost * 100) if self.total_cost > 0 else 0
            daily_transaction['execution'] = 'Sell'
            
            self.capital += daily_transaction['profit']
            
            # Reset position
            self.total_shares_held = 0
            self.total_cost = 0
            self.average_cost = 0
            self.target_price_value = 0
        
        return daily_transaction
    
    def get_summary(self):
        """Get performance summary"""
        if not self.daily_transactions:
            return {}
        
        df = pd.DataFrame(self.daily_transactions)
        total_trades = len(df[df['profit'] > 0])
        total_profit = df['profit'].sum()
        total_return = (total_profit / self.initial_capital) * 100
        final_capital = self.initial_capital + total_profit
        
        return {
            'total_trades': total_trades,
            'total_profit': total_profit,
            'total_return': total_return,
            'final_capital': final_capital,
            'win_rate': 100.0 if total_trades > 0 else 0,
            'avg_profit_per_trade': total_profit / total_trades if total_trades > 0 else 0
        }

