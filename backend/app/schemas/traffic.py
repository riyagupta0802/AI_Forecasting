from typing import List
from pydantic import BaseModel, Field


class TrafficDataPoint(BaseModel):
    """Single time-slice traffic measurement data point."""

    time: str = Field(description="Timestamp in HH:MM format")
    traffic: int = Field(description="Flow throughput or packet rate metric")


class TrafficSampleResponse(BaseModel):
    """Sample network-traffic dataset suitable for displaying the dashboard chart."""

    status: str = Field(
        default="demo",
        description="Dataset status indicator (DEMO/SAMPLE)",
    )
    data: List[TrafficDataPoint] = Field(
        description="Array of sample telemetry flow data points",
    )

