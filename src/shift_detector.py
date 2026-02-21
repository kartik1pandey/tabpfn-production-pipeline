"""Feature-level shift detection using adversarial validation."""
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score
from lightgbm import LGBMClassifier
from scipy.stats import ks_2samp, wasserstein_distance
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class ShiftDetector:
    """Detect distribution shift using adversarial validation."""
    
    def __init__(self, threshold: float = 0.6):
        """
        Args:
            threshold: AUC threshold above which shift is detected
        """
        self.threshold = threshold
        self.detector_model = None
        self.feature_importance = None
        
    def detect_shift(self, reference_data: np.ndarray, 
                     current_data: np.ndarray,
                     feature_names: list = None) -> Dict:
        """
        Detect shift using adversarial validation.
        
        Args:
            reference_data: Reference dataset (e.g., training data)
            current_data: Current dataset to check for shift
            feature_names: Names of features
            
        Returns:
            Dictionary with shift metrics
        """
        # Create labels: 0 for reference, 1 for current
        n_ref = reference_data.shape[0]
        n_cur = current_data.shape[0]
        
        X = np.vstack([reference_data, current_data])
        y = np.hstack([np.zeros(n_ref), np.ones(n_cur)])
        
        # Train adversarial classifier
        self.detector_model = LGBMClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.05,
            random_state=42,
            verbose=-1
        )
        
        # Cross-validation AUC
        cv_scores = cross_val_score(
            self.detector_model, X, y, 
            cv=5, scoring='roc_auc', n_jobs=-1
        )
        auc_score = cv_scores.mean()
        
        # Fit for feature importance
        self.detector_model.fit(X, y)
        self.feature_importance = self.detector_model.feature_importances_
        
        # Get top drifting features
        if feature_names is not None:
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': self.feature_importance
            }).sort_values('importance', ascending=False)
            top_features = importance_df.head(10).to_dict('records')
        else:
            top_features = []
        
        # Per-feature statistical tests
        feature_stats = self._compute_feature_stats(
            reference_data, current_data, feature_names
        )
        
        shift_detected = auc_score > self.threshold
        
        result = {
            'shift_detected': shift_detected,
            'auc_score': auc_score,
            'auc_std': cv_scores.std(),
            'top_drifting_features': top_features,
            'feature_stats': feature_stats
        }
        
        logger.info(f"Shift detection: AUC={auc_score:.4f}, Shift={'YES' if shift_detected else 'NO'}")
        
        return result
    
    def _compute_feature_stats(self, ref_data: np.ndarray, 
                                cur_data: np.ndarray,
                                feature_names: list = None) -> list:
        """Compute per-feature statistical tests."""
        n_features = ref_data.shape[1]
        stats = []
        
        for i in range(min(n_features, 20)):  # Limit to first 20 features for speed
            # KS test
            ks_stat, ks_pval = ks_2samp(ref_data[:, i], cur_data[:, i])
            
            # Wasserstein distance
            wass_dist = wasserstein_distance(ref_data[:, i], cur_data[:, i])
            
            feat_name = feature_names[i] if feature_names else f"feature_{i}"
            
            stats.append({
                'feature': feat_name,
                'ks_statistic': float(ks_stat),
                'ks_pvalue': float(ks_pval),
                'wasserstein_distance': float(wass_dist)
            })
        
        return stats
    
    def inject_shift(self, data: np.ndarray, shift_type: str = 'mean', 
                     magnitude: float = 1.0, feature_idx: int = 0) -> np.ndarray:
        """
        Inject synthetic shift for testing.
        
        Args:
            data: Original data
            shift_type: Type of shift ('mean', 'scale', 'noise')
            magnitude: Magnitude of shift
            feature_idx: Which feature to shift
            
        Returns:
            Shifted data
        """
        shifted_data = data.copy()
        
        if shift_type == 'mean':
            shifted_data[:, feature_idx] += magnitude * np.std(data[:, feature_idx])
        elif shift_type == 'scale':
            shifted_data[:, feature_idx] *= magnitude
        elif shift_type == 'noise':
            noise = np.random.normal(0, magnitude, size=data.shape[0])
            shifted_data[:, feature_idx] += noise
        
        logger.info(f"Injected {shift_type} shift with magnitude {magnitude} on feature {feature_idx}")
        
        return shifted_data
