"""
MySQL Database Manager
======================
MySQL-specific database operations
"""

import logging
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Try to import MySQL connector
try:
    import pymysql
    PYMySQL_AVAILABLE = True
except ImportError:
    try:
        import mysql.connector
        MYSQL_CONNECTOR_AVAILABLE = True
        PYMySQL_AVAILABLE = False
    except ImportError:
        PYMySQL_AVAILABLE = False
        MYSQL_CONNECTOR_AVAILABLE = False
        logger.warning("⚠️ MySQL connector not available. Install: pip install pymysql or mysql-connector-python")


def create_mysql_tables(connection):
    """Create all required tables in MySQL database."""
    # Detect which MySQL connector is being used
    connector_type = type(connection).__module__
    is_pymysql = 'pymysql' in connector_type
    
    cursor = connection.cursor()
    
    try:
        # Create signals table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            signal_id VARCHAR(100) PRIMARY KEY,
            symbol VARCHAR(50) NOT NULL,
            signal_type VARCHAR(10) NOT NULL,
            confidence DECIMAL(5,2) NOT NULL,
            entry_price DECIMAL(15,2) NOT NULL,
            target_price DECIMAL(15,2),
            stop_loss DECIMAL(15,2),
            model_name VARCHAR(100),
            signal_strength VARCHAR(20),
            volume BIGINT,
            risk_reward_ratio DECIMAL(5,2),
            position_size DECIMAL(15,2),
            max_risk_amount DECIMAL(15,2),
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            valid_until TIMESTAMP NULL,
            status VARCHAR(20) DEFAULT 'ACTIVE',
            INDEX idx_symbol (symbol),
            INDEX idx_status (status),
            INDEX idx_generated_at (generated_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Create portfolio table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            position_id VARCHAR(100) PRIMARY KEY,
            trade_id VARCHAR(100),
            symbol VARCHAR(50) NOT NULL UNIQUE,
            quantity INT NOT NULL,
            avg_price DECIMAL(15,2) NOT NULL,
            current_price DECIMAL(15,2),
            invested_amount DECIMAL(15,2) NOT NULL,
            current_value DECIMAL(15,2),
            unrealized_pnl DECIMAL(15,2),
            unrealized_pnl_pct DECIMAL(5,2),
            stop_loss DECIMAL(15,2),
            target DECIMAL(15,2),
            risk_amount DECIMAL(15,2),
            opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_symbol (symbol)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Create trades table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            trade_id VARCHAR(100) PRIMARY KEY,
            signal_id VARCHAR(100),
            symbol VARCHAR(50) NOT NULL,
            trade_type VARCHAR(10) NOT NULL,
            entry_price DECIMAL(15,2) NOT NULL,
            entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            quantity INT NOT NULL,
            entry_amount DECIMAL(15,2) NOT NULL,
            exit_price DECIMAL(15,2),
            exit_time TIMESTAMP NULL,
            exit_amount DECIMAL(15,2),
            profit_loss DECIMAL(15,2),
            profit_loss_pct DECIMAL(5,2),
            stop_loss DECIMAL(15,2),
            target DECIMAL(15,2),
            trailing_stop DECIMAL(15,2),
            status VARCHAR(20) DEFAULT 'OPEN',
            broker_order_id VARCHAR(100),
            commission DECIMAL(15,2) DEFAULT 0,
            notes TEXT,
            INDEX idx_symbol (symbol),
            INDEX idx_status (status),
            INDEX idx_entry_time (entry_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Create user_config table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_config (
            config_id VARCHAR(50) PRIMARY KEY,
            max_risk_per_trade DECIMAL(5,2) DEFAULT 2.0,
            max_portfolio_risk DECIMAL(5,2) DEFAULT 10.0,
            max_positions INT DEFAULT 10,
            max_correlation DECIMAL(3,2) DEFAULT 0.7,
            min_confidence DECIMAL(5,2) DEFAULT 70.0,
            min_risk_reward DECIMAL(3,2) DEFAULT 1.5,
            total_capital DECIMAL(15,2) NOT NULL,
            reserve_cash_pct DECIMAL(5,2) DEFAULT 10.0,
            telegram_enabled TINYINT(1) DEFAULT 1,
            alert_min_confidence DECIMAL(5,2) DEFAULT 75.0,
            use_ensemble TINYINT(1) DEFAULT 1,
            retrain_frequency_days INT DEFAULT 30,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Insert default config if not exists
        cursor.execute('''
        INSERT IGNORE INTO user_config (config_id, total_capital)
        VALUES ('default', 1000000)
        ''')
        
        connection.commit()
        logger.info("✅ MySQL tables created successfully")
        
    except Exception as e:
        connection.rollback()
        logger.error(f"❌ Error creating MySQL tables: {e}")
        # Don't raise on Railway - allow retry
        if not os.getenv('RAILWAY_ENVIRONMENT'):
            raise
    finally:
        cursor.close()

