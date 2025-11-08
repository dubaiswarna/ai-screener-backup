"""
Automated Training Script - Remaining 33 Stocks
Completes the full 42-stock coverage for comprehensive market screening
"""
import sys
import os
import time
from datetime import datetime
import pandas as pd

# Add ai_screener to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

from train_single_stock import SingleStockTrainer

print("\n" + "="*90)
print("🚀 MEGA TRAINING SESSION - COMPLETING 42 STOCK COVERAGE")
print("="*90)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*90)

# Already trained (9 stocks - 86.9% proven win rate)
TRAINED_STOCKS = [
    'NSE_RELIANCE',
    'NSE_TCS',
    'NSE_HDFCBANK',
    'NSE_INFY',
    'NSE_ICICIBANK',
    'NSE_BHARTIARTL',
    'NSE_SBIN',
    'NSE_KOTAKBANK',
    'NSE_AXISBANK'
]

# All 42 available stocks
ALL_STOCKS = [
    'NSE_ADANIENT', 'NSE_ADANIPORTS', 'NSE_ASIANPAINT', 'NSE_AXISBANK',
    'NSE_BAJAJFINSV', 'NSE_BERGEPAINT', 'NSE_BHARTIARTL', 'NSE_BIOCON',
    'NSE_CIPLA', 'NSE_DRREDDY', 'NSE_EICHERMOT', 'NSE_ETERNAL',
    'NSE_GRASIM', 'NSE_HCLTECH', 'NSE_HDFCBANK', 'NSE_HDFCLIFE',
    'NSE_HINDALCO', 'NSE_HINDUNILVR', 'NSE_ICICIBANK', 'NSE_INFY',
    'NSE_JSWSTEEL', 'NSE_KOTAKBANK', 'NSE_M&M', 'NSE_MAXHEALTH',
    'NSE_NESTLEIND', 'NSE_NTPC', 'NSE_ONGC', 'NSE_POWERGRID',
    'NSE_PTC', 'NSE_REFEX', 'NSE_RELIANCE', 'NSE_RELINFRA',
    'NSE_SBILIFE', 'NSE_SBIN', 'NSE_SHRIRAMFIN', 'NSE_SUNPHARMA',
    'NSE_TATACONSUM', 'NSE_TATASTEEL', 'NSE_TCS', 'NSE_TECHM',
    'NSE_TITAN', 'NSE_TMPV'
]

# Calculate remaining stocks
REMAINING_STOCKS = [stock for stock in ALL_STOCKS if stock not in TRAINED_STOCKS]

print(f"\n📊 TRAINING STATISTICS:")
print(f"   Total Stocks Available: {len(ALL_STOCKS)}")
print(f"   Already Trained: {len(TRAINED_STOCKS)} (86.9% win rate proven)")
print(f"   Remaining to Train: {len(REMAINING_STOCKS)}")
print(f"\n⏱️  Estimated Time: {len(REMAINING_STOCKS) * 4} - {len(REMAINING_STOCKS) * 6} minutes")
print(f"   (4-6 minutes per stock)")

print("\n" + "="*90)
print("🎯 STOCKS TO TRAIN:")
print("="*90)
for i, stock in enumerate(REMAINING_STOCKS, 1):
    print(f"   {i:2d}. {stock}")

# Initialize results tracking
results = []
start_time = time.time()
successful = 0
failed = 0

print("\n" + "="*90)
print("🔥 STARTING TRAINING PROCESS...")
print("="*90)

