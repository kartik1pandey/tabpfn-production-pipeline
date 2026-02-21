"""Cost-aware inference controller with tiered routing."""
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class MetaFeatureExtractor:
    """Extract meta-features from datasets."""
    
    @staticmethod
    def extract(X: np.ndarray, y: np.ndarray = None) -> Dict:
        """
        Extract dataset meta-features.
        
        Args:
            X: Feature matrix
            y: Labels (optional)
            
        Returns:
            Dictionary of meta-features
        """
        n_samples, n_features = X.shape
        
        meta_features = {
            'n_samples': n_samples,
            'n_features': n_features,
            'sparsity': np.mean(X == 0),
            'mean_abs_value': np.mean(np.abs(X)),
            'std_value': np.std(X),
            'feature_correlation_mean': np.mean(np.abs(np.corrcoef(X.T))),
        }
        
        if y is not None:
            unique, counts = np.unique(y, return_counts=True)
            meta_features['n_classes'] = len(unique)
            meta_features['class_imbalance'] = counts.max() / counts.min()
            meta_features['entropy'] = -np.sum((counts / counts.sum()) * 
                                               np.log(counts / counts.sum() + 1e-10))
        
        return meta_features


class InferenceController:
    """Cost-aware inference controller with tiered routing."""
    
    def __init__(self, budget_ratio: float = 0.5):
        """
        Args:
            budget_ratio: Cost/benefit threshold for routing decisions
        """
        self.budget_ratio = budget_ratio
        self.meta_model = None
        self.cost_estimates = {
            'cheap': 0.001,      # Logistic regression cost
            'medium': 0.01,      # LightGBM cost
            'expensive': 0.1,    # TabPFN single cost
            'very_expensive': 1.0  # TabPFN ensemble cost
        }
        
    def train_meta_model(self, meta_features_list: list, 
                        performance_gains: np.ndarray):
        """
        Train meta-model to predict performance gain.
        
        Args:
            meta_features_list: List of meta-feature dictionaries
            performance_gains: Expected AUC gain from using expensive model
        """
        from sklearn.ensemble import RandomForestRegressor
        
        # Convert meta-features to matrix
        X_meta = np.array([[mf['n_samples'], mf['n_features'], 
                           mf.get('sparsity', 0), mf.get('class_imbalance', 1)]
                          for mf in meta_features_list])
        
        self.meta_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.meta_model.fit(X_meta, performance_gains)
        
        logger.info("Trained meta-model for inference routing")
    
    def predict_benefit(self, meta_features: Dict) -> float:
        """
        Predict expected benefit of using expensive model.
        
        Args:
            meta_features: Dataset meta-features
            
        Returns:
            Expected AUC gain
        """
        if self.meta_model is None:
            # Default heuristic: benefit increases with complexity
            complexity = meta_features['n_features'] * np.log(meta_features['n_samples'])
            return min(0.1, complexity / 10000)
        
        X_meta = np.array([[meta_features['n_samples'], 
                           meta_features['n_features'],
                           meta_features.get('sparsity', 0),
                           meta_features.get('class_imbalance', 1)]])
        
        return self.meta_model.predict(X_meta)[0]
    
    def route_inference(self, X: np.ndarray, y: np.ndarray = None,
                       uncertainty: float = None) -> str:
        """
        Decide which model tier to use.
        
        Args:
            X: Input features
            y: Labels (optional, for meta-features)
            uncertainty: Uncertainty estimate (optional)
            
        Returns:
            Tier name: 'cheap', 'medium', 'expensive', 'very_expensive', or 'abstain'
        """
        # Extract meta-features
        meta_features = MetaFeatureExtractor.extract(X, y)
        
        # Predict benefit
        expected_benefit = self.predict_benefit(meta_features)
        
        # High uncertainty -> use better model or abstain
        if uncertainty is not None and uncertainty > 0.8:
            if expected_benefit / self.cost_estimates['expensive'] > self.budget_ratio:
                return 'expensive'
            else:
                return 'abstain'
        
        # Cost-benefit analysis
        if expected_benefit / self.cost_estimates['cheap'] > self.budget_ratio:
            # Cheap model is cost-effective
            return 'cheap'
        elif expected_benefit / self.cost_estimates['medium'] > self.budget_ratio:
            return 'medium'
        elif expected_benefit / self.cost_estimates['expensive'] > self.budget_ratio:
            return 'expensive'
        else:
            # Very high benefit needed
            if expected_benefit > 0.05:
                return 'very_expensive'
            else:
                return 'medium'  # Default to medium
    
    def compute_cost_savings(self, routing_decisions: list, 
                            baseline_tier: str = 'very_expensive') -> Dict:
        """
        Compute cost savings from routing.
        
        Args:
            routing_decisions: List of tier decisions
            baseline_tier: Baseline tier (what we'd use without routing)
            
        Returns:
            Dictionary with cost metrics
        """
        baseline_cost = self.cost_estimates[baseline_tier] * len(routing_decisions)
        
        actual_cost = sum(self.cost_estimates.get(tier, 0) 
                         for tier in routing_decisions)
        
        savings = baseline_cost - actual_cost
        savings_pct = (savings / baseline_cost) * 100 if baseline_cost > 0 else 0
        
        tier_distribution = {
            tier: routing_decisions.count(tier) / len(routing_decisions)
            for tier in set(routing_decisions)
        }
        
        result = {
            'baseline_cost': baseline_cost,
            'actual_cost': actual_cost,
            'savings': savings,
            'savings_percentage': savings_pct,
            'tier_distribution': tier_distribution
        }
        
        logger.info(f"Cost savings: {savings_pct:.1f}% (${savings:.2f})")
        
        return result
