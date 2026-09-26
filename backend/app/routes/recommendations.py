"""Security Recommendation Engine API Routes for NETORACLE Phase 10.

Provides endpoints for:
- GET   /api/recommendations/status                 (Recommendation engine readiness and summary)
- GET   /api/recommendations                        (Active defensive recommendations with filters)
- POST  /api/recommendations/generate               (On-demand recommendation generation)
- PATCH /api/recommendations/{recommendation_id}/status (Operator status update: ACKNOWLEDGED, RESOLVED)
- POST  /api/recommendations/{recommendation_id}/status (Alias for status update)
"""

from pathlib import Path
from datetime import datetime, timezone
import logging
import sys
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Path as FastApiPath, status

# Ensure repo root is on sys.path
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.schemas.recommendations import (
    RecommendationsStatusResponse,
    RecommendationsResponse,
    RecommendationGenerateRequest,
    RecommendationStatusUpdateRequest,
    SecurityRecommendationSchema,
    RecommendationsSummarySchema,
)
from ml.recommendations import recommendation_engine

logger = logging.getLogger("NETORACLE.Routes.Recommendations")
router = APIRouter(prefix="/recommendations", tags=["Security Recommendations"])


@router.get(
    "/status",
    response_model=RecommendationsStatusResponse,
    summary="Get Recommendation Engine Readiness & Summary",
    description="Returns recommendation engine status, active threat posture, and statistical breakdown.",
)
async def get_recommendations_status() -> RecommendationsStatusResponse:
    """Return recommendation engine readiness and active summary."""
    try:
        eval_res = recommendation_engine.evaluate(sample_context="auto")
        summary_dict = eval_res.summary.to_dict()

        return RecommendationsStatusResponse(
            status="ready",
            engine_available=True,
            recommendations_available=eval_res.recommendations_available,
            active_threat_posture=eval_res.active_threat_posture,
            total_recommendations=summary_dict["total"],
            pending_count=summary_dict["pending"],
            summary=RecommendationsSummarySchema(**summary_dict),
            last_evaluated=eval_res.generated_at,
            limitations=eval_res.limitations,
        )
    except Exception as e:
        logger.error("Failed to retrieve recommendation status: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating recommendation status: {str(e)}",
        )


@router.get(
    "",
    response_model=RecommendationsResponse,
    summary="Get Defensive Security Recommendations",
    description="Returns active evidence-grounded defensive recommendations with optional filtering.",
)
async def get_recommendations(
    priority: Optional[str] = Query(None, description="Filter by priority ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'ALL')"),
    category: Optional[str] = Query(None, description="Filter by category ('Monitor', 'Investigate', 'Review', 'Isolate', 'Contain', 'Escalate', 'Preserve', 'ALL')"),
    rec_status: Optional[str] = Query(None, alias="status", description="Filter by status ('PENDING', 'ACKNOWLEDGED', 'RESOLVED', 'ALL')"),
    context: Optional[str] = Query("auto", description="Threat context scenario ('auto', 'benign', 'portscan', 'bot', 'ddos')"),
    limit: Optional[int] = Query(50, ge=1, le=500, description="Max telemetry flow events to evaluate"),
) -> RecommendationsResponse:
    """Evaluate and return defensive recommendations with optional filters."""
    # Safely unwrap parameters whether invoked via FastAPI or directly in Python
    prio_val = priority if isinstance(priority, str) else (priority.default if hasattr(priority, "default") and isinstance(priority.default, str) else None)
    cat_val = category if isinstance(category, str) else (category.default if hasattr(category, "default") and isinstance(category.default, str) else None)
    stat_val = rec_status if isinstance(rec_status, str) else (rec_status.default if hasattr(rec_status, "default") and isinstance(rec_status.default, str) else None)
    ctx_val = context if isinstance(context, str) else (context.default if hasattr(context, "default") and isinstance(context.default, str) else "auto")
    lim_val = limit if isinstance(limit, int) else (limit.default if hasattr(limit, "default") and isinstance(limit.default, int) else 50)

    try:
        eval_res = recommendation_engine.evaluate(
            sample_context=ctx_val or "auto",
            event_limit=lim_val or 50,
        )

        res_dict = eval_res.to_dict()
        recs = res_dict["recommendations"]

        # Apply filtering
        if prio_val and prio_val.upper() != "ALL":
            recs = [r for r in recs if r["priority"].upper() == prio_val.upper()]

        if cat_val and cat_val.upper() != "ALL":
            recs = [r for r in recs if r["category"].upper() == cat_val.upper()]

        if stat_val and stat_val.upper() != "ALL":
            recs = [r for r in recs if r["status"].upper() == stat_val.upper()]

        res_dict["recommendations"] = recs
        res_dict["recommendations_available"] = len(recs) > 0

        # Recalculate filtered summary
        filtered_summary = {
            "total": len(recs),
            "pending": sum(1 for r in recs if r["status"] == "PENDING"),
            "acknowledged": sum(1 for r in recs if r["status"] == "ACKNOWLEDGED"),
            "resolved": sum(1 for r in recs if r["status"] == "RESOLVED"),
            "critical_count": sum(1 for r in recs if r["priority"] == "CRITICAL"),
            "high_count": sum(1 for r in recs if r["priority"] == "HIGH"),
            "medium_count": sum(1 for r in recs if r["priority"] == "MEDIUM"),
            "low_count": sum(1 for r in recs if r["priority"] == "LOW"),
        }
        res_dict["summary"] = filtered_summary

        return RecommendationsResponse(**res_dict)
    except Exception as e:
        logger.error("Failed to fetch recommendations: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving recommendations: {str(e)}",
        )


