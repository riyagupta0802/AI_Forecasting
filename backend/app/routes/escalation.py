"""Time-to-Escalation API Routes for HEX HIVE Phase 7.

Provides endpoints for:
- GET  /api/escalation/status  (Active threat escalation status and estimated window)
- GET  /api/escalation/metrics (Real evaluated test-set regression metrics: MAE, RMSE, R²)
- POST /api/escalation/predict (Live Detection -> Forecasting -> Time-to-Escalation inference)
"""

from pathlib import Path
import json
import logging
import sys
from fastapi import APIRouter, HTTPException, status

# Ensure repo root is on sys.path
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.schemas.escalation import (
    EscalationStatusResponse,
    EscalationMetricsResponse,
    EscalationPredictRequest,
    EscalationPredictResponse,
)
from ml.escalation.predict import escalation_predictor

logger = logging.getLogger("HEX_HIVE.Routes.Escalation")
router = APIRouter(prefix="/escalation", tags=["Time-to-Escalation"])

METRICS_PATH = REPO_ROOT / "ml" / "models" / "escalation_metrics.json"


@router.get(
    "/status",
    response_model=EscalationStatusResponse,
    summary="Get Threat Escalation Status & Window",
    description=(
        "Returns current threat escalation window estimation, transition target, "
        "velocity index, confidence, and calibrated risk level."
    ),
)
async def get_escalation_status() -> EscalationStatusResponse:
    """Return active escalation status for the current network telemetry posture."""
    try:
        res = escalation_predictor.predict(sample_type="benign")
        return EscalationStatusResponse(
            status="ready",
            available=res.get("available", True),
            current_state=res.get("current_state", "BENIGN"),
            predicted_state=res.get("predicted_state", "BENIGN"),
            escalation_condition=res.get("escalation_condition", "Baseline traffic"),
            is_escalating=res.get("is_escalating", False),
            estimated_time_seconds=res.get("estimated_time_seconds"),
            estimated_time_minutes=res.get("estimated_time_minutes"),
            formatted_time=res.get("formatted_time", "Not Escalating"),
            risk_level=res.get("risk_level", "LOW"),
            confidence=res.get("confidence", 88.0),
            velocity_index=res.get("velocity_index", 1.0),
            method=res.get("method", "TelemetryVelocityCalibratedProgression"),
            timestamp=res.get("timestamp"),
            explanation=res.get("explanation"),
            limitations=res.get("limitations"),
        )
    except Exception as e:
        logger.error("Failed to compute escalation status: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating escalation status: {str(e)}",
        )


@router.get(
    "/metrics",
    response_model=EscalationMetricsResponse,
    summary="Get Escalation Model Evaluation Metrics",
    description="Returns real evaluated test-set metrics (MAE, RMSE, R-squared, top features).",
)
async def get_escalation_metrics() -> EscalationMetricsResponse:
    """Return genuine evaluated performance metrics for Phase 7 escalation model."""
    if not METRICS_PATH.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Escalation metrics not found. Run 'python ml/escalation/train.py' "
                "to evaluate and generate escalation_metrics.json."
            ),
        )

    try:
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return EscalationMetricsResponse(**data)
    except Exception as e:
        logger.error("Failed to parse escalation metrics: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading escalation metrics: {str(e)}",
        )


@router.post(
    "/predict",
    response_model=EscalationPredictResponse,
    summary="Run Live Time-to-Escalation Inference",
    description=(
        "Executes end-to-end chain: Preprocessing -> Phase 5 Detection -> "
        "Phase 6 Forecasting -> Phase 7 Velocity-Calibrated Time-to-Escalation."
    ),
)
async def predict_escalation(req: EscalationPredictRequest) -> EscalationPredictResponse:
    """Perform live multi-phase detection, forecasting, and escalation window estimation."""
    features = None
    if req.feature_vector is not None:
        if len(req.feature_vector) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Provided feature_vector is empty.",
            )
        features = req.feature_vector
    elif req.features is not None:
        if len(req.features) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Provided features dictionary is empty.",
            )
        features = req.features

    sample_type = req.sample_type or "auto"

    try:
        res = escalation_predictor.predict(features=features, sample_type=sample_type)
        return EscalationPredictResponse(**res)
    except Exception as e:
        logger.error("Escalation prediction failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Escalation inference failed: {str(e)}",
        )

