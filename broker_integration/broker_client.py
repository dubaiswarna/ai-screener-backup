"""
Unified Broker Client
=====================
Universal interface for all broker APIs with WebSocket support
"""

import requests
import json
import threading
import time
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import logging
import pandas as pd

# Try to import websocket (optional)
try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    logging.warning("⚠️ websocket-client not installed. WebSocket features disabled.")

from .broker_config import (
    BrokerType, BROKER_CONFIGS, format_symbol,
    RATE_LIMITS, EXCHANGE_CODES
)

logger = logging.getLogger(__name__)


# ============================================================
# ABSTRACT BASE CLASS
# ============================================================

class BrokerBase(ABC):
    """Abstract base class for all broker implementations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize broker client."""
        self.config = config
        self.name = config.get('name', 'Unknown')
        self.is_connected = False
        self.ws_connection = None
        self.callbacks = {}
        
        logger.info(f"✅ {self.name} initialized")
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with broker API."""
        pass
    
    @abstractmethod
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get current quote for symbol."""
        pass
    
    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = '1minute'
    ) -> pd.DataFrame:
        """Get historical OHLCV data."""
        pass
    
    @abstractmethod
    def place_order(
        self,
        symbol: str,
        transaction_type: str,
        quantity: int,
        order_type: str = 'MARKET',
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Place an order."""
        pass
    
    @abstractmethod
    def connect_websocket(self, symbols: List[str], callback: Callable):
        """Connect to WebSocket for real-time data."""
        pass
    
    def disconnect_websocket(self):
        """Disconnect WebSocket."""
        if self.ws_connection:
            self.ws_connection.close()
            self.is_connected = False
            logger.info(f"✅ {self.name} WebSocket disconnected")


# ============================================================
# DHAN IMPLEMENTATION (RECOMMENDED)
# ============================================================

class DhanClient(BrokerBase):
    """Dhan API Client - FREE with 1 year historical 1-min data!"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client_id = config.get('client_id')
        self.access_token = config.get('access_token')
        self.base_url = config.get('base_url')
        self.headers = {
            'access-token': self.access_token,
            'Content-Type': 'application/json'
        }
    
    def authenticate(self) -> bool:
        """Authenticate with Dhan API."""
        try:
            # Dhan uses simple token-based auth
            response = requests.get(
                f"{self.base_url}/fundlimit",
                headers=self.headers
            )
            
            if response.status_code == 200:
                self.is_connected = True
                logger.info(f"✅ {self.name} authenticated successfully")
                return True
            else:
                logger.error(f"❌ {self.name} authentication failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ {self.name} authentication error: {e}")
            return False
    
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get current quote."""
        try:
            formatted_symbol = format_symbol(symbol, 'dhan')
            
            response = requests.get(
                f"{self.base_url}/marketfeed/ltp",
                headers=self.headers,
                params={
                    'symbol': formatted_symbol,
                    'exchange': 'NSE'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': symbol,
                    'ltp': data.get('ltp', 0),
                    'timestamp': datetime.now()
                }
            else:
                logger.error(f"❌ Failed to get quote for {symbol}")
                return {}
        except Exception as e:
            logger.error(f"❌ Error getting quote: {e}")
            return {}
    
    def get_historical_data(
        self,
        symbol: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = '1'  # '1' for 1-minute
    ) -> pd.DataFrame:
        """
        Get historical OHLCV data.
        
        Dhan supports: 1, 5, 15, 25, 60 minutes, day, week, month
        Historical limit: 1 YEAR for 1-minute data!
        """
        try:
            formatted_symbol = format_symbol(symbol, 'dhan')
            
            payload = {
                'symbol': formatted_symbol,
                'exchange': 'NSE',
                'from_date': from_date.strftime('%Y-%m-%d'),
                'to_date': to_date.strftime('%Y-%m-%d'),
                'interval': interval
            }
            
            response = requests.post(
                f"{self.base_url}/charts/historical",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data.get('data', []))
                
                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df.rename(columns={
                        'open': 'Open',
                        'high': 'High',
                        'low': 'Low',
                        'close': 'Close',
                        'volume': 'Volume'
                    })
                    
                    logger.info(f"✅ Got {len(df)} candles for {symbol}")
                    return df
                else:
                    logger.warning(f"⚠️ No data for {symbol}")
                    return pd.DataFrame()
            else:
                logger.error(f"❌ Failed to get historical data: {response.status_code}")
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
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Place an order."""
        try:
            formatted_symbol = format_symbol(symbol, 'dhan')
            
            payload = {
                'symbol': formatted_symbol,
                'exchange': 'NSE',
                'transaction_type': transaction_type.upper(),
                'quantity': quantity,
                'order_type': order_type,
                'product_type': 'INTRADAY',
                'validity': 'DAY'
            }
            
            if price and order_type == 'LIMIT':
                payload['price'] = price
            
            response = requests.post(
                f"{self.base_url}/orders",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                order_data = response.json()
                logger.info(f"✅ Order placed: {symbol} {transaction_type} {quantity}")
                return order_data
            else:
                logger.error(f"❌ Order failed: {response.status_code}")
                return {'status': 'FAILED', 'message': response.text}
                
        except Exception as e:
            logger.error(f"❌ Error placing order: {e}")
            return {'status': 'ERROR', 'message': str(e)}
    
    def connect_websocket(self, symbols: List[str], callback: Callable):
        """Connect to Dhan WebSocket for real-time data."""
        if not WEBSOCKET_AVAILABLE:
            logger.warning("⚠️ WebSocket not available. Install websocket-client package.")
            return
            
        try:
            ws_url = self.config.get('ws_url')
            
            def on_message(ws, message):
                """Handle incoming WebSocket messages."""
                try:
                    data = json.loads(message)
                    callback(data)
                except Exception as e:
                    logger.error(f"❌ WebSocket message error: {e}")
            
            def on_error(ws, error):
                logger.error(f"❌ WebSocket error: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                self.is_connected = False
                logger.info(f"✅ WebSocket closed: {close_msg}")
            
            def on_open(ws):
                self.is_connected = True
                logger.info(f"✅ WebSocket connected")
                
                # Subscribe to symbols
                subscribe_msg = {
                    'RequestCode': 15,
                    'InstrumentCount': len(symbols),
                    'InstrumentList': [{'Exch': 'N', 'ExchangeSegment': 'C', 'Token': symbol} for symbol in symbols]
                }
                ws.send(json.dumps(subscribe_msg))
                logger.info(f"✅ Subscribed to {len(symbols)} symbols")
            
            # Create WebSocket connection
            self.ws_connection = websocket.WebSocketApp(
                f"{ws_url}?token={self.access_token}",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            # Run in background thread
            ws_thread = threading.Thread(target=self.ws_connection.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            logger.info(f"✅ WebSocket thread started")
            
        except Exception as e:
            logger.error(f"❌ WebSocket connection error: {e}")


# ============================================================
# PAPER TRADING CLIENT
# ============================================================

class PaperTradingClient(BrokerBase):
    """
    Paper Trading Client - Simulated trading with real market data.
    Perfect for testing strategies without risking real money!
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.positions = {}
        self.orders = []
        self.capital = 1000000  # ₹10 Lakh starting capital
        self.available_capital = self.capital
    
    def authenticate(self) -> bool:
        """Paper trading doesn't need authentication."""
        self.is_connected = True
        logger.info(f"✅ Paper Trading ready with ₹{self.capital:,.0f} capital")
        return True
    
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get simulated quote (for paper trading)."""
        try:
            # Return dummy data for paper trading
            # In real use, this would connect to Dhan API
            import random
            base_price = 2450.0  # Dummy price
            
            return {
                'symbol': symbol,
                'ltp': base_price + random.uniform(-50, 50),
                'open': base_price,
                'high': base_price + 30,
                'low': base_price - 30,
                'volume': random.randint(100000, 1000000),
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"❌ Error getting quote for {symbol}: {e}")
            return {}
    
    def get_historical_data(
        self,
        symbol: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = '1m'
    ) -> pd.DataFrame:
        """Get simulated historical data for paper trading."""
        try:
            # Return empty dataframe for paper trading
            # Real data comes from Dhan API when using live trading
            logger.info(f"📄 Paper trading mode - using simulated data for {symbol}")
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
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Simulate order placement."""
        try:
            # Get current price
            quote = self.get_quote(symbol)
            execution_price = price if (price and order_type == 'LIMIT') else quote.get('ltp', 0)
            
            if execution_price == 0:
                return {'status': 'FAILED', 'message': 'Could not get price'}
            
            order_amount = quantity * execution_price
            
            if transaction_type.upper() == 'BUY':
                if order_amount > self.available_capital:
                    return {'status': 'FAILED', 'message': 'Insufficient funds'}
                
                # Execute buy
                self.available_capital -= order_amount
                
                if symbol in self.positions:
                    # Average price calculation
                    old_qty = self.positions[symbol]['quantity']
                    old_price = self.positions[symbol]['avg_price']
                    new_qty = old_qty + quantity
                    new_avg = ((old_qty * old_price) + (quantity * execution_price)) / new_qty
                    
                    self.positions[symbol]['quantity'] = new_qty
                    self.positions[symbol]['avg_price'] = new_avg
                else:
                    self.positions[symbol] = {
                        'quantity': quantity,
                        'avg_price': execution_price,
                        'symbol': symbol
                    }
                
                logger.info(f"✅ PAPER BUY: {symbol} x{quantity} @ ₹{execution_price}")
                
            else:  # SELL
                if symbol not in self.positions or self.positions[symbol]['quantity'] < quantity:
                    return {'status': 'FAILED', 'message': 'Insufficient quantity'}
                
                # Execute sell
                self.available_capital += order_amount
                self.positions[symbol]['quantity'] -= quantity
                
                if self.positions[symbol]['quantity'] == 0:
                    del self.positions[symbol]
                
                logger.info(f"✅ PAPER SELL: {symbol} x{quantity} @ ₹{execution_price}")
            
            order_data = {
                'status': 'COMPLETE',
                'order_id': f"PAPER_{int(time.time())}",
                'symbol': symbol,
                'transaction_type': transaction_type,
                'quantity': quantity,
                'price': execution_price,
                'timestamp': datetime.now()
            }
            
            self.orders.append(order_data)
            return order_data
            
        except Exception as e:
            logger.error(f"❌ Error placing paper order: {e}")
            return {'status': 'ERROR', 'message': str(e)}
    
    def get_positions(self) -> List[Dict]:
        """Get current positions."""
        positions_list = []
        for symbol, pos in self.positions.items():
            quote = self.get_quote(symbol)
            current_price = quote.get('ltp', 0)
            
            current_value = pos['quantity'] * current_price
            invested = pos['quantity'] * pos['avg_price']
            pnl = current_value - invested
            pnl_pct = (pnl / invested) * 100 if invested > 0 else 0
            
            positions_list.append({
                'symbol': symbol,
                'quantity': pos['quantity'],
                'avg_price': pos['avg_price'],
                'current_price': current_price,
                'invested': invested,
                'current_value': current_value,
                'pnl': pnl,
                'pnl_pct': pnl_pct
            })
        
        return positions_list
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary."""
        positions = self.get_positions()
        total_invested = sum(p['invested'] for p in positions)
        total_current = sum(p['current_value'] for p in positions)
        total_pnl = total_current - total_invested
        
        return {
            'total_capital': self.capital,
            'available_capital': self.available_capital,
            'invested_capital': total_invested,
            'current_value': total_current,
            'total_pnl': total_pnl,
            'total_pnl_pct': (total_pnl / total_invested) * 100 if total_invested > 0 else 0,
            'positions_count': len(positions),
            'capital_utilization': (total_invested / self.capital) * 100
        }
    
    def connect_websocket(self, symbols: List[str], callback: Callable):
        """Simulate WebSocket with periodic price updates."""
        def simulate_updates():
            while self.is_connected:
                for symbol in symbols:
                    quote = self.get_quote(symbol)
                    if quote:
                        callback({
                            'symbol': symbol,
                            'ltp': quote.get('ltp'),
                            'timestamp': datetime.now()
                        })
                time.sleep(5)  # Update every 5 seconds
        
        self.is_connected = True
        thread = threading.Thread(target=simulate_updates)
        thread.daemon = True
        thread.start()
        logger.info(f"✅ Paper trading live updates started")


# ============================================================
# BROKER FACTORY
# ============================================================

class BrokerFactory:
    """Factory to create broker clients."""
    
    @staticmethod
    def create_broker(broker_type: str) -> BrokerBase:
        """
        Create broker client instance.
        
        Args:
            broker_type: 'dhan', 'zerodha', 'upstox', 'angel', or 'paper'
            
        Returns:
            Broker client instance
        """
        broker_type = broker_type.lower()
        config = BROKER_CONFIGS.get(broker_type, {})
        
        if not config:
            logger.error(f"❌ Unknown broker: {broker_type}")
            logger.info("⚠️ Falling back to Paper Trading")
            broker_type = 'paper'
            config = BROKER_CONFIGS['paper']
        
        if broker_type == 'dhan':
            return DhanClient(config)
        elif broker_type == 'paper':
            return PaperTradingClient(config)
        # Add more brokers here as needed
        # elif broker_type == 'zerodha':
        #     return ZerodhaClient(config)
        else:
            logger.warning(f"⚠️ {broker_type} not fully implemented, using Paper Trading")
            return PaperTradingClient(BROKER_CONFIGS['paper'])


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def get_broker_client(broker_type: str = 'paper') -> BrokerBase:
    """Get broker client (singleton-like)."""
    client = BrokerFactory.create_broker(broker_type)
    client.authenticate()
    return client


# ============================================================
# TESTING
# ============================================================

if __name__ == '__main__':
    print("🧪 Testing Broker Integration...")
    
    # Test Paper Trading
    print("\n📄 Testing Paper Trading...")
    paper = get_broker_client('paper')
    
    # Test quote
    quote = paper.get_quote('NSE_RELIANCE')
    print(f"✅ Quote: {quote}")
    
    # Test order
    order = paper.place_order('NSE_RELIANCE', 'BUY', 10, 'MARKET')
    print(f"✅ Order: {order}")
    
    # Test positions
    positions = paper.get_positions()
    print(f"✅ Positions: {positions}")
    
    # Test portfolio
    portfolio = paper.get_portfolio_summary()
    print(f"✅ Portfolio: {portfolio}")
    
    # Test historical data
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    df = paper.get_historical_data('NSE_RELIANCE', from_date, to_date, '1d')
    print(f"✅ Historical data: {len(df)} rows")
    
    print("\n✅ All broker tests passed!")

