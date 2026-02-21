"""Representation-level shift detection using embeddings."""
import numpy as np
from scipy.spatial.distance import cdist
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class EmbeddingShiftDetector:
    """Detect shift in embedding/representation space."""
    
    def __init__(self, threshold: float = 0.1):
        """
        Args:
            threshold: MMD threshold for shift detection
        """
        self.threshold = threshold
        
    def compute_mmd(self, X: np.ndarray, Y: np.ndarray, 
                    kernel: str = 'rbf', gamma: float = None) -> float:
        """
        Compute Maximum Mean Discrepancy between two distributions.
        
        Args:
            X: First sample (n_samples_1, n_features)
            Y: Second sample (n_samples_2, n_features)
            kernel: Kernel type ('rbf' or 'linear')
            gamma: RBF kernel bandwidth (auto if None)
            
        Returns:
            MMD value
        """
        if kernel == 'rbf':
            if gamma is None:
                # Median heuristic for bandwidth
                all_data = np.vstack([X, Y])
                pairwise_dists = cdist(all_data, all_data, metric='euclidean')
                gamma = 1.0 / np.median(pairwise_dists[pairwise_dists > 0])
            
            XX = self._rbf_kernel(X, X, gamma)
            YY = self._rbf_kernel(Y, Y, gamma)
            XY = self._rbf_kernel(X, Y, gamma)
        else:  # linear kernel
            XX = np.dot(X, X.T)
            YY = np.dot(Y, Y.T)
            XY = np.dot(X, Y.T)
        
        mmd = XX.mean() + YY.mean() - 2 * XY.mean()
        return max(0, mmd)  # MMD should be non-negative
    
    def _rbf_kernel(self, X: np.ndarray, Y: np.ndarray, gamma: float) -> np.ndarray:
        """Compute RBF kernel matrix."""
        pairwise_sq_dists = cdist(X, Y, metric='sqeuclidean')
        return np.exp(-gamma * pairwise_sq_dists)
    
    def compute_energy_distance(self, X: np.ndarray, Y: np.ndarray) -> float:
        """
        Compute energy distance between two distributions.
        
        Args:
            X: First sample
            Y: Second sample
            
        Returns:
            Energy distance
        """
        n, m = len(X), len(Y)
        
        # Compute pairwise distances
        XY_dist = cdist(X, Y, metric='euclidean').sum() / (n * m)
        XX_dist = cdist(X, X, metric='euclidean').sum() / (n * n)
        YY_dist = cdist(Y, Y, metric='euclidean').sum() / (m * m)
        
        energy_dist = 2 * XY_dist - XX_dist - YY_dist
        return energy_dist
    
    def detect_shift(self, reference_embeddings: np.ndarray,
                     current_embeddings: np.ndarray) -> Dict:
        """
        Detect shift in embedding space.
        
        Args:
            reference_embeddings: Reference embeddings
            current_embeddings: Current embeddings
            
        Returns:
            Dictionary with shift metrics
        """
        # Subsample for computational efficiency
        max_samples = 1000
        if len(reference_embeddings) > max_samples:
            idx = np.random.choice(len(reference_embeddings), max_samples, replace=False)
            reference_embeddings = reference_embeddings[idx]
        if len(current_embeddings) > max_samples:
            idx = np.random.choice(len(current_embeddings), max_samples, replace=False)
            current_embeddings = current_embeddings[idx]
        
        # Compute MMD
        mmd_score = self.compute_mmd(reference_embeddings, current_embeddings)
        
        # Compute energy distance
        energy_dist = self.compute_energy_distance(reference_embeddings, current_embeddings)
        
        shift_detected = mmd_score > self.threshold
        
        result = {
            'shift_detected': shift_detected,
            'mmd_score': float(mmd_score),
            'energy_distance': float(energy_dist),
            'threshold': self.threshold
        }
        
        logger.info(f"Embedding shift: MMD={mmd_score:.6f}, Energy={energy_dist:.6f}, "
                   f"Shift={'YES' if shift_detected else 'NO'}")
        
        return result
    
    def extract_embeddings(self, model, X: np.ndarray) -> np.ndarray:
        """
        Extract embeddings from a model.
        For TabPFN, we'll use the input features as pseudo-embeddings
        since TabPFN doesn't expose internal representations easily.
        
        Args:
            model: Model to extract embeddings from
            X: Input data
            
        Returns:
            Embeddings
        """
        # For now, use PCA-reduced features as proxy embeddings
        from sklearn.decomposition import PCA
        
        if X.shape[1] > 50:
            pca = PCA(n_components=50, random_state=42)
            embeddings = pca.fit_transform(X)
        else:
            embeddings = X
        
        return embeddings
