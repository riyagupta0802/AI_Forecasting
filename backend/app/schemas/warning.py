"""Pydantic schemas for HEX HIVE Phase 9 Early Warning Engine.

Defines API request/response contracts for warning evaluation, active alerts,
evidence breakdowns, and history logs.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EvidenceItemSchema(BaseModel):
    """Schema for individual verified security evidence item."""

    evidence_type: str = Field(description="Evidence category: detection, forecast, escalation, correlation")
    headline: str = Field(description="Concise evidence summary")
    description: str = Field(description="Detailed explanation of empirical evidence")
    source: str = Field(description="Pipeline model or component providing the evidence")
    confidence: Optional[float] = Field(default=None, description="Calibrated confidence score if applicable")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Numerical metrics supporting the evidence")


class EarlyWarningSchema(BaseModel):
    """Schema for a structured early warning alert."""

    warning_id: str = Field(description="Unique alert identifier")
    fingerprint: str = Field(description="Deduplication fingerprint hash")
    warning_type: str = Field(description="Classified warning category")
    severity: str = Field(description="Severity classification: CRITICAL, HIGH, MEDIUM, LOW, INFO")
    status: str = Field(description="Warning lifecycle state: NEW, ACTIVE, RESOLVED")
    title: str = Field(description="Incident title")
    message: str = Field(description="Incident explanation and threat description")
    timestamp: str = Field(description="ISO 8601 alert generation timestamp")
    current_state: str = Field(description="Observed active threat state")
    predicted_state: str = Field(description="Projected next attack stage from Phase 6")
    escalation_window: str = Field(description="Estimated escalation window from Phase 7")
    escalation_seconds: Optional[int] = Field(default=None, description="Escalation countdown in seconds")
    confidence: float = Field(description="Primary model confidence score (0.0 to 1.0)")
    target_ports: List[int] = Field(description="Identified target service ports")
    evidence: List[EvidenceItemSchema] = Field(description="Verifiable evidence items")
    recommended_attention: str = Field(description="SOC analyst triage advice")
    limitations: str = Field(description="Documented scientific limitations")


class WarningsStatusResponse(BaseModel):
    """Schema for GET /api/warnings/status endpoint."""

    status: str = Field(default="ready", description="Early warning engine status")
    engine_available: bool = Field(default=True)
    has_active_warning: bool = Field(description="Whether active warnings requiring triage exist")
    active_warning_count: int = Field(description="Total active elevated warnings")
    active_severity: Optional[str] = Field(default=None, description="Highest active severity level")
    history_count: int = Field(description="Total logged alerts in session buffer")
    last_evaluated: str = Field(description="ISO 8601 timestamp")
    limitations: str = Field(description="Scope and data grounding limitations")


class WarningsResponse(BaseModel):
    """Schema for GET /api/warnings and POST /api/warnings/evaluate."""

    has_active_warning: bool
    active_warning: Optional[EarlyWarningSchema] = None
    warning_count: int
    warnings: List[EarlyWarningSchema] = Field(default_factory=list)
    session_history: List[EarlyWarningSchema] = Field(default_factory=list)
    overall_risk_level: str
    evaluated_at: str
    limitations: str


class WarningEvaluateRequest(BaseModel):
    """Schema for POST /api/warnings/evaluate request."""

    sample_context: Optional[str] = Field(
        default="auto",
        description="Threat context preset: 'auto', 'benign', 'portscan', 'bot', 'ddos'",
    )
    category_filter: Optional[str] = Field(
        default=None,
        description="Optional filter by attack category",
    )
    severity_filter: Optional[str] = Field(
        default=None,
        description="Optional filter by severity",
    )
    event_limit: Optional[int] = Field(
        default=50,
        ge=1,
        le=500,
        description="Max telemetry flow events to ingest",
    )

