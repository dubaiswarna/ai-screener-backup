"""
Automated MCX Alerts Scheduler
===============================
Automatically sends Telegram alerts for Gold & Silver at specified times
Can run continuously in background
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

import time
from datetime import datetime
import schedule

# Import the alert sender
from send_mcx_alerts import send_commodity_alerts

def send_alerts_with_timestamp():
    """Send alerts with timestamp"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running scheduled alert check...")
    send_commodity_alerts()

def main():
    """Run automated alert scheduler"""
    print("\n" + "="*70)
    print("MCX COMMODITY AUTO-ALERT SCHEDULER")
    print("="*70)
    print("\nScheduled alert times:")
    print("  • 09:15 AM - Market opening")
    print("  • 12:00 PM - Mid-day check")
    print("  • 03:30 PM - Market closing")
    print("  • Every 2 hours during market hours")
    print("\nPress Ctrl+C to stop")
    print("="*70 + "\n")
    
    # Schedule alerts
    schedule.every().day.at("09:15").do(send_alerts_with_timestamp)  # Market open
    schedule.every().day.at("12:00").do(send_alerts_with_timestamp)  # Mid-day
    schedule.every().day.at("15:30").do(send_alerts_with_timestamp)  # Market close
    schedule.every(2).hours.do(send_alerts_with_timestamp)          # Every 2 hours
    
    # Send immediate alert on start
    print("📤 Sending initial alert...")
    send_alerts_with_timestamp()
    
    print(f"\n⏰ Scheduler running... Next alert at scheduled time")
    print("   Keep this window open for automated alerts")
    print("   Press Ctrl+C to stop\n")
    
    # Run scheduler
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n⏹️  Scheduler stopped by user")
        print("="*70 + "\n")

if __name__ == '__main__':
    main()

