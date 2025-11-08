"""
Data Loader for AI Stock Screener
==================================

Loads historical OHLCV + VWAP data from CSV files in Nify50_data folder.
Contains 10 years of Nifty50 stock data for training AI models.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class DataLoader:
    """Load and prepare stock data from CSV files."""
    
    def __init__(self, data_dir: str = "Nify50_data"):
        """
        Initialize DataLoader.
        
        Args:
            data_dir: Path to directory containing CSV files
        """
        # Try current directory first, then parent directory
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            # Try parent directory
            parent_dir = Path("..") / data_dir
            if parent_dir.exists():
                self.data_dir = parent_dir
            else:
                # Try grandparent (in case running from ai_screener subdirectory)
                grandparent_dir = Path("../..") / data_dir
                if grandparent_dir.exists():
                    self.data_dir = grandparent_dir
                else:
                    print(f"Warning: Data directory {data_dir} not found")
                    print(f"Current dir: {Path.cwd()}")
                    print(f"Attempted: {Path(data_dir).absolute()}, {parent_dir.absolute()}, {grandparent_dir.absolute()}")
        self.stock_data: Dict[str, pd.DataFrame] = {}
        
    def get_all_stocks(self) -> List[str]:
        """
        Get list of all stock symbols from CSV filenames.
        
        Returns:
            List of stock symbols (e.g., ['NSE_ABCAPITAL', 'NSE_RELIANCE'])
        """
        csv_files = list(self.data_dir.glob("NSE_*.csv"))
        stocks = []
        for file in csv_files:
            # Extract symbol from filename like "NSE_ABCAPITAL, 1D.csv"
            symbol = file.stem.split(",")[0]
            stocks.append(symbol)
        return sorted(stocks)
    
    def load_stock_data(self, symbol: str, fill_volume: bool = True) -> Optional[pd.DataFrame]:
        """
        Load data for a single stock.
        
        Args:
            symbol: Stock symbol (e.g., 'NSE_ABCAPITAL')
            fill_volume: If True, fill missing volume with 1.0
        
        Returns:
            DataFrame with columns: time, open, high, low, close, VWAP, volume
        """
        # Find CSV file matching symbol
        csv_files = list(self.data_dir.glob(f"{symbol}*.csv"))
        if not csv_files:
            print(f"Warning: No CSV file found for {symbol}")
            return None
        
        # Use first matching file
        file_path = csv_files[0]
        
        try:
            # Read CSV
            df = pd.read_csv(file_path)
            
            # Rename time column to lowercase if needed
            if 'time' in df.columns or 'Time' in df.columns:
                time_col = 'time' if 'time' in df.columns else 'Time'
                df = df.rename(columns={time_col: 'time'})
            elif 'date' in df.columns:
                df = df.rename(columns={'date': 'time'})
            else:
                print(f"Warning: No 'time' or 'date' column in {symbol}")
                return None
            
            # Ensure lowercase column names
            df.columns = df.columns.str.lower()
            
            # Convert time to datetime
            df['time'] = pd.to_datetime(df['time'])
            
            # Add volume column if missing (use typical volume based on price)
            if 'volume' not in df.columns:
                if fill_volume:
                    # Estimate volume as 0.1% of price (for normalization)
                    df['volume'] = df['close'] * 1000
                else:
                    df['volume'] = 0
            
            # Select required columns
            required_cols = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"Warning: Missing columns in {symbol}: {missing_cols}")
                return None
            
            df = df[required_cols].copy()
            
            # Remove any rows with NaN values
            df = df.dropna()
            
            # Sort by time
            df = df.sort_values('time').reset_index(drop=True)
            
            # Cache the data
            self.stock_data[symbol] = df
            
            print(f"Loaded {symbol}: {len(df)} rows from {file_path.name}")
            return df
            
        except Exception as e:
            print(f"Error loading {symbol}: {e}")
            return None
    
    def load_all_stocks(self) -> Dict[str, pd.DataFrame]:
        """
        Load data for all stocks found in data directory.
        
        Returns:
            Dictionary mapping stock symbols to DataFrames
        """
        stocks = self.get_all_stocks()
        print(f"\nFound {len(stocks)} stocks to load")
        print("=" * 60)
        
        for symbol in stocks:
            self.load_stock_data(symbol)
        
        print("=" * 60)
        print(f"Successfully loaded {len(self.stock_data)} stocks\n")
        
        return self.stock_data
    
    def get_stock_symbol(self, file_path: Path) -> str:
        """
        Extract stock symbol from file path.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Stock symbol
        """
        return file_path.stem.split(",")[0]
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate loaded data for quality checks.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if data is valid
        """
        if df.empty:
            return False
        
        # Check for required columns
        required = ['time', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required):
            return False
        
        # Check for negative prices
        if (df[['open', 'high', 'low', 'close']] < 0).any().any():
            return False
        
        # Check OHLC logic (high >= low, high >= open/close, low <= open/close)
        invalid = (
            (df['high'] < df['low']) | 
            (df['high'] < df['open']) | 
            (df['high'] < df['close']) |
            (df['low'] > df['open']) | 
            (df['low'] > df['close'])
        )
        if invalid.any():
            return False
        
        return True
    
    def get_data_summary(self) -> pd.DataFrame:
        """
        Get summary statistics for all loaded stocks.
        
        Returns:
            DataFrame with summary stats
        """
        summaries = []
        for symbol, df in self.stock_data.items():
            summary = {
                'symbol': symbol,
                'rows': len(df),
                'start_date': df['time'].min(),
                'end_date': df['time'].max(),
                'avg_price': df['close'].mean(),
                'max_price': df['close'].max(),
                'min_price': df['close'].min(),
                'std_price': df['close'].std()
            }
            summaries.append(summary)
        
        return pd.DataFrame(summaries)


if __name__ == '__main__':
    # Test the loader
    loader = DataLoader()  # Uses default Nify50_data
    
    # Get all stocks
    stocks = loader.get_all_stocks()
    print(f"\nFound {len(stocks)} stocks:")
    for stock in stocks[:10]:
        print(f"  - {stock}")
    if len(stocks) > 10:
        print(f"  ... and {len(stocks) - 10} more")
    
    # Load one stock as example
    if stocks:
        print(f"\nLoading sample stock: {stocks[0]}")
        df = loader.load_stock_data(stocks[0])
        if df is not None:
            print(f"\nData shape: {df.shape}")
            print(f"\nFirst 5 rows:")
            print(df.head())
            print(f"\nData types:")
            print(df.dtypes)
            print(f"\nSummary statistics:")
            print(df.describe())

