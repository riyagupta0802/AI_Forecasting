from fastapi import APIRouter
from app.schemas.network import NetworkSummaryResponse

router = APIRouter(prefix="/network", tags=["Network Telemetry"])


@router.get(
    "/summary",
    response_model=NetworkSummaryResponse,
    summary="Get Network Security Summary (Demo Data)",
    description="Returns simulated network telemetry summary metrics for Phase 3 prototype.",
)
async def get_network_summary() -> NetworkSummaryResponse:
    """Return simulated network metrics (clearly labeled demo/sample data)."""
    return NetworkSummaryResponse(
        network_status="ONLINE",
        active_connections=1248,
        detected_anomalies=7,
        active_warnings=3,
        is_demo=True,
    )

