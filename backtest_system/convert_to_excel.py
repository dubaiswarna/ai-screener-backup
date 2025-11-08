"""
Convert Feb 2025 Signals to Excel
==================================
Create a professional Excel report from signal results
"""

import pandas as pd
from pathlib import Path
import glob

def convert_signals_to_excel():
    """Convert CSV signals to Excel with formatting."""
    
    # Find the latest signals CSV
    csv_files = list(Path('.').glob('signals_feb2025_*.csv'))
    
    if not csv_files:
        print("ERROR: No signal files found!")
        return
    
    # Get the most recent one
    latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
    print(f"Converting: {latest_csv}")
    
    # Read CSV
    df = pd.read_csv(latest_csv)
    
    print(f"\nSignals found: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Create Excel file
    excel_file = latest_csv.stem + '.xlsx'
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Sheet 1: All Signals
        df.to_excel(writer, sheet_name='All Signals', index=False)
        
        # Sheet 2: High Confidence (90%+)
        df_high = df[df['Confidence'].str.rstrip('%').astype(float) >= 90]
        if len(df_high) > 0:
            df_high.to_excel(writer, sheet_name='High Confidence (90%+)', index=False)
        
        # Sheet 3: Strong Confidence (80-89%)
        df_strong = df[(df['Confidence'].str.rstrip('%').astype(float) >= 80) & 
                       (df['Confidence'].str.rstrip('%').astype(float) < 90)]
        if len(df_strong) > 0:
            df_strong.to_excel(writer, sheet_name='Strong (80-89%)', index=False)
        
        # Sheet 4: Good Confidence (70-79%)
        df_good = df[(df['Confidence'].str.rstrip('%').astype(float) >= 70) & 
                     (df['Confidence'].str.rstrip('%').astype(float) < 80)]
        if len(df_good) > 0:
            df_good.to_excel(writer, sheet_name='Good (70-79%)', index=False)
        
        # Sheet 5: Testing Confidence (65-69%)
        df_test = df[(df['Confidence'].str.rstrip('%').astype(float) >= 65) & 
                     (df['Confidence'].str.rstrip('%').astype(float) < 70)]
        if len(df_test) > 0:
            df_test.to_excel(writer, sheet_name='Testing (65-69%)', index=False)
        
        # Sheet 6: Summary
        summary_data = {
            'Metric': [
                'Total Signals',
                'High Confidence (90%+)',
                'Strong Confidence (80-89%)',
                'Good Confidence (70-79%)',
                'Testing Confidence (65-69%)',
                '',
                'BUY Signals',
                'SELL Signals',
                '',
                'Average Confidence',
                'Highest Confidence',
                'Lowest Confidence'
            ],
            'Value': [
                len(df),
                len(df_high),
                len(df_strong),
                len(df_good),
                len(df_test),
                '',
                len(df[df['Signal'] == 'BUY']),
                len(df[df['Signal'] == 'SELL']),
                '',
                df['Confidence'].str.rstrip('%').astype(float).mean(),
                df['Confidence'].str.rstrip('%').astype(float).max(),
                df['Confidence'].str.rstrip('%').astype(float).min()
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"\nExcel file created: {excel_file}")
    print(f"Location: {Path(excel_file).absolute()}")
    
    print("\nSheets created:")
    print("  1. All Signals - Complete list")
    print(f"  2. High Confidence (90%+) - {len(df_high)} signals")
    print(f"  3. Strong (80-89%) - {len(df_strong)} signals")
    print(f"  4. Good (70-79%) - {len(df_good)} signals")
    print(f"  5. Testing (65-69%) - {len(df_test)} signals")
    print("  6. Summary - Statistics")
    
    return excel_file

if __name__ == "__main__":
    print("=" * 70)
    print(" FEB 2025 SIGNALS - EXCEL CONVERTER")
    print("=" * 70)
    
    excel_file = convert_signals_to_excel()
    
    if excel_file:
        print("\n" + "=" * 70)
        print(" CONVERSION COMPLETE!")
        print("=" * 70)
        print(f"\nOpen file: {excel_file}")

