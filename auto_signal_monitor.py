"""
Auto Signal Monitor - 3Jasmines & Hybrid Signal Generator
==========================================================
Runs every 5 minutes and sends new signals to Telegram
"""

import time
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import yfinance as yf
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from three_jasmines_screener import ThreeJasminesScreener
    from hybrid_signal_generator import HybridSignalGenerator
    from patterns.chart_pattern_detector import ChartPatternDetector
    from support_resistance.sr_calculator_enhanced import ProfessionalSRCalculator
    from config.stock_universe import NIFTY_50, NIFTY_200, SMALLCAP_250, ALL_STOCKS
    JASMINES_AVAILABLE = True
    HYBRID_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")
    JASMINES_AVAILABLE = False
    HYBRID_AVAILABLE = False

# Telegram Bot Setup
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Signal tracking file
SIGNAL_TRACKING_FILE = 'sent_signals.json'

# Configuration
RUN_INTERVAL_MINUTES = 5  # Run every 5 minutes (recommended)
STOCK_UNIVERSE = "Nifty 50"  # Options: "Nifty 50", "Nifty 200", "Small Cap 250"
MIN_CONFIDENCE_JASMINES = 70.0
MIN_CONFIDENCE_HYBRID = 75.0
MIN_RR_HYBRID = 1.5


def get_yfinance_symbol(symbol):
    """Convert NSE symbol to Yahoo Finance format"""
    return f"{symbol}.NS"


