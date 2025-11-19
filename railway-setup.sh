#!/bin/bash
# Railway Setup Script
# This script runs on Railway deployment to set up the database

echo "=========================================="
echo "Railway Deployment Setup"
echo "=========================================="

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies for frontend
echo "Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Wait for MySQL to be ready
echo "Waiting for MySQL connection..."
sleep 5

# Initialize MySQL database tables
echo "Initializing MySQL database..."
python -c "
import pymysql
import os
from database.mysql_manager import create_mysql_tables

try:
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'ai_screenr_db'),
        charset='utf8mb4'
    )
    create_mysql_tables(conn)
    conn.close()
    print('✅ Database tables initialized')
except Exception as e:
    print(f'⚠️ Database initialization: {e}')
    print('Tables will be created on first API call')
"

echo "=========================================="
echo "Setup complete!"
echo "=========================================="

