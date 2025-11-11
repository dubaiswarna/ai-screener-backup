"""
Data Download Manager
Easy script to download and backup all data
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_manager.data_organizer import DataOrganizer
from data_manager.data_downloader import DataDownloader
from data_manager.data_exporter import DataExporter


def show_menu():
    """Show main menu"""
    print("\n" + "="*60)
    print("MG AI SCREENER - DATA MANAGER")
    print("="*60)
    print("\n[1] View Data Summary")
    print("[2] Download MCX Data (25 years)")
    print("[3] Create Full Backup (All Data)")
    print("[4] Create MCX Backup Only")
    print("[5] Create Stocks Backup Only")
    print("[6] Organize MCX Data")
    print("[7] List Available Exports")
    print("[0] Exit")
    print()


def main():
    organizer = DataOrganizer()
    downloader = DataDownloader()
    exporter = DataExporter()
    
    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()
        
        if choice == '1':
            # View data summary
            print("\n" + "="*60)
            print("DATA SUMMARY")
            print("="*60)
            
            summary = organizer.get_data_summary()
            
            print(f"\n[*] Total Files: {summary['total_files']}")
            print(f"[*] Total Size: {summary['total_size_mb']:.2f} MB\n")
            
            for category, info in summary['folders'].items():
                print(f"{category:15}: {info['files']:4} files ({info['size_mb']:.2f} MB)")
                print(f"{'':15}  Path: {info['path']}")
                print()
            
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            # Download MCX data
            print("\n" + "="*60)
            print("DOWNLOAD MCX DATA")
            print("="*60)
            print()
            
            symbols = ['GOLD', 'SILVER', 'CRUDE', 'COPPER', 'NATURAL_GAS']
            print(f"[*] Will download {len(symbols)} commodities: {', '.join(symbols)}")
            print("[*] Duration: 25 years")
            print()
            
            confirm = input("Continue? (y/n): ").strip().lower()
            
            if confirm == 'y':
                results = downloader.download_all_mcx(symbols, years=25)
                
                print(f"\n[+] Downloaded {len(results['successful'])} commodities successfully")
                
                if results['failed']:
                    print(f"\n[-] Failed: {len(results['failed'])}")
                    for item in results['failed']:
                        print(f"    - {item['symbol']}: {item['error']}")
            else:
                print("[!] Cancelled")
            
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            # Create full backup
            print("\n" + "="*60)
            print("CREATE FULL BACKUP")
            print("="*60)
            print()
            print("[*] Creating backup of all data...")
            print("[*] This may take a few minutes...")
            print()
            
            result = exporter.create_backup_package()
            
            if result['success']:
                print(f"\n[+] Backup created successfully!")
                print(f"    Location: {result['file']}")
                print(f"    Size: {result['size_mb']} MB")
                print(f"    Files: {result['files_count']}")
            else:
                print(f"\n[-] Error: {result['error']}")
            
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            # MCX backup
            print("\n" + "="*60)
            print("CREATE MCX BACKUP")
            print("="*60)
            print()
            
            result = exporter.export_mcx_only()
            
            if result['success']:
                print(f"\n[+] MCX backup created!")
                print(f"    Location: {result['file']}")
                print(f"    Size: {result['size_mb']} MB")
            else:
                print(f"\n[-] Error: {result['error']}")
            
            input("\nPress Enter to continue...")
        
        elif choice == '5':
            # Stocks backup
            print("\n" + "="*60)
            print("CREATE STOCKS BACKUP")
            print("="*60)
            print()
            
            result = exporter.export_all_stocks()
            
            if result['success']:
                print(f"\n[+] Stocks backup created!")
                print(f"    Location: {result['file']}")
                print(f"    Size: {result['size_mb']} MB")
            else:
                print(f"\n[-] Error: {result['error']}")
            
            input("\nPress Enter to continue...")
        
        elif choice == '6':
            # Organize MCX data
            print("\n" + "="*60)
            print("ORGANIZE MCX DATA")
            print("="*60)
            print()
            
            result = organizer.organize_mcx_data()
            
            if 'error' in result:
                print(f"[-] Error: {result['error']}")
            else:
                print(f"[+] Processed: {result['processed']} files")
                print(f"[+] Copied: {result['copied']} files")
                
                if result['errors']:
                    print(f"\n[-] Errors: {len(result['errors'])}")
                    for error in result['errors']:
                        print(f"    - {error}")
            
            input("\nPress Enter to continue...")
        
        elif choice == '7':
            # List exports
            print("\n" + "="*60)
            print("AVAILABLE EXPORTS")
            print("="*60)
            print()
            
            exports = exporter.list_exports()
            
            if exports:
                for i, exp in enumerate(exports, 1):
                    print(f"[{i}] {exp['name']}")
                    print(f"    Size: {exp['size_mb']} MB")
                    print(f"    Created: {exp['created']}")
                    print()
            else:
                print("[*] No exports found")
            
            input("\nPress Enter to continue...")
        
        elif choice == '0':
            print("\n[*] Goodbye!")
            break
        
        else:
            print("\n[-] Invalid choice!")
            input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
    except Exception as e:
        print(f"\n[-] Error: {e}")

