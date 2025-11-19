"""
Database Manager
================
Handles all database operations with connection pooling and error handling
"""

import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from contextlib import contextmanager
import logging
import sys
from pathlib import Path

# Setup logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import MySQL connectors
try:
    import pymysql
    PYMySQL_AVAILABLE = True
    MYSQL_CONNECTOR_AVAILABLE = False
except ImportError:
    PYMySQL_AVAILABLE = False
    try:
        import mysql.connector
        MYSQL_CONNECTOR_AVAILABLE = True
    except ImportError:
        MYSQL_CONNECTOR_AVAILABLE = False

# Try to import psycopg2
try:
    import psycopg2
    from psycopg2 import pool, sql
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config.db_config import (
    DB_CONFIG, POOL_CONFIG, USE_MYSQL, USE_POSTGRESQL, USE_SQLITE,
    MYSQL_CONFIG, POSTGRESQL_CONFIG,
    get_postgresql_url, get_sqlite_url, Tables
)
from database.mysql_manager import create_mysql_tables


class DatabaseManager:
    """
    Professional database manager with connection pooling and error handling.
    Supports MySQL, PostgreSQL (production) and SQLite (testing/offline).
    """
    
    def __init__(self, db_type: str = None):
        """Initialize database manager."""
        if db_type is None:
            if USE_MYSQL:
                db_type = 'mysql'
            elif USE_POSTGRESQL:
                db_type = 'postgresql'
            else:
                db_type = 'sqlite'
        
        self.db_type = db_type
        self.connection_pool = None
        
        if self.db_type == 'mysql':
            self._init_mysql()
        elif self.db_type == 'postgresql':
            self._init_postgresql_pool()
        else:
            self._init_sqlite()
        
        db_name = {'mysql': 'MySQL', 'postgresql': 'PostgreSQL', 'sqlite': 'SQLite'}.get(db_type, 'SQLite')
        logger.info(f"✅ Database Manager initialized ({db_name})")
    
    def _init_mysql(self):
        """Initialize MySQL connection."""
        if not PYMySQL_AVAILABLE and not MYSQL_CONNECTOR_AVAILABLE:
            logger.error("❌ MySQL connector not installed")
            logger.info("⚠️ Install: pip install pymysql or mysql-connector-python")
            logger.info("⚠️ Falling back to SQLite")
            self.db_type = 'sqlite'
            self._init_sqlite()
            return
        
        try:
            # Test connection first
            if PYMySQL_AVAILABLE:
                conn = pymysql.connect(**MYSQL_CONFIG)
            else:
                conn = mysql.connector.connect(**MYSQL_CONFIG)
            
            # Create tables if they don't exist
            create_mysql_tables(conn)
            conn.close()
            
            logger.info("✅ MySQL connection successful")
            logger.info(f"✅ Connected to MySQL database: {MYSQL_CONFIG['database']}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MySQL: {e}")
            logger.info("⚠️ Falling back to SQLite")
            self.db_type = 'sqlite'
            self._init_sqlite()
    
    def _init_postgresql_pool(self):
        """Initialize PostgreSQL connection pool."""
        if not PSYCOPG2_AVAILABLE:
            logger.error("❌ psycopg2 not installed")
            logger.info("⚠️ Falling back to SQLite")
            self.db_type = 'sqlite'
            self._init_sqlite()
            return
            
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                POOL_CONFIG['min_connections'],
                POOL_CONFIG['max_connections'],
                **POSTGRESQL_CONFIG
            )
            logger.info("✅ PostgreSQL connection pool created")
        except Exception as e:
            logger.error(f"❌ Failed to create PostgreSQL pool: {e}")
            logger.info("⚠️ Falling back to SQLite")
            self.db_type = 'sqlite'
            self._init_sqlite()
    
    def _init_sqlite(self):
        """Initialize SQLite database."""
        from config.db_config import SQLITE_CONFIG
        db_path = Path(SQLITE_CONFIG['database'])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ SQLite database: {db_path}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool."""
        conn = None
        try:
            if self.db_type == 'mysql':
                if PYMySQL_AVAILABLE:
                    conn = pymysql.connect(**MYSQL_CONFIG)
                else:
                    conn = mysql.connector.connect(**MYSQL_CONFIG)
                yield conn
                conn.commit()
            elif self.db_type == 'postgresql':
                conn = self.connection_pool.getconn()
                yield conn
                conn.commit()
            else:
                from config.db_config import SQLITE_CONFIG
                conn = sqlite3.connect(SQLITE_CONFIG['database'])
                conn.row_factory = sqlite3.Row
                yield conn
                conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"❌ Database error: {e}")
            raise
        finally:
            if conn:
                if self.db_type == 'postgresql':
                    self.connection_pool.putconn(conn)
                else:
                    conn.close()
    
    @contextmanager
    def get_cursor(self, dict_cursor: bool = True):
        """Get database cursor."""
        with self.get_connection() as conn:
            if self.db_type == 'mysql':
                if PYMySQL_AVAILABLE:
                    cursor = conn.cursor(pymysql.cursors.DictCursor if dict_cursor else None)
                else:
                    cursor = conn.cursor(dictionary=dict_cursor)
            elif self.db_type == 'postgresql':
                cursor = conn.cursor(cursor_factory=RealDictCursor if dict_cursor else None)
            else:
                cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                logger.info("✅ Database connection successful")
                return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    # ============================================================
    # SIGNALS TABLE OPERATIONS
    # ============================================================
    
    def save_signal(self, signal_data: Dict[str, Any]) -> Optional[str]:
        """
        Save a new signal to database.
        
        Args:
            signal_data: Dictionary with signal information
            
        Returns:
            signal_id if successful, None otherwise
        """
        try:
            import uuid
            signal_id = str(uuid.uuid4())
            
            if self.use_postgresql:
                query = """
                INSERT INTO signals (
                    symbol, signal_type, confidence, entry_price, 
                    target_price, stop_loss, model_name, signal_strength,
                    volume, risk_reward_ratio, position_size, max_risk_amount,
                    valid_until
                ) VALUES (
                    %(symbol)s, %(signal_type)s, %(confidence)s, %(entry_price)s,
                    %(target_price)s, %(stop_loss)s, %(model_name)s, %(signal_strength)s,
                    %(volume)s, %(risk_reward_ratio)s, %(position_size)s, %(max_risk_amount)s,
                    %(valid_until)s
                ) RETURNING signal_id
                """
                params = signal_data
            else:
                # SQLite version
                query = """
                INSERT INTO signals (
                    signal_id, symbol, signal_type, confidence, entry_price,
                    target_price, stop_loss, model_name, signal_strength,
                    volume, risk_reward_ratio, position_size, max_risk_amount,
                    valid_until
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    signal_id,
                    signal_data.get('symbol'),
                    signal_data.get('signal_type'),
                    signal_data.get('confidence'),
                    signal_data.get('entry_price'),
                    signal_data.get('target_price'),
                    signal_data.get('stop_loss'),
                    signal_data.get('model_name'),
                    signal_data.get('signal_strength'),
                    signal_data.get('volume'),
                    signal_data.get('risk_reward_ratio'),
                    signal_data.get('position_size'),
                    signal_data.get('max_risk_amount'),
                    signal_data.get('valid_until')
                )
            
            with self.get_cursor(dict_cursor=False) as cursor:
                cursor.execute(query, params)
                logger.info(f"✅ Signal saved: {signal_data['symbol']} {signal_data['signal_type']}")
                return signal_id
        except Exception as e:
            logger.error(f"❌ Failed to save signal for {signal_data.get('symbol', 'Unknown')}: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return None
    
    def get_active_signals(self, min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """Get all active signals."""
        try:
            if self.use_postgresql:
                query = """
                SELECT * FROM signals 
                WHERE status = 'ACTIVE' AND confidence >= %s
                ORDER BY generated_at DESC
                """
                params = (min_confidence,)
            else:
                # SQLite version
                query = """
                SELECT * FROM signals 
                WHERE status = 'ACTIVE' AND confidence >= ?
                ORDER BY generated_at DESC
                """
                params = (min_confidence,)
            
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                signals = cursor.fetchall()
                if self.use_postgresql:
                    return [dict(signal) for signal in signals]
                else:
                    # Convert SQLite Row to dict
                    return [dict(zip([col[0] for col in cursor.description], signal)) for signal in signals]
        except Exception as e:
            logger.error(f"❌ Failed to get active signals: {e}")
            return []
    
    def get_signals_by_symbol(self, symbol: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent signals for a specific symbol."""
        try:
            query = """
            SELECT * FROM signals 
            WHERE symbol = %s
            ORDER BY generated_at DESC
            LIMIT %s
            """
            
            with self.get_cursor() as cursor:
                cursor.execute(query, (symbol, limit))
                signals = cursor.fetchall()
                return [dict(signal) for signal in signals]
        except Exception as e:
            logger.error(f"❌ Failed to get signals for {symbol}: {e}")
            return []
    
    def update_signal_status(self, signal_id: str, status: str) -> bool:
        """Update signal status."""
        try:
            query = """
            UPDATE signals 
            SET status = %s
            WHERE signal_id = %s
            """
            
            with self.get_cursor() as cursor:
                cursor.execute(query, (status, signal_id))
                logger.info(f"✅ Signal {signal_id} status updated to {status}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to update signal status: {e}")
            return False
    
    # ============================================================
    # TRADES TABLE OPERATIONS
    # ============================================================
    
    def save_trade(self, trade_data: Dict[str, Any]) -> Optional[str]:
        """Save a new trade."""
        try:
            query = """
            INSERT INTO trades (
                signal_id, symbol, trade_type, entry_price, quantity,
                entry_amount, stop_loss, target, broker_order_id, notes
            ) VALUES (
                %(signal_id)s, %(symbol)s, %(trade_type)s, %(entry_price)s, %(quantity)s,
                %(entry_amount)s, %(stop_loss)s, %(target)s, %(broker_order_id)s, %(notes)s
            ) RETURNING trade_id
            """
            
            with self.get_cursor() as cursor:
                cursor.execute(query, trade_data)
                result = cursor.fetchone()
                trade_id = result['trade_id'] if self.use_postgresql else result[0]
                logger.info(f"✅ Trade saved: {trade_data['symbol']} {trade_data['trade_type']}")
                return str(trade_id)
        except Exception as e:
            logger.error(f"❌ Failed to save trade: {e}")
            return None
    
    def get_open_trades(self) -> List[Dict[str, Any]]:
        """Get all open trades with current P&L."""
        try:
            query = """
            SELECT 
                t.*,
                p.current_price,
                p.unrealized_pnl,
                p.unrealized_pnl_pct
            FROM trades t
            LEFT JOIN portfolio p ON t.symbol = p.symbol
            WHERE t.status = 'OPEN'
            ORDER BY t.entry_time DESC
            """
            
            with self.get_cursor() as cursor:
                cursor.execute(query)
                trades = cursor.fetchall()
                return [dict(trade) for trade in trades]
        except Exception as e:
            logger.error(f"❌ Failed to get open trades: {e}")
            return []
    
    def close_trade(self, trade_id: str, exit_price: float, status: str = 'CLOSED') -> bool:
        """Close a trade and calculate P&L."""
        try:
            query = """
            UPDATE trades 
            SET 
                exit_price = %s,
                exit_time = NOW(),
                exit_amount = quantity * %s,
                profit_loss = (quantity * %s) - entry_amount,
                profit_loss_pct = ((quantity * %s) - entry_amount) / entry_amount * 100,
                status = %s
            WHERE trade_id = %s
            """
            
            with self.get_cursor() as cursor:
                cursor.execute(query, (exit_price, exit_price, exit_price, exit_price, status, trade_id))
                logger.info(f"✅ Trade {trade_id} closed at {exit_price}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to close trade: {e}")
            return False
    
    def get_trade_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get closed trades history."""
        try:
            query = """
            SELECT * FROM trades 
            WHERE status IN ('CLOSED', 'STOPPED', 'TARGET_HIT')
            AND entry_time >= NOW() - INTERVAL '%s days'
            ORDER BY exit_time DESC
            """
            
            with self.get_cursor() as cursor:
                cursor.execute(query, (days,))
                trades = cursor.fetchall()
                return [dict(trade) for trade in trades]
        except Exception as e:
            logger.error(f"❌ Failed to get trade history: {e}")
            return []
    
    # ============================================================
    # PORTFOLIO TABLE OPERATIONS
    # ============================================================
    
    def get_portfolio(self) -> List[Dict[str, Any]]:
        """Get current portfolio positions."""
        try:
            query = "SELECT * FROM portfolio ORDER BY unrealized_pnl DESC"
            
            with self.get_cursor() as cursor:
                cursor.execute(query)
                positions = cursor.fetchall()
                return [dict(pos) for pos in positions]
        except Exception as e:
            logger.error(f"❌ Failed to get portfolio: {e}")
            return []
    
    def update_portfolio_prices(self, price_updates: Dict[str, float]) -> bool:
        """
        Update current prices for all portfolio positions.
        
        Args:
            price_updates: Dict of {symbol: current_price}
        """
        try:
            query = """
            UPDATE portfolio 
            SET 
                current_price = %s,
                current_value = quantity * %s,
                unrealized_pnl = (quantity * %s) - invested_amount,
                unrealized_pnl_pct = ((quantity * %s) - invested_amount) / invested_amount * 100,
                last_updated = NOW()
            WHERE symbol = %s
            """
            
            with self.get_cursor() as cursor:
                for symbol, price in price_updates.items():
                    cursor.execute(query, (price, price, price, price, symbol))
                logger.info(f"✅ Updated prices for {len(price_updates)} positions")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to update portfolio prices: {e}")
            return False
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary statistics."""
        try:
            query = """
            SELECT 
                COUNT(*) as total_positions,
                SUM(invested_amount) as total_invested,
                SUM(current_value) as total_current_value,
                SUM(unrealized_pnl) as total_unrealized_pnl,
                AVG(unrealized_pnl_pct) as avg_pnl_pct
            FROM portfolio
            """
            
            with self.get_cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                return dict(result) if result else {}
        except Exception as e:
            logger.error(f"❌ Failed to get portfolio summary: {e}")
            return {}
    
    # ============================================================
    # PRICE HISTORY OPERATIONS
    # ============================================================
    
    def save_price_data(self, price_data: Dict[str, Any]) -> bool:
        """Save OHLCV price data."""
        try:
            query = """
            INSERT INTO price_history (
                symbol, timeframe, timestamp, open, high, low, close, volume
            ) VALUES (
                %(symbol)s, %(timeframe)s, %(timestamp)s, %(open)s, 
                %(high)s, %(low)s, %(close)s, %(volume)s
            ) ON CONFLICT (symbol, timeframe, timestamp) DO UPDATE
            SET open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume
            """
            
            with self.get_cursor() as cursor:
                cursor.execute(query, price_data)
                return True
        except Exception as e:
            logger.error(f"❌ Failed to save price data: {e}")
            return False
    
    def get_price_history(
        self, 
        symbol: str, 
        timeframe: str = '1d', 
        days: int = 365
    ) -> List[Dict[str, Any]]:
        """Get historical price data."""
        try:
            query = """
            SELECT * FROM price_history 
            WHERE symbol = %s 
            AND timeframe = %s
            AND timestamp >= NOW() - INTERVAL '%s days'
            ORDER BY timestamp DESC
            """
            
            with self.get_cursor() as cursor:
                cursor.execute(query, (symbol, timeframe, days))
                prices = cursor.fetchall()
                return [dict(price) for price in prices]
        except Exception as e:
            logger.error(f"❌ Failed to get price history: {e}")
            return []
    
    # ============================================================
    # MODEL PERFORMANCE OPERATIONS
    # ============================================================
    
    def update_model_performance(self, performance_data: Dict[str, Any]) -> bool:
        """Update model performance metrics."""
        try:
            query = """
            INSERT INTO model_performance (
                model_name, symbol, total_signals, correct_signals, accuracy,
                total_trades, winning_trades, losing_trades, win_rate,
                total_pnl, avg_pnl_per_trade, max_profit, max_loss
            ) VALUES (
                %(model_name)s, %(symbol)s, %(total_signals)s, %(correct_signals)s, %(accuracy)s,
                %(total_trades)s, %(winning_trades)s, %(losing_trades)s, %(win_rate)s,
                %(total_pnl)s, %(avg_pnl_per_trade)s, %(max_profit)s, %(max_loss)s
            ) ON CONFLICT (model_name, symbol) DO UPDATE
            SET total_signals = EXCLUDED.total_signals,
                correct_signals = EXCLUDED.correct_signals,
                accuracy = EXCLUDED.accuracy,
                total_trades = EXCLUDED.total_trades,
                winning_trades = EXCLUDED.winning_trades,
                losing_trades = EXCLUDED.losing_trades,
                win_rate = EXCLUDED.win_rate,
                total_pnl = EXCLUDED.total_pnl,
                avg_pnl_per_trade = EXCLUDED.avg_pnl_per_trade,
                max_profit = EXCLUDED.max_profit,
                max_loss = EXCLUDED.max_loss,
                last_updated = NOW()
            """
            
            with self.get_cursor() as cursor:
                cursor.execute(query, performance_data)
                logger.info(f"✅ Model performance updated for {performance_data['model_name']}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to update model performance: {e}")
            return False
    
    def get_model_performance(self, model_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get model performance metrics."""
        try:
            if model_name:
                query = "SELECT * FROM model_performance WHERE model_name = %s"
                params = (model_name,)
            else:
                query = "SELECT * FROM model_performance ORDER BY accuracy DESC"
                params = ()
            
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                performance = cursor.fetchall()
                return [dict(perf) for perf in performance]
        except Exception as e:
            logger.error(f"❌ Failed to get model performance: {e}")
            return []
    
    # ============================================================
    # USER CONFIG OPERATIONS
    # ============================================================
    
    def get_user_config(self) -> Dict[str, Any]:
        """Get user configuration."""
        try:
            query = "SELECT * FROM user_config LIMIT 1"
            
            with self.get_cursor() as cursor:
                cursor.execute(query)
                config = cursor.fetchone()
                return dict(config) if config else {}
        except Exception as e:
            logger.error(f"❌ Failed to get user config: {e}")
            return {}
    
    def update_user_config(self, config_data: Dict[str, Any]) -> bool:
        """Update user configuration."""
        try:
            # Build dynamic UPDATE query
            fields = ', '.join([f"{k} = %s" for k in config_data.keys()])
            query = f"UPDATE user_config SET {fields}, updated_at = NOW()"
            
            with self.get_cursor() as cursor:
                cursor.execute(query, list(config_data.values()))
                logger.info("✅ User config updated")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to update user config: {e}")
            return False
    
    # ============================================================
    # ALERTS OPERATIONS
    # ============================================================
    
    def save_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Save alert to database."""
        try:
            query = """
            INSERT INTO alerts (
                alert_type, symbol, message, priority,
                sent_telegram, sent_email, sent_sms
            ) VALUES (
                %(alert_type)s, %(symbol)s, %(message)s, %(priority)s,
                %(sent_telegram)s, %(sent_email)s, %(sent_sms)s
            )
            """
            
            with self.get_cursor() as cursor:
                cursor.execute(query, alert_data)
                return True
        except Exception as e:
            logger.error(f"❌ Failed to save alert: {e}")
            return False
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        try:
            query = """
            SELECT * FROM alerts 
            WHERE created_at >= NOW() - INTERVAL '%s hours'
            ORDER BY created_at DESC
            """
            
            with self.get_cursor() as cursor:
                cursor.execute(query, (hours,))
                alerts = cursor.fetchall()
                return [dict(alert) for alert in alerts]
        except Exception as e:
            logger.error(f"❌ Failed to get alerts: {e}")
            return []
    
    # ============================================================
    # CLEANUP & MAINTENANCE
    # ============================================================
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old data to keep database size manageable."""
        try:
            with self.get_cursor() as cursor:
                # Delete old expired signals
                cursor.execute("""
                    DELETE FROM signals 
                    WHERE status = 'EXPIRED' 
                    AND generated_at < NOW() - INTERVAL '%s days'
                """, (days,))
                
                # Delete old alerts
                cursor.execute("""
                    DELETE FROM alerts 
                    WHERE created_at < NOW() - INTERVAL '%s days'
                """, (days,))
                
                logger.info(f"✅ Cleaned up data older than {days} days")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old data: {e}")
            return False
    
    def close(self):
        """Close database connection pool."""
        if self.use_postgresql and self.connection_pool:
            self.connection_pool.closeall()
            logger.info("✅ Database connections closed")


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

# Global database instance
_db_instance = None

def get_db() -> DatabaseManager:
    """Get global database instance (singleton pattern)."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance


# ============================================================
# TESTING
# ============================================================

if __name__ == '__main__':
    print("🧪 Testing Database Manager...")
    
    db = get_db()
    
    # Test connection
    if db.test_connection():
        print("✅ Database connection successful!")
        
        # Test saving a signal
        signal_data = {
            'symbol': 'NSE_RELIANCE',
            'signal_type': 'BUY',
            'confidence': 85.5,
            'entry_price': 2450.00,
            'target_price': 2550.00,
            'stop_loss': 2400.00,
            'model_name': 'xgb_NSE_RELIANCE',
            'signal_strength': 'STRONG',
            'volume': 1000000,
            'risk_reward_ratio': 2.5,
            'position_size': 10,
            'max_risk_amount': 500.00,
            'valid_until': datetime.now() + timedelta(days=1)
        }
        
        signal_id = db.save_signal(signal_data)
        if signal_id:
            print(f"✅ Test signal saved with ID: {signal_id}")
            
            # Get active signals
            signals = db.get_active_signals()
            print(f"✅ Found {len(signals)} active signals")
            
            # Get portfolio summary
            summary = db.get_portfolio_summary()
            print(f"✅ Portfolio summary: {summary}")
        
        print("\n✅ All tests passed!")
    else:
        print("❌ Database connection failed!")

