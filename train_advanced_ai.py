"""
ADVANCED AI TRAINING FOR MCX COMMODITIES
=========================================
Maximum accuracy training with hyperparameter optimization
Goal: Build world's best commodity trading AI
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

from train_single_stock import SingleStockTrainer
import time

def train_advanced_commodity(commodity_name, symbol):
    """Train with advanced hyperparameter tuning"""
    print(f"\n{'='*70}")
    print(f"🚀 ADVANCED TRAINING: {commodity_name}")
    print(f"{'='*70}\n")
    
    print("⚙️ Configuration:")
    print("  - Hyperparameter Tuning: ENABLED")
    print("  - Feature Engineering: 89 indicators")
    print("  - Training Method: Grid Search with Cross-Validation")
    print("  - Profit Target: 3% (Conservative)")
    print("  - Strategy: VWAP Ladder")
    print("")
    
    start_time = time.time()
    
    try:
        # Initialize trainer
        trainer = SingleStockTrainer(stock_symbol=symbol)
        
        # Run ADVANCED pipeline with tuning
        results = trainer.run_full_pipeline(
            profit_target=0.03,           # 3% profit target
            forward_days=5,               # Look 5 days ahead
            use_vwap_strategy=True,       # Use VWAP strategy
            tune_hyperparameters=True,    # ✅ ENABLE TUNING (takes longer but better accuracy)
            train_ratio=0.75,             # 75% train, 25% test (more training data)
            save_model=True               # Save the optimized model
        )
        
        duration = time.time() - start_time
        
        # Show results
        print(f"\n{'='*70}")
        print(f"🎯 {commodity_name} - ADVANCED TRAINING RESULTS")
        print(f"{'='*70}")
        
        if results['success']:
            print(f"✅ TRAINING SUCCESSFUL!")
            print(f"\n📊 Performance Metrics:")
            print(f"  🎯 Accuracy:       {results['accuracy']*100:.2f}%")
            print(f"  📈 F1 Score:       {results['f1_score']:.4f}")
            print(f"  ⏱️  Training Time:  {duration:.1f} seconds ({duration/60:.1f} minutes)")
            
            # Show improvement potential
            baseline_acc = 94.83 if 'GOLD' in commodity_name else 83.44
            improvement = results['accuracy']*100 - baseline_acc
            
            if improvement > 0:
                print(f"\n🚀 IMPROVEMENT: +{improvement:.2f}% from baseline!")
            
            print(f"\n✅ Optimized model saved!")
            return results
        else:
            print(f"❌ TRAINING FAILED")
            print(f"Error: {results.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Train advanced AI models for both commodities"""
    print("\n" + "="*70)
    print("🌟 ADVANCED AI TRAINING - MAXIMUM ACCURACY MODE")
    print("="*70)
    print("\n⚡ This uses Grid Search with Cross-Validation")
    print("⏱️  Expected time: 5-15 minutes per commodity")
    print("\n" + "="*70 + "\n")
    
    input("Press Enter to start advanced training...")
    
    commodities = [
        ('GOLD', 'MCX_GOLD'),
        ('SILVER', 'MCX_SILVER')
    ]
    
    results_summary = []
    total_start = time.time()
    
    for name, symbol in commodities:
        result = train_advanced_commodity(name, symbol)
        
        if result and result.get('success'):
            results_summary.append({
                'name': name,
                'accuracy': result['accuracy'] * 100,
                'f1_score': result['f1_score']
            })
        
        # Small delay between trainings
        print("\n" + "-"*70)
        time.sleep(2)
    
    total_time = time.time() - total_start
    
    # Final summary
    print("\n" + "="*70)
    print("🏆 ADVANCED TRAINING COMPLETE!")
    print("="*70)
    
    if results_summary:
        print(f"\n📊 Final Results:")
        print(f"{'Commodity':<12} {'Accuracy':<15} {'F1 Score':<10}")
        print(f"{'-'*12} {'-'*15} {'-'*10}")
        
        for result in results_summary:
            print(f"{result['name']:<12} {result['accuracy']:.2f}%{' '*8} {result['f1_score']:.4f}")
        
        # Find best
        best = max(results_summary, key=lambda x: x['accuracy'])
        print(f"\n🏆 Best Model: {best['name']} with {best['accuracy']:.2f}% accuracy")
        print(f"⏱️  Total Time: {total_time/60:.1f} minutes")
        
        print(f"\n✅ Models saved in: ai_screener/models/")
        print(f"✅ Ready for live trading!")
        
        print("\n🎯 Next Steps:")
        print("  1. Run: python ai_live_predictions.py")
        print("  2. View AI signals in browser")
        print("  3. Start live trading with confidence!")
        
    else:
        print("\n❌ No models were successfully trained")
        print("Check the errors above and try again.")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()

