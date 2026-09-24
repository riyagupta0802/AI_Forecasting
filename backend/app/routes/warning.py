"""Early Warning Engine API Routes for HEX HIVE Phase 9.

Provides endpoints for:
- GET  /api/warnings/status   (Warning engine readiness and active status)
- GET  /api/warnings          (Active early warnings, evidence, and session history with filters)
- POST /api/warnings/evaluate (On-demand multi-phase warning evaluation)
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

from app.schemas.warning import (
    WarningsStatusResponse,
    WarningsResponse,
    WarningEvaluateRequest,
)
from ml.warning import early_warning_engine

logger = logging.getLogger("HEX_HIVE.Routes.Warnings")
router = APIRouter(prefix="/warnings", tags=["Early Warnings"])


@router.get(
    "/status",
    response_model=WarningsStatusResponse,
    summary="Get Early Warning Engine Status",
    description="Returns warning engine availability, active alert count, and history size.",
)
async def get_warnings_status() -> WarningsStatusResponse:
    """Return status and active warning summary."""
    try:
        eval_res = early_warning_engine.evaluate(sample_context="auto")
        history = early_warning_engine.get_history()

        active_sev = None
        if eval_res.active_warning and eval_res.active_warning.severity != "INFO":
            active_sev = eval_res.active_warning.severity

        return WarningsStatusResponse(
            status="ready",
            engine_available=True,
            has_active_warning=eval_res.has_active_warning,
            active_warning_count=eval_res.warning_count,
            active_severity=active_sev,
            history_count=len(history),
            last_evaluated=eval_res.evaluated_at,
            limitations=eval_res.limitations,
        )
    except Exception as e:
        logger.error("Failed to retrieve early warning status: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating warning status: {str(e)}",
        )


@router.get(
    "",
    response_model=WarningsResponse,
    summary="Get Active Early Warnings & History",
    description="Returns current active early warnings, multi-source evidence, and session history with optional filtering.",
)
async def get_warnings(
    severity: Optional[str] = Query(None, description="Filter by severity ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO', 'ALL')"),
    warning_type: Optional[str] = Query(None, description="Filter by warning type ('VOLUMETRIC_DISRUPTION', 'MALICIOUS_STAGING', 'SUSPICIOUS_RECONNAISSANCE', etc.)"),
    warning_status: Optional[str] = Query(None, alias="status", description="Filter by status ('NEW', 'ACTIVE', 'RESOLVED', 'ALL')"),
    context: Optional[str] = Query("auto", description="Threat context preset ('auto', 'benign', 'portscan', 'bot', 'ddos')"),
    limit: Optional[int] = Query(50, ge=1, le=500, description="Max telemetry flow events to evaluate"),
) -> WarningsResponse:
    """Evaluate and return early warnings with optional filters."""
    # Safely unwrap parameters whether invoked via FastAPI or directly in Python
    sev_val = severity if isinstance(severity, str) else (severity.default if hasattr(severity, "default") and isinstance(severity.default, str) else None)
    type_val = warning_type if isinstance(warning_type, str) else (warning_type.default if hasattr(warning_type, "default") and isinstance(warning_type.default, str) else None)
    stat_val = warning_status if isinstance(warning_status, str) else (warning_status.default if hasattr(warning_status, "default") and isinstance(warning_status.default, str) else None)
    ctx_val = context if isinstance(context, str) else (context.default if hasattr(context, "default") and isinstance(context.default, str) else "auto")
    lim_val = limit if isinstance(limit, int) else (limit.default if hasattr(limit, "default") and isinstance(limit.default, int) else 50)

    try:
        eval_res = early_warning_engine.evaluate(
            sample_context=ctx_val or "auto",
            severity_filter=sev_val if sev_val and sev_val.upper() != "ALL" else None,
            event_limit=lim_val or 50,
        )

        res_dict = eval_res.to_dict()

        # Apply post-evaluation filters on warnings and history lists if requested
        if sev_val and sev_val.upper() != "ALL":
            res_dict["warnings"] = [w for w in res_dict["warnings"] if w["severity"].upper() == sev_val.upper()]
            res_dict["session_history"] = [w for w in res_dict["session_history"] if w["severity"].upper() == sev_val.upper()]
            if res_dict["active_warning"] and res_dict["active_warning"]["severity"].upper() != sev_val.upper():
                res_dict["active_warning"] = None
                res_dict["has_active_warning"] = False

        if type_val and type_val.upper() != "ALL":
            res_dict["warnings"] = [w for w in res_dict["warnings"] if w["warning_type"].upper() == type_val.upper()]
            res_dict["session_history"] = [w for w in res_dict["session_history"] if w["warning_type"].upper() == type_val.upper()]

        if stat_val and stat_val.upper() != "ALL":
            res_dict["warnings"] = [w for w in res_dict["warnings"] if w["status"].upper() == stat_val.upper()]
            res_dict["session_history"] = [w for w in res_dict["session_history"] if w["status"].upper() == stat_val.upper()]

        res_dict["warning_count"] = len(res_dict["warnings"])

        return WarningsResponse(**res_dict)
    except Exception as e:
        logger.error("Failed to retrieve early warnings: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error compiling early warnings: {str(e)}",
        )


@router.post(
    "/evaluate",
    response_model=WarningsResponse,
    summary="Evaluate Threat Context for Early Warnings",
    description="Evaluates pipeline telemetry for a given scenario context or filtered event stream.",
)
async def evaluate_warnings(req: WarningEvaluateRequest) -> WarningsResponse:
    """Evaluate pipeline telemetry and return updated warnings."""
    try:
        eval_res = early_warning_engine.evaluate(
            sample_context=req.sample_context or "auto",
            category_filter=req.category_filter,
            severity_filter=req.severity_filter,
            event_limit=req.event_limit or 50,
        )
        return WarningsResponse(**eval_res.to_dict())
    except Exception as e:
        logger.error("Failed to execute on-demand warning evaluation: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Warning evaluation failed: {str(e)}",
        )

