# ⚠️ IMPORTANT: AUC Evaluation Requires Probabilities

## Critical Understanding

**AUC (Area Under ROC Curve) measures RANKING quality, not classification accuracy.**

### ❌ Wrong Approach (Binary Predictions)
```python
# DON'T DO THIS for AUC evaluation
predictions = model.predict(X_test)  # Returns [0, 1, 0, 1, ...]
# This destroys ranking information!
```

### ✅ Correct Approach (Probabilities)
```python
# DO THIS for AUC evaluation
probabilities = model.predict_proba(X_test)  # Returns [0.83, 0.27, 0.61, ...]
# This preserves full ranking information!
```

## Why This Matters

### AUC Evaluates Ranking
- **Question**: How well does your model rank positive samples higher than negative samples?
- **Requirement**: Continuous scores (probabilities) that preserve relative ordering

### Example Comparison

**Scenario**: 3 samples with true labels [1, 0, 1]

**Binary predictions** [1, 0, 1]:
- No ranking information
- Can't distinguish confidence levels
- AUC calculation is ambiguous

**Probability predictions** [0.95, 0.12, 0.78]:
- Clear ranking: Sample 1 (0.95) > Sample 3 (0.78) > Sample 2 (0.12)
- Preserves confidence levels
- AUC can properly evaluate ranking quality

### Impact on Submission

If you submit:
- **Binary (0/1)**: You destroy ranking → Poor AUC evaluation
- **Probabilities (0.0-1.0)**: Full ranking preserved → Proper AUC evaluation

## Implementation in This Project

### ✅ Already Fixed

1. **Submission Generator** (`generate_submission.py`):
   ```python
   # Uses probabilities
   test_probabilities = model.predict_proba(data['X_test'])
   submission['IsDefault'] = test_probabilities
   ```

2. **API Response** (`src/api.py`):
   ```python
   # Returns probabilities
   probabilities = model.predict_proba(X)
   return PredictionResponse(probabilities=probabilities.tolist())
   ```

3. **All Predictors** (`src/predictors.py`):
   ```python
   # All models have predict_proba() method
   def predict_proba(self, X: np.ndarray) -> np.ndarray:
       return self.model.predict_proba(X)[:, 1]  # Probability of class 1
   ```

### Verification

Check your submission file:
```bash
head results/submission.csv
```

Should show:
```
Stock code,IsDefault
X01443,0.0028347551768383513
X01444,0.010310752522258377
X01445,0.013428646155234753
...
```

**✓ Probabilities (continuous values 0-1)**  
**✗ NOT binary (0 or 1)**

## Current Submission Stats

```
Probability range: [0.0012, 0.9961]
Mean probability: 0.2706
Total predictions: 376
```

This is correct! The probabilities:
- Range from near 0 to near 1
- Preserve full ranking information
- Enable proper AUC evaluation

## Key Takeaways

1. **AUC = Ranking metric**, not accuracy metric
2. **Always use probabilities** for AUC evaluation
3. **Binary predictions destroy ranking** information
4. **This project correctly uses probabilities** throughout
5. **Submission file contains probabilities** (verified ✓)

## For Other Metrics

- **Accuracy/Precision/Recall**: Need binary predictions (threshold at 0.5)
- **AUC/ROC**: Need probabilities (no threshold)
- **Log Loss**: Need probabilities
- **Brier Score**: Need probabilities

## Quick Test

```python
from src.predictors import BaselinePredictor
import numpy as np

model = BaselinePredictor('lightgbm')
model.fit(X_train, y_train)

# Get probabilities (correct for AUC)
probs = model.predict_proba(X_test)
print(f"Probabilities: {probs[:5]}")  # [0.83, 0.27, 0.61, ...]

# Get binary predictions (wrong for AUC)
preds = model.predict(X_test)
print(f"Binary: {preds[:5]}")  # [1, 0, 1, ...]

# For AUC evaluation, use probs!
from sklearn.metrics import roc_auc_score
auc = roc_auc_score(y_test, probs)  # ✓ Correct
# auc = roc_auc_score(y_test, preds)  # ✗ Wrong
```

---

**Status**: ✅ This project correctly uses probabilities for AUC evaluation throughout all components.
