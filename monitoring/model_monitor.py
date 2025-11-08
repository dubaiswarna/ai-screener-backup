"""
Model Monitoring System
=======================
Track model performance, detect drift, and trigger retraining
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from scipy import stats
import logging
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelMonitor:
    """
    Monitor model performance and detect concept drift.
    
    Features:
    - Track accuracy over time
    - Detect distribution shift
    - Monitor prediction confidence
    - Trigger retraining alerts
    - Performance degradation detection
    """
    
    def __init__(
        self,
        model_name: str,
        symbol: str,
        accuracy_threshold: float = 0.65,
        drift_threshold: float = 0.05,
        confidence_threshold: float = 0.70
    ):
        """
        Initialize model monitor.
        
        Args:
            model_name: Name of the model
            symbol: Stock symbol
            accuracy_threshold: Min acceptable accuracy
            drift_threshold: Max allowed drift
            confidence_threshold: Min prediction confidence
        """
        self.model_name = model_name
        self.symbol = symbol
        self.accuracy_threshold = accuracy_threshold
        self.drift_threshold = drift_threshold
        self.confidence_threshold = confidence_threshold
        
        # Performance tracking
        self.predictions: List[Dict] = []
        self.accuracy_history: List[float] = []
        self.drift_scores: List[float] = []
        
        # Baseline statistics (from training)
        self.baseline_feature_stats: Optional[Dict] = None
        self.baseline_accuracy: Optional[float] = None
        
        logger.info(f"✅ Model monitor initialized for {symbol}")
    
    def set_baseline(self, feature_stats: Dict, baseline_accuracy: float):
        """
        Set baseline statistics from training data.
        
        Args:
            feature_stats: Dict with mean, std for each feature
            baseline_accuracy: Training/validation accuracy
        """
        self.baseline_feature_stats = feature_stats
        self.baseline_accuracy = baseline_accuracy
        logger.info(f"✅ Baseline set: Accuracy={baseline_accuracy:.4f}")
    
    def log_prediction(
        self,
        timestamp: datetime,
        features: np.ndarray,
        prediction: int,
        confidence: float,
        actual: Optional[int] = None
    ):
        """
        Log a model prediction.
        
        Args:
            timestamp: Prediction timestamp
            features: Input features
            prediction: Model prediction
            confidence: Prediction confidence
            actual: Actual outcome (if known)
        """
        pred_record = {
            'timestamp': timestamp,
            'prediction': prediction,
            'confidence': confidence,
            'actual': actual,
            'correct': None if actual is None else (prediction == actual),
            'features': features
        }
        
        self.predictions.append(pred_record)
    
    def calculate_rolling_accuracy(self, window: int = 50) -> float:
        """
        Calculate rolling accuracy over recent predictions.
        
        Args:
            window: Window size for rolling calculation
            
        Returns:
            Rolling accuracy
        """
        if len(self.predictions) < window:
            window = len(self.predictions)
        
        if window == 0:
            return 0.0
        
        recent_predictions = self.predictions[-window:]
        correct_predictions = [p for p in recent_predictions if p['correct'] is True]
        
        accuracy = len(correct_predictions) / window
        self.accuracy_history.append(accuracy)
        
        return accuracy
    
    def detect_feature_drift(self, current_features: pd.DataFrame) -> Dict:
        """
        Detect distribution shift in features using statistical tests.
        
        Args:
            current_features: Current feature DataFrame
            
        Returns:
            Drift detection results
        """
        if self.baseline_feature_stats is None:
            logger.warning("⚠️ No baseline statistics set")
            return {'drift_detected': False, 'reason': 'NO_BASELINE'}
        
        drift_detected = False
        drifted_features = []
        drift_scores = []
        
        for feature in current_features.columns:
            if feature not in self.baseline_feature_stats:
                continue
            
            baseline_mean = self.baseline_feature_stats[feature]['mean']
            baseline_std = self.baseline_feature_stats[feature]['std']
            
            current_mean = current_features[feature].mean()
            current_std = current_features[feature].std()
            
            # Z-score for mean shift
            if baseline_std > 0:
                z_score = abs((current_mean - baseline_mean) / baseline_std)
            else:
                z_score = 0
            
            # Kolmogorov-Smirnov test for distribution shift
            try:
                # Generate baseline distribution
                baseline_samples = np.random.normal(baseline_mean, baseline_std, 1000)
                ks_statistic, p_value = stats.ks_2samp(baseline_samples, current_features[feature].values)
                
                drift_score = max(z_score / 3, ks_statistic)  # Normalize to 0-1 range
                drift_scores.append(drift_score)
                
                if drift_score > self.drift_threshold:
                    drift_detected = True
                    drifted_features.append({
                        'feature': feature,
                        'drift_score': drift_score,
                        'z_score': z_score,
                        'ks_statistic': ks_statistic,
                        'p_value': p_value,
                        'baseline_mean': baseline_mean,
                        'current_mean': current_mean
                    })
            except Exception as e:
                logger.warning(f"⚠️ Drift test failed for {feature}: {e}")
        
        overall_drift_score = np.mean(drift_scores) if drift_scores else 0
        self.drift_scores.append(overall_drift_score)
        
        return {
            'drift_detected': drift_detected,
            'overall_drift_score': overall_drift_score,
            'num_drifted_features': len(drifted_features),
            'drifted_features': drifted_features
        }
    
    def detect_confidence_degradation(self, window: int = 50) -> Dict:
        """
        Detect if prediction confidence is degrading.
        
        Args:
            window: Window for calculating average confidence
            
        Returns:
            Confidence analysis
        """
        if len(self.predictions) < window:
            window = len(self.predictions)
        
        if window == 0:
            return {'degradation_detected': False, 'reason': 'NO_DATA'}
        
        recent_predictions = self.predictions[-window:]
        confidences = [p['confidence'] for p in recent_predictions]
        
        avg_confidence = np.mean(confidences)
        confidence_trend = np.polyfit(range(len(confidences)), confidences, 1)[0]  # Linear trend
        
        degradation_detected = avg_confidence < self.confidence_threshold
        
        return {
            'degradation_detected': degradation_detected,
            'avg_confidence': avg_confidence,
            'confidence_trend': confidence_trend,
            'min_confidence': np.min(confidences),
            'max_confidence': np.max(confidences),
            'std_confidence': np.std(confidences)
        }
    
    def should_retrain(self, current_features: Optional[pd.DataFrame] = None) -> Dict:
        """
        Determine if model should be retrained.
        
        Args:
            current_features: Current features for drift detection
            
        Returns:
            Retraining recommendation
        """
        reasons = []
        retrain = False
        
        # Check accuracy degradation
        if len(self.accuracy_history) > 0:
            current_accuracy = self.accuracy_history[-1]
            
            if current_accuracy < self.accuracy_threshold:
                retrain = True
                reasons.append(f"Accuracy below threshold ({current_accuracy:.2%} < {self.accuracy_threshold:.2%})")
            
            if self.baseline_accuracy is not None:
                accuracy_drop = self.baseline_accuracy - current_accuracy
                if accuracy_drop > 0.10:  # 10% drop from baseline
                    retrain = True
                    reasons.append(f"Accuracy dropped {accuracy_drop:.2%} from baseline")
        
        # Check feature drift
        if current_features is not None:
            drift_result = self.detect_feature_drift(current_features)
            if drift_result['drift_detected']:
                retrain = True
                reasons.append(f"Feature drift detected ({drift_result['num_drifted_features']} features)")
        
        # Check confidence degradation
        confidence_result = self.detect_confidence_degradation()
        if confidence_result['degradation_detected']:
            retrain = True
            reasons.append(f"Confidence degraded (avg: {confidence_result['avg_confidence']:.2%})")
        
        # Time-based retraining (every 30 days)
        if len(self.predictions) > 0:
            days_since_first = (datetime.now() - self.predictions[0]['timestamp']).days
            if days_since_first > 30:
                retrain = True
                reasons.append(f"Time-based retraining (>{days_since_first} days)")
        
        recommendation = {
            'retrain_recommended': retrain,
            'reasons': reasons,
            'urgency': 'HIGH' if len(reasons) > 2 else 'MEDIUM' if len(reasons) > 0 else 'LOW',
            'current_accuracy': self.accuracy_history[-1] if self.accuracy_history else None,
            'baseline_accuracy': self.baseline_accuracy,
            'drift_score': self.drift_scores[-1] if self.drift_scores else None
        }
        
        if retrain:
            logger.warning(f"⚠️ RETRAINING RECOMMENDED: {', '.join(reasons)}")
        
        return recommendation
    
    def get_performance_report(self) -> Dict:
        """
        Generate comprehensive performance report.
        
        Returns:
            Performance report
        """
        if len(self.predictions) == 0:
            return {'error': 'NO_DATA'}
        
        # Calculate metrics
        total_predictions = len(self.predictions)
        predictions_with_actual = [p for p in self.predictions if p['actual'] is not None]
        correct_predictions = [p for p in predictions_with_actual if p['correct']]
        
        overall_accuracy = len(correct_predictions) / len(predictions_with_actual) if predictions_with_actual else 0
        
        # Recent performance (last 50 predictions)
        recent_accuracy = self.calculate_rolling_accuracy(window=50)
        
        # Confidence analysis
        confidences = [p['confidence'] for p in self.predictions]
        avg_confidence = np.mean(confidences)
        
        # Accuracy trend
        if len(self.accuracy_history) > 5:
            accuracy_trend = np.polyfit(range(len(self.accuracy_history)), self.accuracy_history, 1)[0]
        else:
            accuracy_trend = 0
        
        report = {
            'model_name': self.model_name,
            'symbol': self.symbol,
            'performance': {
                'total_predictions': total_predictions,
                'overall_accuracy': overall_accuracy,
                'recent_accuracy': recent_accuracy,
                'baseline_accuracy': self.baseline_accuracy,
                'accuracy_trend': accuracy_trend
            },
            'confidence': {
                'avg_confidence': avg_confidence,
                'min_confidence': np.min(confidences),
                'max_confidence': np.max(confidences),
                'threshold': self.confidence_threshold
            },
            'drift': {
                'overall_drift_score': self.drift_scores[-1] if self.drift_scores else None,
                'drift_threshold': self.drift_threshold
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return report


class ModelMonitoringDashboard:
    """
    Dashboard for monitoring multiple models.
    """
    
    def __init__(self):
        """Initialize monitoring dashboard."""
        self.monitors: Dict[str, ModelMonitor] = {}
        logger.info("✅ Model Monitoring Dashboard initialized")
    
    def add_monitor(self, monitor: ModelMonitor):
        """
        Add a model monitor to dashboard.
        
        Args:
            monitor: ModelMonitor instance
        """
        key = f"{monitor.model_name}_{monitor.symbol}"
        self.monitors[key] = monitor
        logger.info(f"✅ Added monitor: {key}")
    
    def get_all_reports(self) -> List[Dict]:
        """
        Get performance reports for all monitored models.
        
        Returns:
            List of performance reports
        """
        reports = []
        for key, monitor in self.monitors.items():
            report = monitor.get_performance_report()
            reports.append(report)
        return reports
    
    def get_models_needing_retraining(self, current_features: Optional[Dict[str, pd.DataFrame]] = None) -> List[Dict]:
        """
        Get list of models that need retraining.
        
        Args:
            current_features: Dict of {symbol: features_df}
            
        Returns:
            List of models needing retraining
        """
        models_to_retrain = []
        
        for key, monitor in self.monitors.items():
            features = current_features.get(monitor.symbol) if current_features else None
            recommendation = monitor.should_retrain(features)
            
            if recommendation['retrain_recommended']:
                models_to_retrain.append({
                    'model': monitor.model_name,
                    'symbol': monitor.symbol,
                    'recommendation': recommendation
                })
        
        return models_to_retrain
    
    def get_summary_statistics(self) -> Dict:
        """
        Get summary statistics across all models.
        
        Returns:
            Summary statistics
        """
        if len(self.monitors) == 0:
            return {'error': 'NO_MONITORS'}
        
        reports = self.get_all_reports()
        reports = [r for r in reports if 'error' not in r]
        
        if len(reports) == 0:
            return {'error': 'NO_DATA'}
        
        accuracies = [r['performance']['overall_accuracy'] for r in reports]
        recent_accuracies = [r['performance']['recent_accuracy'] for r in reports]
        confidences = [r['confidence']['avg_confidence'] for r in reports]
        
        summary = {
            'num_models': len(reports),
            'avg_accuracy': np.mean(accuracies),
            'min_accuracy': np.min(accuracies),
            'max_accuracy': np.max(accuracies),
            'avg_recent_accuracy': np.mean(recent_accuracies),
            'avg_confidence': np.mean(confidences),
            'models_below_threshold': len([a for a in accuracies if a < 0.65]),
            'timestamp': datetime.now().isoformat()
        }
        
        return summary
    
    def generate_alert_report(self) -> str:
        """
        Generate alert report for models needing attention.
        
        Returns:
            Alert report as string
        """
        models_to_retrain = self.get_models_needing_retraining()
        summary = self.get_summary_statistics()
        
        report = []
        report.append("=" * 60)
        report.append("MODEL MONITORING ALERT REPORT")
        report.append("=" * 60)
        report.append("")
        
        if 'error' not in summary:
            report.append("SUMMARY:")
            report.append(f"  Total Models: {summary['num_models']}")
            report.append(f"  Avg Accuracy: {summary['avg_accuracy']:.2%}")
            report.append(f"  Avg Recent Accuracy: {summary['avg_recent_accuracy']:.2%}")
            report.append(f"  Models Below Threshold: {summary['models_below_threshold']}")
            report.append("")
        
        if len(models_to_retrain) > 0:
            report.append(f"⚠️ MODELS NEEDING RETRAINING: {len(models_to_retrain)}")
            report.append("")
            
            for model in models_to_retrain:
                report.append(f"  • {model['symbol']} ({model['model']})")
                report.append(f"    Urgency: {model['recommendation']['urgency']}")
                report.append(f"    Reasons:")
                for reason in model['recommendation']['reasons']:
                    report.append(f"      - {reason}")
                report.append("")
        else:
            report.append("✅ ALL MODELS PERFORMING WELL")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)


# ============================================================
# TESTING
# ============================================================

if __name__ == '__main__':
    print("🧪 Testing Model Monitoring System...")
    
    # Create monitor
    monitor = ModelMonitor(
        model_name='xgb_ensemble',
        symbol='RELIANCE',
        accuracy_threshold=0.65
    )
    
    # Set baseline
    baseline_stats = {
        'feature_1': {'mean': 0.5, 'std': 0.1},
        'feature_2': {'mean': 1.0, 'std': 0.2}
    }
    monitor.set_baseline(baseline_stats, baseline_accuracy=0.75)
    
    # Simulate predictions
    np.random.seed(42)
    for i in range(100):
        features = np.random.randn(10)
        prediction = np.random.randint(0, 3)
        confidence = np.random.uniform(0.6, 0.95)
        actual = np.random.randint(0, 3)
        
        monitor.log_prediction(
            timestamp=datetime.now() - timedelta(days=100-i),
            features=features,
            prediction=prediction,
            confidence=confidence,
            actual=actual
        )
    
    # Calculate metrics
    accuracy = monitor.calculate_rolling_accuracy(window=50)
    print(f"\n📊 Rolling Accuracy: {accuracy:.2%}")
    
    # Check if retraining needed
    current_features = pd.DataFrame({
        'feature_1': np.random.normal(0.6, 0.15, 100),  # Slightly drifted
        'feature_2': np.random.normal(1.1, 0.25, 100)   # Slightly drifted
    })
    
    recommendation = monitor.should_retrain(current_features)
    print(f"\n🔄 Retrain Recommended: {recommendation['retrain_recommended']}")
    if recommendation['retrain_recommended']:
        print(f"   Urgency: {recommendation['urgency']}")
        print(f"   Reasons: {', '.join(recommendation['reasons'])}")
    
    # Generate report
    report = monitor.get_performance_report()
    print(f"\n📈 Performance Report:")
    print(f"   Overall Accuracy: {report['performance']['overall_accuracy']:.2%}")
    print(f"   Recent Accuracy: {report['performance']['recent_accuracy']:.2%}")
    print(f"   Avg Confidence: {report['confidence']['avg_confidence']:.2%}")
    
    # Test dashboard
    dashboard = ModelMonitoringDashboard()
    dashboard.add_monitor(monitor)
    
    alert_report = dashboard.generate_alert_report()
    print(f"\n{alert_report}")
    
    print("\n✅ Model monitoring test passed!")

