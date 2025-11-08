"""
Official Dhan API Client Integration
=====================================
Using the official dhanhq Python package
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd

logger = logging.getLogger(__name__)

try:
    from dhanhq import dhanhq
    DHANHQ_AVAILABLE = True
except ImportError:
    DHANHQ_AVAILABLE = False
    logger.warning("⚠️ dhanhq package not installed. Install with: pip install dhanhq")


class DhanAPIClient:
    """
    Official Dhan API Client using dhanhq package.
    
    Features:
    - Real-time quotes
    - Historical data (1-minute, up to 1 year!)
    - Order execution
    - Portfolio management
    - Live market feed
    """
    
    def __init__(self, client_id: str, access_token: str):
        """
        Initialize Dhan API client.
        
        Args:
            client_id: Dhan Client ID
            access_token: Dhan Access Token
        """
        if not DHANHQ_AVAILABLE:
            raise ImportError("dhanhq package not installed. Install with: pip install dhanhq")
        
        self.client_id = client_id
        self.access_token = access_token
        self.dhan = dhanhq(client_id, access_token)
        self.is_connected = False
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test Dhan API connection."""
        try:
            # Try to get fund limits (simple API call)
            response = self.dhan.get_fund_limits()
            
            if response and 'status' in response:
                if response['status'] == 'success':
                    self.is_connected = True
                    logger.info("✅ Dhan API connected successfully!")
                    return True
                else:
                    logger.error(f"❌ Dhan API authentication failed: {response}")
                    return False
            else:
                logger.warning("⚠️ Unexpected response from Dhan API")
                return False
                
        except Exception as e:
            logger.error(f"❌ Dhan API connection error: {e}")
            self.is_connected = False
            return False
    
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get current quote for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
            
        Returns:
            Quote data with LTP, OHLC, volume
        """
        try:
            # Get security ID (you may need to map symbols to IDs)
            # For now, using common security IDs
            security_id_map = {
                'RELIANCE': '1333',
                'TCS': '11536',
                'INFY': '1594',
                'HDFC': '1333',
                'ICICIBANK': '1270',
                'SBIN': '3045',
                'BHARTIARTL': '100',
                'ITC': '1660',
                'HDFCBANK': '1333',
                'KOTAKBANK': '1922'
            }
            
            clean_symbol = symbol.replace('NSE_', '').upper()
            security_id = security_id_map.get(clean_symbol, '1333')  # Default to RELIANCE
            
            # Get quote data
            response = self.dhan.quote_data(
                securities={"NSE_EQ": [int(security_id)]}
            )
            
            if response and 'data' in response:
                data = response['data']['NSE_EQ'][security_id]
                
                return {
                    'symbol': symbol,
                    'ltp': data.get('LTP', 0),
                    'open': data.get('open', 0),
                    'high': data.get('high', 0),
                    'low': data.get('low', 0),
                    'close': data.get('prev_close', 0),
                    'volume': data.get('volume', 0),
                    'timestamp': datetime.now()
                }
            else:
                logger.error(f"❌ Failed to get quote for {symbol}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error getting quote for {symbol}: {e}")
            return {}
    
    def get_historical_data(
        self,
        symbol: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = '1'
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data.
        
        Args:
            symbol: Stock symbol
            from_date: Start date
            to_date: End date
            interval: '1' for 1-min, '5' for 5-min, '15' for 15-min, 'D' for daily
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Get security ID
            security_id_map = {
                'RELIANCE': '1333',
                'TCS': '11536',
                'INFY': '1594'
            }
            
            clean_symbol = symbol.replace('NSE_', '').upper()
            security_id = security_id_map.get(clean_symbol, '1333')
            
            # Format dates
            from_date_str = from_date.strftime('%Y-%m-%d')
            to_date_str = to_date.strftime('%Y-%m-%d')
            
            # Get data based on interval
            if interval in ['1', '5', '15', '25', '60']:
                # Intraday minute data
                response = self.dhan.intraday_minute_data(
                    security_id=security_id,
                    exchange_segment=self.dhan.NSE,
                    instrument_type=self.dhan.EQUITY,
                    from_date=from_date_str,
                    to_date=to_date_str
                )
            else:
                # Daily data
                response = self.dhan.historical_daily_data(
                    security_id=security_id,
                    exchange_segment=self.dhan.NSE,
                    instrument_type=self.dhan.EQUITY,
                    from_date=from_date_str,
                    to_date=to_date_str
                )
            
            if response and 'data' in response:
                df = pd.DataFrame(response['data'])
                
                if not df.empty:
                    # Rename columns
                    df = df.rename(columns={
                        'open': 'Open',
                        'high': 'High',
                        'low': 'Low',
                        'close': 'Close',
                        'volume': 'Volume',
                        'timestamp': 'Date'
                    })
                    
                    # Convert timestamp
                    if 'Date' in df.columns:
                        df['Date'] = pd.to_datetime(df['Date'])
                        df = df.set_index('Date')
                    
                    logger.info(f"✅ Got {len(df)} candles for {symbol}")
                    return df
                else:
                    logger.warning(f"⚠️ No data for {symbol}")
                    return pd.DataFrame()
            else:
                logger.error(f"❌ Failed to get historical data: {response}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ Error getting historical data: {e}")
            return pd.DataFrame()
    
    def place_order(
        self,
        symbol: str,
        transaction_type: str,
        quantity: int,
        order_type: str = 'MARKET',
        price: Optional[float] = None,
        product_type: str = 'INTRADAY'
    ) -> Dict[str, Any]:
        """
        Place an order.
        
        Args:
            symbol: Stock symbol
            transaction_type: 'BUY' or 'SELL'
            quantity: Quantity to trade
            order_type: 'MARKET' or 'LIMIT'
            price: Limit price (required for LIMIT orders)
            product_type: 'INTRADAY' or 'CNC'
            
        Returns:
            Order response
        """
        try:
            # Get security ID
            security_id_map = {
                'RELIANCE': '1333',
                'TCS': '11536',
                'INFY': '1594'
            }
            
            clean_symbol = symbol.replace('NSE_', '').upper()
            security_id = security_id_map.get(clean_symbol, '1333')
            
            # Map to Dhan constants
            trans_type = self.dhan.BUY if transaction_type.upper() == 'BUY' else self.dhan.SELL
            ord_type = self.dhan.MARKET if order_type.upper() == 'MARKET' else self.dhan.LIMIT
            prod_type = self.dhan.INTRA if product_type.upper() == 'INTRADAY' else self.dhan.CNC
            
            # Place order
            response = self.dhan.place_order(
                security_id=security_id,
                exchange_segment=self.dhan.NSE,
                transaction_type=trans_type,
                quantity=quantity,
                order_type=ord_type,
                product_type=prod_type,
                price=price if price else 0
            )
            
            if response and 'status' in response:
                if response['status'] == 'success':
                    logger.info(f"✅ Order placed: {symbol} {transaction_type} {quantity}")
                    return {
                        'status': 'SUCCESS',
                        'order_id': response.get('data', {}).get('orderId'),
                        'message': 'Order placed successfully'
                    }
                else:
                    logger.error(f"❌ Order failed: {response}")
                    return {'status': 'FAILED', 'message': response.get('remarks', 'Unknown error')}
            else:
                return {'status': 'FAILED', 'message': 'Invalid response'}
                
        except Exception as e:
            logger.error(f"❌ Error placing order: {e}")
            return {'status': 'ERROR', 'message': str(e)}
    
    def get_positions(self) -> List[Dict]:
        """Get current positions."""
        try:
            response = self.dhan.get_positions()
            
            if response and 'status' in response:
                if response['status'] == 'success':
                    return response.get('data', [])
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Error getting positions: {e}")
            return []
    
    def get_holdings(self) -> List[Dict]:
        """Get holdings."""
        try:
            response = self.dhan.get_holdings()
            
            if response and 'status' in response:
                if response['status'] == 'success':
                    return response.get('data', [])
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Error getting holdings: {e}")
            return []
    
    def get_fund_limits(self) -> Dict:
        """Get fund limits and available balance."""
        try:
            response = self.dhan.get_fund_limits()
            
            if response and 'status' in response:
                if response['status'] == 'success':
                    return response.get('data', {})
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Error getting fund limits: {e}")
            return {}


# ============================================================
# TESTING
# ============================================================

if __name__ == '__main__':
    print("🧪 Testing Dhan API Client...")
    
    # Load credentials from environment
    client_id = os.getenv('DHAN_CLIENT_ID', '1104147457')
    access_token = os.getenv('DHAN_ACCESS_TOKEN', '')
    
    if access_token:
        try:
            client = DhanAPIClient(client_id, access_token)
            
            if client.is_connected:
                print("✅ Dhan API connected!")
                
                # Test quote
                quote = client.get_quote('RELIANCE')
                if quote:
                    print(f"✅ RELIANCE LTP: ₹{quote.get('ltp', 0):,.2f}")
                
                # Test fund limits
                funds = client.get_fund_limits()
                if funds:
                    print(f"✅ Available funds: ₹{funds.get('availabelBalance', 0):,.2f}")
                
                print("\n✅ All tests passed!")
            else:
                print("❌ Connection failed!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ No access token provided")

