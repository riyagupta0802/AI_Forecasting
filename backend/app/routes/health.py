from fastapi import APIRouter
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health Check"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="HEX HIVE Backend Health Status",
    description="Returns operational status of the HEX HIVE backend service.",
)
async def get_health() -> HealthResponse:
    """Check health status of HEX HIVE backend."""
    return HealthResponse(
        status="ok",
        project="HEX HIVE",
    )

