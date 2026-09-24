"""Data models and structures for HEX HIVE Phase 10 Security Recommendation Engine.

Defines schemas for defensive security actions, evidence items, priority classifications,
and recommendation lifecycle states (PENDING, ACKNOWLEDGED, RESOLVED).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional


class RecommendationPriority(str, Enum):
    """Priority classification for defensive recommendations."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RecommendationCategory(str, Enum):
    """Functional defensive action category."""
    MONITOR = "Monitor"
    INVESTIGATE = "Investigate"
    REVIEW = "Review"
    ISOLATE = "Isolate"
    CONTAIN = "Contain"
    ESCALATE = "Escalate"
    PRESERVE = "Preserve"


class RecommendationStatus(str, Enum):
    """Lifecycle status of a recommendation."""
    PENDING = "PENDING"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


@dataclass
class SecurityRecommendation:
    """Individual defensive recommendation backed by pipeline evidence."""

    id: str
    fingerprint: str
    priority: str
    category: str
    title: str
    action: str
    reason: str
    evidence: List[str]
    source: str
    status: str
    target_asset: str
    created_at: str
    updated_at: str
    rule_id: str
    attack_stage: str
    escalation_window: Optional[str] = None
    warning_severity: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to JSON-serializable dictionary."""
        return {
            "id": self.id,
            "fingerprint": self.fingerprint,
            "priority": self.priority,
            "category": self.category,
            "title": self.title,
            "action": self.action,
            "reason": self.reason,
            "evidence": list(self.evidence),
            "source": self.source,
            "status": self.status,
            "target_asset": self.target_asset,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "rule_id": self.rule_id,
            "attack_stage": self.attack_stage,
            "escalation_window": self.escalation_window,
            "warning_severity": self.warning_severity,
        }


@dataclass
class RecommendationsSummary:
    """Statistical summary of recommendations across priority and status tiers."""

    total: int = 0
    pending: int = 0
    acknowledged: int = 0
    resolved: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert summary to dictionary."""
        return {
            "total": self.total,
            "pending": self.pending,
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "medium_count": self.medium_count,
            "low_count": self.low_count,
        }


@dataclass
class RecommendationEvaluationResult:
    """Complete evaluation result emitted by the Recommendation Engine."""

    recommendations_available: bool
    recommendations: List[SecurityRecommendation]
    summary: RecommendationsSummary
    active_threat_posture: str
    generated_at: str
    limitations: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "recommendations_available": self.recommendations_available,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "summary": self.summary.to_dict(),
            "active_threat_posture": self.active_threat_posture,
            "generated_at": self.generated_at,
            "limitations": self.limitations,
        }

