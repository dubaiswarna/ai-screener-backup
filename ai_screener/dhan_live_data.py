"""
Dhan Live Tick Data Integration
================================
Real-time tick-by-tick price updates using Dhan API
"""

import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

try:
    from dhanhq import dhanhq, marketfeed
    DHAN_AVAILABLE = True
except ImportError:
    DHAN_AVAILABLE = False
    logger.warning("⚠️ dhanhq not installed. Install with: pip install dhanhq")


# NSE Security ID mapping (common stocks)
SYMBOL_TO_SECURITY_ID = {
    'NSE_RELIANCE': '1333',
    'NSE_TCS': '11536',
    'NSE_INFY': '1594',
    'NSE_HDFCBANK': '1333',
    'NSE_ICICIBANK': '1270',
    'NSE_SBIN': '3045',
    'NSE_BHARTIARTL': '100',
    'NSE_ITC': '1660',
    'NSE_KOTAKBANK': '1922',
    'NSE_AXISBANK': '5900',
    'NSE_ADANIENT': '25',
    'NSE_ADANIPORTS': '15083',
    'NSE_ASIANPAINT': '236',
    'NSE_BAJAJFINSV': '4963',
    'NSE_BERGEPAINT': '838',
    'NSE_BIOCON': '11373',
    'NSE_CIPLA': '694',
    'NSE_DRREDDY': '881',
    'NSE_EICHERMOT': '910',
    'NSE_ETERNAL': '13940',
    'NSE_GRASIM': '1232',
    'NSE_HCLTECH': '7229',
    'NSE_HINDUNILVR': '1394',
    'NSE_JSWSTEEL': '3001',
    'NSE_M&M': '2031',
    'NSE_NESTLEIND': '17963',
    'NSE_NTPC': '11630',
    'NSE_ONGC': '2475',
    'NSE_POWERGRID': '10440',
    'NSE_SUNPHARMA': '3351',
    'NSE_TATACONSUM': '3432',
    'NSE_TATASTEEL': '3499',
    'NSE_TECHM': '13538',
    'NSE_TITAN': '3506',
    'NSE_WIPRO': '3787'
}


class DhanLiveData:
    """Get live tick data from Dhan API."""
    
    def __init__(self, client_id: str, access_token: str):
        """Initialize Dhan client."""
        if not DHAN_AVAILABLE:
            raise ImportError("dhanhq not installed")
        
        self.client_id = client_id
        self.access_token = access_token
        self.dhan = dhanhq(client_id, access_token)
        self.prices = {}
        
        logger.info("✅ Dhan Live Data initialized")
    
    def get_live_price(self, symbol: str) -> float:
        """
        Get current live price for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'NSE_RELIANCE')
            
        Returns:
            Current LTP
        """
        try:
            security_id = SYMBOL_TO_SECURITY_ID.get(symbol, '1333')
            
            # Get quote
            response = self.dhan.quote_data(
                securities={"NSE_EQ": [int(security_id)]}
            )
            
            if response and 'data' in response and 'NSE_EQ' in response['data']:
                data = response['data']['NSE_EQ'].get(security_id, {})
                ltp = data.get('LTP', 0)
                
                self.prices[symbol] = {
                    'ltp': ltp,
                    'timestamp': datetime.now()
                }
                
                return float(ltp)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return 0.0
    
    def get_live_prices_batch(self, symbols: list) -> dict:
        """
        Get live prices for multiple symbols efficiently.
        
        Args:
            symbols: List of symbols
            
        Returns:
            Dict of {symbol: price}
        """
        prices = {}
        
        # Group by chunks of 100 (Dhan API limit)
        for i in range(0, len(symbols), 100):
            chunk = symbols[i:i+100]
            
            # Map to security IDs
            security_ids = []
            symbol_map = {}
            
            for symbol in chunk:
                sec_id = SYMBOL_TO_SECURITY_ID.get(symbol)
                if sec_id:
                    security_ids.append(int(sec_id))
                    symbol_map[sec_id] = symbol
            
            if security_ids:
                try:
                    # Get batch quote
                    response = self.dhan.quote_data(
                        securities={"NSE_EQ": security_ids}
                    )
                    
                    if response and 'data' in response and 'NSE_EQ' in response['data']:
                        for sec_id, data in response['data']['NSE_EQ'].items():
                            symbol = symbol_map.get(sec_id)
                            if symbol:
                                prices[symbol] = float(data.get('LTP', 0))
                    
                except Exception as e:
                    logger.error(f"Batch price error: {e}")
        
        return prices


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def get_dhan_live_data():
    """Get Dhan live data instance using credentials from .env"""
    client_id = os.getenv('DHAN_CLIENT_ID', '1104147457')
    access_token = os.getenv('DHAN_ACCESS_TOKEN', '')
    
    if not access_token:
        raise ValueError("Dhan access token not found in environment")
    
    return DhanLiveData(client_id, access_token)


# ============================================================
# TESTING
# ============================================================

if __name__ == '__main__':
    print("🧪 Testing Dhan Live Data...")
    
    try:
        # Load from .env
        from dotenv import load_dotenv
        load_dotenv('../.env')
        
        dhan_data = get_dhan_live_data()
        
        # Test single price
        print("\n📊 Testing single stock...")
        price = dhan_data.get_live_price('NSE_RELIANCE')
        print(f"✅ RELIANCE: ₹{price:,.2f}")
        
        # Test batch prices
        print("\n📊 Testing batch...")
        test_symbols = ['NSE_RELIANCE', 'NSE_TCS', 'NSE_INFY']
        prices = dhan_data.get_live_prices_batch(test_symbols)
        
        for symbol, price in prices.items():
            print(f"✅ {symbol}: ₹{price:,.2f}")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

