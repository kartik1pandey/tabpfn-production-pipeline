"""Simplified FastAPI service for Vercel serverless deployment."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TabPFN Production API",
    version="1.0.0",
    description="Production ML pipeline with shift detection and conformal prediction"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    inference_time: float
    model_tier: str
    message: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint."""
    return HealthResponse(
        status="healthy",
        message="TabPFN Production API - Visit /docs for documentation"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="API is running"
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make predictions (lightweight version for Vercel).
    
    Note: This is a demo endpoint. For full functionality with trained models,
    use the Docker deployment or local setup.
    """
    import time
    start_time = time.time()
    
    try:
        # Convert to numpy array
        X = np.array(request.features)
        n_samples = X.shape[0]
        
        # Simple heuristic predictions for demo
        # In production, this would use the trained model
        # For now, use a simple rule based on feature means
        feature_means = X.mean(axis=1)
        probabilities = 1 / (1 + np.exp(-0.1 * (feature_means - feature_means.mean())))
        predictions = (probabilities > 0.5).astype(int)
        
        inference_time = time.time() - start_time
        
        return PredictionResponse(
            predictions=predictions.tolist(),
            probabilities=probabilities.tolist(),
            inference_time=inference_time,
            model_tier="demo",
            message="Demo predictions - Deploy with Docker for full model"
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return {
        "predictions_total": 0,
        "prediction_latency_seconds": 0.0,
        "shift_detected_total": 0,
        "message": "Metrics endpoint - Full metrics available in Docker deployment"
    }


@app.post("/detect_shift")
async def detect_shift(request: PredictionRequest):
    """
    Detect distribution shift (demo version).
    """
    try:
        X = np.array(request.features)
        
        # Simple demo shift detection
        result = {
            "shift_detected": False,
            "auc_score": 0.5,
            "message": "Demo shift detection - Deploy with Docker for full functionality"
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Shift detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# For Vercel
handler = app
