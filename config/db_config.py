"""
Database Configuration
======================
MySQL/PostgreSQL connection configuration and settings
"""

import os
from typing import Dict, Any

# ============================================================
# DATABASE TYPE CONFIGURATION
# ============================================================

# Database type: 'mysql', 'postgresql', or 'sqlite'
DB_TYPE = os.getenv('DB_TYPE', 'mysql').lower()

# ============================================================
# MYSQL CONFIGURATION
# ============================================================

# MySQL connection parameters
# Railway MySQL uses: MYSQLHOST, MYSQLPORT, MYSQLUSER, MYSQLPASSWORD, MYSQLDATABASE
# Local MySQL uses: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
MYSQL_CONFIG: Dict[str, Any] = {
    'host': os.getenv('MYSQLHOST') or os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('MYSQLPORT') or os.getenv('DB_PORT', 3306)),
    'database': os.getenv('MYSQLDATABASE') or os.getenv('DB_NAME', 'ai_screenr_db'),
    'user': os.getenv('MYSQLUSER') or os.getenv('DB_USER', 'root'),
    'password': os.getenv('MYSQLPASSWORD') or os.getenv('DB_PASSWORD', 'TradingDB@2025!Secure'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': False,
}

# ============================================================
# POSTGRESQL CONFIGURATION (Legacy)
# ============================================================

# PostgreSQL connection parameters
POSTGRESQL_CONFIG: Dict[str, Any] = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'ai_screener_pro'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'your_password_here'),
}

# Use MySQL config by default, fallback to PostgreSQL config for compatibility
DB_CONFIG = MYSQL_CONFIG if DB_TYPE == 'mysql' else POSTGRESQL_CONFIG

# Connection pool settings
POOL_CONFIG: Dict[str, Any] = {
    'min_connections': 2,
    'max_connections': 10,
    'max_idle': 300,  # 5 minutes
    'max_lifetime': 3600,  # 1 hour
}

# SQLite fallback (for testing/offline mode)
SQLITE_CONFIG: Dict[str, str] = {
    'database': 'data/ai_screener.db',
}

# Database selection
USE_MYSQL = DB_TYPE == 'mysql'
USE_POSTGRESQL = DB_TYPE == 'postgresql'
USE_SQLITE = DB_TYPE == 'sqlite' or (not USE_MYSQL and not USE_POSTGRESQL)

# ============================================================
# CONNECTION STRING BUILDERS
# ============================================================

def get_mysql_url() -> str:
    """Get MySQL connection URL."""
    return (
        f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}"
        f"@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}"
        f"?charset={MYSQL_CONFIG['charset']}"
    )

def get_postgresql_url() -> str:
    """Get PostgreSQL connection URL."""
    return (
        f"postgresql://{POSTGRESQL_CONFIG['user']}:{POSTGRESQL_CONFIG['password']}"
        f"@{POSTGRESQL_CONFIG['host']}:{POSTGRESQL_CONFIG['port']}/{POSTGRESQL_CONFIG['database']}"
    )

def get_sqlite_url() -> str:
    """Get SQLite connection URL."""
    return f"sqlite:///{SQLITE_CONFIG['database']}"

def get_database_url() -> str:
    """Get appropriate database URL based on configuration."""
    if USE_MYSQL:
        return get_mysql_url()
    elif USE_POSTGRESQL:
        return get_postgresql_url()
    else:
        return get_sqlite_url()

# ============================================================
# TABLE NAMES (for easy reference)
# ============================================================

class Tables:
    """Database table names."""
    SIGNALS = 'signals'
    TRADES = 'trades'
    PORTFOLIO = 'portfolio'
    PRICE_HISTORY = 'price_history'
    MODEL_PERFORMANCE = 'model_performance'
    RISK_METRICS = 'risk_metrics'
    ALERTS = 'alerts'
    USER_CONFIG = 'user_config'
    BACKTEST_RESULTS = 'backtest_results'

# ============================================================
# QUERY TIMEOUT
# ============================================================

QUERY_TIMEOUT = 30  # seconds

# ============================================================
# ENVIRONMENT SETUP INSTRUCTIONS
# ============================================================

SETUP_INSTRUCTIONS = """
# PostgreSQL Setup Instructions
================================

## Windows:
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Install with default settings
3. Remember your postgres password
4. PostgreSQL will run on port 5432 by default

## Create Database:
Open Command Prompt and run:

```bash
psql -U postgres
CREATE DATABASE ai_screener_pro;
\\q
```

## Initialize Schema:
```bash
cd "C:\\python\\MG AI\\AI_Screener_Complete"
psql -U postgres -d ai_screener_pro -f database_schema.sql
```

## Environment Variables (Optional):
Create .env file with:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_screener_pro
DB_USER=postgres
DB_PASSWORD=your_password
USE_POSTGRESQL=true
```

## Verify Connection:
```python
from config.db_config import get_database_url
from database.db_manager import DatabaseManager

db = DatabaseManager()
if db.test_connection():
    print("✅ Database connected successfully!")
```
"""

if __name__ == '__main__':
    print(SETUP_INSTRUCTIONS)

