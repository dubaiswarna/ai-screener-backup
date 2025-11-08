# -*- coding: utf-8 -*-
"""
COMPREHENSIVE MONTHLY BACKTEST GENERATOR
=========================================
Generates signals at different time points and tracks performance
Creates detailed Excel report with all results

Cutoff Dates:
- May 31, 2025
- June 30, 2025
- July 31, 2025
- Aug 31, 2025
- Sept 30, 2025
- Oct 31, 2025

Performance tracking up to Nov 5, 2025
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_engineering import FeatureEngineer
from signal_generator_fixed import SignalGeneratorFixed
from excel_data_loader import ExcelDataLoader

# ============================================================
# CONFIGURATION
# ============================================================

EXCEL_FILE = r"C:\python\MG AI\Nifty200_Complete_10yeardata.xlsx"  # Separate sheets = faster!
OUTPUT_FILE = r"C:\python\MG AI\AI_Backtest_Results.xlsx"

# Cutoff dates for signal generation
# 3 months: Jan to March 2025 (likely BULLISH period)
CUTOFF_DATES = {
    'January_2025': '2025-01-31',
    'February_2025': '2025-02-28',
    'March_2025': '2025-03-31'
}

# End date for performance tracking (track for 6 months)
END_DATE = '2025-09-30'

# FILTER SETTINGS: Only STRONG BUY signals
MIN_CONFIDENCE = 75.0  # Minimum confidence threshold (75% = STRONG signals)
SIGNAL_TYPE = 'BUY'     # Only BUY signals (no SELL)
MIN_TARGET_PERCENT = 2.5  # Minimum target gain (2.5% or more)
MAX_STOP_PERCENT = 5.0    # Maximum stop-loss (5% max risk)

# TOP 10 MODELS TO TEST (for faster backtesting)
TOP_10_STOCKS = [
    'NSE_RELIANCE', 'NSE_TCS', 'NSE_HDFCBANK', 'NSE_INFY', 'NSE_ICICIBANK',
    'NSE_SBIN', 'NSE_BHARTIARTL', 'NSE_KOTAKBANK', 'NSE_HINDUNILVR', 'NSE_AXISBANK'
]

# ============================================================
# LOAD AI MODELS
# ============================================================

def load_ai_models():
    """Load TOP 10 AI models for faster testing"""
    print("\n" + "="*60)
    print("LOADING TOP 10 AI MODELS")
    print("="*60)
    
    models_dir = Path(__file__).parent / 'models'
    signal_gen = SignalGeneratorFixed(models_dir=str(models_dir))
    
    if models_dir.exists():
        for symbol in TOP_10_STOCKS:
            model_file = models_dir / f"xgb_{symbol}.pkl"
            if model_file.exists():
                signal_gen.load_model(symbol)
            else:
                print(f"   Warning: Model not found for {symbol}")
    
    print(f" Loaded {len(signal_gen.models)} AI models (Top 10 large-caps)")
    return signal_gen

# ============================================================
# GENERATE SIGNALS FOR CUTOFF DATE
# ============================================================

def generate_signals_for_date(excel_loader, signal_gen, cutoff_date, stocks):
    """Generate AI signals using data up to cutoff date"""
    
    print(f"\n Generating signals for cutoff: {cutoff_date}")
    print(f"   Processing {len(stocks)} stocks...")
    
    featured_data = {}
    engineer = FeatureEngineer()
    
    for i, symbol in enumerate(stocks):
        if (i + 1) % 10 == 0:
            print(f"   Processed {i+1}/{len(stocks)} stocks...")
        
        # Load stock data
        df = excel_loader.get_stock_data(symbol)
        
        if df is None or df.empty:
            continue
        
        # Filter to cutoff date
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df[df['date'] <= cutoff_date]
        elif 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])
            df = df[df['time'] <= cutoff_date]
        
        if len(df) < 50:  # Need minimum history
            continue
        
        # Ensure required columns
        if 'close' not in df.columns:
            continue
        
        if 'vwap' not in df.columns and 'high' in df.columns:
            df['vwap'] = (df['high'] + df['low'] + df['close']) / 3
        
        if 'volume' not in df.columns:
            df['volume'] = df['close'] * 1000
        
        if 'time' not in df.columns and 'date' in df.columns:
            df['time'] = pd.to_datetime(df['date'])
        elif 'time' not in df.columns:
            df['time'] = pd.date_range(end=pd.Timestamp(cutoff_date), periods=len(df), freq='D')
        
        # Engineer features
        df_features = engineer.engineer_features(df)
        
        if df_features is not None and not df_features.empty:
            featured_data[symbol] = df_features
    
    print(f"    Prepared {len(featured_data)} stocks for prediction")
    
    # Generate signals
    signals_list = signal_gen.generate_signals_batch(
        symbols=list(featured_data.keys()),
        featured_data=featured_data
    )
    
    if signals_list:
        df_signals = pd.DataFrame(signals_list)
        df_signals['generated_date'] = cutoff_date
        
        # Get entry price (close price at cutoff date)
        for idx, row in df_signals.iterrows():
            symbol = row['symbol']
            if symbol in featured_data:
                df_signals.at[idx, 'entry_price'] = row['current_price']
        
        print(f"    Generated {len(df_signals)} total signals")
        
        # Show signal breakdown before filtering
        buy_count = len(df_signals[df_signals['signal'] == 'BUY'])
        sell_count = len(df_signals[df_signals['signal'] == 'SELL'])
        hold_count = len(df_signals[df_signals['signal'] == 'HOLD'])
        
        if buy_count > 0:
            buy_conf_min = df_signals[df_signals['signal'] == 'BUY']['confidence'].min()
            buy_conf_max = df_signals[df_signals['signal'] == 'BUY']['confidence'].max()
            buy_conf_avg = df_signals[df_signals['signal'] == 'BUY']['confidence'].mean()
            print(f"      BUY: {buy_count} signals (confidence: {buy_conf_min:.1f}% - {buy_conf_max:.1f}%, avg: {buy_conf_avg:.1f}%)")
        else:
            print(f"      BUY: {buy_count} signals")
        
        print(f"      SELL: {sell_count} signals")
        print(f"      HOLD: {hold_count} signals")
        
        # FILTER 1: Only STRONG BUY signals with high confidence
        df_signals = df_signals[
            (df_signals['signal'] == SIGNAL_TYPE) & 
            (df_signals['confidence'] >= MIN_CONFIDENCE)
        ].copy()
        
        print(f"    After confidence filter: {len(df_signals)} {SIGNAL_TYPE} signals (>= {MIN_CONFIDENCE}%)")
        
        if len(df_signals) > 0:
            # FILTER 2: Good risk-reward ratio (target should be at least MIN_TARGET_PERCENT% above entry)
            df_signals['target_pct'] = ((df_signals['target_price'] - df_signals['entry_price']) / df_signals['entry_price'] * 100)
            df_signals['stop_pct'] = ((df_signals['entry_price'] - df_signals['stop_loss']) / df_signals['entry_price'] * 100)
            
            # Filter: Target must be at least MIN_TARGET_PERCENT% gain, stop-loss not more than MAX_STOP_PERCENT%
            df_signals = df_signals[
                (df_signals['target_pct'] >= MIN_TARGET_PERCENT) &  # At least MIN_TARGET_PERCENT% target
                (df_signals['stop_pct'] <= MAX_STOP_PERCENT) &     # Stop-loss not more than MAX_STOP_PERCENT%
                (df_signals['target_pct'] / df_signals['stop_pct'] >= 1.5)  # Risk-reward ratio >= 1.5:1
            ].copy()
            
            print(f"    After quality filters: {len(df_signals)} ULTRA-HIGH-QUALITY signals (min {MIN_TARGET_PERCENT}% target, max {MAX_STOP_PERCENT}% stop)")
            print(f"      (Target >= 2%, Stop <= 5%, Risk-Reward >= 1.5:1)")
        
        return df_signals
    
    return pd.DataFrame()

# ============================================================
# CALCULATE PERFORMANCE
# ============================================================

def calculate_performance(signals_df, excel_loader, cutoff_date, end_date):
    """Calculate actual performance of signals"""
    
    print(f"\n Calculating performance from {cutoff_date} to {end_date}")
    
    results = []
    
    for idx, row in signals_df.iterrows():
        symbol = row['symbol']
        signal = row['signal']
        entry_price = row['entry_price']
        target_price = row.get('target_price', 0)
        stop_loss = row.get('stop_loss', 0)
        confidence = row['confidence']
        
        # Load stock data
        df = excel_loader.get_stock_data(symbol)
        
        if df is None or df.empty:
            continue
        
        # Get date column
        date_col = 'date' if 'date' in df.columns else 'time'
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Get entry and exit prices
        df_after = df[df[date_col] > cutoff_date]
        
        if len(df_after) == 0:
            continue
        
        # Get exit price (latest available or end_date)
        df_exit = df[(df[date_col] > cutoff_date) & (df[date_col] <= end_date)]
        
        if len(df_exit) == 0:
            continue
        
        exit_price = df_exit['close'].iloc[-1]
        exit_date = df_exit[date_col].iloc[-1]
        
        # Calculate returns
        if signal.upper() == 'BUY':
            return_pct = ((exit_price - entry_price) / entry_price) * 100
            prediction_correct = (exit_price > entry_price)
            target_hit = (exit_price >= target_price) if target_price > 0 else False
            stop_hit = (df_after['close'].min() <= stop_loss) if stop_loss > 0 else False
        elif signal.upper() == 'SELL':
            return_pct = ((entry_price - exit_price) / entry_price) * 100
            prediction_correct = (exit_price < entry_price)
            target_hit = (exit_price <= target_price) if target_price > 0 else False
            stop_hit = (df_after['close'].max() >= stop_loss) if stop_loss > 0 else False
        else:
            continue
        
        # Determine exit reason
        if stop_hit:
            exit_reason = 'STOP_LOSS'
            actual_return = -3.0  # Assume 3% stop loss
        elif target_hit:
            exit_reason = 'TARGET'
            actual_return = 5.0  # Assume 5% target
        else:
            exit_reason = 'HOLDING'
            actual_return = return_pct
        
        results.append({
            'symbol': symbol,
            'signal': signal,
            'confidence': confidence * 100,
            'entry_price': entry_price,
            'entry_date': cutoff_date,
            'exit_price': exit_price,
            'exit_date': exit_date,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'return_pct': return_pct,
            'actual_return': actual_return,
            'prediction_correct': prediction_correct,
            'target_hit': target_hit,
            'stop_hit': stop_hit,
            'exit_reason': exit_reason,
            'days_held': (pd.Timestamp(exit_date).replace(tzinfo=None) - pd.Timestamp(cutoff_date).replace(tzinfo=None)).days
        })
    
    df_performance = pd.DataFrame(results)
    
    if len(df_performance) > 0:
        correct = df_performance['prediction_correct'].sum()
        total = len(df_performance)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        avg_return = df_performance['actual_return'].mean()
        total_return = df_performance['actual_return'].sum()
        
        print(f"    Signals: {total}")
        print(f"    Accuracy: {accuracy:.1f}% ({correct}/{total})")
        print(f"    Avg Return: {avg_return:.2f}%")
        print(f"    Total Return: {total_return:.2f}%")
    
    return df_performance

# ============================================================
# CREATE MASTER SUMMARY
# ============================================================

def create_master_summary(all_results):
    """Create master summary comparing all time periods"""
    
    print("\n Creating master summary...")
    
    summary_data = []
    
    for period, data in all_results.items():
        if 'performance' not in data or len(data['performance']) == 0:
            continue
        
        df_perf = data['performance']
        
        total_signals = len(df_perf)
        correct_signals = df_perf['prediction_correct'].sum()
        accuracy = (correct_signals / total_signals * 100) if total_signals > 0 else 0
        
        buy_signals = len(df_perf[df_perf['signal'] == 'BUY'])
        sell_signals = len(df_perf[df_perf['signal'] == 'SELL'])
        
        avg_confidence = df_perf['confidence'].mean()
        avg_return = df_perf['actual_return'].mean()
        total_return = df_perf['actual_return'].sum()
        
        winning_trades = len(df_perf[df_perf['actual_return'] > 0])
        losing_trades = len(df_perf[df_perf['actual_return'] < 0])
        win_rate = (winning_trades / total_signals * 100) if total_signals > 0 else 0
        
        avg_win = df_perf[df_perf['actual_return'] > 0]['actual_return'].mean() if winning_trades > 0 else 0
        avg_loss = df_perf[df_perf['actual_return'] < 0]['actual_return'].mean() if losing_trades > 0 else 0
        
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        targets_hit = df_perf['target_hit'].sum()
        stops_hit = df_perf['stop_hit'].sum()
        
        avg_days_held = df_perf['days_held'].mean()
        
        summary_data.append({
            'Period': period,
            'Total_Signals': total_signals,
            'BUY_Signals': buy_signals,
            'SELL_Signals': sell_signals,
            'Correct_Predictions': correct_signals,
            'Accuracy_%': round(accuracy, 2),
            'Avg_Confidence_%': round(avg_confidence, 2),
            'Win_Rate_%': round(win_rate, 2),
            'Winning_Trades': winning_trades,
            'Losing_Trades': losing_trades,
            'Avg_Return_%': round(avg_return, 2),
            'Total_Return_%': round(total_return, 2),
            'Avg_Win_%': round(avg_win, 2),
            'Avg_Loss_%': round(avg_loss, 2),
            'Profit_Factor': round(profit_factor, 2),
            'Targets_Hit': targets_hit,
            'Stops_Hit': stops_hit,
            'Avg_Days_Held': round(avg_days_held, 1)
        })
    
    df_summary = pd.DataFrame(summary_data)
    
    print("    Master summary created")
    return df_summary

# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    """Main execution function"""
    
    print("\n" + "="*60)
    print("COMPREHENSIVE MONTHLY BACKTEST")
    print("="*60)
    print(f"\nExcel Data: {EXCEL_FILE}")
    print(f"Output File: {OUTPUT_FILE}")
    print(f"\nCutoff Dates:")
    for period, date in CUTOFF_DATES.items():
        print(f"  - {period}: {date}")
    print(f"\nPerformance tracking up to: {END_DATE}")
    print(f"\nFILTERS APPLIED:")
    print(f"  - Signal Type: {SIGNAL_TYPE} only")
    print(f"  - Min Confidence: {MIN_CONFIDENCE}% (STRONG signals only)")
    print("="*60)
    
    # Load Excel data
    print("\n[*] Loading Excel data...")
    try:
        excel_loader = ExcelDataLoader(EXCEL_FILE)
        print(f"[OK] Loaded {len(excel_loader.sheet_names)} sheets from Excel")
    except Exception as e:
        print(f" Error loading Excel: {e}")
        return
    
    # Load AI models
    signal_gen = load_ai_models()
    trained_stocks = sorted(signal_gen.models.keys())
    print(f" Will process {len(trained_stocks)} trained stocks")
    
    # Generate signals and calculate performance for each period
    all_results = {}
    
    for period, cutoff_date in CUTOFF_DATES.items():
        print(f"\n{'='*60}")
        print(f"PROCESSING: {period}")
        print(f"{'='*60}")
        
        # Generate signals
        df_signals = generate_signals_for_date(
            excel_loader, 
            signal_gen, 
            cutoff_date, 
            trained_stocks
        )
        
        if len(df_signals) == 0:
            print(f"    No signals generated for {period}")
            continue
        
        # Calculate performance
        df_performance = calculate_performance(
            df_signals,
            excel_loader,
            cutoff_date,
            END_DATE
        )
        
        all_results[period] = {
            'signals': df_signals,
            'performance': df_performance
        }
    
    # Create master summary
    df_summary = create_master_summary(all_results)
    
    # Save to Excel
    print(f"\n{'='*60}")
    print("SAVING RESULTS TO EXCEL")
    print(f"{'='*60}")
    
    # Helper function to remove timezone from datetime columns
    def strip_timezone(df):
        df = df.copy()
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].apply(lambda x: x.replace(tzinfo=None) if pd.notna(x) and hasattr(x, 'replace') else x)
        return df
    
    try:
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
            # Save master summary first
            df_summary_clean = strip_timezone(df_summary)
            df_summary_clean.to_excel(writer, sheet_name='MASTER_SUMMARY', index=False)
            print(f" Saved MASTER_SUMMARY sheet")
            
            # Save individual period results
            for period, data in all_results.items():
                # Signals sheet
                if len(data['signals']) > 0:
                    sheet_name = f"{period}_Signals"
                    signals_clean = strip_timezone(data['signals'])
                    signals_clean.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f" Saved {sheet_name} sheet")
                
                # Performance sheet
                if len(data['performance']) > 0:
                    sheet_name = f"{period}_Performance"
                    performance_clean = strip_timezone(data['performance'])
                    performance_clean.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f" Saved {sheet_name} sheet")
        
        print(f"\n{'='*60}")
        print(f" SUCCESS!")
        print(f"{'='*60}")
        print(f"\n Results saved to: {OUTPUT_FILE}")
        print(f"\nSheets created:")
        print(f"  1. MASTER_SUMMARY (overall comparison)")
        for period in CUTOFF_DATES.keys():
            print(f"  2. {period}_Signals (generated signals)")
            print(f"  3. {period}_Performance (actual results)")
        
        print(f"\n{'='*60}")
        print("BACKTEST COMPLETE!")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f" Error saving Excel: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

