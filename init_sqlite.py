"""Initialize SQLite Database"""
import sqlite3
from pathlib import Path

db_path = Path("data/ai_screener.db")
db_path.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Create signals table
cursor.execute('''
CREATE TABLE IF NOT EXISTS signals (
    signal_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    confidence REAL NOT NULL,
    entry_price REAL NOT NULL,
    target_price REAL,
    stop_loss REAL,
    model_name TEXT,
    signal_strength TEXT,
    volume INTEGER,
    risk_reward_ratio REAL,
    position_size REAL,
    max_risk_amount REAL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,
    status TEXT DEFAULT 'ACTIVE'
)
''')

# Create portfolio table
cursor.execute('''
CREATE TABLE IF NOT EXISTS portfolio (
    position_id TEXT PRIMARY KEY,
    trade_id TEXT,
    symbol TEXT NOT NULL UNIQUE,
    quantity INTEGER NOT NULL,
    avg_price REAL NOT NULL,
    current_price REAL,
    invested_amount REAL NOT NULL,
    current_value REAL,
    unrealized_pnl REAL,
    unrealized_pnl_pct REAL,
    stop_loss REAL,
    target REAL,
    risk_amount REAL,
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Create trades table
cursor.execute('''
CREATE TABLE IF NOT EXISTS trades (
    trade_id TEXT PRIMARY KEY,
    signal_id TEXT,
    symbol TEXT NOT NULL,
    trade_type TEXT NOT NULL,
    entry_price REAL NOT NULL,
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quantity INTEGER NOT NULL,
    entry_amount REAL NOT NULL,
    exit_price REAL,
    exit_time TIMESTAMP,
    exit_amount REAL,
    profit_loss REAL,
    profit_loss_pct REAL,
    stop_loss REAL,
    target REAL,
    trailing_stop REAL,
    status TEXT DEFAULT 'OPEN',
    broker_order_id TEXT,
    commission REAL DEFAULT 0,
    notes TEXT
)
''')

# Create user_config table
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_config (
    config_id TEXT PRIMARY KEY,
    max_risk_per_trade REAL DEFAULT 2.0,
    max_portfolio_risk REAL DEFAULT 10.0,
    max_positions INTEGER DEFAULT 10,
    max_correlation REAL DEFAULT 0.7,
    min_confidence REAL DEFAULT 70.0,
    min_risk_reward REAL DEFAULT 1.5,
    total_capital REAL NOT NULL,
    reserve_cash_pct REAL DEFAULT 10.0,
    telegram_enabled INTEGER DEFAULT 1,
    alert_min_confidence REAL DEFAULT 75.0,
    use_ensemble INTEGER DEFAULT 1,
    retrain_frequency_days INTEGER DEFAULT 30,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Insert default config if not exists
cursor.execute('''
INSERT OR IGNORE INTO user_config (config_id, total_capital)
VALUES ('default', 1000000)
''')

conn.commit()
conn.close()

print("✅ SQLite database initialized at:", db_path)

