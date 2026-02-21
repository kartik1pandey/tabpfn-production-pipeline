"""Main script to run all experiments."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.experiments import ExperimentRunner


def main():
    """Run all experiments."""
    print("\n" + "=" * 80)
    print("TabPFN Production Pipeline - Comprehensive Experiments")
    print("=" * 80 + "\n")
    
    # Initialize experiment runner
    runner = ExperimentRunner(output_dir="results")
    
    # Run full pipeline
    results = runner.run_full_pipeline(
        train_path="dataset/train.csv",
        test_path="dataset/test.csv"
    )
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Print key results
    if 'baseline_comparison' in results:
        print("\nBaseline Model Performance:")
        for model_name, metrics in results['baseline_comparison'].items():
            if 'auc' in metrics:
                print(f"  {model_name:20s}: AUC={metrics['auc']:.4f}, "
                      f"Time={metrics.get('inference_time', 0):.4f}s")
    
    if 'shift_detection' in results:
        print("\nShift Detection:")
        for test_name, result in results['shift_detection'].items():
            if 'auc_score' in result:
                print(f"  {test_name:20s}: AUC={result['auc_score']:.4f}, "
                      f"Shift={'YES' if result['shift_detected'] else 'NO'}")
    
    if 'calibration' in results:
        print("\nCalibration:")
        uncal = results['calibration'].get('uncalibrated', {})
        cal = results['calibration'].get('calibrated', {})
        if uncal and cal:
            print(f"  Uncalibrated ECE: {uncal.get('ece', 0):.4f}")
            print(f"  Calibrated ECE:   {cal.get('ece', 0):.4f}")
            print(f"  Improvement:      {results['calibration'].get('ece_improvement_pct', 0):.1f}%")
    
    if 'conformal' in results:
        print("\nConformal Prediction:")
        for alpha_key, metrics in results['conformal'].items():
            if alpha_key.startswith('alpha_'):
                print(f"  {alpha_key}: Coverage={metrics.get('coverage', 0):.4f}, "
                      f"Avg Set Size={metrics.get('avg_set_size', 0):.2f}")
    
    print(f"\nTotal execution time: {results.get('total_time', 0):.2f}s")
    print("\nDetailed results saved to: results/experiment_results.json")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
