from pathlib import Path
from fastapi import APIRouter
from app.schemas.system import SystemStatusResponse

router = APIRouter(prefix="/system", tags=["System Status"])
MODEL_PATH = Path(__file__).resolve().parent.parent.parent.parent / "ml" / "models" / "attack_classifier.joblib"


@router.get(
    "/status",
    response_model=SystemStatusResponse,
    summary="Get System Architectural Status",
    description="Returns status of backend, ML engine, and database.",
)
async def get_system_status() -> SystemStatusResponse:
    """Return component status of HEX HIVE system."""
    ml_status = "loaded" if MODEL_PATH.is_file() else "not_loaded"
    return SystemStatusResponse(
        status="online",
        backend="running",
        ml_model=ml_status,
        database="not_connected",
    )


