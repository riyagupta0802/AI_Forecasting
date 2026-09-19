"""Machine Learning and Attack Detection API Routes for HEX HIVE Phase 5.

Provides endpoints for:
- GET  /api/ml/status  (Random Forest model status & readiness)
- GET  /api/ml/metrics (Real test-set evaluation metrics)
- POST /api/ml/predict (Real-time binary attack detection inference)
"""

from pathlib import Path
import json
import sys
from fastapi import APIRouter, HTTPException

# Add project root to sys.path for clean ml package access
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.schemas.ml import (
    MLStatusResponse,
    MLMetricsResponse,
    PredictRequest,
    PredictResponse,
)
from ml.predictions.predict import predictor

router = APIRouter(prefix="/ml", tags=["Machine Learning Attack Detection"])
METRICS_PATH = REPO_ROOT / "ml" / "models" / "model_metrics.json"
MODEL_PATH = REPO_ROOT / "ml" / "models" / "attack_classifier.joblib"


@router.get(
    "/status",
    response_model=MLStatusResponse,
    summary="Get ML Classifier Status",
    description="Returns current Random Forest model availability, architecture, and feature expectations.",
)
async def get_ml_status() -> MLStatusResponse:
    """Return model runtime status."""
    is_loaded = MODEL_PATH.is_file() and predictor.is_ready
    status_str = "ready" if is_loaded else "unavailable"

    return MLStatusResponse(
        status=status_str,
        model_loaded=is_loaded,
        model_type="Random Forest",
        task="Binary Attack Detection",
        features_count=len(predictor.feature_names) if predictor.feature_names else 78,
        classes=["BENIGN", "ATTACK"],
    )


@router.get(
    "/metrics",
    response_model=MLMetricsResponse,
    summary="Get Model Evaluation Metrics",
    description="Returns real calculated test-set performance metrics (Accuracy, Precision, Recall, F1, Confusion Matrix).",
)
async def get_ml_metrics() -> MLMetricsResponse:
    """Read and return real evaluated model performance metrics from disk."""
    if not METRICS_PATH.is_file():
        raise HTTPException(
            status_code=404,
            detail="Model metrics not found. Please ensure ml/training/train.py has been executed.",
        )

    try:
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return MLMetricsResponse(**data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load model evaluation metrics: {str(e)}",
        )


@router.post(
    "/predict",
    response_model=PredictResponse,
    summary="Classify Traffic Sample (BENIGN vs ATTACK)",
    description="Runs real Random Forest model inference on provided flow telemetry or benchmark test vectors.",
)
async def predict_traffic(request: PredictRequest = None) -> PredictResponse:
    """Perform real-time binary attack detection inference."""
    try:
        features_payload = request.features if request else None
        sample_type = request.sample_type if request and request.sample_type else "auto"

        res = predictor.predict(features=features_payload, sample_type=sample_type)
        return PredictResponse(**res)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inference execution failed: {str(e)}",
        )

