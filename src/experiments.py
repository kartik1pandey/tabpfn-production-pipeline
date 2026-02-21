"""Main experiment runner."""
import numpy as np
import pandas as pd
from pathlib import Path
import json
import time
from typing import Dict
import logging

from .data_loader import DataLoader
from .shift_detector import ShiftDetector
from .embedding_shift import EmbeddingShiftDetector
from .calibration import TemperatureScaling, CalibrationEvaluator
from .conformal import SplitConformalClassifier, AbstentionPolicy
from .predictors import BaselinePredictor, TabPFNPredictor, StudentDistilledModel
from .inference_controller import InferenceController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExperimentRunner:
    """Run comprehensive experiments."""
    
    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = {}
        
    def run_baseline_comparison(self, data: Dict) -> Dict:
        """Compare baseline models."""
        logger.info("=" * 80)
        logger.info("BASELINE MODEL COMPARISON")
        logger.info("=" * 80)
        
        results = {}
        
        # Logistic Regression
        logger.info("\n--- Logistic Regression ---")
        lr_model = BaselinePredictor('logistic')
        lr_model.fit(data['X_train'], data['y_train'])
        lr_metrics = lr_model.evaluate(data['X_val'], data['y_val'])
        results['logistic'] = lr_metrics
        logger.info(f"Logistic - AUC: {lr_metrics['auc']:.4f}, Acc: {lr_metrics['accuracy']:.4f}")
        
        # LightGBM
        logger.info("\n--- LightGBM ---")
        lgb_model = BaselinePredictor('lightgbm')
        lgb_model.fit(data['X_train'], data['y_train'])
        lgb_metrics = lgb_model.evaluate(data['X_val'], data['y_val'])
        results['lightgbm'] = lgb_metrics
        logger.info(f"LightGBM - AUC: {lgb_metrics['auc']:.4f}, Acc: {lgb_metrics['accuracy']:.4f}")
        
        # TabPFN (single)
        logger.info("\n--- TabPFN (single) ---")
        try:
            tabpfn_model = TabPFNPredictor(n_ensemble=1)
            tabpfn_model.fit(data['X_train'], data['y_train'])
            tabpfn_metrics = tabpfn_model.evaluate(data['X_val'], data['y_val'])
            results['tabpfn_single'] = tabpfn_metrics
            logger.info(f"TabPFN - AUC: {tabpfn_metrics['auc']:.4f}, Acc: {tabpfn_metrics['accuracy']:.4f}")
            
            # Store model for later use
            self.tabpfn_model = tabpfn_model
        except Exception as e:
            logger.error(f"TabPFN failed: {e}")
            results['tabpfn_single'] = {'error': str(e)}
        
        return results
    
    def run_shift_detection_experiments(self, data: Dict) -> Dict:
        """Test shift detection capabilities."""
        logger.info("\n" + "=" * 80)
        logger.info("SHIFT DETECTION EXPERIMENTS")
        logger.info("=" * 80)
        
        results = {}
        
        # Feature-level shift detection
        logger.info("\n--- Feature-level Shift Detection ---")
        shift_detector = ShiftDetector(threshold=0.6)
        
        # Test 1: No shift (train vs val)
        logger.info("\nTest 1: No shift (train vs val)")
        no_shift_result = shift_detector.detect_shift(
            data['X_train'], data['X_val'], data['feature_names']
        )
        results['no_shift'] = no_shift_result
        
        # Test 2: Injected mean shift
        logger.info("\nTest 2: Injected mean shift")
        X_shifted = shift_detector.inject_shift(
            data['X_val'], shift_type='mean', magnitude=2.0, feature_idx=0
        )
        mean_shift_result = shift_detector.detect_shift(
            data['X_train'], X_shifted, data['feature_names']
        )
        results['mean_shift'] = mean_shift_result
        
        # Test 3: Injected noise
        logger.info("\nTest 3: Injected noise")
        X_noisy = shift_detector.inject_shift(
            data['X_val'], shift_type='noise', magnitude=1.5, feature_idx=1
        )
        noise_shift_result = shift_detector.detect_shift(
            data['X_train'], X_noisy, data['feature_names']
        )
        results['noise_shift'] = noise_shift_result
        
        # Embedding-level shift detection
        logger.info("\n--- Embedding-level Shift Detection ---")
        emb_detector = EmbeddingShiftDetector(threshold=0.1)
        
        # Extract embeddings (using PCA as proxy)
        train_emb = emb_detector.extract_embeddings(None, data['X_train'])
        val_emb = emb_detector.extract_embeddings(None, data['X_val'])
        shifted_emb = emb_detector.extract_embeddings(None, X_shifted)
        
        logger.info("\nEmbedding shift: train vs val")
        emb_no_shift = emb_detector.detect_shift(train_emb, val_emb)
        results['embedding_no_shift'] = emb_no_shift
        
        logger.info("\nEmbedding shift: train vs shifted")
        emb_with_shift = emb_detector.detect_shift(train_emb, shifted_emb)
        results['embedding_with_shift'] = emb_with_shift
        
        return results
    
    def run_calibration_experiments(self, data: Dict) -> Dict:
        """Test calibration methods."""
        logger.info("\n" + "=" * 80)
        logger.info("CALIBRATION EXPERIMENTS")
        logger.info("=" * 80)
        
        results = {}
        
        # Train a model
        model = BaselinePredictor('lightgbm')
        model.fit(data['X_train'], data['y_train'])
        
        # Get predictions
        y_val_prob = model.predict_proba(data['X_val'])
        
        # Evaluate uncalibrated
        logger.info("\n--- Uncalibrated ---")
        uncal_metrics = CalibrationEvaluator.compute_calibration_metrics(
            data['y_val'], y_val_prob
        )
        results['uncalibrated'] = uncal_metrics
        logger.info(f"Uncalibrated - ECE: {uncal_metrics['ece']:.4f}, NLL: {uncal_metrics['nll']:.4f}")
        
        # Temperature scaling
        logger.info("\n--- Temperature Scaling ---")
        # Convert probabilities to logits
        logits = np.log(y_val_prob / (1 - y_val_prob + 1e-10))
        
        # Split val into calibration and test
        n_cal = len(data['y_val']) // 2
        logits_cal, logits_test = logits[:n_cal], logits[n_cal:]
        y_cal, y_test = data['y_val'][:n_cal], data['y_val'][n_cal:]
        
        temp_scaler = TemperatureScaling()
        temp_scaler.fit(logits_cal, y_cal)
        y_test_calibrated = temp_scaler.transform(logits_test)
        
        cal_metrics = CalibrationEvaluator.compute_calibration_metrics(
            y_test, y_test_calibrated
        )
        results['calibrated'] = cal_metrics
        logger.info(f"Calibrated - ECE: {cal_metrics['ece']:.4f}, NLL: {cal_metrics['nll']:.4f}")
        
        # Improvement
        ece_improvement = (uncal_metrics['ece'] - cal_metrics['ece']) / uncal_metrics['ece'] * 100
        logger.info(f"ECE improvement: {ece_improvement:.1f}%")
        results['ece_improvement_pct'] = ece_improvement
        
        return results
    
    def run_conformal_experiments(self, data: Dict) -> Dict:
        """Test conformal prediction."""
        logger.info("\n" + "=" * 80)
        logger.info("CONFORMAL PREDICTION EXPERIMENTS")
        logger.info("=" * 80)
        
        results = {}
        
        # Train model
        model = BaselinePredictor('lightgbm')
        model.fit(data['X_train'], data['y_train'])
        
        # Split val into calibration and test
        n_cal = len(data['y_val']) // 2
        X_cal, X_test = data['X_val'][:n_cal], data['X_val'][n_cal:]
        y_cal, y_test = data['y_val'][:n_cal], data['y_val'][n_cal:]
        
        # Get predictions
        probs_cal = model.predict_proba(X_cal)
        probs_test = model.predict_proba(X_test)
        
        # Conformal prediction
        for alpha in [0.1, 0.05]:
            logger.info(f"\n--- Alpha = {alpha} (target coverage: {1-alpha}) ---")
            
            conformal = SplitConformalClassifier(alpha=alpha)
            conformal.calibrate(y_cal, probs_cal)
            
            pred_sets, set_sizes = conformal.predict_sets(probs_test)
            coverage_metrics = conformal.evaluate_coverage(y_test, pred_sets)
            
            results[f'alpha_{alpha}'] = coverage_metrics
            
            # Abstention policy
            abstention = AbstentionPolicy(set_size_threshold=2, uncertainty_threshold=0.7)
            abstain_mask, abstention_rate = abstention.apply_policy(pred_sets, probs_test)
            
            # Accuracy on non-abstained
            if not abstain_mask.all():
                y_pred_non_abstain = (probs_test[~abstain_mask] > 0.5).astype(int)
                acc_non_abstain = (y_pred_non_abstain == y_test[~abstain_mask]).mean()
            else:
                acc_non_abstain = 0.0
            
            results[f'alpha_{alpha}']['abstention_rate'] = float(abstention_rate)
            results[f'alpha_{alpha}']['accuracy_non_abstained'] = float(acc_non_abstain)
            
            logger.info(f"Abstention rate: {abstention_rate:.4f}, "
                       f"Accuracy (non-abstained): {acc_non_abstain:.4f}")
        
        return results
    
    def run_full_pipeline(self, train_path: str, test_path: str) -> Dict:
        """Run complete pipeline."""
        logger.info("\n" + "=" * 80)
        logger.info("FULL PIPELINE EXECUTION")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        # Load and preprocess data
        loader = DataLoader(train_path, test_path)
        train_df, test_df = loader.load_data()
        data = loader.preprocess(train_df, test_df)
        
        # Run experiments
        results = {
            'baseline_comparison': self.run_baseline_comparison(data),
            'shift_detection': self.run_shift_detection_experiments(data),
            'calibration': self.run_calibration_experiments(data),
            'conformal': self.run_conformal_experiments(data),
        }
        
        # Save results
        results['total_time'] = time.time() - start_time
        
        output_file = self.output_dir / 'experiment_results.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"\n{'=' * 80}")
        logger.info(f"EXPERIMENTS COMPLETE - Total time: {results['total_time']:.2f}s")
        logger.info(f"Results saved to: {output_file}")
        logger.info(f"{'=' * 80}\n")
        
        return results
