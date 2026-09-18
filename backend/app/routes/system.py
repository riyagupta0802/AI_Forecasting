from fastapi import APIRouter
from app.schemas.system import SystemStatusResponse

router = APIRouter(prefix="/system", tags=["System Status"])


@router.get(
    "/status",
    response_model=SystemStatusResponse,
    summary="Get System Architectural Status",
    description="Returns status of backend, ML engine, and database. Explicitly indicates ML and MongoDB are not loaded/connected in Phase 3.",
)
async def get_system_status() -> SystemStatusResponse:
    """Return component status of HEX HIVE system."""
    return SystemStatusResponse(
        status="online",
        backend="running",
        ml_model="not_loaded",
        database="not_connected",
    )

