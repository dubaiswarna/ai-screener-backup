# Data Manager Module

**Centralized data management system for MG AI Screener**

---

## Features

✅ **Data Organization** - Organize and validate all stock/commodity data  
✅ **Data Downloading** - Download MCX commodity data (25+ years)  
✅ **Data Export** - Create compressed backups for easy transfer  
✅ **Data Validation** - Verify data integrity and completeness  

---

## Quick Start

### Option 1: Use the Interactive Manager

**Double-click:**
```
C:\python\MG AI\DOWNLOAD_DATA.bat
```

**Or run:**
```bash
cd "C:\python\MG AI\AI_Screener_Complete"
python DOWNLOAD_DATA.py
```

### Option 2: Use Python API

```python
from data_manager import DataOrganizer, DataDownloader, DataExporter

# View data summary
organizer = DataOrganizer()
summary = organizer.get_data_summary()
print(f"Total files: {summary['total_files']}")

# Download MCX data
downloader = DataDownloader()
result = downloader.download_mcx_commodity('GOLD', years=25)

# Create backup
exporter = DataExporter()
result = exporter.create_backup_package()
print(f"Backup created: {result['file']}")
```

---

## Menu Options

### 1. View Data Summary
- Shows total files and size
- Lists all data folders
- Path information

### 2. Download MCX Data (25 years)
- Downloads GOLD, SILVER, CRUDE, COPPER, NATURAL_GAS
- Uses Yahoo Finance API
- Saves to `MCX_Data/` folder

### 3. Create Full Backup (All Data)
- Backs up ALL stock and commodity data
- Creates compressed ZIP file
- Saves to `data_exports/` folder

### 4. Create MCX Backup Only
- Backs up only MCX commodity data
- Much smaller file size
- Quick download/transfer

### 5. Create Stocks Backup Only
- Backs up Nifty 50/200/500 + Smallcap
- Excludes MCX data
- ~350MB compressed

### 6. Organize MCX Data
- Copies MCX data to app folder
- Validates and formats data
- Ensures consistency

### 7. List Available Exports
- Shows all previously created backups
- File size and creation date
- Easy access to download links

---

## File Structure

```
C:\python\MG AI\
│
├── MCX_Data/                    # Main MCX data storage
│   ├── MCX_GOLD_1d.csv
│   ├── MCX_SILVER_1d.csv
│   └── ...
│
├── Nifty200_Data/               # Nifty 200 stocks
├── Nifty500_Data/               # Nifty 500 stocks
├── Smallcap250_Data/            # Smallcap 250 stocks
│
├── AI_Screener_Complete/
│   ├── MCX_data/                # MCX data for app
│   ├── Nify50_data/             # Nifty 50 stocks
│   │
│   ├── data_manager/            # Data management module
│   │   ├── __init__.py
│   │   ├── data_organizer.py   # Organization & validation
│   │   ├── data_downloader.py  # Download from APIs
│   │   ├── data_exporter.py    # Export & backup
│   │   └── README.md
│   │
│   ├── data_exports/            # Export files (.zip)
│   │   ├── AllData_Backup_20251111_100530.zip
│   │   ├── MCX_Data_Export_20251111_100630.zip
│   │   └── ...
│   │
│   └── DOWNLOAD_DATA.py         # Interactive manager
│
└── DOWNLOAD_DATA.bat            # Quick launch
```

---

## Data Formats

### CSV Structure
All data files follow this format:

```csv
time,open,high,low,close,volume,VWAP
2025-11-10,1000,1020,995,1015,50000,1010
...
```

**Required columns:**
- `time` - Date (YYYY-MM-DD)
- `open` - Opening price
- `high` - Highest price
- `low` - Lowest price
- `close` - Closing price

**Optional columns:**
- `volume` - Trading volume
- `VWAP` - Volume Weighted Average Price

---

## Downloading Fresh Data

### MCX Commodities (Yahoo Finance)

