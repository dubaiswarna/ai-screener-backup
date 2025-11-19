"""
Railway Initialization Script
==============================
Runs on Railway deployment to initialize database
"""

import os
import sys
import time

def init_railway_database():
    """Initialize MySQL database on Railway."""
    print("=" * 60)
    print("Railway Database Initialization")
    print("=" * 60)
    
    # Wait a bit for MySQL to be ready
    print("Waiting for MySQL connection...")
    time.sleep(5)
    
    try:
        import pymysql
        from database.mysql_manager import create_mysql_tables
        
        # Get Railway MySQL credentials from environment
        db_config = {
            'host': os.getenv('MYSQLHOST') or os.getenv('DB_HOST') or 'localhost',
            'port': int(os.getenv('MYSQLPORT') or os.getenv('DB_PORT') or 3306),
            'user': os.getenv('MYSQLUSER') or os.getenv('DB_USER') or 'root',
            'password': os.getenv('MYSQLPASSWORD') or os.getenv('DB_PASSWORD') or '',
            'database': os.getenv('MYSQLDATABASE') or os.getenv('DB_NAME') or 'ai_screenr_db',
            'charset': 'utf8mb4'
        }
        
        print(f"Connecting to MySQL at {db_config['host']}:{db_config['port']}...")
        print(f"Database: {db_config['database']}")
        
        conn = pymysql.connect(**db_config)
        print("✅ MySQL connection successful!")
        
        # Create tables
        print("Creating database tables...")
        create_mysql_tables(conn)
        conn.close()
        
        print("✅ Database initialization complete!")
        return True
        
    except ImportError:
        print("⚠️ pymysql not installed, installing...")
        os.system("pip install pymysql")
        return init_railway_database()
        
    except Exception as e:
        print(f"⚠️ Database initialization error: {e}")
        print("Tables will be created automatically on first API call")
        return False

if __name__ == "__main__":
    success = init_railway_database()
    sys.exit(0 if success else 1)

