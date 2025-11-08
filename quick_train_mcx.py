"""
Quick Training Test for MCX Gold/Silver
========================================

Tests the AI model on MCX commodity data (Gold and Silver).
Uses the same training pipeline as NSE stocks.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

from train_single_stock import SingleStockTrainer
import time


def train_commodity(symbol: str, profit_target: float = 0.02, forward_days: int = 5):
    """
    Train a model for a specific commodity.
    
    Args:
        symbol: Commodity symbol (e.g., 'MCX_GOLD')
        profit_target: Target profit percentage (e.g., 0.02 = 2%)
        forward_days: Days to look ahead for profit target
    """
    print(f"\n{'='*70}")
    print(f"TRAINING: {symbol}")
    print(f"{'='*70}")
    print(f"Profit Target: {profit_target*100}%")
    print(f"Forward Days: {forward_days}")
    print(f"{'='*70}\n")
    
    start_time = time.time()
    
    try:
        # Create trainer
        trainer = SingleStockTrainer(stock_symbol=symbol)
        
        # Run training pipeline
        results = trainer.run_full_pipeline(
            profit_target=profit_target,
            forward_days=forward_days,
            use_vwap_strategy=True,  # Use VWAP ladder strategy
            tune_hyperparameters=False,  # Quick training (set True for better accuracy)
            train_ratio=0.7,  # 70% train, 30% test
            save_model=True  # Save the trained model
        )
        
        duration = time.time() - start_time
        
        # Print results
        print(f"\n{'='*70}")
        if results['success']:
            print(f"✅ SUCCESS - {symbol}")
            print(f"{'='*70}")
            print(f"Accuracy:     {results['accuracy']*100:.2f}%")
            print(f"Precision:    {results.get('precision', 0)*100:.2f}%")
            print(f"Recall:       {results.get('recall', 0)*100:.2f}%")
            print(f"F1 Score:     {results['f1_score']:.4f}")
            print(f"Training Time: {duration:.1f} seconds")
            print(f"Model Saved:  {results.get('model_path', 'N/A')}")
        else:
            print(f"❌ FAILED - {symbol}")
            print(f"{'='*70}")
            print(f"Error: {results.get('error', 'Unknown error')}")
        print(f"{'='*70}\n")
        
        return results
        
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ ERROR - {symbol}")
        print(f"{'='*70}")
        print(f"Exception: {str(e)}")
        print(f"{'='*70}\n")
        return {'success': False, 'error': str(e)}


def main():
    """Main function to train MCX commodities."""
    print("\n" + "="*70)
    print("MCX COMMODITY AI TRAINING")
    print("="*70)
    print("Training AI models for Gold and Silver futures")
    print("="*70 + "\n")
    
    # Define commodities to train
    commodities = [
        {
            'symbol': 'MCX_GOLD',
            'profit_target': 0.015,  # 1.5% for Gold (lower volatility)
            'forward_days': 5
        },
        {
            'symbol': 'MCX_SILVER',
            'profit_target': 0.025,  # 2.5% for Silver (higher volatility)
            'forward_days': 5
        }
    ]
    
    # Train each commodity
    results = {}
    total_start = time.time()
    
    for commodity in commodities:
        result = train_commodity(
            symbol=commodity['symbol'],
            profit_target=commodity['profit_target'],
            forward_days=commodity['forward_days']
        )
        results[commodity['symbol']] = result
        
        # Short pause between trainings
        time.sleep(1)
    
    total_duration = time.time() - total_start
    
    # Print summary
    print("\n" + "="*70)
    print("TRAINING SUMMARY")
    print("="*70)
    
    for symbol, result in results.items():
        if result['success']:
            print(f"✅ {symbol:15} - Accuracy: {result['accuracy']*100:.2f}% | F1: {result['f1_score']:.4f}")
        else:
            print(f"❌ {symbol:15} - Failed: {result.get('error', 'Unknown')[:40]}")
    
    print("="*70)
    print(f"Total Time: {total_duration:.1f} seconds")
    print("="*70)
    
    # Success rate
    success_count = sum(1 for r in results.values() if r['success'])
    total_count = len(results)
    print(f"\nSuccess Rate: {success_count}/{total_count} ({success_count/total_count*100:.0f}%)")
    
    if success_count == total_count:
        print("\n✅ ALL COMMODITIES TRAINED SUCCESSFULLY!")
        print("\nNext Steps:")
        print("1. Test predictions: python test_mcx_predictions.py")
        print("2. Run live screening: python screener_mcx.py")
    else:
        print("\n⚠️  Some commodities failed to train.")
        print("Check the error messages above for details.")


if __name__ == '__main__':
    main()

