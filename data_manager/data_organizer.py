"""
Data Organizer
Organizes and validates all data files (stocks, commodities, MCX)
"""

import os
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple


class DataOrganizer:
    """Organize and validate data files"""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent
        self.base_path = Path(base_path)
        
        # Define data folders
        self.data_folders = {
            'nifty50': self.base_path / 'AI_Screener_Complete' / 'Nify50_data',
            'nifty200': self.base_path / 'Nifty200_Data',
            'nifty500': self.base_path / 'Nifty500_Data',
            'smallcap250': self.base_path / 'Smallcap250_Data',
            'mcx': self.base_path / 'MCX_Data',
            'mcx_app': self.base_path / 'AI_Screener_Complete' / 'MCX_data'
        }
    
    def scan_all_data(self) -> Dict[str, int]:
        """Scan all data folders and count files"""
        results = {}
        
        for category, folder in self.data_folders.items():
            if folder.exists():
                csv_files = list(folder.glob('*.csv'))
                results[category] = len(csv_files)
            else:
                results[category] = 0
        
        return results
    
    def validate_csv_file(self, file_path: Path) -> Tuple[bool, str, Dict]:
        """Validate a CSV file and return status"""
        try:
            df = pd.read_csv(file_path)
            
            # Check required columns
            required_cols = ['time', 'open', 'high', 'low', 'close']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                return False, f"Missing columns: {missing_cols}", {}
            
            # Get data info
            info = {
                'rows': len(df),
                'start_date': df['time'].iloc[0] if len(df) > 0 else None,
                'end_date': df['time'].iloc[-1] if len(df) > 0 else None,
                'columns': list(df.columns)
            }
            
            return True, "Valid", info
            
        except Exception as e:
            return False, f"Error: {str(e)}", {}
    
    def organize_mcx_data(self, source_folder: str = None) -> Dict:
        """Organize MCX data from source to proper locations"""
        if source_folder is None:
            source_folder = self.base_path / 'MCX_Data'
        else:
            source_folder = Path(source_folder)
        
        if not source_folder.exists():
            return {'error': f'Source folder not found: {source_folder}'}
        
        results = {
            'processed': 0,
            'copied': 0,
            'errors': []
        }
        
        # Get all CSV files
        csv_files = list(source_folder.glob('*.csv'))
        results['processed'] = len(csv_files)
        
        # Create destination if needed
        dest_folder = self.data_folders['mcx_app']
        dest_folder.mkdir(parents=True, exist_ok=True)
        
        for file in csv_files:
            try:
                # Read and validate
                df = pd.read_csv(file)
                
                # Save to app folder
                dest_file = dest_folder / file.name
                df.to_csv(dest_file, index=False)
                results['copied'] += 1
                
            except Exception as e:
                results['errors'].append(f"{file.name}: {str(e)}")
        
        return results
    
    def get_data_summary(self) -> Dict:
        """Get summary of all available data"""
        summary = {
            'folders': {},
            'total_files': 0,
            'total_size_mb': 0
        }
        
        for category, folder in self.data_folders.items():
            if folder.exists():
                csv_files = list(folder.glob('*.csv'))
                total_size = sum(f.stat().st_size for f in csv_files)
                
                summary['folders'][category] = {
                    'path': str(folder),
                    'files': len(csv_files),
                    'size_mb': round(total_size / (1024 * 1024), 2)
                }
                
                summary['total_files'] += len(csv_files)
                summary['total_size_mb'] += round(total_size / (1024 * 1024), 2)
        
        return summary
    
    def validate_all_data(self) -> Dict:
        """Validate all data files"""
        results = {
            'valid': 0,
            'invalid': 0,
            'errors': []
        }
        
        for category, folder in self.data_folders.items():
            if folder.exists():
                for file in folder.glob('*.csv'):
                    is_valid, message, info = self.validate_csv_file(file)
                    
                    if is_valid:
                        results['valid'] += 1
                    else:
                        results['invalid'] += 1
                        results['errors'].append({
                            'file': str(file),
                            'error': message
                        })
        
        return results


if __name__ == "__main__":
    organizer = DataOrganizer()
    
    print("="*60)
    print("DATA ORGANIZER - SUMMARY")
    print("="*60)
    
    # Scan all data
    scan_results = organizer.scan_all_data()
    print("\n[*] Data Files Count:")
    for category, count in scan_results.items():
        print(f"    {category:15}: {count:4} files")
    
    # Get summary
    summary = organizer.get_data_summary()
    print(f"\n[*] Total Files: {summary['total_files']}")
    print(f"[*] Total Size: {summary['total_size_mb']:.2f} MB")
    
    print("\n" + "="*60)

