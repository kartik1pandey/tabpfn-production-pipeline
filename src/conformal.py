"""Conformal prediction for uncertainty quantification."""
import numpy as np
from typing import Tuple, List, Dict
import logging

logger = logging.getLogger(__name__)


class SplitConformalClassifier:
    """Split conformal prediction for classification."""
    
    def __init__(self, alpha: float = 0.1):
        """
        Args:
            alpha: Miscoverage level (1-alpha is target coverage)
        """
        self.alpha = alpha
        self.q_hat = None
        
    def calibrate(self, y_cal: np.ndarray, probs_cal: np.ndarray):
        """
        Calibrate conformal predictor on calibration set.
        
        Args:
            y_cal: True labels for calibration set
            probs_cal: Predicted probabilities (n_samples, n_classes) or (n_samples,) for binary
        """
        # Compute nonconformity scores
        if probs_cal.ndim == 1:
            # Binary classification
            scores = 1 - probs_cal[np.arange(len(y_cal)), y_cal] if len(probs_cal.shape) > 1 else 1 - np.where(y_cal == 1, probs_cal, 1 - probs_cal)
        else:
            # Multi-class
            scores = 1 - probs_cal[np.arange(len(y_cal)), y_cal]
        
        # Compute quantile
        n = len(scores)
        q_level = np.ceil((n + 1) * (1 - self.alpha)) / n
        self.q_hat = np.quantile(scores, q_level)
        
        logger.info(f"Calibrated conformal predictor: q_hat={self.q_hat:.4f}, alpha={self.alpha}")
    
    def predict_sets(self, probs: np.ndarray) -> Tuple[List[List[int]], np.ndarray]:
        """
        Predict conformal sets.
        
        Args:
            probs: Predicted probabilities (n_samples, n_classes) or (n_samples,) for binary
            
        Returns:
            prediction_sets: List of prediction sets (list of class indices)
            set_sizes: Size of each prediction set
        """
        if self.q_hat is None:
            raise ValueError("Must calibrate before prediction")
        
        if probs.ndim == 1:
            # Binary classification
            prediction_sets = []
            for p in probs:
                pred_set = []
                if 1 - p <= self.q_hat:
                    pred_set.append(1)
                if 1 - (1 - p) <= self.q_hat:
                    pred_set.append(0)
                prediction_sets.append(pred_set)
        else:
            # Multi-class
            prediction_sets = []
            for prob_vec in probs:
                scores = 1 - prob_vec
                pred_set = np.where(scores <= self.q_hat)[0].tolist()
                prediction_sets.append(pred_set)
        
        set_sizes = np.array([len(s) for s in prediction_sets])
        
        return prediction_sets, set_sizes
    
    def evaluate_coverage(self, y_true: np.ndarray, 
                         prediction_sets: List[List[int]]) -> Dict:
        """
        Evaluate coverage and efficiency.
        
        Args:
            y_true: True labels
            prediction_sets: Predicted sets
            
        Returns:
            Dictionary with metrics
        """
        # Coverage: fraction of times true label is in prediction set
        coverage = np.mean([y in pred_set for y, pred_set in zip(y_true, prediction_sets)])
        
        # Average set size
        avg_set_size = np.mean([len(s) for s in prediction_sets])
        
        # Singleton sets (size 1)
        singleton_rate = np.mean([len(s) == 1 for s in prediction_sets])
        
        # Empty sets
        empty_rate = np.mean([len(s) == 0 for s in prediction_sets])
        
        result = {
            'coverage': float(coverage),
            'target_coverage': 1 - self.alpha,
            'avg_set_size': float(avg_set_size),
            'singleton_rate': float(singleton_rate),
            'empty_rate': float(empty_rate)
        }
        
        logger.info(f"Conformal coverage: {coverage:.4f} (target: {1-self.alpha:.4f}), "
                   f"Avg set size: {avg_set_size:.2f}")
        
        return result


class AbstentionPolicy:
    """Policy for abstaining on uncertain predictions."""
    
    def __init__(self, set_size_threshold: int = 2, 
                 uncertainty_threshold: float = 0.7):
        """
        Args:
            set_size_threshold: Abstain if conformal set size > threshold
            uncertainty_threshold: Abstain if max probability < threshold
        """
        self.set_size_threshold = set_size_threshold
        self.uncertainty_threshold = uncertainty_threshold
    
    def should_abstain(self, prediction_set: List[int], 
                      max_prob: float) -> bool:
        """
        Decide whether to abstain.
        
        Args:
            prediction_set: Conformal prediction set
            max_prob: Maximum predicted probability
            
        Returns:
            True if should abstain
        """
        # Abstain if set is too large or confidence is too low
        return (len(prediction_set) > self.set_size_threshold or 
                max_prob < self.uncertainty_threshold)
    
    def apply_policy(self, prediction_sets: List[List[int]], 
                    probs: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply abstention policy.
        
        Args:
            prediction_sets: Conformal prediction sets
            probs: Predicted probabilities
            
        Returns:
            abstain_mask: Boolean mask indicating abstentions
            abstention_rate: Fraction of abstentions
        """
        max_probs = probs.max(axis=1) if probs.ndim > 1 else np.maximum(probs, 1 - probs)
        
        abstain_mask = np.array([
            self.should_abstain(pred_set, max_prob)
            for pred_set, max_prob in zip(prediction_sets, max_probs)
        ])
        
        abstention_rate = abstain_mask.mean()
        
        logger.info(f"Abstention rate: {abstention_rate:.4f}")
        
        return abstain_mask, abstention_rate
