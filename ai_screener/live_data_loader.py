"""
Live Data Loader Using yfinance
================================

Fetches real-time stock data from Yahoo Finance for live trading.
Auto-updates data for accurate AI predictions.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class LiveDataLoader:
    """Fetch live stock data from Yahoo Finance."""
    
    # NSE stock symbols mapping (Yahoo Finance format)
    NSE_SYMBOLS = {
        'NSE_RELIANCE': 'RELIANCE.NS',
        'NSE_TCS': 'TCS.NS',
        'NSE_HDFCBANK': 'HDFCBANK.NS',
        'NSE_INFY': 'INFY.NS',
        'NSE_ICICIBANK': 'ICICIBANK.NS',
        'NSE_HINDUNILVR': 'HINDUNILVR.NS',
        'NSE_SBIN': 'SBIN.NS',
        'NSE_BHARTIARTL': 'BHARTIARTL.NS',
        'NSE_KOTAKBANK': 'KOTAKBANK.NS',
        'NSE_ASIANPAINT': 'ASIANPAINT.NS',
        'NSE_AXISBANK': 'AXISBANK.NS',
        'NSE_SUNPHARMA': 'SUNPHARMA.NS',
        'NSE_TITAN': 'TITAN.NS',
        'NSE_HCLTECH': 'HCLTECH.NS',
        'NSE_TECHM': 'TECHM.NS',
        'NSE_NESTLEIND': 'NESTLEIND.NS',
        'NSE_TATASTEEL': 'TATASTEEL.NS',
        'NSE_CIPLA': 'CIPLA.NS',
        'NSE_DRREDDY': 'DRREDDY.NS',
        'NSE_BIOCON': 'BIOCON.NS',
        'NSE_EICHERMOT': 'EICHERMOT.NS',
        'NSE_HINDALCO': 'HINDALCO.NS',
        'NSE_GRASIM': 'GRASIM.NS',
        'NSE_JSWSTEEL': 'JSWSTEEL.NS',
        'NSE_NTPC': 'NTPC.NS',
        'NSE_POWERGRID': 'POWERGRID.NS',
        'NSE_ONGC': 'ONGC.NS',
        'NSE_M&M': 'M&M.NS',
        'NSE_ADANIPORTS': 'ADANIPORTS.NS',
        'NSE_ADANIENT': 'ADANIENT.NS',
        'NSE_BAJAJFINSV': 'BAJAJFINSV.NS',
        'NSE_SHRIRAMFIN': 'SHRIRAMFIN.NS',
        'NSE_TATACONSUM': 'TATACONSUM.NS',
        'NSE_HDFCLIFE': 'HDFCLIFE.NS',
        'NSE_SBILIFE': 'SBILIFE.NS',
        'NSE_BERGEPAINT': 'BERGEPAINT.NS',
        'NSE_MAXHEALTH': 'MAXHEALTH.NS',
        'NSE_RELINFRA': 'RELINFRA.NS',
        'NSE_ETERNAL': 'ETERNAL.NS',
        'NSE_PTC': 'PTC.NS',
        'NSE_REFEX': 'REFEX.NS',
        'NSE_TMPV': 'TMPV.NS',
    }
    
    def __init__(self):
        """Initialize live data loader."""
        self.stock_data: Dict[str, pd.DataFrame] = {}
        
    def get_all_stocks(self) -> List[str]:
        """
        Get list of all available stock symbols.
        
        Returns:
            List of stock symbols (e.g., ['NSE_RELIANCE', 'NSE_TCS'])
        """
        return sorted(list(self.NSE_SYMBOLS.keys()))
    
    def fetch_live_data(self, symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
        """
        Fetch live data from Yahoo Finance.
        
        Args:
            symbol: Stock symbol (e.g., 'NSE_RELIANCE')
            period: Data period ('1mo', '3mo', '6mo', '1y', 'max')
        
        Returns:
            DataFrame with columns: time, open, high, low, close, volume, vwap
        """
        try:
            # Get Yahoo Finance symbol
            yf_symbol = self.NSE_SYMBOLS.get(symbol)
            if not yf_symbol:
                print(f"Warning: Symbol {symbol} not found in mapping")
                return None
            
            # Fetch data
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                print(f"Warning: No data fetched for {symbol}")
                return None
            
            # Rename columns to match expected format
            df = df.reset_index()
            df = df.rename(columns={
                'Date': 'time',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Calculate VWAP if not present
            if 'vwap' not in df.columns:
                df['vwap'] = ((df['high'] + df['low'] + df['close']) / 3 * df['volume']).cumsum() / df['volume'].cumsum()
                # Fill any NaN with close price
                df['vwap'] = df['vwap'].fillna(df['close'])
            
            # Ensure we have required columns
            required_cols = ['time', 'open', 'high', 'low', 'close', 'volume', 'vwap']
            df = df[required_cols]
            
            # Fill missing volume with 1.0
            df['volume'] = df['volume'].fillna(1.0)
            
            # Cache the data
            self.stock_data[symbol] = df
            
            return df
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def fetch_multiple_stocks(self, symbols: List[str], period: str = "3mo") -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stocks.
        
        Args:
            symbols: List of stock symbols
            period: Data period
        
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        data = {}
        for symbol in symbols:
            df = self.fetch_live_data(symbol, period)
            if df is not None:
                data[symbol] = df
        return data
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get latest price for a stock.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Latest close price or None
        """
        df = self.fetch_live_data(symbol, period="1d")
        if df is not None and not df.empty:
            return float(df['close'].iloc[-1])
        return None
    
    def is_market_open(self) -> bool:
        """
        Check if Indian stock market is currently open.
        
        Returns:
            True if market is open, False otherwise
        """
        now = datetime.now()
        # Indian market: Monday-Friday, 9:15 AM - 3:30 PM IST
        if now.weekday() >= 5:  # Weekend
            return False
        if now.hour < 9 or (now.hour == 9 and now.minute < 15):
            return False
        if now.hour >= 15 and now.minute >= 30:
            return False
        return True

