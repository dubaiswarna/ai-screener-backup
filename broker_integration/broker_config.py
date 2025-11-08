"""
Broker Configuration
====================
Configuration for different broker APIs
"""

import os
from typing import Dict, Any
from enum import Enum

# ============================================================
# SUPPORTED BROKERS
# ============================================================

class BrokerType(Enum):
    """Supported broker types."""
    ZERODHA = "zerodha"
    UPSTOX = "upstox"
    DHAN = "dhan"
    ANGEL = "angel"
    PAPER = "paper"  # Paper trading (simulation)


# ============================================================
# BROKER CONFIGURATIONS
# ============================================================

BROKER_CONFIGS: Dict[str, Dict[str, Any]] = {
    # Zerodha Kite Connect
    'zerodha': {
        'name': 'Zerodha Kite Connect',
        'api_key': os.getenv('ZERODHA_API_KEY', ''),
        'api_secret': os.getenv('ZERODHA_API_SECRET', ''),
        'access_token': os.getenv('ZERODHA_ACCESS_TOKEN', ''),
        'base_url': 'https://api.kite.trade',
        'ws_url': 'wss://ws.kite.trade',
        'cost': '₹2000/month',
        'features': {
            'real_time_data': True,
            'historical_data': True,
            'historical_1min': True,
            'historical_days': 60,
            'order_execution': True,
            'websocket': True
        }
    },
    
    # Upstox API
    'upstox': {
        'name': 'Upstox API',
        'api_key': os.getenv('UPSTOX_API_KEY', ''),
        'api_secret': os.getenv('UPSTOX_API_SECRET', ''),
        'access_token': os.getenv('UPSTOX_ACCESS_TOKEN', ''),
        'base_url': 'https://api.upstox.com/v2',
        'ws_url': 'wss://api.upstox.com/v2/feed/market-data-feed',
        'cost': 'Free with account',
        'features': {
            'real_time_data': True,
            'historical_data': True,
            'historical_1min': True,
            'historical_days': 365,
            'order_execution': True,
            'websocket': True
        }
    },
    
    # Dhan API
    'dhan': {
        'name': 'Dhan API',
        'client_id': os.getenv('DHAN_CLIENT_ID', ''),
        'access_token': os.getenv('DHAN_ACCESS_TOKEN', ''),
        'base_url': 'https://api.dhan.co',
        'ws_url': 'wss://api-feed.dhan.co',
        'cost': 'Free with account',
        'features': {
            'real_time_data': True,
            'historical_data': True,
            'historical_1min': True,
            'historical_days': 365,  # 1 year!
            'order_execution': True,
            'websocket': True
        }
    },
    
    # Angel One (Formerly Angel Broking)
    'angel': {
        'name': 'Angel One SmartAPI',
        'api_key': os.getenv('ANGEL_API_KEY', ''),
        'client_id': os.getenv('ANGEL_CLIENT_ID', ''),
        'password': os.getenv('ANGEL_PASSWORD', ''),
        'base_url': 'https://apiconnect.angelbroking.com',
        'ws_url': 'wss://smartapisocket.angelone.in',
        'cost': 'Free with account',
        'features': {
            'real_time_data': True,
            'historical_data': True,
            'historical_1min': True,
            'historical_days': 90,
            'order_execution': True,
            'websocket': True
        }
    },
    
    # Paper Trading (Simulation)
    'paper': {
        'name': 'Paper Trading (Simulation)',
        'base_url': 'http://localhost:8000/api',
        'cost': 'Free',
        'features': {
            'real_time_data': False,  # Uses delayed data
            'historical_data': True,
            'historical_1min': False,
            'historical_days': 365,
            'order_execution': True,  # Simulated
            'websocket': False
        }
    }
}


# ============================================================
# SYMBOL MAPPING
# ============================================================

# NSE symbol format conversion
SYMBOL_MAPPING = {
    'zerodha': {
        'prefix': 'NSE:',
        'suffix': '',
        'example': 'NSE:RELIANCE'
    },
    'upstox': {
        'prefix': 'NSE_EQ|',
        'suffix': '',
        'example': 'NSE_EQ|RELIANCE'
    },
    'dhan': {
        'prefix': '',
        'suffix': '',
        'example': 'RELIANCE'
    },
    'angel': {
        'prefix': '',
        'suffix': '-EQ',
        'example': 'RELIANCE-EQ'
    }
}


# ============================================================
# RATE LIMITS
# ============================================================

RATE_LIMITS = {
    'zerodha': {
        'requests_per_second': 10,
        'requests_per_minute': 600
    },
    'upstox': {
        'requests_per_second': 10,
        'requests_per_minute': 250
    },
    'dhan': {
        'requests_per_second': 10,
        'requests_per_minute': 500
    },
    'angel': {
        'requests_per_second': 10,
        'requests_per_minute': 300
    }
}


# ============================================================
# EXCHANGE CODES
# ============================================================

EXCHANGE_CODES = {
    'NSE': {
        'zerodha': 'NSE',
        'upstox': 'NSE_EQ',
        'dhan': 'NSE',
        'angel': 'NSE'
    },
    'BSE': {
        'zerodha': 'BSE',
        'upstox': 'BSE_EQ',
        'dhan': 'BSE',
        'angel': 'BSE'
    }
}


