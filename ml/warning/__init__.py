"""HEX HIVE Early Warning Engine (Phase 9).

Combines Phase 5 Detection, Phase 6 Forecasting, Phase 7 Time-to-Escalation,
and Phase 8 Attack Story Correlated Events to generate evidence-backed,
actionable security alerts for SOC analysts.
"""

from ml.warning.models import EvidenceItem, EarlyWarning, WarningEvaluationResult
from ml.warning.rules import evaluate_warning_decision
from ml.warning.formatter import (
    format_warning_title,
    format_warning_message,
    format_recommended_attention,
    compile_evidence_items,
)
from ml.warning.engine import EarlyWarningEngine, early_warning_engine

__all__ = [
    "EvidenceItem",
    "EarlyWarning",
    "WarningEvaluationResult",
    "evaluate_warning_decision",
    "format_warning_title",
    "format_warning_message",
    "format_recommended_attention",
    "compile_evidence_items",
    "EarlyWarningEngine",
    "early_warning_engine",
]