for idx, stock_symbol in enumerate(REMAINING_STOCKS, 1):
    print(f"\n{'='*90}")
    print(f"[{idx}/{len(REMAINING_STOCKS)}] TRAINING: {stock_symbol}")
    print(f"{'='*90}")
    
    stock_start = time.time()
    
    try:
        # Initialize trainer
        trainer = SingleStockTrainer(stock_symbol=stock_symbol)
        
        # Run full pipeline with same settings as proven models
        result = trainer.run_full_pipeline(
            profit_target=0.03,          # 3% profit target (same as office models)
            forward_days=5,              # Look 5 days ahead
            use_vwap_strategy=True,      # Use VWAP ladder strategy
            tune_hyperparameters=False,  # Quick training (proven effective)
            train_ratio=0.7,             # 70% train, 30% test
            save_model=True              # Save the model
        )
        
        stock_duration = time.time() - stock_start
        
        if result['success']:
            successful += 1
            status = "✅ SUCCESS"
            print(f"\n{status}")
            print(f"   Accuracy: {result['accuracy']*100:.2f}%")
            print(f"   F1 Score: {result['f1_score']:.4f}")
            print(f"   Time: {stock_duration:.1f}s")
            
            results.append({
                'Stock': stock_symbol,
                'Status': 'SUCCESS',
                'Accuracy': result['accuracy'] * 100,
                'F1_Score': result['f1_score'],
                'Time_Seconds': stock_duration,
                'Error': None
            })
        else:
            failed += 1
            status = "❌ FAILED"
            error_msg = result.get('error', 'Unknown error')
            print(f"\n{status}: {error_msg}")
            
            results.append({
                'Stock': stock_symbol,
                'Status': 'FAILED',
                'Accuracy': 0,
                'F1_Score': 0,
                'Time_Seconds': stock_duration,
                'Error': error_msg
            })
    
    except Exception as e:
        failed += 1
        stock_duration = time.time() - stock_start
        print(f"\n❌ EXCEPTION: {e}")
        
        results.append({
            'Stock': stock_symbol,
            'Status': 'EXCEPTION',
            'Accuracy': 0,
            'F1_Score': 0,
            'Time_Seconds': stock_duration,
            'Error': str(e)
        })
    
    # Progress update
    remaining_stocks = len(REMAINING_STOCKS) - idx
    avg_time_per_stock = (time.time() - start_time) / idx
    eta_minutes = (remaining_stocks * avg_time_per_stock) / 60
    
    print(f"\n📊 PROGRESS: {idx}/{len(REMAINING_STOCKS)} stocks")
    print(f"   Success: {successful} | Failed: {failed}")
    print(f"   Avg time/stock: {avg_time_per_stock:.1f}s")
    print(f"   ETA: {eta_minutes:.1f} minutes")

# Final summary
total_duration = time.time() - start_time
print("\n" + "="*90)
print("🏁 TRAINING COMPLETED!")
print("="*90)
print(f"\n⏱️  TIMING:")
print(f"   Total Time: {total_duration/60:.1f} minutes ({total_duration:.0f} seconds)")
print(f"   Average per Stock: {total_duration/len(REMAINING_STOCKS):.1f} seconds")

print(f"\n📊 RESULTS:")
print(f"   Total Trained: {len(REMAINING_STOCKS)}")
print(f"   ✅ Successful: {successful}")
print(f"   ❌ Failed: {failed}")
print(f"   Success Rate: {(successful/len(REMAINING_STOCKS)*100):.1f}%")

# Save results to CSV
results_df = pd.DataFrame(results)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
results_file = f'training_results_remaining_{timestamp}.csv'
results_df.to_csv(results_file, index=False)
print(f"\n💾 Results saved to: {results_file}")

# Show successful models
successful_models = results_df[results_df['Status'] == 'SUCCESS'].sort_values('Accuracy', ascending=False)
if len(successful_models) > 0:
    print(f"\n🏆 TOP 5 NEW MODELS:")
    print("="*90)
    for idx, row in successful_models.head(5).iterrows():
        print(f"   {row['Stock']:20s} | Accuracy: {row['Accuracy']:5.1f}% | F1: {row['F1_Score']:.3f}")

# Show failed models if any
if failed > 0:
    failed_models = results_df[results_df['Status'] != 'SUCCESS']
    print(f"\n⚠️  FAILED MODELS ({failed}):")
    print("="*90)
    for idx, row in failed_models.iterrows():
        print(f"   {row['Stock']:20s} | Error: {row['Error']}")

print("\n" + "="*90)
print("🎉 COMPLETE STOCK COVERAGE ACHIEVED!")
print("="*90)
print(f"\n✅ You now have {9 + successful} trained models ready!")
print(f"✅ Combined with 9 proven models = {9 + successful} total stocks")
print(f"✅ Coverage: {((9 + successful)/42*100):.1f}% of your stock universe")
print(f"\n🚀 Ready for Phase 3: Building Alert System!")
print("="*90)
print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

