"""FastAPI service for production deployment."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from typing import List, Dict, Optional
import time
import logging
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response

from .predictors import BaselinePredictor, TabPFNPredictor
from .shift_detector import ShiftDetector
from .calibration import TemperatureScaling
from .conformal import SplitConformalClassifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
prediction_counter = Counter('predictions_total', 'Total predictions', ['model_tier'])
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')
shift_detected_counter = Counter('shift_detected_total', 'Total shift detections')

app = FastAPI(title="TabPFN Production API", version="1.0.0")


class PredictionRequest(BaseModel):
    """Prediction request schema."""
    features: List[List[float]]
    use_calibration: bool = True
    use_conformal: bool = False
    alpha: float = 0.1


class PredictionResponse(BaseModel):
    """Prediction response schema."""
    predictions: List[int]
    probabilities: List[float]
    conformal_sets: Optional[List[List[int]]] = None
    inference_time: float
    model_tier: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    models_loaded: Dict[str, bool]


# Global model storage
models = {
    'cheap': None,
    'medium': None,
    'expensive': None
}

shift_detector = None
calibrator = None
conformal_predictor = None


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup."""
    global models, shift_detector, calibrator, conformal_predictor
    
    logger.info("Loading models...")
    
    try:
        # Load baseline models
        models['cheap'] = BaselinePredictor('logistic')
        models['medium'] = BaselinePredictor('lightgbm')
        
        # Initialize shift detector
        shift_detector = ShiftDetector(threshold=0.6)
        
        # Initialize calibrator
        calibrator = TemperatureScaling()
        
        # Initialize conformal predictor
        conformal_predictor = SplitConformalClassifier(alpha=0.1)
        
        logger.info("Models loaded successfully")
    except Exception as e:
        logger.error(f"Error loading models: {e}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        models_loaded={
            'cheap': models['cheap'] is not None,
            'medium': models['medium'] is not None,
            'expensive': models['expensive'] is not None
        }
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type="text/plain")


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make predictions with optional calibration and conformal prediction.
    """
    start_time = time.time()
    
    try:
        # Convert to numpy array
        X = np.array(request.features)
        
        # Select model tier (simplified routing)
        if X.shape[0] < 100:
            model_tier = 'cheap'
        else:
            model_tier = 'medium'
        
        model = models[model_tier]
        
        if model is None:
            raise HTTPException(status_code=503, detail=f"Model {model_tier} not loaded")
        
        # Get predictions
        probabilities = model.predict_proba(X)
        predictions = (probabilities > 0.5).astype(int)
        
        # Apply calibration if requested
        if request.use_calibration and calibrator.temperature != 1.0:
            logits = np.log(probabilities / (1 - probabilities + 1e-10))
            probabilities = calibrator.transform(logits)
            predictions = (probabilities > 0.5).astype(int)
        
        # Apply conformal prediction if requested
        conformal_sets = None
        if request.use_conformal and conformal_predictor.q_hat is not None:
            conformal_sets, _ = conformal_predictor.predict_sets(probabilities)
        
        inference_time = time.time() - start_time
        
        # Update metrics
        prediction_counter.labels(model_tier=model_tier).inc(len(X))
        prediction_latency.observe(inference_time)
        
        return PredictionResponse(
            predictions=predictions.tolist(),
            probabilities=probabilities.tolist(),
            conformal_sets=conformal_sets,
            inference_time=inference_time,
            model_tier=model_tier
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect_shift")
async def detect_shift(request: PredictionRequest):
    """
    Detect distribution shift in incoming data.
    """
    try:
        X = np.array(request.features)
        
        # For demo, compare against itself (in production, compare against reference)
        result = shift_detector.detect_shift(X[:len(X)//2], X[len(X)//2:])
        
        if result['shift_detected']:
            shift_detected_counter.inc()
        
        return result
        
    except Exception as e:
        logger.error(f"Shift detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
