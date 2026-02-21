# TabPFN Production Pipeline - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.10+ installed
- pip package manager
- 2GB RAM minimum
- Internet connection (for package installation)

### Step 1: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

This installs:
- scikit-learn, pandas, numpy (data processing)
- lightgbm (baseline model)
- fastapi, uvicorn (API server)
- prometheus-client (monitoring)
- matplotlib, seaborn (visualization)

### Step 2: Run Quick Test (10 seconds)

```bash
python quick_test.py
```

**Expected Output:**
```
✓ Data Loading: 1442 train samples, 376 test samples
✓ LightGBM: AUC=1.0000
✓ Shift Detection (no shift): AUC=0.5395, Shift=NO
✓ Shift Detection (mean shift): AUC=0.9936, Shift=YES
✓ Calibration: ECE improved 100%
✓ Conformal Prediction: 90% coverage
```

### Step 3: Generate Predictions (5 seconds)

```bash
python generate_submission.py
```

**Output:**
- `results/submission.csv` - Predictions for test set
- Validation AUC: 1.0000
- 376 predictions generated

### Step 4: Run Full Experiments (2-5 minutes)

```bash
python run_experiments.py
```

**Generates:**
- `results/experiment_results.json` - Complete metrics
- Baseline comparison (Logistic, LightGBM, TabPFN)
- Shift detection experiments
- Calibration evaluation
- Conformal prediction validation

### Step 5: Generate Report (5 seconds)

```bash
python generate_report.py
```

**Generates:**
- `results/REPORT.md` - Technical report
- `results/model_comparison.png`
- `results/shift_detection.png`
- `results/calibration.png`
- `results/conformal_prediction.png`

## 🌐 Run API Server

### Option A: Python (Development)

```bash
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Access:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Option B: Docker (Production)

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

Access:
- API: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### Test API

```bash
python test_api.py
```

Or use curl:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [[2.42, 0.15, 0.0, ...]],
    "use_calibration": true,
    "use_conformal": true
  }'
```

## 📊 View Results

### Web Frontend
Open `frontend/index.html` in your browser for an interactive demo.

### Monitoring Dashboards
- **Grafana**: http://localhost:3000
  - Username: admin
  - Password: admin
  - Add panels for predictions, latency, shift detection

- **Prometheus**: http://localhost:9090
  - Query: `predictions_total`
  - Query: `prediction_latency_seconds`
  - Query: `shift_detected_total`

## 🎯 Common Tasks

### Run Specific Experiments

```python
from src.experiments import ExperimentRunner

runner = ExperimentRunner()
results = runner.run_baseline_comparison(data)
results = runner.run_shift_detection_experiments(data)
results = runner.run_calibration_experiments(data)
results = runner.run_conformal_experiments(data)
```

### Use Individual Components

```python
# Shift Detection
from src.shift_detector import ShiftDetector
detector = ShiftDetector(threshold=0.6)
result = detector.detect_shift(reference_data, current_data)

# Calibration
from src.calibration import TemperatureScaling
calibrator = TemperatureScaling()
calibrator.fit(logits, y_true)
calibrated_probs = calibrator.transform(new_logits)

# Conformal Prediction
from src.conformal import SplitConformalClassifier
conformal = SplitConformalClassifier(alpha=0.1)
conformal.calibrate(y_cal, probs_cal)
pred_sets, sizes = conformal.predict_sets(probs_test)
```

### Train Custom Model

```python
from src.predictors import BaselinePredictor
from src.data_loader import DataLoader

# Load data
loader = DataLoader("dataset/train.csv", "dataset/test.csv")
train_df, test_df = loader.load_data()
data = loader.preprocess(train_df, test_df)

# Train model
model = BaselinePredictor('lightgbm')
model.fit(data['X_train'], data['y_train'])

# Evaluate
metrics = model.evaluate(data['X_val'], data['y_val'])
print(f"AUC: {metrics['auc']:.4f}")

# Predict
predictions = model.predict(data['X_test'])
```

## 🐛 Troubleshooting

### Issue: Import errors
**Solution:** Make sure you're in the project root directory and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: TabPFN not working
**Solution:** TabPFN is optional. The system automatically falls back to LightGBM:
```bash
pip install tabpfn  # Optional
```

### Issue: API won't start
**Solution:** Check if port 8000 is available:
```bash
# Windows
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <PID> /F
```

### Issue: Docker containers won't start
**Solution:** Check Docker is running and ports are available:
```bash
docker-compose down
docker-compose up -d
```

### Issue: Out of memory
**Solution:** Reduce dataset size in experiments:
```python
# In experiments.py, use subset
X_train = X_train[:500]
y_train = y_train[:500]
```

## 📚 File Structure

```
.
├── src/                    # Core pipeline code
├── dataset/                # Real financial data
│   ├── train.csv          # 1442 samples
│   ├── test.csv           # 376 samples
│   └── sample_submission.csv
├── results/                # Generated outputs
│   ├── submission.csv     # Test predictions
│   ├── experiment_results.json
│   └── REPORT.md
├── monitoring/             # Prometheus & Grafana config
├── frontend/               # Web demo
├── quick_test.py          # ⭐ Start here
├── generate_submission.py # ⭐ Generate predictions
├── run_experiments.py     # ⭐ Full experiments
├── generate_report.py     # ⭐ Create report
└── README.md              # Full documentation
```

## 🎓 Learning Path

1. **Beginner**: Run `quick_test.py` to see all components
2. **Intermediate**: Run `run_experiments.py` for full evaluation
3. **Advanced**: Modify `src/` modules for custom behavior
4. **Production**: Deploy with `docker-compose up -d`

## 💡 Tips

- Use `quick_test.py` for rapid iteration
- Check `results/experiment_results.json` for detailed metrics
- Monitor API with Prometheus/Grafana
- Customize thresholds in config files
- Add new models in `src/predictors.py`
- Extend experiments in `src/experiments.py`

## 🔗 Resources

- **API Docs**: http://localhost:8000/docs (when running)
- **README**: Full documentation
- **IMPLEMENTATION_SUMMARY**: Complete feature list
- **Code**: Well-documented inline comments

## ✅ Verification Checklist

After setup, verify:
- [ ] `quick_test.py` runs successfully
- [ ] All 6 tests pass with ✓
- [ ] `results/submission.csv` generated
- [ ] API responds at http://localhost:8000/health
- [ ] Frontend opens in browser
- [ ] Prometheus accessible at :9090
- [ ] Grafana accessible at :3000

## 🎉 Success!

You now have a complete production ML pipeline running!

**Next Steps:**
1. Explore the web frontend
2. Try the API with different inputs
3. View monitoring dashboards
4. Read the technical report
5. Customize for your use case

**Questions?** Check:
- README.md for detailed docs
- IMPLEMENTATION_SUMMARY.md for features
- Code comments for implementation details

---

**Built with ❤️ using real financial data**
