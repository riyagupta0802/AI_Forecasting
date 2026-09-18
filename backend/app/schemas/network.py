from pydantic import BaseModel, Field


class NetworkSummaryResponse(BaseModel):
    """Schema for network security summary metrics.

    Disclosed as DEMO/SAMPLE backend data for the Phase 3 prototype.
    """

    network_status: str = Field(
        default="ONLINE",
        description="Demo network operational status (DEMO)",
    )
    active_connections: int = Field(
        default=1248,
        description="Simulated active TCP/UDP connections count (SAMPLE)",
    )
    detected_anomalies: int = Field(
        default=7,
        description="Simulated detected anomalous traffic clusters (DEMO)",
    )
    active_warnings: int = Field(
        default=3,
        description="Simulated active early warning advisories (SAMPLE)",
    )
    is_demo: bool = Field(
        default=True,
        description="Explicit flag indicating data is simulated prototype data",
    )

