from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Schema for API health status check."""

    status: str = Field(default="ok", description="Service operational status")
    project: str = Field(default="HEX HIVE", description="Project name")

