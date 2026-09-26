"""Pydantic Schemas for NETORACLE Phase 8 Attack Story.

Defines schemas for normalized security events, correlated campaign clusters,
chronological timeline nodes, structured narratives, and story generation requests.
"""

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class EventDetailSchema(BaseModel):
    """Schema for an individual normalized network flow event."""

    event_id: str
    sequence_index: int
    destination_port: int
    service_name: str
    protocol: str
    duration_ms: float
    packet_count: int
    byte_count: int
    flow_packets_sec: float
    flow_bytes_sec: float
    syn_flag_count: int
    ack_flag_count: int
    attack_category: str
    severity: str
    relative_time_s: float
    description: str


class ClusterDetailSchema(BaseModel):
    """Schema for a correlated cluster of related security events."""

    cluster_id: str
    attack_stage: str
    severity: str
    target_services: List[str]
    target_ports: List[int]
    event_count: int
    start_time_s: float
    end_time_s: float
    duration_s: float
    total_packets: int
    total_bytes: int
    correlation_rationale: str
    sample_events: List[Dict[str, Any]]


class TimelineNodeSchema(BaseModel):
    """Schema for a milestone entry on the chronological attack timeline."""

    node_id: str
    sequence_order: int
    timestamp_label: str
    title: str
    stage: str
    severity: str
    event_type: str
    description: str
    target_ports: List[int]
    is_current: bool
    is_forecast: bool
    details: Dict[str, Any]


class NarrativeSchema(BaseModel):
    """Structured answers to the 5 core SOC security incident questions."""

    what_happened: str = Field(description="Initial attack or baseline detection")
    what_happened_next: str = Field(description="Subsequent correlated events and progression")
    what_is_happening_now: str = Field(description="Current detected threat posture")
    what_may_happen_next: str = Field(description="Phase 6 forecast projection")
    how_is_threat_escalating: str = Field(description="Phase 7 time-to-escalation estimate")


class AttackStoryStatusResponse(BaseModel):
    """Schema for GET /api/attack-story/status endpoint."""

    status: str = Field(default="ready", description="Attack story engine status: ready, unavailable, or error")
    story_available: bool = Field(default=True)
    events_ingested: int = Field(description="Total normalized events available in dataset")
    clusters_identified: int = Field(description="Total correlated attack clusters")
    active_threat_state: str = Field(description="Current active posture")
    last_updated: str = Field(description="ISO 8601 timestamp")
    limitations: str = Field(description="Documented temporal data scope and limitations")


class AttackStoryResponse(BaseModel):
    """Schema for GET /api/attack-story and POST /api/attack-story/generate."""

    story_available: bool
    story_id: str
    generated_at: str
    current_state: str
    overall_severity: str
    event_count: int
    cluster_count: int
    timeline_node_count: int
    narrative: NarrativeSchema
    timeline: List[TimelineNodeSchema]
    clusters: List[ClusterDetailSchema]
    events_sample: List[EventDetailSchema]
    forecast: Dict[str, Any]
    escalation: Dict[str, Any]
    limitations: str


class AttackStoryGenerateRequest(BaseModel):
    """Schema for POST /api/attack-story/generate request."""

    category_filter: Optional[str] = Field(
        default=None,
        description="Filter events by category: 'ALL', 'BENIGN', 'PortScan', 'Bot', 'DDoS'",
    )
    severity_filter: Optional[str] = Field(
        default=None,
        description="Filter events by severity: 'ALL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'",
    )
    sample_context: Optional[str] = Field(
        default="auto",
        description="Threat context preset: 'auto', 'benign', 'portscan', 'bot', 'ddos'",
    )
    event_limit: Optional[int] = Field(
        default=50,
        description="Maximum number of individual events to ingest (default: 50, max: 500)",
    )