@router.post(
    "/generate",
    response_model=RecommendationsResponse,
    summary="Generate Contextual Recommendations",
    description="Evaluates telemetry context and returns defensive recommendations with full evidence grounding.",
)
async def generate_recommendations(
    payload: RecommendationGenerateRequest,
) -> RecommendationsResponse:
    """Generate recommendations on demand for a given threat context."""
    try:
        eval_res = recommendation_engine.evaluate(
            sample_context=payload.sample_context or "auto",
            category_filter=payload.category_filter,
            severity_filter=payload.severity_filter,
            event_limit=payload.event_limit or 50,
        )
        return RecommendationsResponse(**eval_res.to_dict())
    except Exception as e:
        logger.error("Failed to generate recommendations: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}",
        )


@router.patch(
    "/{recommendation_id}/status",
    response_model=SecurityRecommendationSchema,
    summary="Update Recommendation Lifecycle Status (PATCH)",
    description="Updates operator status for a recommendation (e.g. ACKNOWLEDGED, RESOLVED).",
)
async def update_recommendation_status_patch(
    recommendation_id: str = FastApiPath(..., description="Unique recommendation ID (e.g. REC-20260925-0001)"),
    payload: RecommendationStatusUpdateRequest = ...,
) -> SecurityRecommendationSchema:
    """Update operator status for a specific recommendation."""
    try:
        updated = recommendation_engine.update_recommendation_status(
            recommendation_id=recommendation_id,
            new_status=payload.status,
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation with ID '{recommendation_id}' not found.",
            )
        return SecurityRecommendationSchema(**updated.to_dict())
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update recommendation status: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating recommendation status: {str(e)}",
        )


@router.post(
    "/{recommendation_id}/status",
    response_model=SecurityRecommendationSchema,
    summary="Update Recommendation Lifecycle Status (POST alias)",
    description="Alternative POST endpoint to update operator status for client compatibility.",
)
async def update_recommendation_status_post(
    recommendation_id: str = FastApiPath(..., description="Unique recommendation ID"),
    payload: RecommendationStatusUpdateRequest = ...,
) -> SecurityRecommendationSchema:
    """POST alias for updating recommendation status."""
    return await update_recommendation_status_patch(recommendation_id, payload)

