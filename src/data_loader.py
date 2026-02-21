"""Data loading and preprocessing module."""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """Handle data loading and preprocessing."""
    
    def __init__(self, train_path: str, test_path: str):
        self.train_path = train_path
        self.test_path = test_path
        self.scaler = StandardScaler()
        self.feature_names = None
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load train and test datasets."""
        logger.info(f"Loading data from {self.train_path} and {self.test_path}")
        train_df = pd.read_csv(self.train_path)
        test_df = pd.read_csv(self.test_path)
        
        logger.info(f"Train shape: {train_df.shape}, Test shape: {test_df.shape}")
        return train_df, test_df
    
    def preprocess(self, train_df: pd.DataFrame, test_df: pd.DataFrame, 
                   val_size: float = 0.2, random_state: int = 42) -> dict:
        """Preprocess data with train/val split."""
        # Separate features and target
        X_train_full = train_df.drop(['Stock code', 'IsDefault'], axis=1)
        y_train_full = train_df['IsDefault']
        X_test = test_df.drop(['Stock code'], axis=1)
        test_ids = test_df['Stock code']
        
        # Convert all columns to numeric, handling strings
        for col in X_train_full.columns:
            X_train_full[col] = pd.to_numeric(X_train_full[col], errors='coerce')
        for col in X_test.columns:
            X_test[col] = pd.to_numeric(X_test[col], errors='coerce')
        
        # Store feature names
        self.feature_names = X_train_full.columns.tolist()
        
        # Handle missing values
        X_train_full = X_train_full.fillna(X_train_full.median())
        X_test = X_test.fillna(X_test.median())
        
        # Replace inf values
        X_train_full = X_train_full.replace([np.inf, -np.inf], np.nan)
        X_test = X_test.replace([np.inf, -np.inf], np.nan)
        X_train_full = X_train_full.fillna(X_train_full.median())
        X_test = X_test.fillna(X_test.median())
        
        # Train/val split
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_full, y_train_full, test_size=val_size, 
            random_state=random_state, stratify=y_train_full
        )
        
        # Fit scaler on training data only
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)
        
        logger.info(f"Preprocessing complete. Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
        logger.info(f"Class distribution - Train: {y_train.value_counts().to_dict()}")
        
        return {
            'X_train': X_train_scaled,
            'X_val': X_val_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train.values,
            'y_val': y_val.values,
            'test_ids': test_ids.values,
            'feature_names': self.feature_names,
            'X_train_raw': X_train.values,
            'X_val_raw': X_val.values,
            'X_test_raw': X_test.values
        }
