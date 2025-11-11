"""
Live Data Downloader for Railway App
Fetches fresh data from Yahoo Finance on-demand
"""

import pandas as pd
import yfinance as yf
from io import BytesIO
from datetime import datetime
from typing import List, Dict
import zipfile


def get_yfinance_symbol(symbol: str) -> str:
    """Convert symbol to Yahoo Finance format"""
    commodity_map = {
        'GOLD': 'GC=F',
        'SILVER': 'SI=F',
    }
    
    if symbol.upper() in commodity_map:
        return commodity_map[symbol.upper()]
    else:
        return f"{symbol}.NS"


def download_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """
    Download stock data from Yahoo Finance
    
    Args:
        symbol: Stock symbol
        period: Time period (1y, 2y, 5y, max)
    
    Returns:
        DataFrame with OHLCV data
    """
    try:
        yf_symbol = get_yfinance_symbol(symbol)
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            return None
        
        # Format to standard structure
        df_formatted = pd.DataFrame({
            'time': df.index.strftime('%Y-%m-%d'),
            'open': df['Open'],
            'high': df['High'],
            'low': df['Low'],
            'close': df['Close'],
            'volume': df['Volume']
        })
        
        return df_formatted
    
    except Exception as e:
        print(f"[!] Error downloading {symbol}: {e}")
        return None


def create_excel_live(symbols: List[str], period: str = "1y") -> Dict:
    """
    Create Excel file with live data from Yahoo Finance
    
    Args:
        symbols: List of stock symbols
        period: Time period
    
    Returns:
        Dict with success status and BytesIO data
    """
    try:
        output = BytesIO()
        sheets_added = 0
        errors = []
        
        print(f"[*] Downloading data for {len(symbols)} symbols...")
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for idx, symbol in enumerate(symbols, 1):
                try:
                    # Download data
                    df = download_stock_data(symbol, period=period)
                    
                    if df is not None and not df.empty:
                        # Create sheet name
                        sheet_name = symbol.replace('-', '_')[:31]
                        
                        # Write to Excel
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        sheets_added += 1
                        
                        if idx % 5 == 0:
                            print(f"[*] Downloaded {idx}/{len(symbols)}...")
                    else:
                        errors.append(f"{symbol}: No data")
                
                except Exception as e:
                    errors.append(f"{symbol}: {str(e)}")
                    continue
        
        output.seek(0)
        
        if sheets_added == 0:
            return {
                'success': False,
                'error': 'Failed to download any stock data'
            }
        
        return {
            'success': True,
            'data': output,
            'sheets_count': sheets_added,
            'errors': errors
        }
    
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': f'Fatal error: {str(e)}\n{traceback.format_exc()}'
        }


def create_zip_live(symbols: List[str], period: str = "1y") -> Dict:
    """
    Create ZIP file with CSV files from live data
    
    Args:
        symbols: List of stock symbols
        period: Time period
    
    Returns:
        Dict with success status and BytesIO data
    """
    try:
        output = BytesIO()
        files_added = 0
        errors = []
        
        print(f"[*] Downloading data for {len(symbols)} symbols...")
        
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for idx, symbol in enumerate(symbols, 1):
                try:
                    # Download data
                    df = download_stock_data(symbol, period=period)
                    
                    if df is not None and not df.empty:
                        # Convert to CSV
                        csv_buffer = BytesIO()
                        df.to_csv(csv_buffer, index=False)
                        csv_buffer.seek(0)
                        
                        # Add to ZIP
                        filename = f"{symbol}.csv"
                        zipf.writestr(filename, csv_buffer.getvalue())
                        files_added += 1
                        
                        if idx % 5 == 0:
                            print(f"[*] Downloaded {idx}/{len(symbols)}...")
                    else:
                        errors.append(f"{symbol}: No data")
                
                except Exception as e:
                    errors.append(f"{symbol}: {str(e)}")
                    continue
            
            # Add metadata
            metadata = {
                'created': datetime.now().isoformat(),
                'period': period,
                'symbols': symbols,
                'files_added': files_added,
                'errors': errors
            }
            import json
            zipf.writestr('metadata.json', json.dumps(metadata, indent=2))
        
        output.seek(0)
        
        if files_added == 0:
            return {
                'success': False,
                'error': 'Failed to download any stock data'
            }
        
        return {
            'success': True,
            'data': output,
            'files_count': files_added,
            'errors': errors
        }
    
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': f'Fatal error: {str(e)}\n{traceback.format_exc()}'
        }


# Stock lists
NIFTY_50 = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR', 'ICICIBANK', 'KOTAKBANK',
    'SBIN', 'BHARTIARTL', 'ITC', 'AXISBANK', 'LT', 'BAJFINANCE', 'ASIANPAINT',
    'MARUTI', 'HCLTECH', 'WIPRO', 'ULTRACEMCO', 'TITAN', 'SUNPHARMA', 'NESTLEIND',
    'POWERGRID', 'NTPC', 'M&M', 'TATAMOTORS', 'ONGC', 'TECHM', 'BAJAJFINSV',
    'ADANIPORTS', 'HINDALCO', 'JSWSTEEL', 'COALINDIA', 'DIVISLAB', 'GRASIM',
    'DRREDDY', 'CIPLA', 'BRITANNIA', 'HEROMOTOCO', 'EICHERMOT', 'APOLLOHOSP',
    'INDUSINDBK', 'SBILIFE', 'TATASTEEL', 'HDFCLIFE', 'SHREECEM', 'BAJAJ-AUTO',
    'UPL', 'BPCL', 'TATACONSUM', 'IOC'
]

MCX_COMMODITIES = ['GOLD', 'SILVER']

ALL_STOCKS = NIFTY_50 + MCX_COMMODITIES

