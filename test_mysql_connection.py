"""
Test MySQL Connection
=====================
Quick script to test MySQL database connection
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
env_path = Path('.env')
if env_path.exists():
    load_dotenv(env_path)
    print("[OK] Loaded .env file")
else:
    print("[WARNING] No .env file found. Using default config.")

print("\n" + "=" * 60)
print("Testing MySQL Connection")
print("=" * 60)
print()

# Get config
from config.db_config import MYSQL_CONFIG, DB_TYPE

print(f"Database Type: {DB_TYPE}")
print(f"Host: {MYSQL_CONFIG['host']}")
print(f"Port: {MYSQL_CONFIG['port']}")
print(f"Database: {MYSQL_CONFIG['database']}")
print(f"User: {MYSQL_CONFIG['user']}")
print(f"Password: {'*' * len(MYSQL_CONFIG['password']) if MYSQL_CONFIG['password'] else '(empty)'}")
print()

# Test connection
try:
    from database.db_manager import DatabaseManager
    
    print("Attempting to connect...")
    db = DatabaseManager()
    
    if db.test_connection():
        print("\n[SUCCESS] MySQL connection working!")
        print(f"[OK] Connected to database: {MYSQL_CONFIG['database']}")
        print("\nYou're all set! Start the API server with: python api_server.py")
    else:
        print("\n[ERROR] Connection failed. Check your credentials.")
        
except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\nTroubleshooting:")
    print("1. Make sure MySQL server is running")
    print("2. Check your credentials in .env file or config/db_config.py")
    print("3. Verify database 'ai_screener' exists")
    print("4. Check user permissions")

