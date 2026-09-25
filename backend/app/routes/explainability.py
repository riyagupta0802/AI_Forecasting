"""Explainable AI (XAI) API Routes for HEX HIVE Phase 11.

Provides endpoints for:
- GET  /api/explainability/status  (XAI engine readiness, model type, and metadata)
- POST /api/explainability/explain (Local SHAP explanation for an individual prediction)
- GET  /api/explainability/global  (Global feature importance rankings via mean |SHAP|)
"""

from pathlib import Path
from datetime import datetime, timezone
import logging
import sys
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

# Ensure repo root is on sys.path
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.schemas.explainability import (
    ExplainabilityStatusResponse,
    LocalExplanationResponse,
    GlobalExplanationResponse,
    ExplainRequest,
)
from ml.explainability import attack_explainer

logger = logging.getLogger("HEX_HIVE.Routes.Explainability")
router = APIRouter(prefix="/explainability", tags=["Explainable AI (XAI)"])


@router.get(
    "/status",
    response_model=ExplainabilityStatusResponse,
    summary="Get XAI Engine Status",
    description="Returns SHAP TreeExplainer availability, model architecture, feature count, and limitations.",
)
async def get_explainability_status() -> ExplainabilityStatusResponse:
    """Return XAI readiness and explainer configuration."""
    try:
        return ExplainabilityStatusResponse(
            status="ready" if attack_explainer.is_ready else "not_ready",
            explainer_ready=attack_explainer.is_ready,
            model_type="RandomForestClassifier",
            method="SHAP (TreeExplainer)",
            features_count=len(attack_explainer.feature_names) or 78,
            global_importance_ready=True,
            limitations=attack_explainer.limitations_note,
        )
    except Exception as e:
        logger.error("Failed to retrieve explainability status: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating XAI status: {str(e)}",
        )


@router.post(
    "/explain",
    response_model=LocalExplanationResponse,
    summary="Explain Network Traffic Detection",
    description="Calculates exact SHAP Shapley feature contributions for a network traffic flow observation.",
)
async def explain_detection(
    payload: ExplainRequest,
) -> LocalExplanationResponse:
    """Produce local SHAP feature contributions for a specific prediction."""
    try:
        top_n = payload.top_n if payload.top_n is not None else 5
        result = attack_explainer.explain_instance(
            features=payload.features,
            sample_type=payload.sample_type or "auto",
            top_n=top_n,
        )
        return LocalExplanationResponse(**result.to_dict())
    except ValueError as ve:
        logger.warning("Invalid input for explanation: %s", ve)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        logger.error("Failed to generate SHAP explanation: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating SHAP explanation: {str(e)}",
        )


@router.get(
    "/global",
    response_model=GlobalExplanationResponse,
    summary="Get Global Feature Importance",
    description="Returns global model feature importance rankings based on mean absolute SHAP values across benchmark evaluation flows.",
)
async def get_global_importance(
    top_n: Optional[int] = Query(10, ge=1, le=78, description="Number of top global features to return"),
) -> GlobalExplanationResponse:
    """Return overall global model feature importance via SHAP."""
    try:
        limit = top_n if isinstance(top_n, int) else 10
        global_result = attack_explainer.get_global_importance(top_n=limit)
        return GlobalExplanationResponse(**global_result.to_dict())
    except Exception as e:
        logger.error("Failed to retrieve global feature importance: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving global feature importance: {str(e)}",
        )

