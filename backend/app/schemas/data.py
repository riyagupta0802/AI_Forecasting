"""Data status schemas for HEX HIVE Phase 4 data preprocessing."""

from typing import List
from pydantic import BaseModel, Field


class DataStatusResponse(BaseModel):
    """Schema for GET /api/data/status endpoint."""
    status: str = Field(..., description="Overall dataset status: ready, pending, or not_found")
    dataset: str = Field("CICIDS2017", description="Benchmark dataset name")
    mode: str = Field("demo", description="Data execution mode (strictly 'demo' for benchmark/sample data)")
    records_available: int = Field(..., description="Total raw/sample flow records available")
    preprocessing: str = Field(..., description="Status of preprocessing: ready, processing, or pending")
    processed_records: int = Field(..., description="Count of processed feature records ready for ML")
    classes_detected: List[str] = Field(default_factory=list, description="Unique traffic attack/benign classes identified")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "ready",
                "dataset": "CICIDS2017",
                "mode": "demo",
                "records_available": 500,
                "preprocessing": "ready",
                "processed_records": 500,
                "classes_detected": ["BENIGN", "DDoS", "PortScan", "Bot"]
            }
        }
    }

