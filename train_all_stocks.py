"""
Train AI Models for All 42 Stocks
==================================

Automatically trains XGBoost models for all Nifty stocks with VWAP strategy.
"""

import sys
import os
import time
from datetime import datetime

# Add path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

from ai_screener.data_loader import DataLoader
from ai_screener.feature_engineering import FeatureEngineer
from ai_screener.xgboost_trainer import XGBoostTrainer
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.utils.class_weight import compute_sample_weight
import numpy as np


def train_single_stock(stock_symbol, show_details=False):
    """Train model for single stock."""
    try:
        if show_details:
            print(f"\n{'='*70}")
            print(f"Training: {stock_symbol}")
            print(f"{'='*70}")
        
        # Load data
        loader = DataLoader()
        df = loader.load_stock_data(stock_symbol)
        
        if df is None or len(df) < 100:
            return {'success': False, 'error': 'Insufficient data', 'stock': stock_symbol}
        
        if show_details:
            print(f"  ✓ Loaded {len(df)} days")
        
        # Engineer features
        engineer = FeatureEngineer()
        df_features = engineer.engineer_features(df)
        
        # Create labels
        trainer = XGBoostTrainer()
        labels = trainer.create_vwap_ladder_labels(
            df_features,
            profit_target=0.03,
            threshold_amount=500000,
            max_investment=15000,
            forward_days=5
        )
        
        # Get features
        feature_cols = trainer.get_feature_columns(df_features)
        X = df_features[feature_cols].values
        y = labels
        
        # Split
        split_idx = int(len(X) * 0.7)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Calculate sample weights
        sample_weights = compute_sample_weight('balanced', y_train)
        
        # Train model with class weights
        model = XGBClassifier(
            max_depth=5,
            n_estimators=200,
            learning_rate=0.1,
            objective='binary:logistic',
            eval_metric='logloss',
            random_state=42,
            use_label_encoder=False,
            scale_pos_weight=3
        )
        
        model.fit(X_train, y_train, sample_weight=sample_weights)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='binary', zero_division=0)
        
        report = classification_report(y_test, y_pred, 
                                      target_names=['Hold', 'Buy'], 
                                      output_dict=True, 
                                      zero_division=0)
        
        buy_precision = report['Buy']['precision']
        buy_recall = report['Buy']['recall']
        
        if show_details:
            print(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.1f}%)")
            print(f"  Buy Precision: {buy_precision:.4f} ({buy_precision*100:.1f}%)")
            print(f"  Buy Recall:    {buy_recall:.4f} ({buy_recall*100:.1f}%)")
        
        # Save model
        os.makedirs('ai_screener/models', exist_ok=True)
        trainer.model = model
        model_path = f'ai_screener/models/xgb_{stock_symbol}.pkl'
        trainer.save_model(model_path)
        
        if show_details:
            print(f"  ✓ Model saved")
        
        return {
            'success': True,
            'stock': stock_symbol,
            'accuracy': accuracy,
            'buy_precision': buy_precision,
            'buy_recall': buy_recall,
            'f1_score': f1,
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
        
    except Exception as e:
        return {
            'success': False,
            'stock': stock_symbol,
            'error': str(e)
        }


def main():
    """Train models for all stocks."""
    print("\n" + "="*70)
    print("AI SCREENER - BATCH TRAINING FOR ALL STOCKS")
    print("="*70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    # Get all stocks
    loader = DataLoader()
    all_stocks = loader.get_all_stocks()
    
    print(f"\nFound {len(all_stocks)} stocks to train")
    print("\nConfiguration:")
    print("  Profit Target: 3%")
    print("  Forward Days: 5")
    print("  Strategy: VWAP Ladder")
    print("  Class Weights: Balanced (3x for BUY)")
    print("  Model: XGBoost (200 trees)")
    
    confirm = input(f"\nProceed with training {len(all_stocks)} stocks? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Training cancelled.")
        return
    
    print("\n" + "="*70)
    print("STARTING BATCH TRAINING...")
    print("="*70)
    
    results = []
    successful = 0
    failed = 0
    
    for idx, stock in enumerate(all_stocks, 1):
        print(f"\n[{idx}/{len(all_stocks)}] {stock}...", end=" ", flush=True)
        
        result = train_single_stock(stock, show_details=False)
        results.append(result)
        
        if result['success']:
            successful += 1
            print(f"✓ (Acc: {result['accuracy']*100:.1f}%, Buy Prec: {result['buy_precision']*100:.1f}%)")
        else:
            failed += 1
            print(f"✗ ({result.get('error', 'Unknown error')})")
    
    # Summary
    duration = time.time() - start_time
    
    print("\n" + "="*70)
    print("TRAINING COMPLETED!")
    print("="*70)
    print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"Successful: {successful}/{len(all_stocks)}")
    print(f"Failed: {failed}/{len(all_stocks)}")
    
    # Calculate averages
    successful_results = [r for r in results if r['success']]
    if successful_results:
        avg_accuracy = np.mean([r['accuracy'] for r in successful_results])
        avg_precision = np.mean([r['buy_precision'] for r in successful_results])
        avg_recall = np.mean([r['buy_recall'] for r in successful_results])
        
        print(f"\nAverage Performance:")
        print(f"  Accuracy:      {avg_accuracy:.4f} ({avg_accuracy*100:.1f}%)")
        print(f"  Buy Precision: {avg_precision:.4f} ({avg_precision*100:.1f}%)")
        print(f"  Buy Recall:    {avg_recall:.4f} ({avg_recall*100:.1f}%)")
    
    # Top performers
    print(f"\nTop 10 Best Performers (by Buy Precision):")
    top_10 = sorted(successful_results, key=lambda x: x['buy_precision'], reverse=True)[:10]
    for i, r in enumerate(top_10, 1):
        print(f"  {i:2d}. {r['stock']:<20s} - Precision: {r['buy_precision']*100:.1f}%, Recall: {r['buy_recall']*100:.1f}%")
    
    # Failed stocks
    if failed > 0:
        print(f"\nFailed Stocks:")
        for r in results:
            if not r['success']:
                print(f"  - {r['stock']}: {r.get('error', 'Unknown')}")
    
    print(f"\nAll models saved in: ai_screener/models/")
    print(f"Ready to use in Daily Screener!")
    print("="*70)
    
    # Save summary
    import pandas as pd
    df_results = pd.DataFrame(successful_results)
    df_results.to_csv('training_summary.csv', index=False)
    print(f"\n✓ Training summary saved: training_summary.csv")


if __name__ == '__main__':
    main()

