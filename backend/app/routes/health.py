from fastapi import APIRouter
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health Check"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="NETORACLE Backend Health Status",
    description="Returns operational status of the NETORACLE backend service.",
)
async def get_health() -> HealthResponse:
    """Check health status of NETORACLE backend."""
    return HealthResponse(
        status="ok",
        project="NETORACLE",
    )

