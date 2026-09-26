"""Attack Story API Routes for NETORACLE Phase 8.

Provides endpoints for:
- GET  /api/attack-story/status   (Attack story engine inventory and readiness)
- GET  /api/attack-story          (Filtered chronological attack story and timeline)
- POST /api/attack-story/generate (On-demand context-driven incident narrative generation)
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

from app.schemas.attack_story import (
    AttackStoryStatusResponse,
    AttackStoryResponse,
    AttackStoryGenerateRequest,
)
from ml.attack_story.story import attack_story_engine

logger = logging.getLogger("NETORACLE.Routes.AttackStory")
router = APIRouter(prefix="/attack-story", tags=["Attack Story"])


@router.get(
    "/status",
    response_model=AttackStoryStatusResponse,
    summary="Get Attack Story Engine Status",
    description="Returns availability, total ingested events, cluster count, and dataset limitations.",
)
async def get_attack_story_status() -> AttackStoryStatusResponse:
    """Return status and event summary for the Attack Story engine."""
    try:
        story = attack_story_engine.generate_story(event_limit=50)
        return AttackStoryStatusResponse(
            status="ready",
            story_available=True,
            events_ingested=story["event_count"],
            clusters_identified=story["cluster_count"],
            active_threat_state=story["current_state"],
            last_updated=datetime.now(timezone.utc).isoformat(),
            limitations=story["limitations"],
        )
    except Exception as e:
        logger.error("Failed to retrieve attack story status: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating attack story status: {str(e)}",
        )


@router.get(
    "",
    response_model=AttackStoryResponse,
    summary="Get Chronological Attack Story & Timeline",
    description="Returns correlated security event timeline, incident narrative, and prediction context with optional filters.",
)
async def get_attack_story(
    category: Optional[str] = Query(None, description="Filter by category ('BENIGN', 'PortScan', 'Bot', 'DDoS', 'ALL')"),
    severity: Optional[str] = Query(None, description="Filter by severity ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', 'ALL')"),
    context: Optional[str] = Query("auto", description="Threat context preset ('auto', 'benign', 'portscan', 'bot', 'ddos')"),
    limit: Optional[int] = Query(50, ge=1, le=500, description="Max individual flow events to process (1-500)"),
) -> AttackStoryResponse:
    """Retrieve filtered chronological attack story timeline and narrative."""
    # Safely unwrap parameters whether invoked via FastAPI or directly
    cat_val = category if isinstance(category, str) else (category.default if hasattr(category, "default") and isinstance(category.default, str) else None)
    sev_val = severity if isinstance(severity, str) else (severity.default if hasattr(severity, "default") and isinstance(severity.default, str) else None)
    ctx_val = context if isinstance(context, str) else (context.default if hasattr(context, "default") and isinstance(context.default, str) else "auto")
    lim_val = limit if isinstance(limit, int) else (limit.default if hasattr(limit, "default") and isinstance(limit.default, int) else 50)

    try:
        story = attack_story_engine.generate_story(
            category_filter=cat_val,
            severity_filter=sev_val,
            sample_context=ctx_val or "auto",
            event_limit=lim_val or 50,
        )
        return AttackStoryResponse(**story)
    except Exception as e:
        logger.error("Failed to generate attack story: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error compiling attack story: {str(e)}",
        )


@router.post(
    "/generate",
    response_model=AttackStoryResponse,
    summary="Generate Custom Attack Story Narrative",
    description="Generates an on-demand attack story tailored to specific category, severity, and context parameters.",
)
async def generate_attack_story(req: AttackStoryGenerateRequest) -> AttackStoryResponse:
    """Generate dynamic attack narrative and correlated timeline."""
    try:
        story = attack_story_engine.generate_story(
            category_filter=req.category_filter,
            severity_filter=req.severity_filter,
            sample_context=req.sample_context or "auto",
            event_limit=req.event_limit or 50,
        )
        return AttackStoryResponse(**story)
    except Exception as e:
        logger.error("Failed to execute on-demand story generation: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Story generation failed: {str(e)}",
        )
