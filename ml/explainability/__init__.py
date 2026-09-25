"""HEX HIVE Phase 11: Real Explainable AI (XAI) Package.

Exposes models, formatters, and singleton attack_explainer.
"""

from ml.explainability.models import (
    FeatureContribution,
    LocalExplanationResult,
    GlobalFeatureImportance,
    GlobalExplanationResult,
)
from ml.explainability.formatter import (
    FRIENDLY_FEATURE_MAP,
    get_friendly_feature_meta,
    format_explanation_summary,
    format_technical_summary,
)
from ml.explainability.explainer import AttackExplainer, attack_explainer

__all__ = [
    "FeatureContribution",
    "LocalExplanationResult",
    "GlobalFeatureImportance",
    "GlobalExplanationResult",
    "FRIENDLY_FEATURE_MAP",
    "get_friendly_feature_meta",
    "format_explanation_summary",
    "format_technical_summary",
    "AttackExplainer",
    "attack_explainer",
]

