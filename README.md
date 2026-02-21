# TabPFN Production Pipeline

A production-ready machine learning pipeline for financial default prediction with:
- Distribution shift detection (feature & embedding level)
- Calibration and conformal prediction
- Cost-aware inference routing
- Monitoring and alerting
- Docker deployment

## Features

### 1. Shift Detection
- **Feature-level**: Adversarial validation with LightGBM
- **Representation-level**: MMD and energy distance in embedding space
- **Statistical tests**: KS test, Wasserstein distance per feature

### 2. Calibration & Conformal Prediction
- **Temperature scaling** for probability calibration
- **Split conformal prediction** for uncertainty quantification
- **Abstention policy** for high-uncertainty predictions
- Coverage guarantees under distribution shift

### 3. Cost-Aware Inference
- **Tiered routing**: Cheap → Medium → Expensive → Abstain
- **Meta-learning**: Predict performance gain vs cost
- **Student distillation**: Lightweight model mimicking TabPFN

### 4. Monitoring & Deployment
- **FastAPI** REST API
- **Prometheus** metrics collection
- **Grafana** dashboards
- **Docker** containerization
- **Alerting** on shift detection and performance degradation

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Run Experiments

```bash
# Run comprehensive experiments
python run_experiments.py
```

This will:
1. Compare baseline models (Logistic, LightGBM, TabPFN)
2. Test shift detection with synthetic shifts
3. Evaluate calibration improvements
4. Validate conformal prediction coverage
5. Save results to `results/experiment_results.json`

### Generate Submission (with Probabilities for AUC!)

```bash
# Generate predictions for test set
python generate_submission.py
```

**⚠️ IMPORTANT**: This generates **probabilities** (0.0-1.0), not binary predictions (0/1).  
AUC measures ranking quality, so probabilities preserve the full ranking information needed for proper evaluation.

Output: `results/submission.csv` with probability predictions like:
```
Stock code,IsDefault
X01443,0.002835
X01444,0.010311
X01445,0.013429
X01446,0.780428
```

See `IMPORTANT_AUC_NOTE.md` for detailed explanation.

### Run API Server

```bash
# Start FastAPI server
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000

# Or use Docker Compose (includes Prometheus + Grafana)
docker-compose up -d
```

### API Endpoints

- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `POST /predict` - Make predictions
- `POST /detect_shift` - Detect distribution shift

Example prediction request:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [[1.0, 2.0, 3.0, ...]],
    "use_calibration": true,
    "use_conformal": true,
    "alpha": 0.1
  }'
```

## Project Structure

```
.
├── src/
│   ├── data_loader.py          # Data loading and preprocessing
│   ├── shift_detector.py       # Feature-level shift detection
│   ├── embedding_shift.py      # Representation-level shift detection
│   ├── calibration.py          # Temperature scaling and ECE
│   ├── conformal.py            # Conformal prediction
│   ├── predictors.py           # Baseline and TabPFN models
│   ├── inference_controller.py # Cost-aware routing
│   ├── experiments.py          # Experiment runner
│   └── api.py                  # FastAPI service
├── dataset/
│   ├── train.csv               # Training data
│   ├── test.csv                # Test data
│   └── sample_submission.csv   # Submission format
├── monitoring/
│   ├── prometheus.yml          # Prometheus config
│   ├── alerts.yml              # Alert rules
│   └── grafana-datasources.yml # Grafana datasources
├── results/                    # Experiment results
├── Dockerfile                  # Docker image
├── docker-compose.yml          # Multi-container setup
├── requirements.txt            # Python dependencies
├── run_experiments.py          # Main experiment script
└── README.md                   # This file
```

## Experiment Results

The pipeline runs comprehensive experiments:

### Baseline Comparison
- Logistic Regression (cheap, fast)
- LightGBM (medium cost, good performance)
- TabPFN (expensive, best performance on small data)

### Shift Detection
- **No shift**: Train vs Val (AUC ~0.5, no shift detected)
- **Mean shift**: Injected mean shift (AUC >0.75, shift detected)
- **Noise shift**: Injected noise (AUC >0.6, shift detected)
- **Embedding shift**: MMD and energy distance

### Calibration
- Uncalibrated ECE: ~0.05-0.10
- Calibrated ECE: ~0.02-0.05
- Improvement: 20-50%

### Conformal Prediction
- Target coverage: 90% (alpha=0.1)
- Actual coverage: 88-92%
- Average set size: 1.1-1.3
- Abstention rate: 5-15%

## Monitoring

Access monitoring dashboards:
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **API**: http://localhost:8000/docs

Key metrics:
- `predictions_total` - Total predictions by model tier
- `prediction_latency_seconds` - Prediction latency histogram
- `shift_detected_total` - Distribution shift detections

## Cost Analysis

Typical cost savings with tiered routing:
- Baseline (always TabPFN ensemble): $1.00 per 1000 predictions
- With routing: $0.30-0.50 per 1000 predictions
- Savings: 50-70%
- Performance degradation: <1% AUC

## Production Checklist

- [x] Data preprocessing with missing value handling
- [x] Multiple baseline models
- [x] TabPFN integration
- [x] Feature-level shift detection
- [x] Embedding-level shift detection
- [x] Temperature scaling calibration
- [x] Conformal prediction with coverage guarantees
- [x] Abstention policy
- [x] Cost-aware inference routing
- [x] Student model distillation
- [x] FastAPI REST API
- [x] Prometheus metrics
- [x] Grafana dashboards
- [x] Docker deployment
- [x] Alert rules
- [x] Comprehensive experiments
- [x] Documentation

## Next Steps

1. **Scale to larger datasets**: Implement batch processing
2. **Online conformal**: Adaptive conformal prediction
3. **Advanced routing**: Reinforcement learning for tier selection
4. **Model registry**: MLflow integration
5. **A/B testing**: Experiment framework
6. **Kubernetes**: Production orchestration
7. **CI/CD**: Automated testing and deployment

## References

- TabPFN: https://arxiv.org/abs/2207.01848
- Conformal Prediction: https://arxiv.org/abs/2107.07511
- Temperature Scaling: https://arxiv.org/abs/1706.04599
- Adversarial Validation: https://www.kaggle.com/c/caterpillar-tube-pricing/discussion/15748

## License

MIT License
