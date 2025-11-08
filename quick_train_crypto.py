"""Quick training for Cryptocurrencies - Test Mode"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

from train_single_stock import SingleStockTrainer

# Test with Bitcoin first
crypto = 'CRYPTO_BTC'  # Change to test other cryptos: ETH, BNB, SOL, etc.

print(f"Starting training for {crypto}...")
print("="*70)

trainer = SingleStockTrainer(stock_symbol=crypto)

results = trainer.run_full_pipeline(
    profit_target=0.05,      # 5% profit target (crypto is more volatile)
    forward_days=3,          # Look 3 days ahead (crypto moves fast)
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
    print("\n💡 TIP: For crypto, try different profit targets:")
    print("   • Day trading: profit_target=0.03 (3%)")
    print("   • Swing trading: profit_target=0.05 (5%)")
    print("   • Position trading: profit_target=0.10 (10%)")
else:
    print("FAILED!")
    print(f"Error: {results.get('error', 'Unknown')}")
print("="*70)

