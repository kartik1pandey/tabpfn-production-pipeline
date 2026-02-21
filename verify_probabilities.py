"""Verify that submission contains probabilities, not binary predictions."""
import pandas as pd
import numpy as np

print("=" * 80)
print("Verifying Submission Format for AUC Evaluation")
print("=" * 80)

# Load submission
submission = pd.read_csv("results/submission.csv")

print("\n📊 Submission Statistics:")
print(f"  Total predictions: {len(submission)}")
print(f"  Probability range: [{submission['IsDefault'].min():.6f}, {submission['IsDefault'].max():.6f}]")
print(f"  Mean probability: {submission['IsDefault'].mean():.6f}")
print(f"  Std probability: {submission['IsDefault'].std():.6f}")

# Check if probabilities (continuous) or binary (0/1)
unique_values = submission['IsDefault'].nunique()
is_binary = set(submission['IsDefault'].unique()).issubset({0, 1})

print(f"\n🔍 Format Check:")
print(f"  Unique values: {unique_values}")
print(f"  Is binary (0/1 only): {is_binary}")

if is_binary:
    print("\n  ❌ ERROR: Submission contains binary predictions!")
    print("  This will NOT work properly for AUC evaluation.")
    print("  AUC requires probabilities to measure ranking quality.")
else:
    print("\n  ✅ CORRECT: Submission contains probabilities!")
    print("  This preserves ranking information for proper AUC evaluation.")

# Show distribution
print(f"\n📈 Probability Distribution:")
print(f"  < 0.1:  {(submission['IsDefault'] < 0.1).sum()} samples ({(submission['IsDefault'] < 0.1).mean()*100:.1f}%)")
print(f"  0.1-0.3: {((submission['IsDefault'] >= 0.1) & (submission['IsDefault'] < 0.3)).sum()} samples")
print(f"  0.3-0.5: {((submission['IsDefault'] >= 0.3) & (submission['IsDefault'] < 0.5)).sum()} samples")
print(f"  0.5-0.7: {((submission['IsDefault'] >= 0.5) & (submission['IsDefault'] < 0.7)).sum()} samples")
print(f"  0.7-0.9: {((submission['IsDefault'] >= 0.7) & (submission['IsDefault'] < 0.9)).sum()} samples")
print(f"  > 0.9:  {(submission['IsDefault'] > 0.9).sum()} samples ({(submission['IsDefault'] > 0.9).mean()*100:.1f}%)")

# Show sample predictions
print(f"\n📋 Sample Predictions (first 10):")
print(submission.head(10).to_string(index=False))

print(f"\n📋 High Confidence Predictions (top 5 by probability):")
top5 = submission.nlargest(5, 'IsDefault')
print(top5.to_string(index=False))

print(f"\n📋 Low Confidence Predictions (bottom 5 by probability):")
bottom5 = submission.nsmallest(5, 'IsDefault')
print(bottom5.to_string(index=False))

# Demonstrate ranking preservation
print(f"\n🎯 Ranking Preservation Example:")
print("  If we had binary predictions [1, 0, 1]:")
print("    → No way to know which '1' is more confident")
print("    → Ranking information lost")
print("\n  With probabilities [0.95, 0.12, 0.78]:")
print("    → Clear ranking: 0.95 > 0.78 > 0.12")
print("    → Full ranking preserved for AUC calculation")

print("\n" + "=" * 80)
print("Verification Complete!")
print("=" * 80)

if not is_binary:
    print("\n✅ Your submission is correctly formatted for AUC evaluation!")
    print("   Probabilities preserve ranking information needed for proper scoring.")
else:
    print("\n❌ WARNING: Your submission needs to be fixed!")
    print("   Use model.predict_proba() instead of model.predict()")
