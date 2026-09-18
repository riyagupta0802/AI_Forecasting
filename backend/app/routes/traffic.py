from fastapi import APIRouter
from app.schemas.traffic import TrafficSampleResponse, TrafficDataPoint

router = APIRouter(prefix="/traffic", tags=["Traffic Telemetry"])


@router.get(
    "/sample",
    response_model=TrafficSampleResponse,
    summary="Get Sample Network Traffic Dataset (Demo Data)",
    description="Returns sample time-series flow traffic volume points for chart visualization. Labeled as demo.",
)
async def get_traffic_sample() -> TrafficSampleResponse:
    """Return sample time-series traffic data for dashboard chart."""
    sample_points = [
        TrafficDataPoint(time="10:00", traffic=120),
        TrafficDataPoint(time="10:05", traffic=180),
        TrafficDataPoint(time="10:10", traffic=150),
        TrafficDataPoint(time="10:15", traffic=210),
        TrafficDataPoint(time="10:20", traffic=190),
        TrafficDataPoint(time="10:25", traffic=260),
        TrafficDataPoint(time="10:30", traffic=220),
        TrafficDataPoint(time="10:35", traffic=310),
        TrafficDataPoint(time="10:40", traffic=280),
        TrafficDataPoint(time="10:45", traffic=340),
        TrafficDataPoint(time="10:50", traffic=300),
        TrafficDataPoint(time="10:55", traffic=290),
    ]
    return TrafficSampleResponse(
        status="demo",
        data=sample_points,
    )

