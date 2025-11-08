"""
Excel Master Data Loader
=========================
Loads data from your Nifty200_MASTER_10yeardata.xlsx
Much faster than 169 separate CSV files!
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import warnings
warnings.filterwarnings('ignore')


class ExcelDataLoader:
    """Load stock data from master Excel file."""
    
    def __init__(self, excel_path: str = "../../Nifty200_MASTER_10yeardata.xlsx"):
        """
        Initialize Excel data loader.
        
        Args:
            excel_path: Path to master Excel file
        """
        self.excel_path = Path(excel_path)
        
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.excel_path}")
        
        # Load Excel file
        self.excel_file = pd.ExcelFile(self.excel_path)
        self.sheet_names = self.excel_file.sheet_names
        
        print(f"✅ Loaded Excel with {len(self.sheet_names)} sheets")
    
    def get_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Get data for a specific stock.
        
        Args:
            symbol: Stock symbol (e.g., 'NSE_RELIANCE' or 'RELIANCE')
            
        Returns:
            DataFrame with OHLCV data
        """
        # First, try reading from combined sheet (All_Data, etc.)
        try:
            # Check common combined sheet names
            for sheet in ['All_Data', 'AllData', 'Data', 'Nifty200', self.sheet_names[0]]:
                if sheet in self.sheet_names:
                    df = pd.read_excel(self.excel_path, sheet_name=sheet)
                    
                    # Standardize column names
                    df.columns = df.columns.str.lower()
                    
                    # Filter by symbol
                    symbol_col = None
                    for col in df.columns:
                        if 'symbol' in col.lower() or 'stock' in col.lower():
                            symbol_col = col
                            break
                    
                    if symbol_col:
                        clean_symbol = symbol.replace('NSE_', '')
                        # Try exact match first
                        df_filtered = df[df[symbol_col].str.upper() == clean_symbol.upper()]
                        
                        # If no exact match, try contains
                        if df_filtered.empty:
                            df_filtered = df[df[symbol_col].str.contains(clean_symbol, case=False, na=False)]
                        
                        if not df_filtered.empty:
                            # Ensure required columns exist
                            required = ['open', 'high', 'low', 'close']
                            if all(col in df_filtered.columns for col in required):
                                return df_filtered.copy()
        except Exception as e:
            print(f"Error reading from combined sheet: {e}")
        
        # Fallback: Try separate sheets
        possible_names = [
            symbol,
            symbol.replace('NSE_', ''),
            f"{symbol}_1D",
            symbol.replace('NSE_', '') + '_1D'
        ]
        
        for sheet_name in possible_names:
            if sheet_name in self.sheet_names:
                try:
                    df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
                    
                    # Standardize column names
                    df.columns = df.columns.str.lower()
                    
                    # Ensure required columns exist
                    required = ['open', 'high', 'low', 'close']
                    if all(col in df.columns for col in required):
                        return df
                    
                except Exception as e:
                    print(f"Error reading {sheet_name}: {e}")
                    continue
        
        return None
    
    def get_all_available_stocks(self) -> list:
        """Get list of all available stock symbols."""
        # First, try to get from combined sheet
        try:
            for sheet in ['All_Data', 'AllData', 'Data', 'Nifty200', self.sheet_names[0]]:
                if sheet in self.sheet_names:
                    df = pd.read_excel(self.excel_path, sheet_name=sheet)
                    
                    # Find symbol column
                    symbol_col = None
                    for col in df.columns:
                        if 'symbol' in col.lower() or 'stock' in col.lower():
                            symbol_col = col
                            break
                    
                    if symbol_col:
                        # Get unique symbols and add NSE_ prefix if not present
                        symbols = df[symbol_col].unique().tolist()
                        stocks = []
                        for sym in symbols:
                            sym_str = str(sym).strip()
                            if sym_str and sym_str != 'nan':
                                if not sym_str.startswith('NSE_'):
                                    stocks.append(f'NSE_{sym_str}')
                                else:
                                    stocks.append(sym_str)
                        return sorted(stocks)
        except Exception as e:
            print(f"Error getting stocks from combined sheet: {e}")
        
        # Fallback: Assume each sheet is a stock
        stocks = []
        for sheet in self.sheet_names:
            if '_1D' in sheet or len(sheet) < 20:  # Likely a stock symbol
                stocks.append(sheet.replace('_1D', ''))
        return sorted(stocks)
    
    def get_latest_price(self, symbol: str) -> float:
        """
        Get latest close price for a stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Latest close price
        """
        df = self.get_stock_data(symbol)
        
        if df is not None and not df.empty:
            if 'close' in df.columns:
                return float(df['close'].iloc[-1])
        
        return 0.0
    
    def get_latest_date(self, symbol: str) -> str:
        """Get latest date in data."""
        df = self.get_stock_data(symbol)
        
        if df is not None and not df.empty:
            date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols:
                return str(df[date_cols[0]].iloc[-1])
        
        return "Unknown"


# ============================================================
# TESTING
# ============================================================

if __name__ == '__main__':
    print("🧪 Testing Excel Data Loader...")
    
    try:
        loader = ExcelDataLoader("../Nifty200_MASTER_10yeardata.xlsx")
        
        print(f"\n✅ Total sheets: {len(loader.sheet_names)}")
        print(f"First 10 sheets: {loader.sheet_names[:10]}")
        
        # Test loading a stock
        test_symbol = 'NSE_RELIANCE'
        df = loader.get_stock_data(test_symbol)
        
        if df is not None:
            print(f"\n✅ {test_symbol} data loaded:")
            print(f"   Rows: {len(df)}")
            print(f"   Columns: {df.columns.tolist()}")
            print(f"   Latest close: ₹{loader.get_latest_price(test_symbol):,.2f}")
            print(f"   Latest date: {loader.get_latest_date(test_symbol)}")
        else:
            print(f"\n⚠️ Could not load {test_symbol}")
        
        print("\n✅ Excel loader test complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

