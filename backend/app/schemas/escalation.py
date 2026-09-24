"""Pydantic Schemas for HEX HIVE Phase 7 Time-to-Escalation.

Defines request and response interfaces for escalation window estimation,
evaluation metrics, risk thresholds, and live multi-phase prediction.
"""

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class EscalationStatusResponse(BaseModel):
    """Schema for GET /api/escalation/status endpoint."""

    status: str = Field(default="ready", description="Escalation engine status: ready, unavailable, or error")
    available: bool = Field(default=True, description="Whether escalation estimation is available")
    current_state: str = Field(description="Current identified threat state: BENIGN, PortScan, Bot, DDoS")
    predicted_state: str = Field(description="Projected next attack stage from Phase 6")
    escalation_condition: str = Field(description="Specific condition defining escalation")
    is_escalating: bool = Field(description="Whether threat is actively escalating to a higher severity stage")
    estimated_time_seconds: Optional[int] = Field(default=None, description="Estimated time until escalation in seconds")
    estimated_time_minutes: Optional[float] = Field(default=None, description="Estimated time until escalation in minutes")
    formatted_time: str = Field(description="Human readable formatted escalation window or status tag")
    risk_level: str = Field(description="Threat risk classification: LOW, MODERATE, HIGH, CRITICAL")
    confidence: float = Field(description="Confidence percentage score (0-100)")
    velocity_index: float = Field(description="Normalized telemetry velocity factor")
    method: str = Field(description="Estimation algorithm/method name")
    timestamp: str = Field(description="ISO 8601 calculation timestamp")
    explanation: str = Field(description="Technically grounded explanation of escalation estimation")
    limitations: str = Field(description="Documented temporal data scope and limitations")


class EscalationMetricsResponse(BaseModel):
    """Schema for GET /api/escalation/metrics endpoint."""

    model_type: str = Field(description="Architecture name")
    task: str = Field(description="Machine learning task description")
    random_state: int = Field(default=42)
    n_estimators: int = Field(default=100)
    max_depth: int = Field(default=8)
    train_samples: int = Field(description="Training set sample count")
    test_samples: int = Field(description="Held-out test set sample count")
    target_unit: str = Field(default="seconds")
    mean_absolute_error: float = Field(description="Held-out test Mean Absolute Error in seconds")
    root_mean_squared_error: float = Field(description="Held-out test RMSE in seconds")
    r2_score: float = Field(description="Held-out test R-squared coefficient")
    top_features: List[Dict[str, Any]] = Field(description="Ranked top temporal/velocity features")
    risk_thresholds: Dict[str, str] = Field(description="Configured window thresholds for risk classification")
    limitations: str = Field(description="Documented scientific limitations of current dataset/baseline")


class EscalationPredictRequest(BaseModel):
    """Schema for POST /api/escalation/predict request."""

    sample_type: Optional[str] = Field(
        default="auto",
        description="Benchmark sample preset: 'benign', 'portscan', 'bot', 'ddos', or 'auto'",
    )
    features: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional dictionary mapping feature column names to float values",
    )
    feature_vector: Optional[List[float]] = Field(
        default=None,
        description="Optional ordered float array of 78 continuous flow features",
    )


class EscalationPredictResponse(BaseModel):
    """Schema for POST /api/escalation/predict response."""

    available: bool
    current_state: str
    predicted_state: str
    escalation_condition: str
    is_escalating: bool
    estimated_time_seconds: Optional[int] = None
    estimated_time_minutes: Optional[float] = None
    formatted_time: str
    risk_level: str
    confidence: float
    velocity_index: float
    method: str
    timestamp: str
    explanation: str
    limitations: str
    latency_ms: float
    sample_type: Optional[str] = None
    detection_stage: Dict[str, Any]
    forecast_context: Dict[str, Any]

