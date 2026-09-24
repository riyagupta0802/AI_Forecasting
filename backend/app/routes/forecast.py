"""Attack Forecasting API Routes for HEX HIVE Phase 6.

Provides endpoints for:
- GET  /api/forecast/status  (Real attack forecast status & lifecycle progression)
- GET  /api/forecast/metrics (Real test-set evaluation metrics for stage classification)
- POST /api/forecast/predict (End-to-end detection -> stage -> next-attack forecast inference)
"""

from pathlib import Path
import json
import logging
import sys
from fastapi import APIRouter, HTTPException, status

# Ensure repo root is on sys.path for clean ml imports
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.schemas.forecast import (
    ForecastStatusResponse,
    ForecastMetricsResponse,
    ForecastPredictRequest,
    ForecastPredictResponse,
)
from ml.forecasting.predict import forecaster
from ml.escalation.predict import escalation_predictor

logger = logging.getLogger("HEX_HIVE.Routes.Forecast")
router = APIRouter(prefix="/forecast", tags=["Attack Forecasting"])

METRICS_PATH = REPO_ROOT / "ml" / "models" / "forecast_metrics.json"
MODEL_PATH = REPO_ROOT / "ml" / "models" / "forecast_stage_classifier.joblib"


@router.get(
    "/status",
    response_model=ForecastStatusResponse,
    summary="Get Attack Forecast Status",
    description=(
        "Returns active machine learning attack forecast, current stage identification, "
        "projected next transition stage, confidence, risk level, trajectory, and limitations."
    ),
)
async def get_forecast_status() -> ForecastStatusResponse:
    """Return active forecast status with real machine learning stage transition output."""
    if not forecaster.is_ready or not MODEL_PATH.is_file():
        return ForecastStatusResponse(
            status="unavailable",
            forecast_available=False,
            current_pattern="Awaiting ML model",
            possible_next_stage="Forecasting unavailable",
            confidence=None,
            time_to_escalation=None,
            current_state="UNAVAILABLE",
            predicted_next_stage="None",
            risk_level="LOW",
            model="None",
            explanation="Forecasting stage classifier weights are unavailable on the server.",
            limitations=(
                "Forecasting requires trained model artifacts at ml/models/forecast_stage_classifier.joblib. "
                "Run 'python ml/forecasting/train.py' to generate artifacts."
            ),
        )

    # Execute real baseline forecast inference and escalation timing
    try:
        res = forecaster.predict(sample_type="benign")
        esc_res = escalation_predictor.predict(sample_type="benign")
        time_to_esc = esc_res.get("estimated_time_seconds")

        return ForecastStatusResponse(
            status="active",
            current_pattern=res.get("current_state", "BENIGN"),
            possible_next_stage=res.get("predicted_next_stage", "BENIGN"),
            confidence=res.get("confidence", 88.0),
            time_to_escalation=time_to_esc,
            forecast_available=True,
            current_state=res.get("current_state", "BENIGN"),
            current_state_desc=res.get("current_state_desc", "Normal Baseline Traffic"),
            predicted_next_stage=res.get("predicted_next_stage", "BENIGN"),
            predicted_next_stage_display=res.get("predicted_next_stage_display", "BENIGN (Normal Baseline)"),
            risk_level=res.get("risk_level", "LOW"),
            model=res.get("model", "StageClassifier + EmpiricalKillChainTransition"),
            timestamp=res.get("timestamp"),
            explanation=res.get("explanation"),
            transition_probabilities=res.get("transition_probabilities"),
            trajectory=res.get("trajectory"),
            limitations=res.get("limitations"),
        )
    except Exception as e:
        logger.error("Error generating forecast status: %s", e)
        return ForecastStatusResponse(
            status="error",
            forecast_available=False,
            current_pattern="Error",
            possible_next_stage="Error",
            confidence=None,
            time_to_escalation=None,
            explanation=f"Runtime error during forecast inference: {str(e)}",
        )


@router.get(
    "/metrics",
    response_model=ForecastMetricsResponse,
    summary="Get Forecasting Evaluation Metrics",
    description="Returns real evaluated test-set metrics (Accuracy, Precision, Recall, F1, Confusion Matrix).",
)
async def get_forecast_metrics() -> ForecastMetricsResponse:
    """Return genuine evaluated performance metrics for Phase 6 forecasting."""
    if not METRICS_PATH.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Forecast metrics not found. Run 'python ml/forecasting/train.py' "
                "to evaluate and generate forecast_metrics.json."
            ),
        )

    try:
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ForecastMetricsResponse(**data)
    except Exception as e:
        logger.error("Failed to parse forecast metrics: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading forecast metrics: {str(e)}",
        )


@router.post(
    "/predict",
    response_model=ForecastPredictResponse,
    summary="Run Live Attack Forecast Inference",
    description=(
        "Executes end-to-end pipeline: Preprocessing -> Phase 5 Detection -> "
        "Phase 6 Stage Classification -> Transition Forecasting."
    ),
)
async def predict_forecast(req: ForecastPredictRequest) -> ForecastPredictResponse:
    """Perform real-time attack detection and transition forecasting."""
    if not forecaster.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Attack forecasting model is not initialized or model weights are missing.",
        )

    # Validate input: feature vector or dictionary or preset sample
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
        result = forecaster.predict(features=features, sample_type=sample_type)
        return ForecastPredictResponse(**result)
    except Exception as e:
        logger.error("Forecast prediction error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forecast inference failed: {str(e)}",
        )
