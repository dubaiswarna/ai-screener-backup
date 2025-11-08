# Feb 2025 Experiment - README

## Purpose
Generate signals using data up to February 28, 2025

## What This Does
1. Extracts historical data till Feb 2025
2. Uses trained AI models (read-only from base system)
3. Generates delivery-based signals
4. Saves results to CSV

## Base System Protection
✅ Base system files: UNTOUCHED
✅ Trained models: READ ONLY
✅ Original data: NOT MODIFIED
✅ All work: In Feb2025_Experiment folder only

## How to Run

### Quick Start:
```
Double-click: RUN_FEB2025_EXPERIMENT.bat
```

### Manual:
```bash
cd Feb2025_Experiment
python extract_feb2025_data.py
python generate_feb2025_signals.py
```

## What You Get
- CSV file: signals_feb2025_TIMESTAMP.csv
- Contains: Symbol, Signal, Confidence, Entry, Target, Stop, Validation
- Only HIGH-QUALITY signals (80%+ confidence, 3/4 checks passed)

## Settings
- Cutoff date: February 28, 2025
- Mode: DELIVERY (30-60 days)
- Confidence: 80%+ only
- Target: 10% gain
- Stop Loss: 7%

## Validation Criteria (Must pass 3/4)
1. Price above 50-day MA
2. SMA 50 > SMA 200
3. RSI < 50
4. Momentum positive (20d)

## Workflow
```
Original Data (Nifty200_Data/)
        ↓ (read, filter, copy)
Feb 2025 Data (data_till_feb2025/)
        ↓ (use for analysis)
AI Models (Nifty200_Models_Pro/) - READ ONLY
        ↓ (generate signals)
Results (signals_feb2025_*.csv)
```

## Safety
- No files modified outside Feb2025_Experiment/
- Base system remains intact
- Can delete this folder anytime

## Time Required
- Data extraction: 1-2 minutes
- Signal generation: 3-5 minutes
- Total: 5-7 minutes

Ready to generate signals! 🚀

