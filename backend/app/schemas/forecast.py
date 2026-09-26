"""Pydantic Schemas for NETORACLE Phase 6 Attack Forecasting.

Preserves the existing Phase 3/5 ForecastStatusResponse contract while extending it
with real machine learning progression states, metrics, and inference interfaces.
"""

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class TrajectoryNode(BaseModel):
    """Schema for a single stage in the attack progression trajectory."""

    stage: str = Field(description="Stage name, e.g. BENIGN, PortScan, Bot, DDoS")
    display_name: str = Field(description="Human readable stage description")
    status: str = Field(description="Lifecycle status: active, forecasted, completed, projected")
    probability: str = Field(description="Probability or state tag string")
    is_current: bool = Field(default=False, description="Whether this is the current active stage")
    is_projected: bool = Field(default=False, description="Whether this is the forecasted next stage")


class ForecastStatusResponse(BaseModel):
    """Extended schema for attack forecast status.

    Preserves backward compatibility with existing Phase 3 frontend consumers
    while reporting real machine-learning stage forecasting and empirical transitions.
    """

    # Existing Phase 3 fields preserved
    status: str = Field(
        default="active",
        description="Forecasting pipeline state (active, awaiting_model, unavailable)",
    )
    current_pattern: str = Field(
        default="BENIGN",
        description="Current observed network pattern classification",
    )
    possible_next_stage: str = Field(
        default="BENIGN",
        description="Predicted next attack transition stage",
    )
    confidence: Optional[float] = Field(
        default=88.0,
        description="Model confidence score percentage (0-100)",
    )
    time_to_escalation: Optional[int] = Field(
        default=None,
        description="Estimated seconds to escalation (null until escalation regression is implemented)",
    )

    # Phase 6 Extended Real ML Fields
    forecast_available: bool = Field(
        default=True,
        description="Whether a valid real forecast model is loaded and generating predictions",
    )
    current_state: Optional[str] = Field(
        default="BENIGN",
        description="Identified current attack state",
    )
    current_state_desc: Optional[str] = Field(
        default="Normal Baseline Traffic",
        description="Lifecycle description of current state",
    )
    predicted_next_stage: Optional[str] = Field(
        default="BENIGN",
        description="Machine learning projected next stage",
    )
    predicted_next_stage_display: Optional[str] = Field(
        default="BENIGN (Normal Baseline)",
        description="Display label of projected next stage",
    )
    risk_level: Optional[str] = Field(
        default="LOW",
        description="Calculated threat risk level: LOW, MEDIUM, HIGH, CRITICAL",
    )
    model: Optional[str] = Field(
        default="Multi-Class StageClassifier + Empirical Transition Dynamics",
        description="Underlying forecasting model descriptor",
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="ISO 8601 timestamp of forecast generation",
    )
    explanation: Optional[str] = Field(
        default=None,
        description="Technically grounded explanation of transition probability",
    )
    transition_probabilities: Optional[Dict[str, float]] = Field(
        default=None,
        description="Full transition probability distribution across possible next states",
    )
    trajectory: Optional[List[TrajectoryNode]] = Field(
        default=None,
        description="Full progression lifecycle nodes for timeline visualization",
    )
    limitations: Optional[str] = Field(
        default=None,
        description="Documented scientific limitations of current dataset/baseline",
    )


class PerClassMetric(BaseModel):
    """Evaluation metrics for an individual attack stage."""

    class_code: int
    precision: float
    recall: float
    f1_score: float
    support: int


class ForecastMetricsResponse(BaseModel):
    """Schema for Phase 6 forecasting evaluation metrics."""

    model_type: str = Field(description="Architecture name")
    task: str = Field(description="Machine learning task description")
    random_state: int = Field(default=42)
    n_estimators: int = Field(default=100)
    max_depth: int = Field(default=12)
    train_samples: int = Field(description="Training set sample count")
    test_samples: int = Field(description="Held-out test set sample count")
    classes: List[str] = Field(description="Target classes evaluated")
    class_mapping: Dict[str, str] = Field(description="Integer code to class name mapping")
    accuracy: float = Field(description="Test set accuracy (0.0 to 1.0)")
    precision_macro: float = Field(description="Macro-averaged precision")
    recall_macro: float = Field(description="Macro-averaged recall")
    f1_score_macro: float = Field(description="Macro-averaged F1 score")
    precision_weighted: float = Field(description="Weighted precision")
    recall_weighted: float = Field(description="Weighted recall")
    f1_score_weighted: float = Field(description="Weighted F1 score")
    confusion_matrix: List[List[int]] = Field(description="4x4 Confusion matrix")
    per_class_metrics: Dict[str, PerClassMetric] = Field(description="Detailed per-class metrics")
    top_features: List[Dict[str, Any]] = Field(description="Ranked top predictive features")
    limitations: str = Field(description="Documented dataset and model scope limitations")


class ForecastPredictRequest(BaseModel):
    """Request schema for live attack forecast inference."""

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


class DetectionStageDetail(BaseModel):
    """Telemetry context from Phase 5 detection."""

    is_attack: bool
    detection_confidence: float
    identified_stage: str
    stage_probabilities: Dict[str, float]


class ForecastPredictResponse(BaseModel):
    """Response schema for live attack forecast inference."""

    forecast_available: bool
    current_state: str
    current_state_desc: str
    predicted_next_stage: str
    predicted_next_stage_display: str
    confidence: float
    risk_level: str
    timestamp: str
    model: str
    explanation: str
    transition_probabilities: Dict[str, float]
    trajectory: List[TrajectoryNode]
    detection_stage: DetectionStageDetail
    latency_ms: float
    sample_type: Optional[str] = None
    limitations: Optional[str] = None