def load_sent_signals():
    """Load previously sent signals to avoid duplicates"""
    if os.path.exists(SIGNAL_TRACKING_FILE):
        with open(SIGNAL_TRACKING_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_sent_signal(signal_id, signal_data):
    """Save sent signal to tracking file"""
    sent_signals = load_sent_signals()
    sent_signals[signal_id] = {
        'timestamp': datetime.now().isoformat(),
        'data': signal_data
    }
    with open(SIGNAL_TRACKING_FILE, 'w') as f:
        json.dump(sent_signals, f, indent=2)


def is_signal_new(signal_id):
    """Check if signal was already sent"""
    sent_signals = load_sent_signals()
    return signal_id not in sent_signals


def send_telegram_message(message):
    """Send message to Telegram (OPTIONAL - for future live signals)"""
    # Telegram disabled for now - will be used for live signals later
    return False
    
    # Future implementation:
    # if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    #     return False
    # try:
    #     import requests
    #     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    #     data = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    #     response = requests.post(url, data=data, timeout=10)
    #     return response.status_code == 200
    # except Exception as e:
    #     return False


def format_jasmines_signal(signal):
    """Format 3Jasmines signal for Telegram"""
    msg = f"""
🌸 <b>3JASMINES SIGNAL</b> 🌸

📊 <b>{signal['symbol']}</b>
🎯 Confidence: {signal['confidence']:.1f}%

💰 <b>Trade Setup:</b>
Entry: ₹{signal['entry']:.2f}
Target: ₹{signal['target']:.2f}
Stop Loss: ₹{signal['stop_loss']:.2f}
R:R Ratio: 1:{signal['rr_ratio']:.2f}

📈 <b>Criteria Met:</b>
✅ Near Support: {signal['jasmine1_support']['reason']}
✅ RSI Oversold: {signal['jasmine2_rsi']['reason']}
✅ Pattern: {signal['jasmine3_pattern']['reason']}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    return msg.strip()


def format_hybrid_signal(signal):
    """Format Hybrid signal for Telegram"""
    msg = f"""
💎 <b>TREASURE SIGNAL</b> 💎

📊 <b>{signal['symbol']}</b>
🎯 Confidence: {signal['confidence']:.1f}%
📊 Signal: {signal['signal']}

💰 <b>Trade Setup:</b>
Entry: ₹{signal['trade_setup']['entry']:.2f}
Target: ₹{signal['trade_setup']['target1']:.2f}
Stop Loss: ₹{signal['trade_setup']['stop_loss']:.2f}
R:R Ratio: 1:{signal['trade_setup']['rr_ratio']:.2f}

📈 <b>3-Layer Analysis:</b>
Technical: {signal['technical']['confidence_pct']:.0f}%
S&R: {signal['sr_analysis']['confidence_pct']:.0f}%
Pattern: {signal['chart_pattern']['confidence_pct']:.0f}%

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    return msg.strip()


def run_jasmines_screener(stock_list):
    """Run 3Jasmines screener"""
    if not JASMINES_AVAILABLE:
        return []
    
    jasmines_gen = ThreeJasminesScreener(
        max_support_distance_pct=0.5,
        max_rsi_threshold=35.0,
        target_buffer_pct=1.0,
        stop_loss_buffer_pct=2.0
    )
    
    try:
        sr_calc = ProfessionalSRCalculator(sensitivity=3, min_touches=2)
    except:
        from support_resistance.sr_calculator import SupportResistanceCalculator
        sr_calc = SupportResistanceCalculator(sensitivity=3, min_touches=2)
    
    pattern_detector = ChartPatternDetector()
    
    signals = []
    
    for symbol in stock_list[:50]:  # Limit to 50 stocks per run
        try:
            ticker = yf.Ticker(get_yfinance_symbol(symbol))
            df_raw = ticker.history(period="6mo", interval="1d")
            
            if df_raw.empty or len(df_raw) < 20:
                continue
            
            df = pd.DataFrame({
                'time': df_raw.index,
                'open': df_raw['Open'].values,
                'high': df_raw['High'].values,
                'low': df_raw['Low'].values,
                'close': df_raw['Close'].values,
                'volume': df_raw['Volume'].values
            })
            
            # Use EOD data only
            df_eod = df[:-1].copy() if len(df) > 5 else df
            
            signal = jasmines_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
            
            if signal and signal['confidence'] >= MIN_CONFIDENCE_JASMINES:
                signals.append(signal)
            
            time.sleep(0.2)  # Rate limiting
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            continue
    
    return signals


def run_hybrid_screener(stock_list):
    """Run Hybrid Signal Generator"""
    if not HYBRID_AVAILABLE:
        return []
    
    hybrid_gen = HybridSignalGenerator(
        min_confidence=MIN_CONFIDENCE_HYBRID,
        min_rr_ratio=MIN_RR_HYBRID
    )
    
    try:
        sr_calc = ProfessionalSRCalculator(sensitivity=3, min_touches=2)
    except:
        from support_resistance.sr_calculator import SupportResistanceCalculator
        sr_calc = SupportResistanceCalculator(sensitivity=3, min_touches=2)
    
    pattern_detector = ChartPatternDetector()
    
    signals = []
    
    for symbol in stock_list[:50]:  # Limit to 50 stocks per run
        try:
            ticker = yf.Ticker(get_yfinance_symbol(symbol))
            df_raw = ticker.history(period="6mo", interval="1d")
            
            if df_raw.empty or len(df_raw) < 50:
                continue
            
            df = pd.DataFrame({
                'time': df_raw.index,
                'open': df_raw['Open'].values,
                'high': df_raw['High'].values,
                'low': df_raw['Low'].values,
                'close': df_raw['Close'].values,
                'volume': df_raw['Volume'].values
            })
            
            # Use EOD data only
            df_eod = df[:-1].copy() if len(df) > 5 else df
            
            result = hybrid_gen.analyze_stock(symbol, df_eod, sr_calc, pattern_detector)
            
            if result and result.get('is_treasure'):
                signals.append(result)
            
            time.sleep(0.2)  # Rate limiting
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            continue
    
    return signals


def get_stock_list():
    """Get stock list based on universe"""
    if STOCK_UNIVERSE == "Nifty 50":
        return NIFTY_50 if len(NIFTY_50) > 0 else ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
    elif STOCK_UNIVERSE == "Nifty 200":
        return NIFTY_200 if len(NIFTY_200) > 0 else NIFTY_50
    elif STOCK_UNIVERSE == "Small Cap 250":
        return SMALLCAP_250 if len(SMALLCAP_250) > 0 else NIFTY_50
    else:
        return NIFTY_50


def main():
    """Main monitoring loop"""
    print("="*80)
    print("AUTO SIGNAL MONITOR - 3Jasmines & Hybrid Signal Generator")
    print("="*80)
    print(f"Run Interval: {RUN_INTERVAL_MINUTES} minutes")
    print(f"Stock Universe: {STOCK_UNIVERSE}")
    print(f"Telegram: {'✅ Configured' if TELEGRAM_BOT_TOKEN else '❌ Not configured'}")
    print("="*80)
    print()
    
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ WARNING: Telegram not configured!")
        print("Set environment variables:")
        print("  TELEGRAM_BOT_TOKEN=your_bot_token")
        print("  TELEGRAM_CHAT_ID=your_chat_id")
        print()
    
    stock_list = get_stock_list()
    print(f"📊 Monitoring {len(stock_list)} stocks")
    print()
    
    iteration = 0
    
    while True:
        iteration += 1
        print(f"\n{'='*80}")
        print(f"🔄 Iteration #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        # Run 3Jasmines Screener
        print("\n🌸 Running 3Jasmines Screener...")
        jasmines_signals = run_jasmines_screener(stock_list)
        print(f"Found {len(jasmines_signals)} 3Jasmines signals")
        
        # Send new 3Jasmines signals
        for signal in jasmines_signals:
            signal_id = f"jasmines_{signal['symbol']}_{signal['entry']:.2f}"
            if is_signal_new(signal_id):
                message = format_jasmines_signal(signal)
                if send_telegram_message(message):
                    save_sent_signal(signal_id, signal)
                    print(f"✅ Sent 3Jasmines signal: {signal['symbol']}")
                else:
                    print(f"❌ Failed to send: {signal['symbol']}")
        
        # Run Hybrid Signal Generator
        print("\n💎 Running Hybrid Signal Generator...")
        hybrid_signals = run_hybrid_screener(stock_list)
        print(f"Found {len(hybrid_signals)} Treasure signals")
        
        # Send new Hybrid signals
        for signal in hybrid_signals:
            signal_id = f"hybrid_{signal['symbol']}_{signal['trade_setup']['entry']:.2f}"
            if is_signal_new(signal_id):
                message = format_hybrid_signal(signal)
                if send_telegram_message(message):
                    save_sent_signal(signal_id, signal)
                    print(f"✅ Sent Treasure signal: {signal['symbol']}")
                else:
                    print(f"❌ Failed to send: {signal['symbol']}")
        
        # Wait for next iteration
        wait_seconds = RUN_INTERVAL_MINUTES * 60
        print(f"\n⏳ Waiting {RUN_INTERVAL_MINUTES} minutes until next scan...")
        print(f"Next run: {(datetime.now() + timedelta(minutes=RUN_INTERVAL_MINUTES)).strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(wait_seconds)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

