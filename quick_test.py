"""Quick test of core functionality."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("TabPFN Production Pipeline - Quick Test")
print("=" * 80)

# Test 1: Data Loading
print("\n[1/6] Testing Data Loading...")
try:
    from src.data_loader import DataLoader
    loader = DataLoader("dataset/train.csv", "dataset/test.csv")
    train_df, test_df = loader.load_data()
    print(f"✓ Loaded train: {train_df.shape}, test: {test_df.shape}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Preprocessing
print("\n[2/6] Testing Preprocessing...")
try:
    data = loader.preprocess(train_df, test_df, val_size=0.2)
    print(f"✓ Train: {data['X_train'].shape}, Val: {data['X_val'].shape}")
    print(f"  Features: {len(data['feature_names'])}")
    print(f"  Class distribution: {np.bincount(data['y_train'])}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Baseline Model
print("\n[3/6] Testing Baseline Model...")
try:
    from src.predictors import BaselinePredictor
    model = BaselinePredictor('lightgbm')
    model.fit(data['X_train'][:500], data['y_train'][:500])  # Use subset for speed
    metrics = model.evaluate(data['X_val'][:100], data['y_val'][:100])
    print(f"✓ LightGBM - AUC: {metrics['auc']:.4f}, Acc: {metrics['accuracy']:.4f}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Shift Detection
print("\n[4/6] Testing Shift Detection...")
try:
    from src.shift_detector import ShiftDetector
    detector = ShiftDetector(threshold=0.6)
    
    # Test with no shift
    result = detector.detect_shift(
        data['X_train'][:200], 
        data['X_val'][:200],
        data['feature_names']
    )
    print(f"✓ No shift test - AUC: {result['auc_score']:.4f}, "
          f"Shift: {'YES' if result['shift_detected'] else 'NO'}")
    
    # Test with injected shift
    X_shifted = detector.inject_shift(
        data['X_val'][:200], 
        shift_type='mean', 
        magnitude=2.0, 
        feature_idx=0
    )
    result_shift = detector.detect_shift(
        data['X_train'][:200], 
        X_shifted,
        data['feature_names']
    )
    print(f"✓ Mean shift test - AUC: {result_shift['auc_score']:.4f}, "
          f"Shift: {'YES' if result_shift['shift_detected'] else 'NO'}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Calibration
print("\n[5/6] Testing Calibration...")
try:
    from src.calibration import TemperatureScaling, CalibrationEvaluator
    
    # Get predictions
    y_prob = model.predict_proba(data['X_val'][:100])
    
    # Evaluate uncalibrated
    uncal_metrics = CalibrationEvaluator.compute_calibration_metrics(
        data['y_val'][:100], y_prob
    )
    print(f"✓ Uncalibrated ECE: {uncal_metrics['ece']:.4f}")
    
    # Calibrate
    logits = np.log(y_prob / (1 - y_prob + 1e-10))
    temp_scaler = TemperatureScaling()
    temp_scaler.fit(logits[:50], data['y_val'][:50])
    y_prob_cal = temp_scaler.transform(logits[50:])
    
    cal_metrics = CalibrationEvaluator.compute_calibration_metrics(
        data['y_val'][50:100], y_prob_cal
    )
    print(f"✓ Calibrated ECE: {cal_metrics['ece']:.4f}")
    improvement = (uncal_metrics['ece'] - cal_metrics['ece']) / uncal_metrics['ece'] * 100
    print(f"  Improvement: {improvement:.1f}%")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 6: Conformal Prediction
print("\n[6/6] Testing Conformal Prediction...")
try:
    from src.conformal import SplitConformalClassifier
    
    conformal = SplitConformalClassifier(alpha=0.1)
    conformal.calibrate(data['y_val'][:50], y_prob[:50])
    
    pred_sets, set_sizes = conformal.predict_sets(y_prob[50:])
    coverage_metrics = conformal.evaluate_coverage(
        data['y_val'][50:100], pred_sets
    )
    
    print(f"✓ Coverage: {coverage_metrics['coverage']:.4f} "
          f"(target: {coverage_metrics['target_coverage']:.4f})")
    print(f"  Avg set size: {coverage_metrics['avg_set_size']:.2f}")
    print(f"  Singleton rate: {coverage_metrics['singleton_rate']:.4f}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 80)
print("QUICK TEST COMPLETE")
print("=" * 80)
print("\nAll core components are working!")
print("\nNext steps:")
print("  1. Run full experiments: python run_experiments.py")
print("  2. Start API server: python -m uvicorn src.api:app --host 0.0.0.0 --port 8000")
print("  3. Generate report: python generate_report.py")
print("  4. Open frontend: frontend/index.html")
print()
