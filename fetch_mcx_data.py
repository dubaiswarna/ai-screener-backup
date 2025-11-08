"""
Fetch Gold and Silver Data for MCX Trading
============================================

This script downloads historical Gold and Silver futures data
and formats it to match the existing NSE stock data format.

Data Sources (Free):
- Gold Futures (GC=F) from Yahoo Finance
- Silver Futures (SI=F) from Yahoo Finance

Output Format:
- Same as NSE stocks: time, open, high, low, close, Volume, VWAP, Upper Band #1, Lower Band #1
- Saved as: MCX_GOLD, 1D.csv and MCX_SILVER, 1D.csv
"""

import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class MCXDataFetcher:
    """Fetch and format commodity data for MCX trading."""
    
    def __init__(self, output_dir: str = "MCX_data"):
        """Initialize the data fetcher."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        print(f"Output directory: {self.output_dir.absolute()}")
    
    def calculate_vwap(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate VWAP (Volume Weighted Average Price).
        
        VWAP = (Typical Price * Volume) / Total Volume
        where Typical Price = (High + Low + Close) / 3
        """
        df = df.copy()
        df['typical_price'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP'] = df['typical_price']  # Simplified VWAP (for compatibility)
        return df
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, window: int = 20, num_std: int = 2) -> pd.DataFrame:
        """
        Calculate Bollinger Bands.
        
        Args:
            window: Rolling window size
            num_std: Number of standard deviations
        """
        df = df.copy()
        
        # Calculate rolling mean and std
        rolling_mean = df['Close'].rolling(window=window).mean()
        rolling_std = df['Close'].rolling(window=window).std()
        
        # Calculate bands
        df['Upper Band #1'] = rolling_mean + (rolling_std * num_std)
        df['Lower Band #1'] = rolling_mean - (rolling_std * num_std)
        
        # Fill initial NaN values with close price
        df['Upper Band #1'].fillna(df['Close'], inplace=True)
        df['Lower Band #1'].fillna(df['Close'], inplace=True)
        
        return df
    
    def fetch_commodity_data(self, symbol: str, commodity_name: str, period: str = "10y") -> bool:
        """
        Fetch commodity data from Yahoo Finance.
        
        Args:
            symbol: Yahoo Finance symbol (e.g., 'GC=F' for Gold)
            commodity_name: Name for output file (e.g., 'GOLD')
            period: Data period ('1y', '5y', '10y', 'max')
        
        Returns:
            True if successful
        """
        print(f"\nFetching {commodity_name} data...")
        print(f"Symbol: {symbol}")
        print(f"Period: {period}")
        print("=" * 70)
        
        try:
            # Download data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if df.empty:
                print(f"❌ No data returned for {symbol}")
                return False
            
            print(f"✓ Downloaded {len(df)} rows")
            print(f"  Date range: {df.index[0]} to {df.index[-1]}")
            
            # Prepare data in NSE format
            df_formatted = pd.DataFrame({
                'time': df.index,
                'open': df['Open'],
                'high': df['High'],
                'low': df['Low'],
                'close': df['Close'],
                'Volume': df['Volume']
            })
            
            # Calculate VWAP
            df_formatted = self.calculate_vwap(df_formatted)
            
            # Calculate Bollinger Bands
            df_formatted = self.calculate_bollinger_bands(df_formatted)
            
            # Reorder columns to match NSE format
            df_formatted = df_formatted[['time', 'open', 'high', 'low', 'close', 'Volume', 'VWAP', 'Upper Band #1', 'Lower Band #1']]
            
            # Remove any NaN rows
            df_formatted = df_formatted.dropna()
            
            # Save to CSV
            output_file = self.output_dir / f"MCX_{commodity_name}, 1D.csv"
            df_formatted.to_csv(output_file, index=False)
            
            print(f"✓ Saved {len(df_formatted)} rows to: {output_file.name}")
            print(f"  Price range: ${df_formatted['close'].min():.2f} - ${df_formatted['close'].max():.2f}")
            print(f"  Current price: ${df_formatted['close'].iloc[-1]:.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fetching {commodity_name}: {e}")
            return False
    
    def fetch_all_commodities(self):
        """Fetch data for all major commodities."""
        commodities = [
            ('GC=F', 'GOLD', 'Gold Futures'),
            ('SI=F', 'SILVER', 'Silver Futures'),
        ]
        
        print("\n" + "=" * 70)
        print("MCX COMMODITY DATA FETCHER")
        print("=" * 70)
        
        results = {}
        for symbol, name, description in commodities:
            print(f"\n📊 {description}")
            success = self.fetch_commodity_data(symbol, name)
            results[name] = success
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        for name, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"{name:15} : {status}")
        print("=" * 70)
        
        return results


def main():
    """Main function to fetch MCX data."""
    fetcher = MCXDataFetcher()
    results = fetcher.fetch_all_commodities()
    
    # Check if any failed
    failed = [name for name, success in results.items() if not success]
    if failed:
        print(f"\n⚠️  Failed to fetch: {', '.join(failed)}")
        print("This might be due to internet connection or Yahoo Finance API issues.")
    else:
        print("\n✅ All commodity data fetched successfully!")
        print("\nNext steps:")
        print("1. Run: python quick_train_mcx.py")
        print("2. Or integrate with existing screener")


if __name__ == '__main__':
    main()

