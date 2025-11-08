"""
Easy Dhan Credentials Setup
============================
Run this script to configure your Dhan API credentials
"""

import os
from pathlib import Path

def setup_dhan_credentials():
    """Interactive setup for Dhan API credentials."""
    
    print("="*60)
    print("🔐 DHAN API CREDENTIALS SETUP")
    print("="*60)
    print()
    print("📋 To get your Dhan API credentials:")
    print("1. Open Dhan app")
    print("2. Go to Settings → API")
    print("3. Generate API credentials")
    print("4. Copy Client ID and Access Token")
    print()
    print("="*60)
    print()
    
    # Get credentials
    client_id = input("Enter your Dhan Client ID: ").strip()
    access_token = input("Enter your Dhan Access Token: ").strip()
    
    if not client_id or not access_token:
        print("\n❌ Invalid credentials. Please try again.")
        return False
    
    # Create .env file
    env_path = Path(__file__).parent / '.env'
    
    env_content = f"""# ============================================================
# PROFESSIONAL AI SCREENER - ENVIRONMENT VARIABLES
# ============================================================

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_screener_pro
DB_USER=postgres
DB_PASSWORD=postgres
USE_POSTGRESQL=true

# Dhan API Credentials
DHAN_CLIENT_ID={client_id}
DHAN_ACCESS_TOKEN={access_token}

# Risk Management
TOTAL_CAPITAL=1000000
MAX_RISK_PER_TRADE=2.0
MAX_POSITIONS=10
MIN_CONFIDENCE=70.0

# Broker Selection (dhan, paper, zerodha, upstox)
ACTIVE_BROKER=dhan
"""
    
    # Write to file
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print()
    print("="*60)
    print("✅ CREDENTIALS SAVED SUCCESSFULLY!")
    print("="*60)
    print()
    print(f"📁 Configuration saved to: {env_path}")
    print()
    print("🧪 Testing connection...")
    print()
    
    # Test connection
    try:
        # Set environment variables
        os.environ['DHAN_CLIENT_ID'] = client_id
        os.environ['DHAN_ACCESS_TOKEN'] = access_token
        
        from broker_integration.broker_client import get_broker_client
        
        client = get_broker_client('dhan')
        
        if client.is_connected:
            print("✅ SUCCESS! Dhan API connected successfully!")
            print()
            print("🚀 You're ready to trade with live data!")
            print()
            
            # Test getting a quote
            print("📊 Testing live data...")
            quote = client.get_quote('NSE_RELIANCE')
            if quote:
                print(f"✅ RELIANCE Live Price: ₹{quote.get('ltp', 0):,.2f}")
            
            print()
            print("="*60)
            print("🎉 SETUP COMPLETE!")
            print("="*60)
            print()
            print("Next steps:")
            print("1. Run: python enhanced_screener.py")
            print("2. Or double-click: LAUNCH_PROFESSIONAL_SYSTEM.bat")
            print()
            
            return True
        else:
            print("⚠️ Connected but not authenticated. Check credentials.")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print()
        print("💡 Possible issues:")
        print("- Invalid Client ID or Access Token")
        print("- Dhan account not activated")
        print("- API not enabled in Dhan app")
        print()
        return False

if __name__ == '__main__':
    setup_dhan_credentials()
    input("\nPress Enter to exit...")

