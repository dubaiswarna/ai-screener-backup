"""
Train Ensemble AI Models for MCX Commodities
=============================================
Trains multiple AI algorithms for better accuracy through ensemble voting:
1. XGBoost (Gradient Boosting)
2. Random Forest
3. Extra Trees
4. LightGBM
5. CatBoost
6. AdaBoost
7. Gradient Boosting Classifier
8. Voting Classifier (combines all)
9. Stacking Classifier (meta-learner)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_screener'))

import pandas as pd
import numpy as np
from datetime import datetime
import pickle
from pathlib import Path
import time

# Scikit-learn models
from sklearn.ensemble import (
    RandomForestClassifier, 
    ExtraTreesClassifier, 
    AdaBoostClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
    StackingClassifier
)
from sklearn.metrics import accuracy_score, f1_score, classification_report
from xgboost import XGBClassifier

# Try importing advanced models
try:
    from lightgbm import LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("⚠️  LightGBM not available (optional)")

try:
    from catboost import CatBoostClassifier
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    print("⚠️  CatBoost not available (optional)")

# Import our modules
from ai_screener.data_loader_universal import UniversalDataLoader
from ai_screener.feature_engineering import FeatureEngineer
from ai_screener.xgboost_trainer import XGBoostTrainer

class EnsembleTrainer:
    """Train ensemble of multiple AI models"""
    
    def __init__(self, symbol):
        self.symbol = symbol
        self.models = {}
        self.voting_model = None
        self.stacking_model = None
        
    def prepare_data(self):
        """Load and prepare data"""
        print(f"\n{'='*70}")
        print(f"LOADING DATA FOR {self.symbol}")
        print(f"{'='*70}")
        
        # Load data
        loader = UniversalDataLoader()
        self.df = loader.load_symbol_data(self.symbol)
        
        if self.df is None:
            raise ValueError(f"Could not load data for {self.symbol}")
        
        print(f"✓ Loaded {len(self.df)} days of data")
        
        # Engineer features
        print("\nEngineering features...")
        engineer = FeatureEngineer()
        self.df_features = engineer.create_features(self.df.copy())
        
        # Create labels (VWAP strategy)
        print("Creating labels...")
        trainer_temp = XGBoostTrainer(n_classes=2)
        self.labels = trainer_temp.create_vwap_ladder_labels(
            self.df_features,
            profit_target=0.03,
            forward_days=5
        )
        
        # Remove NaN rows
        valid_indices = ~pd.isna(self.labels)
        self.df_features = self.df_features[valid_indices].reset_index(drop=True)
        self.labels = self.labels[valid_indices]
        
        # Get feature columns
        exclude_cols = ['time', 'open', 'high', 'low', 'close', 'vwap', 'volume']
        self.feature_cols = [col for col in self.df_features.columns if col not in exclude_cols]
        self.feature_cols = [col for col in self.feature_cols 
                            if self.df_features[col].dtype in [np.int64, np.float64]]
        
        # Prepare X and y
        X = self.df_features[self.feature_cols].fillna(0).values
        y = self.labels
        
        # Split data (70% train, 30% test)
        split_idx = int(len(X) * 0.7)
        self.X_train = X[:split_idx]
        self.X_test = X[split_idx:]
        self.y_train = y[:split_idx]
        self.y_test = y[split_idx:]
        
        print(f"\n✓ Features: {len(self.feature_cols)}")
        print(f"✓ Training samples: {len(self.X_train)}")
        print(f"✓ Test samples: {len(self.X_test)}")
        
    def train_all_models(self):
        """Train all available AI models"""
        print(f"\n{'='*70}")
        print("TRAINING ENSEMBLE OF AI MODELS")
        print(f"{'='*70}\n")
        
        # Model 1: XGBoost
        print("[1/9] Training XGBoost...")
        self.models['XGBoost'] = XGBClassifier(
            max_depth=5,
            n_estimators=200,
            learning_rate=0.1,
            objective='binary:logistic',
            random_state=42,
            use_label_encoder=False
        )
        self.models['XGBoost'].fit(self.X_train, self.y_train)
        print("✓ XGBoost trained")
        
        # Model 2: Random Forest
        print("[2/9] Training Random Forest...")
        self.models['RandomForest'] = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        self.models['RandomForest'].fit(self.X_train, self.y_train)
        print("✓ Random Forest trained")
        
        # Model 3: Extra Trees
        print("[3/9] Training Extra Trees...")
        self.models['ExtraTrees'] = ExtraTreesClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.models['ExtraTrees'].fit(self.X_train, self.y_train)
        print("✓ Extra Trees trained")
        
        # Model 4: AdaBoost
        print("[4/9] Training AdaBoost...")
        self.models['AdaBoost'] = AdaBoostClassifier(
            n_estimators=100,
            learning_rate=0.1,
            random_state=42
        )
        self.models['AdaBoost'].fit(self.X_train, self.y_train)
        print("✓ AdaBoost trained")
        
        # Model 5: Gradient Boosting
        print("[5/9] Training Gradient Boosting...")
        self.models['GradientBoosting'] = GradientBoostingClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        self.models['GradientBoosting'].fit(self.X_train, self.y_train)
        print("✓ Gradient Boosting trained")
        
        # Model 6: LightGBM (if available)
        if LIGHTGBM_AVAILABLE:
            print("[6/9] Training LightGBM...")
            self.models['LightGBM'] = LGBMClassifier(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.1,
                random_state=42,
                verbose=-1
            )
            self.models['LightGBM'].fit(self.X_train, self.y_train)
            print("✓ LightGBM trained")
        else:
            print("[6/9] LightGBM not available - skipping")
        
        # Model 7: CatBoost (if available)
        if CATBOOST_AVAILABLE:
            print("[7/9] Training CatBoost...")
            self.models['CatBoost'] = CatBoostClassifier(
                iterations=200,
                depth=5,
                learning_rate=0.1,
                random_state=42,
                verbose=False
            )
            self.models['CatBoost'].fit(self.X_train, self.y_train)
            print("✓ CatBoost trained")
        else:
            print("[7/9] CatBoost not available - skipping")
        
        # Model 8: Voting Classifier (Hard Voting)
        print("[8/9] Creating Voting Ensemble...")
        voting_estimators = [(name, model) for name, model in self.models.items()]
        self.voting_model = VotingClassifier(
            estimators=voting_estimators,
            voting='hard'
        )
        self.voting_model.fit(self.X_train, self.y_train)
        print("✓ Voting Ensemble created")
        
        # Model 9: Stacking Classifier (Meta-learner)
        print("[9/9] Creating Stacking Ensemble...")
        self.stacking_model = StackingClassifier(
            estimators=voting_estimators,
            final_estimator=XGBClassifier(
                max_depth=3,
                n_estimators=100,
                random_state=42,
                use_label_encoder=False
            )
        )
        self.stacking_model.fit(self.X_train, self.y_train)
        print("✓ Stacking Ensemble created")
        
    def evaluate_all_models(self):
        """Evaluate all models on test set"""
        print(f"\n{'='*70}")
        print("EVALUATING ALL MODELS")
        print(f"{'='*70}\n")
        
        results = {}
        
        print(f"{'Model':<25} {'Accuracy':<12} {'F1 Score':<12}")
        print(f"{'-'*25} {'-'*12} {'-'*12}")
        
        # Evaluate individual models
        for name, model in self.models.items():
            y_pred = model.predict(self.X_test)
            acc = accuracy_score(self.y_test, y_pred)
            f1 = f1_score(self.y_test, y_pred, average='binary', zero_division=0)
            results[name] = {'accuracy': acc, 'f1_score': f1}
            print(f"{name:<25} {acc*100:>10.2f}% {f1:>11.4f}")
        
        # Evaluate voting ensemble
        if self.voting_model:
            y_pred = self.voting_model.predict(self.X_test)
            acc = accuracy_score(self.y_test, y_pred)
            f1 = f1_score(self.y_test, y_pred, average='binary', zero_division=0)
            results['Voting Ensemble'] = {'accuracy': acc, 'f1_score': f1}
            print(f"{'Voting Ensemble':<25} {acc*100:>10.2f}% {f1:>11.4f}")
        
        # Evaluate stacking ensemble
        if self.stacking_model:
            y_pred = self.stacking_model.predict(self.X_test)
            acc = accuracy_score(self.y_test, y_pred)
            f1 = f1_score(self.y_test, y_pred, average='binary', zero_division=0)
            results['Stacking Ensemble'] = {'accuracy': acc, 'f1_score': f1}
            print(f"{'Stacking Ensemble':<25} {acc*100:>10.2f}% {f1:>11.4f}")
        
        # Find best model
        best_model = max(results.items(), key=lambda x: x[1]['accuracy'])
        print(f"\n🏆 BEST MODEL: {best_model[0]} with {best_model[1]['accuracy']*100:.2f}% accuracy")
        
        return results, best_model[0]
    
    def save_models(self, best_model_name):
        """Save all trained models"""
        print(f"\n{'='*70}")
        print("SAVING MODELS")
        print(f"{'='*70}\n")
        
        models_dir = Path("ai_screener/models")
        models_dir.mkdir(exist_ok=True)
        
        # Save all individual models
        for name, model in self.models.items():
            filename = f"ensemble_{self.symbol}_{name.replace(' ', '_')}.pkl"
            filepath = models_dir / filename
            with open(filepath, 'wb') as f:
                pickle.dump(model, f)
            print(f"✓ Saved {name}")
        
        # Save ensemble models
        if self.voting_model:
            filepath = models_dir / f"ensemble_{self.symbol}_Voting.pkl"
            with open(filepath, 'wb') as f:
                pickle.dump(self.voting_model, f)
            print(f"✓ Saved Voting Ensemble")
        
        if self.stacking_model:
            filepath = models_dir / f"ensemble_{self.symbol}_Stacking.pkl"
            with open(filepath, 'wb') as f:
                pickle.dump(self.stacking_model, f)
            print(f"✓ Saved Stacking Ensemble")
        
        # Save best model as default
        best_model = self.models.get(best_model_name) or self.stacking_model
        if best_model:
            filepath = models_dir / f"best_{self.symbol}.pkl"
            with open(filepath, 'wb') as f:
                pickle.dump(best_model, f)
            print(f"\n✅ BEST MODEL ({best_model_name}) saved as: best_{self.symbol}.pkl")
        
        # Save feature columns
        filepath = models_dir / f"features_{self.symbol}.pkl"
        with open(filepath, 'wb') as f:
            pickle.dump(self.feature_cols, f)
        print(f"✓ Saved feature list")

def train_commodity_ensemble(symbol, commodity_name):
    """Train ensemble for one commodity"""
    print(f"\n{'='*70}")
    print(f"ENSEMBLE TRAINING: {commodity_name}")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    try:
        trainer = EnsembleTrainer(symbol)
        
        # Step 1: Prepare data
        trainer.prepare_data()
        
        # Step 2: Train all models
        trainer.train_all_models()
        
        # Step 3: Evaluate
        results, best_model = trainer.evaluate_all_models()
        
        # Step 4: Save
        trainer.save_models(best_model)
        
        duration = time.time() - start_time
        
        print(f"\n{'='*70}")
        print(f"{commodity_name} ENSEMBLE TRAINING COMPLETE!")
        print(f"{'='*70}")
        print(f"Duration: {duration:.1f} seconds")
        print(f"Best Model: {best_model}")
        print(f"Best Accuracy: {results[best_model]['accuracy']*100:.2f}%")
        print(f"{'='*70}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Train ensemble for both commodities"""
    print("\n" + "="*70)
    print("WORLD-CLASS AI ENSEMBLE TRAINING SYSTEM")
    print("="*70)
    print("\nTraining 9 AI models for each commodity:")
    print("1. XGBoost")
    print("2. Random Forest")
    print("3. Extra Trees")
    print("4. AdaBoost")
    print("5. Gradient Boosting")
    print("6. LightGBM (if available)")
    print("7. CatBoost (if available)")
    print("8. Voting Ensemble (Hard voting)")
    print("9. Stacking Ensemble (Meta-learner)")
    print("\nThis will take 5-10 minutes...")
    print("="*70)
    
    commodities = [
        ('MCX_GOLD', 'GOLD'),
        ('MCX_SILVER', 'SILVER')
    ]
    
    results_summary = []
    
    for symbol, name in commodities:
        success = train_commodity_ensemble(symbol, name)
        results_summary.append({'name': name, 'success': success})
        time.sleep(1)
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    
    for result in results_summary:
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        print(f"{result['name']:<12} {status}")
    
    print("\n" + "="*70)
    print("✅ ENSEMBLE TRAINING COMPLETE!")
    print("="*70)
    print("\nAll models saved in: ai_screener/models/")
    print("\nNext step: Run the AI dashboard to see ensemble predictions!")
    print("Command: python ai_powered_dashboard.py")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()

