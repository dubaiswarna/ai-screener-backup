"""
Universal Data Loader for AI Screener
======================================

Loads historical OHLCV + VWAP data from CSV files.
Supports both NSE stocks and MCX commodities.

Data Sources:
- NSE Stocks: Nify50_data/ folder (NSE_*.csv)
- MCX Commodities: MCX_data/ folder (MCX_*.csv)
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class UniversalDataLoader:
    """Load and prepare stock/commodity data from CSV files."""
    
    def __init__(self, data_dirs: List[str] = None):
        """
        Initialize UniversalDataLoader.
        
        Args:
            data_dirs: List of directories containing CSV files
                      Default: ['Nify50_data', 'MCX_data']
        """
        if data_dirs is None:
            data_dirs = ['Nify50_data', 'MCX_data', 'Crypto_data']
        
        self.data_dirs = []
        for data_dir in data_dirs:
            dir_path = Path(data_dir)
            if not dir_path.exists():
                # Try parent directory
                parent_dir = Path("..") / data_dir
                if parent_dir.exists():
                    dir_path = parent_dir
                else:
                    # Try grandparent
                    grandparent_dir = Path("../..") / data_dir
                    if grandparent_dir.exists():
                        dir_path = grandparent_dir
                    else:
                        print(f"Warning: Data directory {data_dir} not found")
                        continue
            
            self.data_dirs.append(dir_path)
            print(f"✓ Found data directory: {dir_path}")
        
        self.stock_data: Dict[str, pd.DataFrame] = {}
        
    def get_all_symbols(self, exchange: str = None) -> List[str]:
        """
        Get list of all symbols from CSV filenames.
        
        Args:
            exchange: Filter by exchange ('NSE', 'MCX', or None for all)
        
        Returns:
            List of symbols (e.g., ['NSE_RELIANCE', 'MCX_GOLD'])
        """
        symbols = []
        for data_dir in self.data_dirs:
            # Look for all CSV files
            csv_files = list(data_dir.glob("*.csv"))
            for file in csv_files:
                # Extract symbol from filename like "NSE_RELIANCE, 1D.csv" or "MCX_GOLD, 1D.csv"
                symbol = file.stem.split(",")[0].strip()
                
                # Filter by exchange if specified
                if exchange:
                    if symbol.startswith(f"{exchange}_"):
                        symbols.append(symbol)
                else:
                    symbols.append(symbol)
        
        return sorted(list(set(symbols)))
    
    def load_symbol_data(self, symbol: str, fill_volume: bool = True, verbose: bool = True) -> Optional[pd.DataFrame]:
        """
        Load data for a single symbol (stock or commodity).
        
        Args:
            symbol: Symbol (e.g., 'NSE_RELIANCE' or 'MCX_GOLD')
            fill_volume: If True, fill missing volume with estimates
        
        Returns:
            DataFrame with columns: time, open, high, low, close, VWAP, volume
        """
        # Search all data directories for matching file
        csv_file = None
        for data_dir in self.data_dirs:
            files = list(data_dir.glob(f"{symbol}*.csv"))
            if files:
                csv_file = files[0]
                break
        
        if not csv_file:
            print(f"Warning: No CSV file found for {symbol}")
            return None
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Rename time column to lowercase if needed
            if 'time' in df.columns or 'Time' in df.columns:
                time_col = 'time' if 'time' in df.columns else 'Time'
                df = df.rename(columns={time_col: 'time'})
            elif 'date' in df.columns or 'Date' in df.columns:
                date_col = 'date' if 'date' in df.columns else 'Date'
                df = df.rename(columns={date_col: 'time'})
            else:
                print(f"Warning: No 'time' or 'date' column in {symbol}")
                return None
            
            # Ensure lowercase column names
            df.columns = df.columns.str.lower()
            
            # Convert time to datetime
            df['time'] = pd.to_datetime(df['time'])
            
            # Add volume column if missing
            if 'volume' not in df.columns:
                if fill_volume:
                    # Estimate volume based on price
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
            
            print(f"Loaded {symbol}: {len(df)} rows from {csv_file.name}")
            return df
            
        except Exception as e:
            print(f"Error loading {symbol}: {e}")
            return None
    
    def load_all_symbols(self, exchange: str = None) -> Dict[str, pd.DataFrame]:
        """
        Load data for all symbols.
        
        Args:
            exchange: Filter by exchange ('NSE', 'MCX', or None for all)
        
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        symbols = self.get_all_symbols(exchange)
        print(f"\nFound {len(symbols)} symbols to load")
        print("=" * 60)
        
        for symbol in symbols:
            self.load_symbol_data(symbol)
        
        print("=" * 60)
        print(f"Successfully loaded {len(self.stock_data)} symbols\n")
        
        return self.stock_data
    
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
        
        # Check OHLC logic
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
        Get summary statistics for all loaded symbols.
        
        Returns:
            DataFrame with summary stats
        """
        summaries = []
        for symbol, df in self.stock_data.items():
            summary = {
                'symbol': symbol,
                'exchange': symbol.split('_')[0],
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
    loader = UniversalDataLoader()
    
    # Get all symbols
    print("\n=== NSE Stocks ===")
    nse_stocks = loader.get_all_symbols(exchange='NSE')
    print(f"Found {len(nse_stocks)} NSE stocks")
    for stock in nse_stocks[:5]:
        print(f"  - {stock}")
    if len(nse_stocks) > 5:
        print(f"  ... and {len(nse_stocks) - 5} more")
    
    print("\n=== MCX Commodities ===")
    mcx_commodities = loader.get_all_symbols(exchange='MCX')
    print(f"Found {len(mcx_commodities)} MCX commodities")
    for commodity in mcx_commodities:
        print(f"  - {commodity}")
    
    # Load one MCX commodity as example
    if mcx_commodities:
        print(f"\n=== Loading sample commodity: {mcx_commodities[0]} ===")
        df = loader.load_symbol_data(mcx_commodities[0])
        if df is not None:
            print(f"\nData shape: {df.shape}")
            print(f"\nFirst 5 rows:")
            print(df.head())
            print(f"\nLast 5 rows:")
            print(df.tail())

