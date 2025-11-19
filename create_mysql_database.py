"""
Create MySQL Database
=====================
Creates the database if it doesn't exist
"""

import pymysql
from config.db_config import MYSQL_CONFIG

print("=" * 60)
print("Creating MySQL Database")
print("=" * 60)
print()

# Connect to MySQL server (without specifying database)
try:
    print(f"Connecting to MySQL server at {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}...")
    conn = pymysql.connect(
        host=MYSQL_CONFIG['host'],
        port=MYSQL_CONFIG['port'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        charset=MYSQL_CONFIG['charset']
    )
    
    cursor = conn.cursor()
    
    # Create database if it doesn't exist
    db_name = MYSQL_CONFIG['database']
    print(f"Creating database '{db_name}' if it doesn't exist...")
    
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    conn.commit()
    
    print(f"[SUCCESS] Database '{db_name}' is ready!")
    print()
    print("Next steps:")
    print("1. Run: python test_mysql_connection.py")
    print("2. Start API server: python api_server.py")
    print("3. Tables will be created automatically")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"[ERROR] Failed to create database: {e}")
    print()
    print("Troubleshooting:")
    print("1. Make sure MySQL server is running")
    print("2. Check your credentials")
    print("3. Verify MySQL user has CREATE DATABASE permission")

