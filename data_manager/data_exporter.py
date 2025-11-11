"""
Data Exporter
Export and backup data for easy transfer between systems
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import json
import pandas as pd
from io import BytesIO


class DataExporter:
    """Export and package data for download/transfer"""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent
        self.base_path = Path(base_path)
        self.export_dir = self.base_path / 'data_exports'
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup_package(self, include_folders: List[str] = None, 
                            output_name: str = None) -> Dict:
        """
        Create a compressed backup of all data
        
        Args:
            include_folders: List of folders to include
            output_name: Custom output filename
        
        Returns:
            Dict with status and file path
        """
        if include_folders is None:
            include_folders = [
                'Nifty200_Data',
                'Nifty500_Data',
                'Smallcap250_Data',
                'MCX_Data',
                'AI_Screener_Complete/MCX_data',
                'AI_Screener_Complete/Nify50_data'
            ]
        
        if output_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_name = f'AllData_Backup_{timestamp}.zip'
        
        output_path = self.export_dir / output_name
        
        print(f"[*] Creating backup package: {output_name}")
        
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                total_files = 0
                
                for folder in include_folders:
                    folder_path = self.base_path / folder
                    
                    if not folder_path.exists():
                        print(f"[!] Skipping {folder} (not found)")
                        continue
                    
                    print(f"[*] Adding {folder}...")
                    
                    # Add all CSV files from this folder
                    for file in folder_path.glob('*.csv'):
                        arcname = f"{folder}/{file.name}"
                        zipf.write(file, arcname)
                        total_files += 1
                
                # Add metadata
                metadata = {
                    'created': datetime.now().isoformat(),
                    'folders': include_folders,
                    'total_files': total_files,
                    'source': 'MG AI Screener Data Manager'
                }
                
                zipf.writestr('metadata.json', json.dumps(metadata, indent=2))
            
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            
            print(f"[+] Backup created successfully!")
            print(f"    Files: {total_files}")
            print(f"    Size: {file_size_mb:.2f} MB")
            print(f"    Location: {output_path}")
            
            return {
                'success': True,
                'file': str(output_path),
                'size_mb': round(file_size_mb, 2),
                'files_count': total_files
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_mcx_only(self, output_name: str = None) -> Dict:
        """Export only MCX data"""
        if output_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_name = f'MCX_Data_Export_{timestamp}.zip'
        
        return self.create_backup_package(
            include_folders=['MCX_Data', 'AI_Screener_Complete/MCX_data'],
            output_name=output_name
        )
    
    def export_nifty50(self, output_name: str = None) -> Dict:
        """Export only Nifty 50 data"""
        if output_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_name = f'Nifty50_Data_Export_{timestamp}.zip'
        
        return self.create_backup_package(
            include_folders=['AI_Screener_Complete/Nify50_data'],
            output_name=output_name
        )
    
    def export_all_stocks(self, output_name: str = None) -> Dict:
        """Export all stock data (Nifty 200/500, Smallcap)"""
        if output_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_name = f'AllStocks_Data_Export_{timestamp}.zip'
        
        return self.create_backup_package(
            include_folders=[
                'Nifty200_Data',
                'Nifty500_Data',
                'Smallcap250_Data',
                'AI_Screener_Complete/Nify50_data'
            ],
            output_name=output_name
        )
    
    def list_exports(self) -> List[Dict]:
        """List all available export files"""
        exports = []
        
        for file in self.export_dir.glob('*.zip'):
            exports.append({
                'name': file.name,
                'size_mb': round(file.stat().st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return sorted(exports, key=lambda x: x['created'], reverse=True)
    
    def create_download_link(self, export_name: str) -> str:
        """Generate download link for an export"""
        export_path = self.export_dir / export_name
        
        if export_path.exists():
            return str(export_path.absolute())
        else:
            return None
    
    def create_excel_package(self, include_folders: List[str] = None, 
                            output_name: str = None, max_sheets: int = 50) -> Dict:
        """
        Create an Excel file with multiple sheets (one per stock)
        
        Args:
            include_folders: List of folders to include
            output_name: Custom output filename
            max_sheets: Maximum number of sheets per Excel file (Excel limit: 255)
        
        Returns:
            Dict with status and file path
        """
        if include_folders is None:
            include_folders = [
                'AI_Screener_Complete/Nify50_data',
                'AI_Screener_Complete/MCX_data'
            ]
        
        if output_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_name = f'StockData_Excel_{timestamp}.xlsx'
        
        output_path = self.export_dir / output_name
        
        print(f"[*] Creating Excel package: {output_name}")
        
        try:
            # Collect all CSV files
            csv_files = []
            for folder in include_folders:
                folder_path = self.base_path / folder
                if folder_path.exists():
                    csv_files.extend(list(folder_path.glob('*.csv'))[:max_sheets])
            
            if not csv_files:
                return {
                    'success': False,
                    'error': 'No CSV files found'
                }
            
            print(f"[*] Processing {len(csv_files)} files...")
            
            # Create Excel writer
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for idx, csv_file in enumerate(csv_files, 1):
                    try:
                        # Read CSV
                        df = pd.read_csv(csv_file)
                        
                        # Create sheet name (Excel sheet names max 31 chars)
                        sheet_name = csv_file.stem[:31]
                        
                        # Write to Excel
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        if idx % 10 == 0:
                            print(f"[*] Processed {idx}/{len(csv_files)} files...")
                    
                    except Exception as e:
                        print(f"[!] Error processing {csv_file.name}: {e}")
                        continue
            
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            
            print(f"[+] Excel package created!")
            print(f"    Sheets: {len(csv_files)}")
            print(f"    Size: {file_size_mb:.2f} MB")
            print(f"    Location: {output_path}")
            
            return {
                'success': True,
                'file': str(output_path),
                'size_mb': round(file_size_mb, 2),
                'sheets_count': len(csv_files)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_excel_bytesio(self, include_folders: List[str] = None, 
                             max_sheets: int = 50) -> BytesIO:
        """
        Create Excel file in memory (for Streamlit downloads)
        
        Args:
            include_folders: List of folders to include
            max_sheets: Maximum sheets per file
        
        Returns:
            BytesIO object with Excel data
        """
        if include_folders is None:
            include_folders = [
                'AI_Screener_Complete/Nify50_data',
                'AI_Screener_Complete/MCX_data'
            ]
        
        # Collect CSV files
        csv_files = []
        for folder in include_folders:
            folder_path = self.base_path / folder
            if folder_path.exists():
                csv_files.extend(list(folder_path.glob('*.csv'))[:max_sheets])
        
        if not csv_files:
            return None
        
        # Create Excel in memory
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file)
                    sheet_name = csv_file.stem[:31]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                except Exception as e:
                    print(f"[!] Error: {csv_file.name}: {e}")
                    continue
        
        output.seek(0)
        return output


if __name__ == "__main__":
    exporter = DataExporter()
    
    print("="*60)
    print("DATA EXPORTER")
    print("="*60)
    print()
    
    # Show existing exports
    exports = exporter.list_exports()
    if exports:
        print("[*] Existing exports:")
        for exp in exports:
            print(f"    - {exp['name']} ({exp['size_mb']} MB) - {exp['created']}")
    else:
        print("[*] No existing exports found")
    
    print("\n" + "="*60)
    print("Ready to create new exports!")
    print("="*60)

