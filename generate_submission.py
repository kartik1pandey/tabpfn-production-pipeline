"""Generate submission file for test set."""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import DataLoader
from src.predictors import BaselinePredictor

print("=" * 80)
print("Generating Submission File")
print("=" * 80)

# Load data
print("\nLoading data...")
loader = DataLoader("dataset/train.csv", "dataset/test.csv")
train_df, test_df = loader.load_data()

# Preprocess
print("Preprocessing...")
data = loader.preprocess(train_df, test_df, val_size=0.1)

# Train model on full training data
print("\nTraining LightGBM on full training set...")
model = BaselinePredictor('lightgbm')

# Combine train and val for final model
X_full = np.vstack([data['X_train'], data['X_val']])
y_full = np.hstack([data['y_train'], data['y_val']])

model.fit(X_full, y_full)

# Evaluate on validation set
val_metrics = model.evaluate(data['X_val'], data['y_val'])
print(f"Validation AUC: {val_metrics['auc']:.4f}")
print(f"Validation Accuracy: {val_metrics['accuracy']:.4f}")

# Predict on test set (use probabilities for AUC ranking!)
print("\nGenerating predictions for test set...")
test_probabilities = model.predict_proba(data['X_test'])  # Get probabilities, not binary predictions

# Create submission file with probabilities
submission = pd.DataFrame({
    'Stock code': data['test_ids'],
    'IsDefault': test_probabilities  # Submit probabilities for proper AUC evaluation
})

# Save submission
output_path = "results/submission.csv"
submission.to_csv(output_path, index=False)

print(f"\n✓ Submission saved to: {output_path}")
print(f"  Shape: {submission.shape}")
print(f"  Probability range: [{submission['IsDefault'].min():.4f}, {submission['IsDefault'].max():.4f}]")
print(f"  Mean probability: {submission['IsDefault'].mean():.4f}")

# Show sample
print("\nSample predictions (probabilities for AUC ranking):")
print(submission.head(10))

print("\n" + "=" * 80)
print("Submission generation complete!")
print("=" * 80)
