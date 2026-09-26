"""Pydantic schemas for NETORACLE System Architectural and Phase Component Status."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ComponentStatus(BaseModel):
    """Status details for an individual system component or ML phase."""
    id: str
    name: str
    status: str  # "ONLINE", "READY", "NOT AVAILABLE", "PREPARED"
    is_available: bool = True
    details: str
    metric: Optional[str] = None
    phase: Optional[str] = None


class SystemStatusResponse(BaseModel):
    """Schema for overall system architectural component status.

    Provides verified live status for all phases from Phase 1 to Phase 11.
    """
    status: str = Field(default="online", description="Overall gateway status")
    backend: str = Field(default="running", description="FastAPI service status")
    ml_model: str = Field(default="loaded", description="Phase 5 attack classifier status")
    database: str = Field(default="in_memory_stub", description="Database connection mode")
    
    # Granular phase components
    components: Dict[str, ComponentStatus] = Field(
        default_factory=dict,
        description="Dictionary of verified subsystem and ML phase operational statuses"
    )
