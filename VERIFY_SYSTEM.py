"""
System Verification Script
===========================
Comprehensive check of all components
"""

import sys
import os
from pathlib import Path

print("="*70)
print("PROFESSIONAL AI SCREENER v3.0 - SYSTEM VERIFICATION")
print("="*70)
print()

# Results tracking
results = {
    'passed': [],
    'failed': [],
    'warnings': []
}

# ============================================================
# 1. CHECK PYTHON VERSION
# ============================================================

print("🔍 Checking Python version...")
version = sys.version_info
if version.major == 3 and version.minor >= 8:
    print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
    results['passed'].append("Python version")
else:
    print(f"   ❌ Python {version.major}.{version.minor} (need 3.8+)")
    results['failed'].append("Python version")

# ============================================================
# 2. CHECK REQUIRED PACKAGES
# ============================================================

print("\n🔍 Checking required packages...")

required_packages = {
    'pandas': 'Data manipulation',
    'numpy': 'Numerical computing',
    'streamlit': 'Web dashboard',
    'plotly': 'Visualizations',
    'psycopg2': 'PostgreSQL driver',
    'fastapi': 'REST API',
    'yfinance': 'Market data',
    'dhanhq': 'Dhan API',
    'sklearn': 'Machine learning',
    'xgboost': 'XGBoost models'
}

for package, description in required_packages.items():
    try:
        __import__(package)
        print(f"   ✅ {package:15} - {description}")
        results['passed'].append(f"Package: {package}")
    except ImportError:
        print(f"   ❌ {package:15} - {description} (NOT INSTALLED)")
        results['failed'].append(f"Package: {package}")

# ============================================================
# 3. CHECK DIRECTORY STRUCTURE
# ============================================================

print("\n🔍 Checking directory structure...")

required_dirs = [
    'database',
    'risk_management',
    'broker_integration',
    'models',
    'backtesting',
    'monitoring',
    'config'
]

for dir_name in required_dirs:
    dir_path = Path(dir_name)
    if dir_path.exists():
        print(f"   ✅ {dir_name}/")
        results['passed'].append(f"Directory: {dir_name}")
    else:
        print(f"   ❌ {dir_name}/ (MISSING)")
        results['failed'].append(f"Directory: {dir_name}")

# ============================================================
# 4. CHECK REQUIRED FILES
# ============================================================

print("\n🔍 Checking required files...")

required_files = [
    'database_schema.sql',
    'enhanced_screener.py',
    'api_server.py',
    'requirements_professional.txt',
    '.env',
    'database/db_manager.py',
    'risk_management/risk_engine.py',
    'broker_integration/broker_client.py'
]

for file_name in required_files:
    file_path = Path(file_name)
    if file_path.exists():
        print(f"   ✅ {file_name}")
        results['passed'].append(f"File: {file_name}")
    else:
        print(f"   ⚠️ {file_name} (MISSING)")
        results['warnings'].append(f"File: {file_name}")

# ============================================================
# 5. CHECK DATABASE CONNECTION
# ============================================================

print("\n🔍 Checking database connection...")

try:
    from database.db_manager import get_db
    
    db = get_db()
    if db.test_connection():
        print("   ✅ PostgreSQL connected")
        results['passed'].append("Database connection")
    else:
        print("   ⚠️ PostgreSQL not connected (will use SQLite)")
        results['warnings'].append("Database connection")
except Exception as e:
    print(f"   ⚠️ Database: {str(e)[:50]}")
    results['warnings'].append("Database connection")

# ============================================================
# 6. CHECK ENVIRONMENT VARIABLES
# ============================================================

print("\n🔍 Checking environment variables...")

try:
    from dotenv import load_dotenv
    load_dotenv()
    
    env_vars = [
        'DHAN_CLIENT_ID',
        'DHAN_ACCESS_TOKEN',
        'DB_NAME',
        'ACTIVE_BROKER'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var:20} = {value[:20]}...")
            results['passed'].append(f"Env var: {var}")
        else:
            print(f"   ⚠️ {var:20} (NOT SET)")
            results['warnings'].append(f"Env var: {var}")
            
except Exception as e:
    print(f"   ⚠️ Error loading .env: {e}")
    results['warnings'].append("Environment file")

# ============================================================
# 7. CHECK DHAN API
# ============================================================

print("\n🔍 Checking Dhan API...")

try:
    client_id = os.getenv('DHAN_CLIENT_ID')
    access_token = os.getenv('DHAN_ACCESS_TOKEN')
    
    if client_id and access_token:
        print(f"   ✅ Credentials configured")
        print(f"      Client ID: {client_id}")
        print(f"      Token: {access_token[:30]}...")
        results['passed'].append("Dhan credentials")
        
        # Try to import dhanhq
        try:
            import dhanhq
            print(f"   ✅ dhanhq package available")
            results['passed'].append("Dhan package")
        except ImportError:
            print(f"   ❌ dhanhq package not installed")
            results['failed'].append("Dhan package")
    else:
        print(f"   ⚠️ Dhan credentials not configured")
        results['warnings'].append("Dhan credentials")
        
except Exception as e:
    print(f"   ⚠️ Error checking Dhan: {e}")
    results['warnings'].append("Dhan API")

# ============================================================
# 8. CHECK PORTS
# ============================================================

print("\n🔍 Checking ports...")

import socket

ports_to_check = {
    8501: 'Streamlit Dashboard',
    8000: 'FastAPI Backend',
    5432: 'PostgreSQL Database'
}

for port, service in ports_to_check.items():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    
    if result == 0:
        print(f"   ⚠️ Port {port:5} - {service:25} (IN USE)")
        results['warnings'].append(f"Port {port} in use")
    else:
        print(f"   ✅ Port {port:5} - {service:25} (AVAILABLE)")
        results['passed'].append(f"Port {port} available")

# ============================================================
# FINAL REPORT
# ============================================================

print("\n" + "="*70)
print("VERIFICATION REPORT")
print("="*70)

print(f"\n✅ Passed:   {len(results['passed'])}")
print(f"❌ Failed:   {len(results['failed'])}")
print(f"⚠️ Warnings: {len(results['warnings'])}")

if results['failed']:
    print("\n❌ FAILED CHECKS:")
    for item in results['failed']:
        print(f"   - {item}")

if results['warnings']:
    print("\n⚠️ WARNINGS:")
    for item in results['warnings']:
        print(f"   - {item}")

print("\n" + "="*70)

# Overall status
if len(results['failed']) == 0:
    if len(results['warnings']) == 0:
        print("🎉 ALL CHECKS PASSED! System is PERFECT!")
        print("\nYou're ready to launch:")
        print("   Double-click: START_SYSTEM.bat")
    else:
        print("✅ SYSTEM IS READY! (with minor warnings)")
        print("\nWarnings can be ignored for now.")
        print("System will work, but consider fixing warnings.")
        print("\nYou're ready to launch:")
        print("   Double-click: START_SYSTEM.bat")
else:
    print("⚠️ SYSTEM HAS ISSUES!")
    print("\nPlease fix the failed checks above.")
    print("Run: COMPLETE_SETUP.bat to fix most issues")

print("="*70)
print()

input("\nPress Enter to exit...")

