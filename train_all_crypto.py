"""
Train AI Models for All Cryptocurrencies
=========================================
Batch training for all 8 major cryptocurrencies
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

from train_single_stock import SingleStockTrainer
import time
import pandas as pd

def train_crypto(symbol, name):
    """Train AI model for one cryptocurrency"""
    print(f"\n{'='*70}")
    print(f"[{name}] TRAINING AI MODEL")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    try:
        trainer = SingleStockTrainer(stock_symbol=symbol)
        
        results = trainer.run_full_pipeline(
            profit_target=0.05,           # 5% profit (crypto is volatile)
            forward_days=3,               # 3 days ahead (crypto moves fast)
            use_vwap_strategy=True,
            tune_hyperparameters=False,   # Quick training
            train_ratio=0.7,
            save_model=True
        )
        
        duration = time.time() - start_time
        
        if results['success']:
            return {
                'symbol': symbol,
                'name': name,
                'success': True,
                'accuracy': results['accuracy'],
                'f1_score': results['f1_score'],
                'duration': duration
            }
        else:
            return {
                'symbol': symbol,
                'name': name,
                'success': False,
                'error': results.get('error', 'Unknown'),
                'duration': duration
            }
            
    except Exception as e:
        return {
            'symbol': symbol,
            'name': name,
            'success': False,
            'error': str(e),
            'duration': time.time() - start_time
        }

def main():
    """Train all cryptocurrencies"""
    print("\n" + "="*70)
    print("CRYPTOCURRENCY AI TRAINING - BATCH MODE")
    print("="*70)
    print("\nTraining AI models for 8 major cryptocurrencies...")
    print("Estimated time: 5-8 minutes")
    print("="*70 + "\n")
    
    cryptos = [
        ('CRYPTO_BTC', 'Bitcoin 🟠'),
        ('CRYPTO_ETH', 'Ethereum 🔷'),
        ('CRYPTO_BNB', 'Binance Coin 🟡'),
        ('CRYPTO_SOL', 'Solana 🟣'),
        ('CRYPTO_XRP', 'Ripple 🔵'),
        ('CRYPTO_ADA', 'Cardano 🔴'),
        ('CRYPTO_DOGE', 'Dogecoin 🟤'),
        ('CRYPTO_DOT', 'Polkadot ⚪')
    ]
    
    results = []
    start_total = time.time()
    
    for i, (symbol, name) in enumerate(cryptos, 1):
        print(f"\n[{i}/{len(cryptos)}] Processing {name}...")
        result = train_crypto(symbol, name)
        results.append(result)
        
        # Brief pause between trainings
        if i < len(cryptos):
            time.sleep(1)
    
    total_duration = time.time() - start_total
    
    # Summary
    print("\n" + "="*70)
    print("TRAINING SUMMARY - ALL CRYPTOCURRENCIES")
    print("="*70 + "\n")
    
    print(f"{'Crypto':<20} {'Status':<12} {'Accuracy':<12} {'F1 Score':<12} {'Time':<10}")
    print(f"{'-'*20} {'-'*12} {'-'*12} {'-'*12} {'-'*10}")
    
    for result in results:
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        accuracy = f"{result['accuracy']*100:.2f}%" if result['success'] else "N/A"
        f1 = f"{result['f1_score']:.4f}" if result['success'] else "N/A"
        duration = f"{result['duration']:.1f}s"
        print(f"{result['name']:<20} {status:<12} {accuracy:<12} {f1:<12} {duration:<10}")
    
    # Statistics
    successful = [r for r in results if r['success']]
    print("\n" + "="*70)
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    
    if successful:
        avg_accuracy = sum(r['accuracy'] for r in successful) / len(successful)
        best = max(successful, key=lambda x: x['accuracy'])
        
        print(f"📊 Average Accuracy: {avg_accuracy*100:.2f}%")
        print(f"🏆 Best Performer: {best['name']} with {best['accuracy']*100:.2f}%")
    
    print(f"⏱️  Total Time: {total_duration/60:.1f} minutes")
    print("="*70)
    
    print("\n✅ All models saved in: ai_screener/models/")
    print("\nNext steps:")
    print("1. View crypto dashboard: python crypto_dashboard.py")
    print("2. Send Telegram alerts: python send_crypto_alerts.py")
    print("3. Start auto-alerts: python auto_crypto_alerts.py")
    print("="*70 + "\n")
    
    # Save summary
    df_summary = pd.DataFrame(results)
    df_summary.to_csv('crypto_training_summary.csv', index=False)
    print("📄 Summary saved to: crypto_training_summary.csv\n")

if __name__ == '__main__':
    main()

