"""
Real-Time Alert System for AI Screener
======================================
Sends instant notifications via Email, Telegram, and SMS when signals appear

Features:
- Email alerts with HTML formatting
- Telegram bot integration  
- SMS alerts (via Twilio)
- Custom alert rules
- Signal filtering
- Rate limiting to avoid spam
"""

import smtplib
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests


class AlertSystem:
    """
    Manages all alert notifications for the AI Screener.
    """
    
    def __init__(self, config_file='alert_config.json'):
        """
        Initialize alert system with configuration.
        
        Args:
            config_file: Path to JSON config file with credentials
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.last_alert_time = {}  # Track when we last sent alerts
        self.min_alert_interval = 300  # Minimum 5 minutes between same alerts
        
    def _load_config(self) -> Dict:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Create default config
            default_config = {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "your_email@gmail.com",
                    "sender_password": "your_app_password",
                    "recipient_emails": ["your_email@gmail.com"]
                },
                "telegram": {
                    "enabled": False,
                    "bot_token": "YOUR_BOT_TOKEN",
                    "chat_ids": ["YOUR_CHAT_ID"]
                },
                "sms": {
                    "enabled": False,
                    "twilio_account_sid": "YOUR_ACCOUNT_SID",
                    "twilio_auth_token": "YOUR_AUTH_TOKEN",
                    "twilio_phone": "+1234567890",
                    "recipient_phones": ["+1234567890"]
                },
                "alert_rules": {
                    "min_confidence": 0.70,
                    "signals": ["buy", "sell"],
                    "stocks": [],  # Empty = all stocks
                    "min_interval_minutes": 5
                }
            }
            
            # Save default config
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
    
    def should_send_alert(self, signal: Dict) -> bool:
        """
        Check if alert should be sent based on rules and rate limiting.
        
        Args:
            signal: Signal dictionary with stock info
            
        Returns:
            True if alert should be sent
        """
        # Check confidence threshold
        min_conf = self.config['alert_rules']['min_confidence']
        if signal.get('confidence', 0) < min_conf:
            return False
        
        # Check signal type
        allowed_signals = self.config['alert_rules']['signals']
        if signal.get('signal') not in allowed_signals:
            return False
        
        # Check stock filter
        stock_filter = self.config['alert_rules']['stocks']
        if stock_filter and signal.get('symbol') not in stock_filter:
            return False
        
        # Check rate limiting
        alert_key = f"{signal.get('symbol')}_{signal.get('signal')}"
        now = datetime.now()
        
        if alert_key in self.last_alert_time:
            time_since_last = (now - self.last_alert_time[alert_key]).seconds
            if time_since_last < self.min_alert_interval:
                return False  # Too soon since last alert
        
        # Update last alert time
        self.last_alert_time[alert_key] = now
        return True
    
    def send_email_alert(self, signals: List[Dict]) -> bool:
        """
        Send email alert with signal details.
        
        Args:
            signals: List of signal dictionaries
            
        Returns:
            True if successful
        """
        if not self.config['email']['enabled']:
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'🚨 AI Screener Alert - {len(signals)} New Signal(s)'
            msg['From'] = self.config['email']['sender_email']
            msg['To'] = ', '.join(self.config['email']['recipient_emails'])
            
            # Create HTML body
            html = self._create_email_html(signals)
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            with smtplib.SMTP(self.config['email']['smtp_server'], 
                             self.config['email']['smtp_port']) as server:
                server.starttls()
                server.login(self.config['email']['sender_email'],
                           self.config['email']['sender_password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Email alert failed: {e}")
            return False
    
    def _create_email_html(self, signals: List[Dict]) -> str:
        """Create formatted HTML email body."""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
                .signal {{ border: 2px solid #4CAF50; margin: 10px; padding: 15px; border-radius: 5px; }}
                .buy {{ border-color: #4CAF50; background-color: #E8F5E9; }}
                .sell {{ border-color: #F44336; background-color: #FFEBEE; }}
                .detail {{ margin: 5px 0; }}
                .confidence {{ font-weight: bold; font-size: 18px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚨 AI Stock Screener Alert</h1>
                <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        """
        
        for signal in signals:
            signal_type = signal.get('signal', 'hold').lower()
            confidence = signal.get('confidence', 0) * 100
            
            html += f"""
            <div class="signal {signal_type}">
                <h2>{signal.get('symbol', 'N/A')}</h2>
                <div class="detail"><strong>Signal:</strong> {signal.get('signal', 'N/A').upper()}</div>
                <div class="detail confidence">Confidence: {confidence:.1f}%</div>
                <div class="detail"><strong>Current Price:</strong> ₹{signal.get('current_price', 0):.2f}</div>
                <div class="detail"><strong>Target Price:</strong> ₹{signal.get('target_price', 0):.2f}</div>
                <div class="detail"><strong>Stop Loss:</strong> ₹{signal.get('stop_loss', 0):.2f}</div>
                <div class="detail"><strong>VWAP Deviation:</strong> {signal.get('vwap_deviation', 0):.2f}%</div>
            </div>
            """
        
        html += """
            <div class="footer">
                <p>AI Stock Screener - Powered by MG AI Trading System</p>
                <p>86.9% Proven Win Rate | 10 Years Backtested</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_telegram_alert(self, signals: List[Dict]) -> bool:
        """
        Send Telegram alert via bot.
        
        Args:
            signals: List of signal dictionaries
            
        Returns:
            True if successful
        """
        if not self.config['telegram']['enabled']:
            return False
        
        try:
            bot_token = self.config['telegram']['bot_token']
            chat_ids = self.config['telegram']['chat_ids']
            
            # Create message
            message = f"🚨 *AI SCREENER ALERT*\n"
            message += f"_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n\n"
            
            for signal in signals:
                signal_emoji = "🟢" if signal.get('signal') == 'buy' else "🔴"
                confidence = signal.get('confidence', 0) * 100
                
                message += f"{signal_emoji} *{signal.get('symbol')}*\n"
                message += f"Signal: *{signal.get('signal', 'N/A').upper()}*\n"
                message += f"Confidence: *{confidence:.1f}%*\n"
                message += f"Price: ₹{signal.get('current_price', 0):.2f}\n"
                message += f"Target: ₹{signal.get('target_price', 0):.2f}\n"
                message += f"Stop: ₹{signal.get('stop_loss', 0):.2f}\n"
                message += f"VWAP Dev: {signal.get('vwap_deviation', 0):.2f}%\n\n"
            
            message += "✨ _MG AI Trading System_"
            
            # Send to all chat IDs
            success = True
            for chat_id in chat_ids:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                data = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'Markdown'
                }
                response = requests.post(url, data=data)
                if response.status_code != 200:
                    success = False
            
            return success
            
        except Exception as e:
            print(f"Telegram alert failed: {e}")
            return False
    
    def send_sms_alert(self, signals: List[Dict]) -> bool:
        """
        Send SMS alert via Twilio.
        
        Args:
            signals: List of signal dictionaries
            
        Returns:
            True if successful
        """
        if not self.config['sms']['enabled']:
            return False
        
        try:
            # Import Twilio (optional dependency)
            from twilio.rest import Client
            
            account_sid = self.config['sms']['twilio_account_sid']
            auth_token = self.config['sms']['twilio_auth_token']
            from_phone = self.config['sms']['twilio_phone']
            to_phones = self.config['sms']['recipient_phones']
            
            client = Client(account_sid, auth_token)
            
            # Create short message (SMS has character limits)
            message = f"AI SCREENER: {len(signals)} signal(s)\n"
            for signal in signals[:3]:  # Max 3 signals in SMS
                conf = signal.get('confidence', 0) * 100
                message += f"{signal.get('symbol')} {signal.get('signal').upper()} {conf:.0f}%\n"
            
            # Send to all phones
            success = True
            for to_phone in to_phones:
                try:
                    client.messages.create(
                        body=message,
                        from_=from_phone,
                        to=to_phone
                    )
                except:
                    success = False
            
            return success
            
        except Exception as e:
            print(f"SMS alert failed: {e}")
            return False
    
    def send_alerts(self, signals: List[Dict]) -> Dict[str, bool]:
        """
        Send alerts via all enabled channels.
        
        Args:
            signals: List of signal dictionaries
            
        Returns:
            Dictionary with status for each channel
        """
        # Filter signals based on rules
        filtered_signals = [s for s in signals if self.should_send_alert(s)]
        
        if not filtered_signals:
            return {'filtered': True, 'count': 0}
        
        results = {
            'email': False,
            'telegram': False,
            'sms': False,
            'count': len(filtered_signals)
        }
        
        # Send via each enabled channel
        if self.config['email']['enabled']:
            results['email'] = self.send_email_alert(filtered_signals)
        
        if self.config['telegram']['enabled']:
            results['telegram'] = self.send_telegram_alert(filtered_signals)
        
        if self.config['sms']['enabled']:
            results['sms'] = self.send_sms_alert(filtered_signals)
        
        return results
    
    def test_alerts(self) -> Dict[str, bool]:
        """
        Send test alerts to verify configuration.
        
        Returns:
            Status for each channel
        """
        test_signal = {
            'symbol': 'NSE_RELIANCE',
            'signal': 'buy',
            'confidence': 0.85,
            'current_price': 2850.00,
            'target_price': 2936.00,
            'stop_loss': 2807.00,
            'vwap_deviation': -0.8
        }
        
        print("\n🧪 Testing Alert System...")
        print("="*60)
        
        results = {}
        
        if self.config['email']['enabled']:
            print("📧 Testing Email...")
            results['email'] = self.send_email_alert([test_signal])
            print(f"   {'✅ Success' if results['email'] else '❌ Failed'}")
        
        if self.config['telegram']['enabled']:
            print("📱 Testing Telegram...")
            results['telegram'] = self.send_telegram_alert([test_signal])
            print(f"   {'✅ Success' if results['telegram'] else '❌ Failed'}")
        
        if self.config['sms']['enabled']:
            print("📲 Testing SMS...")
            results['sms'] = self.send_sms_alert([test_signal])
            print(f"   {'✅ Success' if results['sms'] else '❌ Failed'}")
        
        print("="*60)
        
        return results


if __name__ == '__main__':
    # Demo / Test
    print("🚨 AI Screener Alert System")
    print("="*60)
    
    alert_system = AlertSystem()
    
    print("\n📝 Configuration file created/loaded:")
    print(f"   {alert_system.config_file}")
    print("\n💡 Edit this file to configure your alert preferences")
    print("\n✅ Alert system ready!")
    print("="*60)

