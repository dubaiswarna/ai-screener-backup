"""
Fetch Data for Expanded Stock Universe (Nifty 500 + Smallcap 250)
===================================================================
Downloads historical data for up to 750 stocks

Features:
- Multi-threaded downloading for speed
- Progress tracking
- Error handling
- Resume capability
- Auto-retry on failures

Author: AI Screener v3.0
Date: November 2025
"""

import os
import sys
import time
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import logging

# Add config to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.stock_universe import get_stock_universe, get_universe_info

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_fetch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StockDataFetcher:
    """
    Fetches historical stock data for multiple stocks.
    """
    
    def __init__(self, data_dir: str = 'data/stocks', period: str = '2y'):
        """
        Initialize data fetcher.
        
        Args:
            data_dir: Directory to save data
            period: Data period ('1y', '2y', '5y', 'max')
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.period = period
        self.success_count = 0
        self.failed_count = 0
        self.failed_stocks = []
        
    def fetch_single_stock(self, symbol: str, retry: int = 3) -> bool:
        """
        Fetch data for a single stock.
        
        Args:
            symbol: Stock symbol
            retry: Number of retry attempts
            
        Returns:
            True if successful, False otherwise
        """
        for attempt in range(retry):
            try:
                # Add .NS for NSE stocks
                ticker_symbol = f"{symbol}.NS"
                
                # Download data
                logger.info(f"📥 Fetching {symbol}... (Attempt {attempt + 1}/{retry})")
                ticker = yf.Ticker(ticker_symbol)
                df = ticker.history(period=self.period)
                
                if df.empty:
                    logger.warning(f"⚠️ No data for {symbol}")
                    continue
                
                # Prepare DataFrame
                df = df.reset_index()
                df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
                
                # Keep only required columns
                df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
                
                # Calculate VWAP (approximate)
                df['VWAP'] = (df['High'] + df['Low'] + df['Close']) / 3
                
                # Save to CSV
                file_path = self.data_dir / f"{symbol}.csv"
                df.to_csv(file_path, index=False)
                
                logger.info(f"✅ {symbol}: {len(df)} rows saved")
                self.success_count += 1
                return True
                
            except Exception as e:
                logger.error(f"❌ Error fetching {symbol} (Attempt {attempt + 1}): {e}")
                if attempt < retry - 1:
                    time.sleep(2)  # Wait before retry
                    
        # All attempts failed
        self.failed_count += 1
        self.failed_stocks.append(symbol)
        return False
    
    def fetch_multiple_stocks(self, symbols: list, max_workers: int = 10) -> dict:
        """
        Fetch data for multiple stocks using threading.
        
        Args:
            symbols: List of stock symbols
            max_workers: Number of parallel threads
            
        Returns:
            Dict with statistics
        """
        logger.info(f"🚀 Starting data fetch for {len(symbols)} stocks...")
        logger.info(f"📁 Saving to: {self.data_dir}")
        logger.info(f"⏱️ Period: {self.period}")
        logger.info(f"🔧 Max workers: {max_workers}")
        
        start_time = time.time()
        
        # Use ThreadPoolExecutor for parallel downloads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_symbol = {
                executor.submit(self.fetch_single_stock, symbol): symbol 
                for symbol in symbols
            }
            
            # Process as completed
            for i, future in enumerate(as_completed(future_to_symbol), 1):
                symbol = future_to_symbol[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"❌ Exception for {symbol}: {e}")
                    self.failed_count += 1
                    self.failed_stocks.append(symbol)
                
                # Progress update every 10 stocks
                if i % 10 == 0:
                    progress = (i / len(symbols)) * 100
                    logger.info(f"📊 Progress: {i}/{len(symbols)} ({progress:.1f}%)")
        
        elapsed_time = time.time() - start_time
        
        # Summary
        stats = {
            'total': len(symbols),
            'success': self.success_count,
            'failed': self.failed_count,
            'failed_stocks': self.failed_stocks,
            'elapsed_time': elapsed_time,
            'avg_time_per_stock': elapsed_time / len(symbols)
        }
        
        return stats
    
    def print_summary(self, stats: dict):
        """Print summary of data fetch."""
        print("\n" + "=" * 60)
        print("📊 DATA FETCH SUMMARY")
        print("=" * 60)
        print(f"Total Stocks: {stats['total']}")
        print(f"✅ Success: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
        print(f"❌ Failed: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
        print(f"⏱️ Total Time: {stats['elapsed_time']:.1f} seconds ({stats['elapsed_time']/60:.1f} minutes)")
        print(f"⚡ Avg Time/Stock: {stats['avg_time_per_stock']:.2f} seconds")
        print("=" * 60)
        
        if stats['failed_stocks']:
            print(f"\n❌ Failed stocks ({len(stats['failed_stocks'])}):")
            for stock in stats['failed_stocks'][:20]:  # Show first 20
                print(f"  - {stock}")
            if len(stats['failed_stocks']) > 20:
                print(f"  ... and {len(stats['failed_stocks']) - 20} more")
        
        print("\n✅ Data saved to:", self.data_dir.absolute())
        print("=" * 60)


def main():
    """Main function."""
    print("\n" + "=" * 60)
    print("🚀 EXPANDED STOCK UNIVERSE DATA FETCHER")
    print("=" * 60)
    
    # Show available universes
    print("\n📊 Available Stock Universes:")
    info = get_universe_info()
    for i, (name, data) in enumerate(info.items(), 1):
        print(f"{i}. {name.upper()}: {data['count']} stocks - {data['description']}")
    
    # User selection
    print("\n" + "=" * 60)
    choice = input("Select universe (1-5) or press Enter for ALL: ").strip()
    
    universe_map = {
        '1': 'nifty50',
        '2': 'nifty200',
        '3': 'nifty500',
        '4': 'smallcap250',
        '5': 'all',
        '': 'all'
    }
    
    universe_type = universe_map.get(choice, 'all')
    stocks = get_stock_universe(universe_type)
    
    print(f"\n✅ Selected: {universe_type.upper()} ({len(stocks)} stocks)")
    
    # Period selection
    print("\n📅 Select data period:")
    print("1. 1 year (faster)")
    print("2. 2 years (recommended)")
    print("3. 5 years (comprehensive)")
    print("4. Max available")
    
    period_choice = input("\nSelect period (1-4) or press Enter for 2 years: ").strip()
    period_map = {
        '1': '1y',
        '2': '2y',
        '3': '5y',
        '4': 'max',
        '': '2y'
    }
    period = period_map.get(period_choice, '2y')
    
    print(f"✅ Selected period: {period}")
    
    # Workers selection
    workers_choice = input("\nMax parallel downloads (1-20, default 10): ").strip()
    try:
        max_workers = int(workers_choice) if workers_choice else 10
        max_workers = max(1, min(20, max_workers))
    except:
        max_workers = 10
    
    print(f"✅ Parallel downloads: {max_workers}")
    
    # Create data directory
    data_dir = f"data/stocks_{universe_type}"
    
    # Confirm
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    print(f"  Universe: {universe_type.upper()}")
    print(f"  Stocks: {len(stocks)}")
    print(f"  Period: {period}")
    print(f"  Workers: {max_workers}")
    print(f"  Save to: {data_dir}")
    print("=" * 60)
    
    confirm = input("\n🚀 Start downloading? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled by user")
        return
    
    # Fetch data
    fetcher = StockDataFetcher(data_dir=data_dir, period=period)
    stats = fetcher.fetch_multiple_stocks(stocks, max_workers=max_workers)
    
    # Print summary
    fetcher.print_summary(stats)
    
    # Save failed stocks list
    if stats['failed_stocks']:
        failed_file = Path(data_dir) / 'failed_stocks.txt'
        with open(failed_file, 'w') as f:
            f.write('\n'.join(stats['failed_stocks']))
        print(f"\n📝 Failed stocks list saved to: {failed_file}")
    
    # Save stats
    stats_file = Path(data_dir) / 'fetch_stats.txt'
    with open(stats_file, 'w') as f:
        f.write(f"Data Fetch Statistics\n")
        f.write(f"=" * 50 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Universe: {universe_type}\n")
        f.write(f"Total Stocks: {stats['total']}\n")
        f.write(f"Successful: {stats['success']}\n")
        f.write(f"Failed: {stats['failed']}\n")
        f.write(f"Time Elapsed: {stats['elapsed_time']:.1f} seconds\n")
        f.write(f"Avg Time/Stock: {stats['avg_time_per_stock']:.2f} seconds\n")
    
    print(f"📊 Statistics saved to: {stats_file}")
    print("\n✅ DATA FETCH COMPLETE!")
    print("\n💡 Next steps:")
    print(f"1. Run training: python train_all_stocks.py --data-dir {data_dir}")
    print(f"2. Run screening: python enhanced_screener.py")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

