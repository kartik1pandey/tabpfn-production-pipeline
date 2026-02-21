"""Calibration module for probability calibration."""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, brier_score_loss
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class TemperatureScaling:
    """Temperature scaling for probability calibration."""
    
    def __init__(self):
        self.temperature = 1.0
        
    def fit(self, logits: np.ndarray, y_true: np.ndarray, 
            max_iter: int = 100) -> 'TemperatureScaling':
        """
        Fit temperature parameter on validation set.
        
        Args:
            logits: Uncalibrated logits or log-odds
            y_true: True labels
            max_iter: Maximum iterations for optimization
            
        Returns:
            self
        """
        from scipy.optimize import minimize
        
        def objective(T):
            scaled_probs = self._apply_temperature(logits, T[0])
            return log_loss(y_true, scaled_probs)
        
        result = minimize(objective, x0=[1.0], bounds=[(0.01, 10.0)], 
                         method='L-BFGS-B', options={'maxiter': max_iter})
        
        self.temperature = result.x[0]
        logger.info(f"Fitted temperature: {self.temperature:.4f}")
        
        return self
    
    def _apply_temperature(self, logits: np.ndarray, temperature: float) -> np.ndarray:
        """Apply temperature scaling to logits."""
        # Convert to probabilities if needed
        if logits.ndim == 1:
            # Binary classification
            scaled_logits = logits / temperature
            probs = 1 / (1 + np.exp(-scaled_logits))
        else:
            # Multi-class
            scaled_logits = logits / temperature
            exp_logits = np.exp(scaled_logits - np.max(scaled_logits, axis=1, keepdims=True))
            probs = exp_logits / exp_logits.sum(axis=1, keepdims=True)
        
        return probs
    
    def transform(self, logits: np.ndarray) -> np.ndarray:
        """Apply temperature scaling to new logits."""
        return self._apply_temperature(logits, self.temperature)
    
    def fit_transform(self, logits: np.ndarray, y_true: np.ndarray) -> np.ndarray:
        """Fit and transform in one step."""
        self.fit(logits, y_true)
        return self.transform(logits)


class CalibrationEvaluator:
    """Evaluate calibration quality."""
    
    @staticmethod
    def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, 
                    n_bins: int = 10) -> float:
        """
        Compute Expected Calibration Error.
        
        Args:
            y_true: True labels
            y_prob: Predicted probabilities
            n_bins: Number of bins
            
        Returns:
            ECE value
        """
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        ece = 0.0
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            in_bin = (y_prob > bin_lower) & (y_prob <= bin_upper)
            prop_in_bin = in_bin.mean()
            
            if prop_in_bin > 0:
                accuracy_in_bin = y_true[in_bin].mean()
                avg_confidence_in_bin = y_prob[in_bin].mean()
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
        
        return ece
    
    @staticmethod
    def compute_calibration_metrics(y_true: np.ndarray, 
                                    y_prob: np.ndarray) -> Dict:
        """
        Compute comprehensive calibration metrics.
        
        Args:
            y_true: True labels
            y_prob: Predicted probabilities
            
        Returns:
            Dictionary of metrics
        """
        # Clip probabilities to avoid log(0)
        y_prob_clipped = np.clip(y_prob, 1e-10, 1 - 1e-10)
        
        ece = CalibrationEvaluator.compute_ece(y_true, y_prob)
        nll = log_loss(y_true, y_prob_clipped)
        brier = brier_score_loss(y_true, y_prob)
        
        return {
            'ece': float(ece),
            'nll': float(nll),
            'brier_score': float(brier)
        }
    
    @staticmethod
    def plot_reliability_diagram(y_true: np.ndarray, y_prob: np.ndarray, 
                                 n_bins: int = 10, save_path: str = None):
        """Plot reliability diagram."""
        import matplotlib.pyplot as plt
        
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        bin_centers = []
        accuracies = []
        confidences = []
        counts = []
        
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            in_bin = (y_prob > bin_lower) & (y_prob <= bin_upper)
            prop_in_bin = in_bin.sum()
            
            if prop_in_bin > 0:
                accuracy_in_bin = y_true[in_bin].mean()
                avg_confidence_in_bin = y_prob[in_bin].mean()
                
                bin_centers.append((bin_lower + bin_upper) / 2)
                accuracies.append(accuracy_in_bin)
                confidences.append(avg_confidence_in_bin)
                counts.append(prop_in_bin)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot([0, 1], [0, 1], 'k--', label='Perfect calibration')
        ax.plot(confidences, accuracies, 'o-', label='Model')
        ax.set_xlabel('Confidence')
        ax.set_ylabel('Accuracy')
        ax.set_title('Reliability Diagram')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Saved reliability diagram to {save_path}")
        
        return fig
