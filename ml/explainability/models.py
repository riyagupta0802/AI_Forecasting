"""Data models for HEX HIVE Phase 11: Real Explainable AI (XAI).

Defines structured schemas for local and global SHAP feature contributions,
mathematical base values, directionality, and human-readable summaries.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class FeatureContribution:
    """Individual feature contribution to a model prediction via SHAP."""

    name: str
    friendly_name: str
    value: float
    shap_value: float
    abs_shap: float
    direction: str  # 'toward_prediction' or 'away_from_prediction'
    rank: int
    description: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert contribution to dictionary."""
        return {
            "name": self.name,
            "friendly_name": self.friendly_name,
            "value": round(float(self.value), 4),
            "shap_value": round(float(self.shap_value), 5),
            "abs_shap": round(float(self.abs_shap), 5),
            "direction": self.direction,
            "rank": self.rank,
            "description": self.description,
        }


@dataclass
class LocalExplanationResult:
    """Complete local explanation result for an individual network traffic sample."""

    available: bool
    prediction: str
    confidence: float
    base_value: float
    predicted_value: float
    features: List[FeatureContribution]
    summary: str
    technical_summary: str
    method: str = "SHAP (TreeExplainer)"
    model: str = "RandomForestClassifier"
    features_evaluated: int = 78
    timestamp: Optional[str] = None
    limitations: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert local explanation to dictionary."""
        return {
            "available": self.available,
            "prediction": self.prediction,
            "confidence": round(float(self.confidence), 2),
            "base_value": round(float(self.base_value), 5),
            "predicted_value": round(float(self.predicted_value), 5),
            "features": [f.to_dict() for f in self.features],
            "summary": self.summary,
            "technical_summary": self.technical_summary,
            "method": self.method,
            "model": self.model,
            "features_evaluated": self.features_evaluated,
            "timestamp": self.timestamp,
            "limitations": self.limitations,
        }


@dataclass
class GlobalFeatureImportance:
    """Global feature importance derived from aggregate SHAP values across evaluation data."""

    name: str
    friendly_name: str
    mean_abs_shap: float
    rank: int
    description: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert global feature importance to dictionary."""
        return {
            "name": self.name,
            "friendly_name": self.friendly_name,
            "mean_abs_shap": round(float(self.mean_abs_shap), 5),
            "rank": self.rank,
            "description": self.description,
        }


@dataclass
class GlobalExplanationResult:
    """Global model explanation reflecting overall feature importance."""

    available: bool
    method: str
    model: str
    dataset_source: str
    samples_evaluated: int
    top_features: List[GlobalFeatureImportance]
    generated_at: str
    limitations: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert global explanation to dictionary."""
        return {
            "available": self.available,
            "method": self.method,
            "model": self.model,
            "dataset_source": self.dataset_source,
            "samples_evaluated": self.samples_evaluated,
            "top_features": [f.to_dict() for f in self.top_features],
            "generated_at": self.generated_at,
            "limitations": self.limitations,
        }

