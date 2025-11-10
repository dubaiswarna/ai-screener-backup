"""
Update System Configuration for Expanded Universe
==================================================
Updates database and configuration to handle Nifty 500 + Smallcap 250

Features:
- Updates database schema if needed
- Adds new stock symbols
- Updates configuration files
- Creates batch processing support

Author: AI Screener v3.0
Date: November 2025
"""

import os
import sys
import sqlite3
from pathlib import Path
import logging

# Add config to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.stock_universe import ALL_STOCKS, get_universe_info

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemUpdater:
    """Updates system for expanded stock universe."""
    
    def __init__(self, db_path: str = 'data/ai_screener.db'):
        """Initialize updater."""
        self.db_path = db_path
        self.conn = None
        
    def connect_db(self):
        """Connect to database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            logger.info(f"✅ Connected to database: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def create_stock_universe_table(self):
        """Create stock universe table."""
        if not self.conn:
            return False
            
        try:
            cursor = self.conn.cursor()
            
            # Create table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_universe (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL,
                    name TEXT,
                    universe TEXT,
                    sector TEXT,
                    industry TEXT,
                    market_cap TEXT,
                    is_active INTEGER DEFAULT 1,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_symbol 
                ON stock_universe(symbol)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_universe 
                ON stock_universe(universe)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_active 
                ON stock_universe(is_active)
            ''')
            
            self.conn.commit()
            logger.info("✅ Stock universe table created/verified")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating table: {e}")
            return False
    
    def populate_stock_universe(self):
        """Populate stock universe with symbols."""
        if not self.conn:
            return False
            
        try:
            cursor = self.conn.cursor()
            
            # Get universe info
            from config.stock_universe import NIFTY_50, NIFTY_200, NIFTY_500, SMALLCAP_250
            
            # Insert stocks
            inserted = 0
            updated = 0
            
            for symbol in ALL_STOCKS:
                # Determine universe
                if symbol in NIFTY_50:
                    universe = 'NIFTY50'
                elif symbol in NIFTY_200:
                    universe = 'NIFTY200'
                elif symbol in NIFTY_500:
                    universe = 'NIFTY500'
                elif symbol in SMALLCAP_250:
                    universe = 'SMALLCAP250'
                else:
                    universe = 'OTHER'
                
                # Insert or update
                cursor.execute('''
                    INSERT INTO stock_universe (symbol, universe, is_active)
                    VALUES (?, ?, 1)
                    ON CONFLICT(symbol) DO UPDATE SET
                        universe = excluded.universe,
                        is_active = 1,
                        last_updated = CURRENT_TIMESTAMP
                ''', (symbol, universe))
                
                if cursor.rowcount > 0:
                    if cursor.lastrowid:
                        inserted += 1
                    else:
                        updated += 1
            
            self.conn.commit()
            
            # Get total count
            cursor.execute('SELECT COUNT(*) FROM stock_universe WHERE is_active = 1')
            total = cursor.fetchone()[0]
            
            logger.info(f"✅ Stock universe populated:")
            logger.info(f"   - Inserted: {inserted}")
            logger.info(f"   - Updated: {updated}")
            logger.info(f"   - Total active: {total}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error populating stock universe: {e}")
            return False
    
    def update_config_file(self):
        """Update configuration file."""
        try:
            config_content = f'''# AI Screener Configuration - Updated for Expanded Universe
# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# Stock Universe Settings
STOCK_UNIVERSE = "all"  # Options: nifty50, nifty200, nifty500, smallcap250, all
MAX_STOCKS_PER_BATCH = 50  # Process stocks in batches for performance
ENABLE_BATCH_PROCESSING = True

# Data Settings
DATA_PERIOD = "2y"  # How much historical data to use
MIN_DATA_POINTS = 200  # Minimum data points required

# Screening Settings
MIN_CONFIDENCE = 70  # Minimum confidence for signals (70%)
MAX_SIGNALS_TO_SHOW = 50  # Maximum signals to show in dashboard
ENABLE_PARALLEL_PROCESSING = True
MAX_WORKERS = 10  # Number of parallel workers

# Model Settings
USE_ENSEMBLE = True
LSTM_WEIGHT = 0.7
XGBOOST_WEIGHT = 0.3

# Risk Management
MAX_RISK_PER_TRADE = 0.02  # 2%
PROFIT_TARGET = 0.03  # 3%
STOP_LOSS = 0.015  # 1.5%

# Performance Optimization
CACHE_ENABLED = True
CACHE_DURATION = 300  # 5 minutes in seconds
DATABASE_POOL_SIZE = 10

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "screener.log"
'''
            
            config_path = Path('config/screener_config.py')
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            logger.info(f"✅ Configuration file updated: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating config: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("✅ Database connection closed")


def main():
    """Main update function."""
    print("\n" + "=" * 60)
    print("🔧 SYSTEM UPDATE FOR EXPANDED UNIVERSE")
    print("=" * 60)
    
    # Show what will be updated
    info = get_universe_info()
    print("\n📊 New Stock Universe Coverage:")
    for name, data in info.items():
        print(f"  {name.upper()}: {data['count']} stocks")
    
    print(f"\n✅ Total unique stocks: {len(ALL_STOCKS)}")
    
    print("\n" + "=" * 60)
    print("This will update:")
    print("  1. Database schema")
    print("  2. Stock universe table")
    print("  3. Configuration files")
    print("  4. System settings")
    print("=" * 60)
    
    confirm = input("\n🚀 Proceed with update? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Update cancelled")
        return
    
    # Initialize updater
    updater = SystemUpdater()
    
    # Connect to database
    print("\n📊 Connecting to database...")
    if not updater.connect_db():
        print("❌ Failed to connect to database")
        return
    
    # Create/update tables
    print("\n🔧 Creating/updating tables...")
    if not updater.create_stock_universe_table():
        print("❌ Failed to create tables")
        updater.close()
        return
    
    # Populate stock universe
    print("\n📥 Populating stock universe...")
    if not updater.populate_stock_universe():
        print("❌ Failed to populate stock universe")
        updater.close()
        return
    
    # Update config
    print("\n⚙️ Updating configuration...")
    from datetime import datetime
    if not updater.update_config_file():
        print("❌ Failed to update configuration")
    
    # Close connection
    updater.close()
    
    print("\n" + "=" * 60)
    print("✅ SYSTEM UPDATE COMPLETE!")
    print("=" * 60)
    
    print("\n💡 Next steps:")
    print("1. Run: FETCH_EXPANDED_DATA.bat")
    print("2. Wait for data download to complete")
    print("3. Train models on new data")
    print("4. Start using expanded screener!")
    
    print("\n📊 You now have access to:")
    print(f"  ✅ Nifty 50: {info['nifty50']['count']} stocks")
    print(f"  ✅ Nifty 200: {info['nifty200']['count']} stocks")
    print(f"  ✅ Nifty 500: {info['nifty500']['count']} stocks")
    print(f"  ✅ Smallcap 250: {info['smallcap250']['count']} stocks")
    print(f"  ✅ Total: {len(ALL_STOCKS)} unique stocks!")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"❌ Update failed: {e}")
        sys.exit(1)

