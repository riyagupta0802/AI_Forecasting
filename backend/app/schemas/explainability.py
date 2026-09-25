"""Pydantic schemas for HEX HIVE Phase 11: Real Explainable AI (XAI).

Defines API request/response contracts for local and global SHAP explanations,
feature contributions, mathematical margin scores, and human-readable summaries.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field


class FeatureContributionSchema(BaseModel):
    """Schema for individual feature contribution to a prediction."""

    name: str = Field(description="Technical feature column name from CICIDS2017")
    friendly_name: str = Field(description="Human-readable network telemetry description")
    value: float = Field(description="Raw observed input value for this flow")
    shap_value: float = Field(description="Calculated SHAP Shapley contribution score")
    abs_shap: float = Field(description="Absolute impact magnitude (|SHAP|)")
    direction: str = Field(description="'toward_prediction' or 'away_from_prediction'")
    rank: int = Field(description="Rank by absolute SHAP contribution (1 is highest impact)")
    description: str = Field(description="Contextual security description of the metric")


class LocalExplanationResponse(BaseModel):
    """Schema for POST /api/explainability/explain response."""

    available: bool = Field(default=True, description="Whether SHAP explanation was computed successfully")
    prediction: str = Field(description="Model prediction label: 'ATTACK' or 'BENIGN'")
    confidence: float = Field(description="Model prediction confidence percentage (0.0 - 100.0)")
    base_value: float = Field(description="Model base expected value E[f(x)] across training distribution")
    predicted_value: float = Field(description="Final model margin score (base_value + sum(shap_values))")
    features: List[FeatureContributionSchema] = Field(description="Top N influential features ranked by impact")
    summary: str = Field(description="Careful, human-readable non-causal explanation")
    technical_summary: str = Field(description="Mathematical SHAP decomposition summary")
    method: str = Field(default="SHAP (TreeExplainer)", description="Explanation algorithm")
    model: str = Field(default="RandomForestClassifier", description="Underlying ML model explained")
    features_evaluated: int = Field(default=78, description="Total continuous features evaluated")
    timestamp: Optional[str] = Field(default=None, description="ISO 8601 evaluation timestamp")
    limitations: Optional[str] = Field(default=None, description="Documented XAI limitations")


class GlobalFeatureItemSchema(BaseModel):
    """Schema for a feature in global SHAP importance rankings."""

    name: str = Field(description="Technical feature column name")
    friendly_name: str = Field(description="Human-readable feature name")
    mean_abs_shap: float = Field(description="Mean absolute SHAP value across evaluation dataset")
    rank: int = Field(description="Global importance rank (1 = highest influence)")
    description: str = Field(description="Contextual description of the feature")


class GlobalExplanationResponse(BaseModel):
    """Schema for GET /api/explainability/global response."""

    available: bool = Field(default=True, description="Whether global SHAP metrics are available")
    method: str = Field(default="Mean Absolute SHAP (TreeExplainer)", description="Methodology")
    model: str = Field(default="RandomForestClassifier", description="Model architecture")
    dataset_source: str = Field(description="Evaluation dataset source (e.g. CICIDS2017)")
    samples_evaluated: int = Field(description="Number of evaluation flow records analyzed")
    top_features: List[GlobalFeatureItemSchema] = Field(description="Ranked global feature importance")
    generated_at: str = Field(description="Generation timestamp")
    limitations: str = Field(description="Disclosed scientific limitations")


class ExplainabilityStatusResponse(BaseModel):
    """Schema for GET /api/explainability/status response."""

    status: str = Field(default="ready", description="XAI engine readiness status")
    explainer_ready: bool = Field(default=True, description="Whether TreeExplainer is initialized")
    model_type: str = Field(default="RandomForestClassifier", description="Model architecture explained")
    method: str = Field(default="SHAP (TreeExplainer)", description="Explanation algorithm")
    features_count: int = Field(default=78, description="Number of feature dimensions")
    global_importance_ready: bool = Field(default=True, description="Whether global importance is precomputed")
    limitations: str = Field(description="Documented scientific scope and limitations")


class ExplainRequest(BaseModel):
    """Schema for POST /api/explainability/explain request."""

    sample_type: Optional[str] = Field(
        default="auto",
        description="Benchmark representative sample: 'auto', 'benign', 'attack'",
    )
    features: Optional[Union[Dict[str, float], List[float]]] = Field(
        default=None,
        description="Optional custom feature dictionary or array of 78 continuous numerical features",
    )
    top_n: Optional[int] = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of top contributing features to return (default: 5, max: 20)",
    )

