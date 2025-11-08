"""Quick training for Commodities (Gold/Silver) - Auto mode"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

from train_single_stock import SingleStockTrainer

# Test with MCX Gold
commodity = 'MCX_GOLD'  # Change to 'MCX_SILVER' to test silver

print(f"Starting training for {commodity}...")
print("="*70)

trainer = SingleStockTrainer(stock_symbol=commodity)

results = trainer.run_full_pipeline(
    profit_target=0.03,      # 3% profit target
    forward_days=5,          # Look 5 days ahead
    use_vwap_strategy=True,  # Use VWAP ladder strategy
    tune_hyperparameters=False,  # Quick training (set True for better accuracy)
    train_ratio=0.7,         # 70% train, 30% test
    save_model=True          # Save the model
)

print("\n" + "="*70)
if results['success']:
    print("SUCCESS!")
    print(f"Accuracy: {results['accuracy']*100:.2f}%")
    print(f"F1 Score: {results['f1_score']:.4f}")
    print(f"Time: {results['duration']:.1f} seconds")
else:
    print("FAILED!")
    print(f"Error: {results.get('error', 'Unknown')}")
print("="*70)