# ============================================================
# SETUP INSTRUCTIONS
# ============================================================

SETUP_INSTRUCTIONS = {
    'zerodha': """
# Zerodha Kite Connect Setup
=============================

1. Visit: https://developers.kite.trade/
2. Login with your Zerodha credentials
3. Create a new app
4. Get API Key and Secret
5. Generate access token (valid for 1 day)

## Get Started:
- Cost: ₹2000/month
- Historical Data: 60 days of 1-minute data
- Best for: Active traders, algo trading

## Environment Variables:
```
ZERODHA_API_KEY=your_api_key
ZERODHA_API_SECRET=your_api_secret
ZERODHA_ACCESS_TOKEN=your_access_token
```

## Generate Access Token Daily:
```python
from kiteconnect import KiteConnect

kite = KiteConnect(api_key="your_api_key")
print(kite.login_url())  # Visit this URL, login, copy request_token
access_token = kite.generate_session(request_token, api_secret="your_secret")
print(access_token)  # Save this
```
""",
    
    'upstox': """
# Upstox API Setup
==================

1. Visit: https://upstox.com/developer/api
2. Login with your Upstox credentials
3. Create API app
4. Get API Key and Secret

## Benefits:
- Cost: FREE with trading account
- Historical Data: 1 year of 1-minute data!
- Best for: Cost-conscious traders

## Environment Variables:
```
UPSTOX_API_KEY=your_api_key
UPSTOX_API_SECRET=your_api_secret
UPSTOX_ACCESS_TOKEN=your_access_token
```
""",
    
    'dhan': """
# Dhan API Setup (RECOMMENDED!)
================================

1. Open Dhan trading account: https://dhan.co
2. Go to API section in app
3. Generate API credentials
4. Get Client ID and Access Token

## Benefits:
- Cost: FREE with account
- Historical Data: 1 YEAR of 1-minute data!!
- API Limit: 500 calls/min
- Best for: Backtesting + live trading

## Environment Variables:
```
DHAN_CLIENT_ID=your_client_id
DHAN_ACCESS_TOKEN=your_access_token
```

## Why Dhan? (BEST CHOICE!)
✅ Free API
✅ 1 year historical 1-min data (vs 60 days in Zerodha)
✅ Easy authentication (no daily token generation)
✅ Good rate limits
✅ Modern API design
""",
    
    'angel': """
# Angel One SmartAPI Setup
===========================

1. Open Angel One account
2. Enable SmartAPI in app
3. Get API credentials

## Environment Variables:
```
ANGEL_API_KEY=your_api_key
ANGEL_CLIENT_ID=your_client_id
ANGEL_PASSWORD=your_password
```
"""
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_broker_config(broker: str) -> Dict[str, Any]:
    """Get configuration for specified broker."""
    return BROKER_CONFIGS.get(broker.lower(), {})


def format_symbol(symbol: str, broker: str) -> str:
    """
    Format symbol according to broker requirements.
    
    Args:
        symbol: Base symbol (e.g., 'RELIANCE', 'NSE_RELIANCE')
        broker: Broker name
        
    Returns:
        Formatted symbol for broker
    """
    # Remove any existing prefixes
    clean_symbol = symbol.replace('NSE_', '').replace('NSE:', '').replace('NSE_EQ|', '')
    
    mapping = SYMBOL_MAPPING.get(broker.lower(), {})
    return f"{mapping.get('prefix', '')}{clean_symbol}{mapping.get('suffix', '')}"


def get_recommended_broker() -> str:
    """Get recommended broker based on features and cost."""
    return 'dhan'  # Best combination of features and cost


# ============================================================
# COMPARISON TABLE
# ============================================================

def print_broker_comparison():
    """Print broker comparison table."""
    print("\n" + "="*80)
    print("BROKER API COMPARISON")
    print("="*80)
    print(f"{'Feature':<25} {'Zerodha':<15} {'Upstox':<15} {'Dhan':<15} {'Angel':<15}")
    print("-"*80)
    print(f"{'Cost':<25} {'₹2000/month':<15} {'FREE':<15} {'FREE':<15} {'FREE':<15}")
    print(f"{'Historical 1min Data':<25} {'60 days':<15} {'365 days':<15} {'365 days':<15} {'90 days':<15}")
    print(f"{'Real-time WebSocket':<25} {'✅':<15} {'✅':<15} {'✅':<15} {'✅':<15}")
    print(f"{'Order Execution':<25} {'✅':<15} {'✅':<15} {'✅':<15} {'✅':<15}")
    print(f"{'API Rate Limit':<25} {'600/min':<15} {'250/min':<15} {'500/min':<15} {'300/min':<15}")
    print("="*80)
    print("\n🏆 RECOMMENDED: Dhan (Best features + FREE!)")
    print("   - 1 year historical 1-min data")
    print("   - No cost")
    print("   - Easy setup")
    print("="*80 + "\n")


if __name__ == '__main__':
    print_broker_comparison()
    print("\n📖 Setup Instructions:")
    print(SETUP_INSTRUCTIONS['dhan'])

