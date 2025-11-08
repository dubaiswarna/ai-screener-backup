"""
Train AI Models on Commodity Data (Gold & Silver)
=================================================
Quick training script for MCX commodities using the same pipeline as stocks.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

from train_single_stock import SingleStockTrainer
from pathlib import Path

def train_commodity(commodity_symbol: str, data_folder: str = "Commodity_data"):
    """
    Train model for a commodity.
    
    Args:
        commodity_symbol: MCX_GOLD or MCX_SILVER
        data_folder: Folder containing commodity CSV files
    """
    print("\n" + "="*70)
    print(f"TRAINING AI MODEL FOR {commodity_symbol}")
    print("="*70)
    
    # Check if data exists
    data_path = Path(data_folder)
    csv_file = data_path / f"{commodity_symbol}, 1D.csv"
    
    if not csv_file.exists():
        print(f"ERROR: Data file not found: {csv_file}")
        print(f"\nPlease run: python fetch_commodity_data.py first")
        return None
    
    print(f"Data file: {csv_file.name}")
    print(f"File size: {csv_file.stat().st_size / 1024:.1f} KB")
    
    # Create trainer with custom data directory
    trainer = SingleStockTrainer(
        stock_symbol=commodity_symbol,
        data_dir=str(data_folder)
    )
    
    # Run training pipeline
    print("\nStarting training pipeline...")
    print("-" * 70)
    
    results = trainer.run_full_pipeline(
        profit_target=0.02,          # 2% profit target (commodities can be less volatile)
        forward_days=3,              # Look 3 days ahead
        use_vwap_strategy=True,      # Use VWAP ladder strategy
        tune_hyperparameters=False,  # Quick training (set True for better accuracy)
        train_ratio=0.7,             # 70% train, 30% test
        save_model=True              # Save the trained model
    )
    
    # Print results
    print("\n" + "="*70)
    if results['success']:
        print("✓ TRAINING SUCCESSFUL!")
        print("="*70)
        print(f"Commodity:      {commodity_symbol}")
        print(f"Accuracy:       {results['accuracy']*100:.2f}%")
        print(f"Precision:      {results.get('precision', 0)*100:.2f}%")
        print(f"Recall:         {results.get('recall', 0)*100:.2f}%")
        print(f"F1 Score:       {results['f1_score']:.4f}")
        print(f"Training Time:  {results['duration']:.1f} seconds")
        
        if 'model_path' in results:
            print(f"Model Saved:    {results['model_path']}")
    else:
        print("✗ TRAINING FAILED!")
        print("="*70)
        print(f"Error: {results.get('error', 'Unknown error')}")
    
    print("="*70)
    
    return results


def train_all_commodities():
    """Train models for all commodities."""
    commodities = ['MCX_GOLD', 'MCX_SILVER']
    
    print("\n" + "="*70)
    print("TRAINING ALL COMMODITIES")
    print("="*70)
    print(f"Total commodities: {len(commodities)}")
    for commodity in commodities:
        print(f"  - {commodity}")
    print("="*70)
    
    results = {}
    
    for commodity in commodities:
        result = train_commodity(commodity)
        results[commodity] = result
        
        # Wait a moment between trainings
        import time
        time.sleep(2)
    
    # Summary
    print("\n" + "="*70)
    print("TRAINING SUMMARY")
    print("="*70)
    
    for commodity, result in results.items():
        if result and result['success']:
            acc = result['accuracy'] * 100
            f1 = result['f1_score']
            time_taken = result['duration']
            print(f"{commodity:15} ✓ SUCCESS  Acc: {acc:5.1f}%  F1: {f1:.3f}  Time: {time_taken:.0f}s")
        else:
            print(f"{commodity:15} ✗ FAILED")
    
    print("="*70)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train AI models on commodity data')
    parser.add_argument('--commodity', type=str, choices=['MCX_GOLD', 'MCX_SILVER', 'ALL'],
                       default='ALL', help='Commodity to train (default: ALL)')
    parser.add_argument('--data-folder', type=str, default='Commodity_data',
                       help='Folder containing commodity CSV files')
    
    args = parser.parse_args()
    
    if args.commodity == 'ALL':
        train_all_commodities()
    else:
        train_commodity(args.commodity, args.data_folder)

