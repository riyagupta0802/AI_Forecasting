"""Pydantic schemas for Machine Learning endpoints in HEX HIVE Phase 5."""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class MLStatusResponse(BaseModel):
    """Schema for GET /api/ml/status."""
    status: str = Field("ready", description="ML subsystem health and readiness")
    model_loaded: bool = Field(True, description="Whether the classifier is in-memory")
    model_type: str = Field("Random Forest", description="Classifier algorithm")
    task: str = Field("Binary Attack Detection", description="Classification objective")
    features_count: int = Field(78, description="Number of expected flow input features")
    classes: List[str] = Field(default_factory=lambda: ["BENIGN", "ATTACK"], description="Target classes")


class ConfusionMatrixResponse(BaseModel):
    """Confusion matrix metrics schema."""
    true_negative: int = Field(..., description="BENIGN correctly identified")
    false_positive: int = Field(..., description="BENIGN misclassified as ATTACK")
    false_negative: int = Field(..., description="ATTACK misclassified as BENIGN")
    true_positive: int = Field(..., description="ATTACK correctly identified")


class TopFeatureSchema(BaseModel):
    """Top feature importance weight."""
    feature: str
    importance: float


class MLMetricsResponse(BaseModel):
    """Schema for GET /api/ml/metrics."""
    model_type: str = Field("Random Forest", description="Model algorithm")
    task: str = Field("Binary Attack Detection", description="Task description")
    evaluation_dataset: str = Field("CICIDS2017 Test Partition (20%)", description="Test dataset")
    test_samples: int = Field(..., description="Number of test flow instances evaluated")
    train_samples: int = Field(..., description="Number of training flow instances")
    accuracy: float = Field(..., description="Test classification accuracy (0..1)")
    precision: float = Field(..., description="Test precision score (0..1)")
    recall: float = Field(..., description="Test recall score (0..1)")
    f1_score: float = Field(..., description="Test harmonic F1 score (0..1)")
    roc_auc: float = Field(..., description="Test Area under ROC curve (0..1)")
    confusion_matrix: ConfusionMatrixResponse
    classes: List[str] = Field(default_factory=lambda: ["BENIGN", "ATTACK"])
    top_features: List[TopFeatureSchema] = Field(default_factory=list)


class PredictRequest(BaseModel):
    """Schema for POST /api/ml/predict request."""
    features: Optional[Union[Dict[str, float], List[float]]] = Field(
        None, description="78-dimensional flow feature vector or dictionary of feature names"
    )
    sample_type: Optional[str] = Field(
        "auto", description="Pre-cached sample type if features omitted ('auto', 'benign', or 'attack')"
    )


class PredictResponse(BaseModel):
    """Schema for POST /api/ml/predict response."""
    prediction: str = Field(..., description="Classification output: 'BENIGN' or 'ATTACK'")
    is_attack: bool = Field(..., description="Boolean flag for easy triage")
    confidence: float = Field(..., description="Predicted probability percentage (0..100%)")
    probabilities: Dict[str, float] = Field(..., description="Class probability distribution")
    inference_latency_ms: float = Field(..., description="Model compute time in milliseconds")
    model_type: str = Field("Random Forest", description="Evaluating model")
    features_evaluated: int = Field(78, description="Number of features evaluated")

