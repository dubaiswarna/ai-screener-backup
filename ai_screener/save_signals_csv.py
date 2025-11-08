"""
CSV Signal Saver - BACKUP SOLUTION
===================================
Saves signals to CSV file so you can track them even if database has issues
"""

import pandas as pd
from datetime import datetime
from pathlib import Path

def save_signals_to_csv(df_signals, filename=None):
    """
    Save signals to CSV file.
    
    Args:
        df_signals: DataFrame with signals
        filename: Optional custom filename
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_signals_{timestamp}.csv"
    
    # Create signals directory
    signals_dir = Path("saved_signals")
    signals_dir.mkdir(exist_ok=True)
    
    # Save to CSV
    filepath = signals_dir / filename
    df_signals.to_csv(filepath, index=False)
    
    print(f"✅ Signals saved to: {filepath}")
    return str(filepath)

def load_all_saved_signals():
    """Load all saved signal CSV files."""
    signals_dir = Path("saved_signals")
    
    if not signals_dir.exists():
        return pd.DataFrame()
    
    all_signals = []
    for csv_file in signals_dir.glob("ai_signals_*.csv"):
        df = pd.read_csv(csv_file)
        all_signals.append(df)
    
    if all_signals:
        return pd.concat(all_signals, ignore_index=True)
    else:
        return pd.DataFrame()

def get_latest_signals():
    """Get signals from most recent file."""
    signals_dir = Path("saved_signals")
    
    if not signals_dir.exists():
        return pd.DataFrame()
    
    csv_files = list(signals_dir.glob("ai_signals_*.csv"))
    if not csv_files:
        return pd.DataFrame()
    
    # Get most recent file
    latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
    return pd.read_csv(latest_file)

