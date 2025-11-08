"""
Database Configuration
======================
PostgreSQL connection configuration and settings
"""

import os
from typing import Dict, Any

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

# PostgreSQL connection parameters
DB_CONFIG: Dict[str, Any] = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'ai_screener_pro'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'your_password_here'),
}

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

# Default to PostgreSQL, fallback to SQLite if not available
USE_POSTGRESQL = os.getenv('USE_POSTGRESQL', 'true').lower() == 'true'

# ============================================================
# CONNECTION STRING BUILDERS
# ============================================================

def get_postgresql_url() -> str:
    """Get PostgreSQL connection URL."""
    return (
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )

def get_sqlite_url() -> str:
    """Get SQLite connection URL."""
    return f"sqlite:///{SQLITE_CONFIG['database']}"

def get_database_url() -> str:
    """Get appropriate database URL based on configuration."""
    return get_postgresql_url() if USE_POSTGRESQL else get_sqlite_url()

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

