# -*- coding: utf-8 -*-
"""Simple test to check if backtest setup works"""

import sys
import os

print("="*60, flush=True)
print("TESTING BACKTEST SETUP", flush=True)
print("="*60, flush=True)

# Test 1: Check Python
print(f"\n1. Python version: {sys.version}", flush=True)
print(f"2. Working directory: {os.getcwd()}", flush=True)

# Test 2: Check imports
print("\n3. Testing imports...", flush=True)
try:
    import pandas as pd
    print("   ✅ pandas imported", flush=True)
except Exception as e:
    print(f"   ❌ pandas error: {e}", flush=True)

try:
    import numpy as np
    print("   ✅ numpy imported", flush=True)
except Exception as e:
    print(f"   ❌ numpy error: {e}", flush=True)

# Test 3: Check Excel file
print("\n4. Testing Excel file...", flush=True)
excel_file = r"C:\python\MG AI\Nifty200_MASTER_10yeardata.xlsx"
if os.path.exists(excel_file):
    print(f"   ✅ Excel file found: {excel_file}", flush=True)
    try:
        from excel_data_loader import ExcelDataLoader
        loader = ExcelDataLoader(excel_file)
        print(f"   ✅ Excel loader works, found {len(loader.sheet_names)} sheets", flush=True)
    except Exception as e:
        print(f"   ❌ Excel loader error: {e}", flush=True)
else:
    print(f"   ❌ Excel file not found: {excel_file}", flush=True)

# Test 4: Check AI models
print("\n5. Testing AI models...", flush=True)
try:
    from signal_generator_fixed import SignalGeneratorFixed
    from pathlib import Path
    
    models_dir = Path(__file__).parent / 'models'
    signal_gen = SignalGeneratorFixed(models_dir=str(models_dir))
    
    if models_dir.exists():
        model_count = 0
        for model_file in models_dir.glob("xgb_NSE_*.pkl"):
            symbol = model_file.stem.replace("xgb_", "")
            signal_gen.load_model(symbol)
            model_count += 1
        print(f"   ✅ Loaded {model_count} AI models", flush=True)
    else:
        print(f"   ❌ Models directory not found: {models_dir}", flush=True)
except Exception as e:
    print(f"   ❌ AI models error: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("\n" + "="*60, flush=True)
print("TEST COMPLETE!", flush=True)
print("="*60, flush=True)

