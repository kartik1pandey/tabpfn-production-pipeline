"""Baseline and TabPFN predictors."""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score, log_loss
from lightgbm import LGBMClassifier
import time
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class BaselinePredictor:
    """Baseline models (Logistic Regression, LightGBM)."""
    
    def __init__(self, model_type: str = 'lightgbm'):
        """
        Args:
            model_type: 'logistic' or 'lightgbm'
        """
        self.model_type = model_type
        self.model = None
        
        if model_type == 'logistic':
            self.model = LogisticRegression(max_iter=1000, random_state=42)
        elif model_type == 'lightgbm':
            self.model = LGBMClassifier(
                n_estimators=100,
                max_depth=7,
                learning_rate=0.05,
                random_state=42,
                verbose=-1
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def fit(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train the model."""
        start_time = time.time()
        self.model.fit(X_train, y_train)
        train_time = time.time() - start_time
        logger.info(f"{self.model_type} training time: {train_time:.2f}s")
        return self
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities."""
        return self.model.predict_proba(X)[:, 1]
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        return self.model.predict(X)
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Evaluate model performance."""
        start_time = time.time()
        y_pred = self.predict(X)
        y_prob = self.predict_proba(X)
        inference_time = time.time() - start_time
        
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'auc': roc_auc_score(y, y_prob),
            'logloss': log_loss(y, y_prob),
            'inference_time': inference_time,
            'inference_time_per_sample': inference_time / len(X)
        }
        
        return metrics


class TabPFNPredictor:
    """TabPFN model wrapper."""
    
    def __init__(self, n_ensemble: int = 1):
        """
        Args:
            n_ensemble: Number of ensemble members (1 for single model)
        """
        self.n_ensemble = n_ensemble
        self.model = None
        
    def fit(self, X_train: np.ndarray, y_train: np.ndarray):
        """
        Fit TabPFN model.
        Note: TabPFN has limitations on dataset size (max 1024 samples, 100 features)
        """
        try:
            from tabpfn import TabPFNClassifier
            
            # TabPFN limitations
            max_samples = 1024
            max_features = 100
            
            if X_train.shape[0] > max_samples:
                logger.warning(f"TabPFN: Subsampling from {X_train.shape[0]} to {max_samples} samples")
                idx = np.random.choice(X_train.shape[0], max_samples, replace=False)
                X_train = X_train[idx]
                y_train = y_train[idx]
            
            if X_train.shape[1] > max_features:
                logger.warning(f"TabPFN: Using first {max_features} features (total: {X_train.shape[1]})")
                X_train = X_train[:, :max_features]
            
            start_time = time.time()
            self.model = TabPFNClassifier(
                device='cpu',
                N_ensemble_configurations=self.n_ensemble
            )
            self.model.fit(X_train, y_train)
            train_time = time.time() - start_time
            
            logger.info(f"TabPFN (ensemble={self.n_ensemble}) training time: {train_time:.2f}s")
            
        except ImportError:
            logger.error("TabPFN not installed. Using LightGBM as fallback.")
            self.model = LGBMClassifier(n_estimators=100, random_state=42, verbose=-1)
            self.model.fit(X_train, y_train)
        
        return self
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities."""
        # Handle feature dimension
        if hasattr(self.model, 'n_features_in_'):
            n_features = self.model.n_features_in_
            if X.shape[1] > n_features:
                X = X[:, :n_features]
        
        probs = self.model.predict_proba(X)
        if probs.ndim > 1:
            return probs[:, 1]
        return probs
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        if hasattr(self.model, 'n_features_in_'):
            n_features = self.model.n_features_in_
            if X.shape[1] > n_features:
                X = X[:, :n_features]
        return self.model.predict(X)
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Evaluate model performance."""
        start_time = time.time()
        y_pred = self.predict(X)
        y_prob = self.predict_proba(X)
        inference_time = time.time() - start_time
        
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'auc': roc_auc_score(y, y_prob),
            'logloss': log_loss(y, y_prob),
            'inference_time': inference_time,
            'inference_time_per_sample': inference_time / len(X)
        }
        
        return metrics


class StudentDistilledModel:
    """Distilled student model trained to mimic TabPFN."""
    
    def __init__(self):
        self.model = LGBMClassifier(
            n_estimators=50,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            verbose=-1
        )
    
    def distill(self, X_train: np.ndarray, teacher_probs: np.ndarray):
        """
        Train student to mimic teacher predictions.
        
        Args:
            X_train: Training features
            teacher_probs: Soft labels from teacher model
        """
        start_time = time.time()
        
        # Convert probabilities to pseudo-labels with soft targets
        # Use teacher probabilities as weights
        y_pseudo = (teacher_probs > 0.5).astype(int)
        
        self.model.fit(X_train, y_pseudo, 
                      sample_weight=np.abs(teacher_probs - 0.5) + 0.5)
        
        train_time = time.time() - start_time
        logger.info(f"Student distillation time: {train_time:.2f}s")
        
        return self
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities."""
        return self.model.predict_proba(X)[:, 1]
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        return self.model.predict(X)
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Evaluate model performance."""
        start_time = time.time()
        y_pred = self.predict(X)
        y_prob = self.predict_proba(X)
        inference_time = time.time() - start_time
        
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'auc': roc_auc_score(y, y_prob),
            'logloss': log_loss(y, y_prob),
            'inference_time': inference_time,
            'inference_time_per_sample': inference_time / len(X)
        }
        
        return metrics
