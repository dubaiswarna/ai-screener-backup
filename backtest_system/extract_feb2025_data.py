"""
Feb 2025 Data Extractor
========================
Extract data up to February 2025 for signal generation
This is experimental work - does not modify base system
"""

import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime

def extract_data_till_feb2025():
    """Extract data from base system up to Feb 2025."""
    
    print("=" * 70)
    print(" FEB 2025 DATA EXTRACTION")
    print("=" * 70)
    
    # Source and destination
    source_dir = Path("../Nifty200_Data")
    dest_dir = Path("data_till_feb2025")
    dest_dir.mkdir(exist_ok=True)
    
    if not source_dir.exists():
        print(f"\nERROR: Source directory not found: {source_dir}")
        print("Make sure you're running from Feb2025_Experiment folder")
        return None
    
    # Cutoff date: February 28, 2025
    cutoff_date = pd.Timestamp("2025-02-28", tz='UTC').tz_convert('Asia/Kolkata')
    
    print(f"\nCutoff date: {cutoff_date.strftime('%B %d, %Y')}")
    print(f"Source: {source_dir.absolute()}")
    print(f"Destination: {dest_dir.absolute()}")
    
    # Process each stock
    all_files = list(source_dir.glob("*.csv"))
    print(f"\nFound {len(all_files)} stock files")
    print("\nProcessing...")
    
    processed = 0
    total_candles_original = 0
    total_candles_filtered = 0
    
    for csv_file in all_files:
        try:
            # Read original data
            df = pd.read_csv(csv_file, parse_dates=['time'])
            original_count = len(df)
            total_candles_original += original_count
            
            # Filter till Feb 2025
            df['time'] = pd.to_datetime(df['time'])
            df_filtered = df[df['time'] <= cutoff_date].copy()
            filtered_count = len(df_filtered)
            total_candles_filtered += filtered_count
            
            # Save filtered data
            output_file = dest_dir / csv_file.name
            df_filtered.to_csv(output_file, index=False)
            
            processed += 1
            if processed % 20 == 0:
                print(f"  Processed {processed}/{len(all_files)} stocks...")
        
        except Exception as e:
            print(f"  ERROR processing {csv_file.name}: {e}")
    
    print(f"\nCompleted: {processed}/{len(all_files)} stocks")
    print(f"\nData Summary:")
    print(f"  Original candles: {total_candles_original:,}")
    print(f"  Filtered candles (till Feb 2025): {total_candles_filtered:,}")
    print(f"  Removed: {total_candles_original - total_candles_filtered:,}")
    
    print(f"\nFiltered data saved to: {dest_dir.absolute()}")
    
    return dest_dir


def main():
    """Main extraction function."""
    print("\nExtracting data till February 2025...")
    print("This will NOT modify your base data!\n")
    
    data_dir = extract_data_till_feb2025()
    
    if data_dir:
        print("\n" + "=" * 70)
        print(" EXTRACTION COMPLETE!")
        print("=" * 70)
        print("\nReady for signal generation!")
        print(f"Data location: {data_dir.absolute()}")


if __name__ == "__main__":
    main()