```python
from data_manager import DataDownloader

downloader = DataDownloader()

# Download single commodity
result = downloader.download_mcx_commodity('GOLD', years=25)

# Download all major commodities
results = downloader.download_all_mcx(
    symbols=['GOLD', 'SILVER', 'CRUDE', 'COPPER', 'NATURAL_GAS'],
    years=25
)
```

### Update Existing Data

```python
result = downloader.update_existing_data('MCX_Data/MCX_GOLD_1d.csv')
print(f"Added {result['rows_added']} new rows")
```

---

## Creating Backups

### Full Backup (All Data)

```python
from data_manager import DataExporter

exporter = DataExporter()
result = exporter.create_backup_package()

print(f"Created: {result['file']}")
print(f"Size: {result['size_mb']} MB")
print(f"Files: {result['files_count']}")
```

### MCX Only

```python
result = exporter.export_mcx_only()
# Creates: data_exports/MCX_Data_Export_YYYYMMDD_HHMMSS.zip
```

### Stocks Only

```python
result = exporter.export_all_stocks()
# Creates: data_exports/AllStocks_Data_Export_YYYYMMDD_HHMMSS.zip
```

---

## Organizing Data

### Copy MCX to App Folder

```python
from data_manager import DataOrganizer

organizer = DataOrganizer()
result = organizer.organize_mcx_data()

print(f"Processed: {result['processed']} files")
print(f"Copied: {result['copied']} files")
```

### Validate All Data

```python
result = organizer.validate_all_data()

print(f"Valid: {result['valid']}")
print(f"Invalid: {result['invalid']}")

for error in result['errors']:
    print(f"Error: {error['file']} - {error['error']}")
```

---

## Transferring Data to Another System

### Method 1: Using Backup ZIP

1. Create backup:
   ```
   DOWNLOAD_DATA.bat → Option 3 (Full Backup)
   ```

2. Copy ZIP file from:
   ```
   C:\python\MG AI\AI_Screener_Complete\data_exports\
   ```

3. On new system, extract to:
   ```
   C:\python\MG AI\
   ```

### Method 2: Using Git (for smaller files)

```bash
# Add data to git (be careful with file sizes!)
cd "C:\python\MG AI"
git add MCX_Data/*.csv
git commit -m "Added MCX data"
git push
```

**Note:** GitHub has a 100MB file limit. Use Git LFS for large files or use Method 1.

---

## Troubleshooting

### Issue: No data downloaded

**Solution:**
- Check internet connection
- Yahoo Finance may have rate limits
- Try again after 1-2 minutes

### Issue: Cannot find MCX_Data folder

**Solution:**
```python
from pathlib import Path
Path("C:/python/MG AI/MCX_Data").mkdir(parents=True, exist_ok=True)
```

### Issue: Export file too large

**Solution:**
- Create separate backups (MCX only, Stocks only)
- Upload to Google Drive / Dropbox
- Use Git LFS for large files

---

## API Reference

### DataOrganizer

| Method | Description |
|--------|-------------|
| `scan_all_data()` | Count files in all folders |
| `get_data_summary()` | Get detailed summary with sizes |
| `validate_csv_file(path)` | Validate single CSV |
| `validate_all_data()` | Validate all CSVs |
| `organize_mcx_data(source)` | Copy MCX data to app folder |

### DataDownloader

| Method | Description |
|--------|-------------|
| `download_mcx_commodity(symbol, years)` | Download single commodity |
| `download_all_mcx(symbols, years)` | Download multiple commodities |
| `update_existing_data(file_path)` | Update CSV with latest data |

### DataExporter

| Method | Description |
|--------|-------------|
| `create_backup_package(folders, name)` | Create custom backup |
| `export_mcx_only(name)` | Export MCX data only |
| `export_all_stocks(name)` | Export stock data only |
| `export_nifty50(name)` | Export Nifty 50 only |
| `list_exports()` | List all backup files |

---

## Support

For issues or questions:
1. Check the main README.md
2. Review TODAYS_WORK_SUMMARY_NOV10.md
3. Contact support

---

**Created:** November 11, 2025  
**Version:** 1.0  
**Part of:** MG AI Screener System

