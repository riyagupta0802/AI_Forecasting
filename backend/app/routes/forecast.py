from fastapi import APIRouter
from app.schemas.forecast import ForecastStatusResponse

router = APIRouter(prefix="/forecast", tags=["Attack Forecasting"])


@router.get(
    "/status",
    response_model=ForecastStatusResponse,
    summary="Get Attack Forecast Status",
    description="Returns placeholder forecast status awaiting ML integration. Does not generate fake AI predictions.",
)
async def get_forecast_status() -> ForecastStatusResponse:
    """Return forecast status placeholder awaiting Phase 4 ML models."""
    return ForecastStatusResponse(
        status="awaiting_model",
        current_pattern="Awaiting ML model",
        possible_next_stage="Awaiting ML model",
        confidence=None,
        time_to_escalation=None,
    )

