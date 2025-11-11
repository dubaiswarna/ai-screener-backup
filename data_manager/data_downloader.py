"""
Data Downloader
Download stock and commodity data from various sources
"""

import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
import time


class DataDownloader:
    """Download market data from Yahoo Finance and other sources"""
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / 'MCX_Data'
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download_mcx_commodity(self, symbol: str, years: int = 25, 
                               interval: str = '1d') -> Dict:
        """
        Download MCX commodity data
        
        Args:
            symbol: Commodity symbol (GOLD, SILVER, CRUDE, etc.)
            years: Number of years of historical data
            interval: Data interval (1d, 1wk, 1mo)
        
        Returns:
            Dict with status and file path
        """
        # Symbol mapping for Yahoo Finance
        symbol_map = {
            'GOLD': 'GC=F',      # Gold Futures
            'SILVER': 'SI=F',    # Silver Futures
            'CRUDE': 'CL=F',     # Crude Oil Futures
            'COPPER': 'HG=F',    # Copper Futures
            'NATURAL_GAS': 'NG=F',  # Natural Gas Futures
            'ZINC': 'ZN=F',      # Zinc (not directly available, using proxy)
            'ALUMINIUM': 'ALI=F', # Aluminium
            'LEAD': 'PB=F'       # Lead
        }
        
        yf_symbol = symbol_map.get(symbol.upper(), f"{symbol}=F")
        
        print(f"[*] Downloading {symbol} data ({years} years)...")
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years*365)
            
            # Download data
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if df.empty:
                return {
                    'success': False,
                    'error': f'No data found for {symbol}'
                }
            
            # Format dataframe
            df_formatted = pd.DataFrame({
                'time': df.index.strftime('%Y-%m-%d'),
                'open': df['Open'],
                'high': df['High'],
                'low': df['Low'],
                'close': df['Close'],
                'volume': df['Volume']
            })
            
            # Add VWAP if available
            if 'Volume' in df.columns and df['Volume'].sum() > 0:
                df_formatted['VWAP'] = ((df['High'] + df['Low'] + df['Close']) / 3 * df['Volume']).cumsum() / df['Volume'].cumsum()
            
            # Save to CSV
            output_file = self.output_dir / f"MCX_{symbol}_{interval}.csv"
            df_formatted.to_csv(output_file, index=False)
            
            print(f"[+] Saved {len(df_formatted)} rows to {output_file.name}")
            
            return {
                'success': True,
                'file': str(output_file),
                'rows': len(df_formatted),
                'start_date': df_formatted['time'].iloc[0],
                'end_date': df_formatted['time'].iloc[-1]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_all_mcx(self, symbols: List[str] = None, years: int = 25) -> Dict:
        """Download data for all MCX commodities"""
        if symbols is None:
            symbols = ['GOLD', 'SILVER', 'CRUDE', 'COPPER', 'NATURAL_GAS']
        
        results = {
            'successful': [],
            'failed': []
        }
        
        for symbol in symbols:
            result = self.download_mcx_commodity(symbol, years=years)
            
            if result['success']:
                results['successful'].append(symbol)
            else:
                results['failed'].append({
                    'symbol': symbol,
                    'error': result.get('error', 'Unknown error')
                })
            
            # Rate limiting
            time.sleep(1)
        
        return results
    
    def update_existing_data(self, file_path: str) -> Dict:
        """Update existing CSV file with latest data"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'success': False,
                'error': 'File not found'
            }
        
        try:
            # Read existing data
            df_existing = pd.read_csv(file_path)
            
            # Get last date
            last_date = pd.to_datetime(df_existing['time'].iloc[-1])
            
            # Check if update is needed
            if last_date.date() >= datetime.now().date():
                return {
                    'success': True,
                    'message': 'Data is already up to date',
                    'rows_added': 0
                }
            
            # Extract symbol from filename
            filename = file_path.stem
            parts = filename.split('_')
            if len(parts) < 2:
                return {
                    'success': False,
                    'error': 'Cannot extract symbol from filename'
                }
            
            symbol = parts[1]
            
            # Download new data
            result = self.download_mcx_commodity(symbol, years=1)
            
            if not result['success']:
                return result
            
            # Read new data
            df_new = pd.read_csv(result['file'])
            
            # Filter only new rows
            df_new_filtered = df_new[pd.to_datetime(df_new['time']) > last_date]
            
            if len(df_new_filtered) > 0:
                # Append new rows
                df_combined = pd.concat([df_existing, df_new_filtered], ignore_index=True)
                df_combined.to_csv(file_path, index=False)
                
                return {
                    'success': True,
                    'message': 'Data updated successfully',
                    'rows_added': len(df_new_filtered)
                }
            else:
                return {
                    'success': True,
                    'message': 'No new data available',
                    'rows_added': 0
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


if __name__ == "__main__":
    downloader = DataDownloader()
    
    print("="*60)
    print("MCX DATA DOWNLOADER")
    print("="*60)
    print()
    
    # Download major commodities
    print("[*] Downloading major commodities...")
    results = downloader.download_all_mcx(['GOLD', 'SILVER'], years=25)
    
    print(f"\n[+] Successful: {len(results['successful'])}")
    for symbol in results['successful']:
        print(f"    - {symbol}")
    
    if results['failed']:
        print(f"\n[-] Failed: {len(results['failed'])}")
        for item in results['failed']:
            print(f"    - {item['symbol']}: {item['error']}")
    
    print("\n" + "="*60)

