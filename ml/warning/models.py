"""Data models and schemas for HEX HIVE Phase 9 Early Warning Engine.

Defines dataclasses for individual evidence items, structured early warnings,
and evaluation results combining outputs from Phases 5 through 8.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


@dataclass
class EvidenceItem:
    """An individual piece of verifiable security evidence supporting a warning."""

    evidence_type: str  # 'detection', 'forecast', 'escalation', 'correlation'
    headline: str
    description: str
    source: str  # Component generating the evidence
    confidence: Optional[float] = None
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EarlyWarning:
    """A structured, evidence-backed security early warning alert."""

    warning_id: str
    fingerprint: str  # Hash for deduplication
    warning_type: str  # 'VOLUMETRIC_DISRUPTION', 'MALICIOUS_STAGING', 'SUSPICIOUS_RECONNAISSANCE', etc.
    severity: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'
    status: str  # 'NEW', 'ACTIVE', 'RESOLVED'
    title: str
    message: str
    timestamp: str
    current_state: str  # 'BENIGN', 'PortScan', 'Bot', 'DDoS'
    predicted_state: str  # Projected next stage
    escalation_window: str  # e.g. "475s (~7.9m)" or "0s (Active Impact)"
    escalation_seconds: Optional[int]
    confidence: float  # Composite or primary model confidence (0.0 to 1.0)
    target_ports: List[int]
    evidence: List[EvidenceItem]
    recommended_attention: str
    limitations: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["evidence"] = [e.to_dict() if isinstance(e, EvidenceItem) else e for e in self.evidence]
        return data


@dataclass
class WarningEvaluationResult:
    """Aggregated result of an Early Warning Engine evaluation cycle."""

    has_active_warning: bool
    active_warning: Optional[EarlyWarning]
    warning_count: int
    warnings: List[EarlyWarning]
    session_history: List[EarlyWarning]
    overall_risk_level: str
    evaluated_at: str
    limitations: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_active_warning": self.has_active_warning,
            "active_warning": self.active_warning.to_dict() if self.active_warning else None,
            "warning_count": self.warning_count,
            "warnings": [w.to_dict() for w in self.warnings],
            "session_history": [w.to_dict() for w in self.session_history],
            "overall_risk_level": self.overall_risk_level,
            "evaluated_at": self.evaluated_at,
            "limitations": self.limitations,
        }

