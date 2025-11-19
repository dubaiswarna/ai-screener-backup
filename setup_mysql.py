"""
MySQL Setup Script
==================
Quick setup script to configure MySQL connection
"""

import os
from pathlib import Path

print("=" * 60)
print("MySQL Database Setup for AI Screener")
print("=" * 60)
print()

# Get MySQL credentials
print("Please provide your MySQL connection details:")
print()

host = input("MySQL Host [localhost]: ").strip() or "localhost"
port = input("MySQL Port [3306]: ").strip() or "3306"
user = input("MySQL Username [root]: ").strip() or "root"
password = input("MySQL Password: ").strip()
database = input("Database Name [ai_screener]: ").strip() or "ai_screener"

print()
print("Creating .env file...")

# Create .env file
env_content = f"""# MySQL Database Configuration
DB_TYPE=mysql
DB_HOST={host}
DB_PORT={port}
DB_NAME={database}
DB_USER={user}
DB_PASSWORD={password}
"""

env_path = Path(".env")
env_path.write_text(env_content)

print(f"✅ Configuration saved to {env_path}")
print()
print("Next steps:")
print("1. Install MySQL connector: pip install pymysql")
print("2. Make sure MySQL server is running")
print("3. Verify database '{}' exists".format(database))
print("4. Start the API server: python api_server.py")
print()
print("The tables will be created automatically on first run!")

