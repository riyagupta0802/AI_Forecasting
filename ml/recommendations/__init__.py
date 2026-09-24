"""HEX HIVE Phase 10: Real Security Recommendation Engine.

Exposes models, rules, formatters, and the singleton recommendation_engine.
"""

from ml.recommendations.models import (
    SecurityRecommendation,
    RecommendationsSummary,
    RecommendationEvaluationResult,
    RecommendationPriority,
    RecommendationCategory,
    RecommendationStatus,
)
from ml.recommendations.rules import evaluate_recommendation_rules
from ml.recommendations.formatter import compile_recommendation_evidence
from ml.recommendations.engine import RecommendationEngine, recommendation_engine

__all__ = [
    "SecurityRecommendation",
    "RecommendationsSummary",
    "RecommendationEvaluationResult",
    "RecommendationPriority",
    "RecommendationCategory",
    "RecommendationStatus",
    "evaluate_recommendation_rules",
    "compile_recommendation_evidence",
    "RecommendationEngine",
    "recommendation_engine",
]

