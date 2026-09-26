"""Pydantic schemas for NETORACLE Dataset Ingestion and Full-Pipeline Analysis."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DatasetValidationResult(BaseModel):
    """Schema validation result for an uploaded network traffic dataset."""
    filename: str = Field(..., description="Uploaded or selected dataset filename")
    record_count: int = Field(..., description="Number of flow records in dataset")
    required_feature_count: int = Field(78, description="Number of features required by Phase 5 model")
    available_required_count: int = Field(..., description="Number of required features found")
    is_compatible: bool = Field(..., description="Whether dataset satisfies model input schema")
    available_features: List[str] = Field(default_factory=list, description="Required features found")
    missing_features: List[str] = Field(default_factory=list, description="Required features missing from CSV")
    extra_columns: List[str] = Field(default_factory=list, description="Non-required metadata or label columns")
    message: str = Field(..., description="Human-readable compatibility status")


class SamplePrediction(BaseModel):
    """Prediction summary for an individual network flow record."""
    index: int
    prediction: str  # "BENIGN" or "ATTACK"
    is_attack: bool
    confidence: float
    benign_probability: float
    attack_probability: float
    destination_port: Optional[int] = None
    flow_duration: Optional[float] = None
    total_packets: Optional[int] = None
    identified_stage: Optional[str] = None


class StageDistribution(BaseModel):
    """Distribution of detected traffic categories across the dataset."""
    BENIGN: int = 0
    Bot: int = 0
    DDoS: int = 0
    PortScan: int = 0


class AnalyzeResponse(BaseModel):
    """Complete multi-phase analysis response for an ingested dataset."""
    success: bool
    dataset_name: str
    source_type: str = "Uploaded Dataset"  # "Uploaded Dataset" or "Local Test Dataset"
    total_records: int
    benign_count: int
    attack_count: int
    attack_percentage: float
    average_confidence: float
    analysis_timestamp: str
    model: str = "Phase 5 Random Forest Classifier (100 Trees, 78 Features)"
    stage_distribution: Dict[str, int]
    dominant_attack_stage: Optional[str] = None
    risk_score: int
    risk_level: str
    
    # Phase 5 Sample Predictions (subset for UI table display)
    sample_predictions: List[SamplePrediction] = Field(default_factory=list)
    
    # Connected Phase 6–11 Results
    forecast: Dict[str, Any] = Field(default_factory=dict)
    escalation: Dict[str, Any] = Field(default_factory=dict)
    attack_story: Dict[str, Any] = Field(default_factory=dict)
    early_warning: Dict[str, Any] = Field(default_factory=dict)
    recommendations: Dict[str, Any] = Field(default_factory=dict)
    explainability: Dict[str, Any] = Field(default_factory=dict)


class AnalyzeJsonRequest(BaseModel):
    """Optional JSON payload for dataset analysis."""
    filename: Optional[str] = "custom_traffic.csv"
    csv_text: Optional[str] = None
    use_local_test: bool = False

