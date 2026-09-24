"""Pydantic schemas for HEX HIVE Phase 10 Security Recommendation Engine.

Defines API request/response contracts for defensive recommendations, statistical summaries,
and operator status updates (PENDING, ACKNOWLEDGED, RESOLVED).
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SecurityRecommendationSchema(BaseModel):
    """Schema for individual defensive security recommendation."""

    id: str = Field(description="Unique recommendation identifier (e.g. REC-20260925-0001)")
    fingerprint: str = Field(description="Deduplication fingerprint hash")
    priority: str = Field(description="Priority level: CRITICAL, HIGH, MEDIUM, LOW")
    category: str = Field(description="Defensive action category: Monitor, Investigate, Review, Isolate, Contain, Escalate, Preserve")
    title: str = Field(description="Recommendation headline")
    action: str = Field(description="Defensive, advisory recommended action")
    reason: str = Field(description="Grounded explanation based on empirical findings")
    evidence: List[str] = Field(description="Supporting evidence traces from Phases 5-9")
    source: str = Field(description="Defensive decision rule identifier")
    status: str = Field(description="Lifecycle status: PENDING, ACKNOWLEDGED, RESOLVED")
    target_asset: str = Field(description="Affected or targeted infrastructure asset")
    created_at: str = Field(description="ISO 8601 creation timestamp")
    updated_at: str = Field(description="ISO 8601 last update timestamp")
    rule_id: str = Field(description="Internal rule identifier")
    attack_stage: str = Field(description="Associated attack stage")
    escalation_window: Optional[str] = Field(default=None, description="Escalation countdown if applicable")
    warning_severity: Optional[str] = Field(default=None, description="Active warning severity tier")


class RecommendationsSummarySchema(BaseModel):
    """Schema for statistical breakdown of recommendations."""

    total: int = Field(default=0, description="Total active recommendations")
    pending: int = Field(default=0, description="Recommendations awaiting operator review")
    acknowledged: int = Field(default=0, description="Recommendations acknowledged by operator")
    resolved: int = Field(default=0, description="Recommendations marked resolved")
    critical_count: int = Field(default=0, description="Critical priority recommendations")
    high_count: int = Field(default=0, description="High priority recommendations")
    medium_count: int = Field(default=0, description="Medium priority recommendations")
    low_count: int = Field(default=0, description="Low priority recommendations")


class RecommendationsStatusResponse(BaseModel):
    """Schema for GET /api/recommendations/status endpoint."""

    status: str = Field(default="ready", description="Engine status")
    engine_available: bool = Field(default=True, description="Availability flag")
    recommendations_available: bool = Field(description="Whether recommendations are available")
    active_threat_posture: str = Field(description="Current system threat level")
    total_recommendations: int = Field(description="Total count in current evaluation")
    pending_count: int = Field(description="Count of pending actions")
    summary: RecommendationsSummarySchema = Field(description="Statistical breakdown")
    last_evaluated: str = Field(description="ISO 8601 timestamp")
    limitations: str = Field(description="Scope and data grounding limitations")


class RecommendationsResponse(BaseModel):
    """Schema for GET /api/recommendations and POST /api/recommendations/generate endpoints."""

    recommendations_available: bool = Field(description="Whether recommendations are available")
    recommendations: List[SecurityRecommendationSchema] = Field(default_factory=list)
    summary: RecommendationsSummarySchema = Field(description="Statistical breakdown")
    active_threat_posture: str = Field(description="Current system threat level")
    generated_at: str = Field(description="ISO 8601 timestamp")
    limitations: str = Field(description="Scope and data grounding limitations")


class RecommendationGenerateRequest(BaseModel):
    """Schema for POST /api/recommendations/generate request."""

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


class RecommendationStatusUpdateRequest(BaseModel):
    """Schema for updating operator lifecycle status (e.g. ACKNOWLEDGED, RESOLVED)."""

    status: str = Field(
        description="Target lifecycle state: 'PENDING', 'ACKNOWLEDGED', 'RESOLVED'"
    )

