"""
Live Price Simulator - Realistic Market Price Movements
========================================================
Simulates live price updates based on historical volatility patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class LivePriceSimulator:
    """Simulate realistic live price movements."""
    
    def __init__(self, stock_data):
        """
        Initialize price simulator.
        
        Args:
            stock_data: Dictionary of {symbol: DataFrame} with historical data
        """
        self.stock_data = stock_data
        self.live_prices = {}
        self.price_history = {}
        self.volatilities = {}
        self.trends = {}
        
        # Calculate volatility for each stock
        self._calculate_volatilities()
        
        # Initialize live prices to last known prices
        self._initialize_prices()
    
    def _calculate_volatilities(self):
        """Calculate historical volatility for each stock."""
        for symbol, df in self.stock_data.items():
            # Calculate daily returns
            returns = df['close'].pct_change().dropna()
            
            # Volatility = standard deviation of returns (annualized)
            daily_vol = returns.std()
            
            # Per-minute volatility (assuming 375 trading minutes per day)
            minute_vol = daily_vol / np.sqrt(375)
            
            # Recent trend (last 20 days)
            recent_returns = returns.tail(20).mean()
            
            self.volatilities[symbol] = minute_vol
            self.trends[symbol] = recent_returns
    
    def _initialize_prices(self):
        """Initialize live prices to last known prices."""
        for symbol, df in self.stock_data.items():
            last_price = df.iloc[-1]['close']
            self.live_prices[symbol] = {
                'price': last_price,
                'open': last_price,
                'high': last_price,
                'low': last_price,
                'last_update': datetime.now(),
                'tick_count': 0
            }
            self.price_history[symbol] = [last_price]
    
    def update_prices(self):
        """
        Update all stock prices with realistic movement.
        Uses Geometric Brownian Motion with trend bias.
        """
        current_time = datetime.now()
        
        for symbol in self.live_prices.keys():
            price_data = self.live_prices[symbol]
            current_price = price_data['price']
            volatility = self.volatilities.get(symbol, 0.02)
            trend = self.trends.get(symbol, 0)
            
            # Time since last update (in minutes)
            time_delta = (current_time - price_data['last_update']).total_seconds() / 60
            if time_delta == 0:
                time_delta = 0.1  # Minimum 0.1 minute
            
            # Geometric Brownian Motion
            # Price change = trend * dt + volatility * random_shock * sqrt(dt)
            drift = trend * time_delta
            shock = volatility * np.random.normal(0, 1) * np.sqrt(time_delta)
            
            # Calculate new price
            price_change = drift + shock
            new_price = current_price * (1 + price_change)
            
            # Add some realism - prices don't move smoothly
            # Occasional larger moves (news, orders)
            if random.random() < 0.05:  # 5% chance of larger move
                spike = random.choice([-1, 1]) * volatility * 2
                new_price *= (1 + spike)
            
            # Ensure price doesn't go negative or too extreme
            last_close = self.stock_data[symbol].iloc[-1]['close']
            new_price = max(new_price, last_close * 0.90)  # Max 10% down
            new_price = min(new_price, last_close * 1.10)  # Max 10% up
            
            # Update high/low
            price_data['high'] = max(price_data['high'], new_price)
            price_data['low'] = min(price_data['low'], new_price)
            
            # Update current price
            price_data['price'] = round(new_price, 2)
            price_data['last_update'] = current_time
            price_data['tick_count'] += 1
            
            # Store in history
            self.price_history[symbol].append(new_price)
            
            # Keep only last 100 ticks
            if len(self.price_history[symbol]) > 100:
                self.price_history[symbol].pop(0)
    
    def get_current_price(self, symbol):
        """Get current simulated price for a symbol."""
        if symbol in self.live_prices:
            return self.live_prices[symbol]['price']
        elif symbol in self.stock_data:
            return self.stock_data[symbol].iloc[-1]['close']
        return None
    
    def get_all_current_prices(self):
        """Get all current prices as dictionary."""
        return {symbol: data['price'] for symbol, data in self.live_prices.items()}
    
    def get_price_change(self, symbol):
        """Get price change % from open."""
        if symbol not in self.live_prices:
            return 0
        
        data = self.live_prices[symbol]
        change = ((data['price'] - data['open']) / data['open']) * 100
        return round(change, 2)
    
    def get_ohlc(self, symbol):
        """Get current OHLC for symbol."""
        if symbol not in self.live_prices:
            return None
        
        data = self.live_prices[symbol]
        return {
            'open': data['open'],
            'high': data['high'],
            'low': data['low'],
            'close': data['price']
        }
    
    def reset_day(self):
        """Reset for new trading day (reset OHLC)."""
        for symbol, data in self.live_prices.items():
            data['open'] = data['price']
            data['high'] = data['price']
            data['low'] = data['price']
            data['tick_count'] = 0
    
    def get_volatility(self, symbol):
        """Get volatility for symbol."""
        return self.volatilities.get(symbol, 0.02)
    
    def simulate_market_hours(self):
        """Check if currently in simulated market hours."""
        current_time = datetime.now()
        # Simulate market hours: 9:15 AM - 3:30 PM
        market_open = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = current_time.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_open <= current_time <= market_close
    
    def get_price_trend(self, symbol, periods=10):
        """Get recent price trend direction."""
        if symbol not in self.price_history:
            return 'NEUTRAL'
        
        history = self.price_history[symbol]
        if len(history) < periods:
            return 'NEUTRAL'
        
        recent = history[-periods:]
        trend = (recent[-1] - recent[0]) / recent[0]
        
        if trend > 0.002:  # 0.2% up
            return 'BULLISH'
        elif trend < -0.002:  # 0.2% down
            return 'BEARISH'
        else:
            return 'NEUTRAL'

