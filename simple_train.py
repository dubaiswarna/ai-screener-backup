"""Simplified training with output"""
import sys
import os

print("="*70, flush=True)
print("AI SCREENER - TRAINING HINDALCO", flush=True)
print("="*70, flush=True)

try:
    # Add path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))
    print("\n1. Importing modules...", flush=True)
    
    from ai_screener.data_loader import DataLoader
    from ai_screener.feature_engineering import FeatureEngineer
    from ai_screener.xgboost_trainer import XGBoostTrainer
    import numpy as np
    
    print("   ✓ Imports successful", flush=True)
    
    # Load data
    print("\n2. Loading HINDALCO data...", flush=True)
    loader = DataLoader()
    df = loader.load_stock_data('NSE_HINDALCO')
    print(f"   ✓ Loaded {len(df)} days of data", flush=True)
    print(f"   Date range: {df['time'].min()} to {df['time'].max()}", flush=True)
    
    # Engineer features
    print("\n3. Engineering features...", flush=True)
    engineer = FeatureEngineer()
    df_features = engineer.engineer_features(df)
    print(f"   ✓ Created {len(df_features.columns)} features", flush=True)
    
    # Create labels
    print("\n4. Creating labels (VWAP strategy)...", flush=True)
    trainer = XGBoostTrainer()
    labels = trainer.create_vwap_ladder_labels(
        df_features,
        profit_target=0.03,
        threshold_amount=500000,
        max_investment=15000,
        forward_days=5
    )
    
    unique, counts = np.unique(labels, return_counts=True)
    print(f"   ✓ Created {len(labels)} labels", flush=True)
    print(f"   Distribution: Hold={counts[0]}, Buy={counts[1] if len(counts)>1 else 0}", flush=True)
    
    # Get features
    print("\n5. Preparing train/test split...", flush=True)
    feature_cols = trainer.get_feature_columns(df_features)
    X = df_features[feature_cols].values
    y = labels
    
    # Split 70/30
    split_idx = int(len(X) * 0.7)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"   ✓ Train: {len(X_train)} samples, Test: {len(X_test)} samples", flush=True)
    
    # Train - Binary classification for VWAP strategy (0=Hold, 1=Buy)
    print("\n6. Training XGBoost model...", flush=True)
    print("   (This may take 10-30 seconds...)", flush=True)
    
    # Calculate class weights to handle imbalance
    # Give more importance to BUY signals (minority class)
    from sklearn.utils.class_weight import compute_sample_weight
    sample_weights = compute_sample_weight('balanced', y_train)
    
    print(f"   Using class weights to balance Hold vs Buy signals...", flush=True)
    
    # For VWAP strategy, we have binary labels (0, 1), not (-1, 0, 1)
    from xgboost import XGBClassifier
    
    model = XGBClassifier(
        max_depth=5,
        n_estimators=200,
        learning_rate=0.1,
        objective='binary:logistic',  # Binary classification
        eval_metric='logloss',
        random_state=42,
        use_label_encoder=False,
        scale_pos_weight=3  # Give 3x weight to positive (BUY) class
    )
    
    model.fit(X_train, y_train, sample_weight=sample_weights)
    trainer.model = model  # Save to trainer object
    print(f"   ✓ Training complete!", flush=True)
    
    # Evaluate
    print("\n7. Evaluating on test set...", flush=True)
    
    # Binary evaluation
    from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
    
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='binary', zero_division=0)
    
    # Classification report
    report = classification_report(y_test, y_pred, target_names=['Hold', 'Buy'], output_dict=True, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)
    
    print("\n" + "="*70, flush=True)
    print("RESULTS", flush=True)
    print("="*70, flush=True)
    print(f"Accuracy:  {accuracy:.4f}  ({accuracy*100:.2f}%)", flush=True)
    print(f"F1 Score:  {f1:.4f}", flush=True)
    print(f"\nBuy Signal Performance:", flush=True)
    print(f"  Precision: {report['Buy']['precision']:.4f} (When model says BUY, it's right {report['Buy']['precision']*100:.1f}% of time)", flush=True)
    print(f"  Recall:    {report['Buy']['recall']:.4f} (Catches {report['Buy']['recall']*100:.1f}% of profitable opportunities)", flush=True)
    print("="*70, flush=True)
    
    # Interpretation
    print("\nInterpretation:", flush=True)
    buy_precision = report['Buy']['precision']
    buy_recall = report['Buy']['recall']
    
    if buy_precision >= 0.40 and buy_recall >= 0.30:
        print("  ✓✓✓ EXCELLENT! Model finds good BUY signals!", flush=True)
    elif buy_precision >= 0.30 and buy_recall >= 0.20:
        print("  ✓✓ GOOD! Usable for screening.", flush=True)
    elif buy_precision >= 0.20:
        print("  ✓ OK. Better than random, but needs improvement.", flush=True)
    else:
        print("  ✗ Poor. Model needs different settings.", flush=True)
    
    # Save model
    print("\n8. Saving model...", flush=True)
    os.makedirs('ai_screener/models', exist_ok=True)
    trainer.save_model('ai_screener/models/xgb_NSE_HINDALCO.pkl')
    
    print("\n" + "="*70, flush=True)
    print("TRAINING COMPLETED SUCCESSFULLY!", flush=True)
    print("="*70, flush=True)

except Exception as e:
    print(f"\n✗ ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

