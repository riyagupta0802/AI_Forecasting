from typing import Optional
from pydantic import BaseModel, Field


class ForecastStatusResponse(BaseModel):
    """Schema for attack forecast status placeholder.

    Explicitly returns awaiting_model placeholders with null confidence
    until ML sequence models are integrated in subsequent phases.
    """

    status: str = Field(
        default="awaiting_model",
        description="Forecasting pipeline state",
    )
    current_pattern: str = Field(
        default="Awaiting ML model",
        description="Current observed network pattern classification",
    )
    possible_next_stage: str = Field(
        default="Awaiting ML model",
        description="Predicted next attack transition stage",
    )
    confidence: Optional[float] = Field(
        default=None,
        description="Model confidence score (null until ML is connected)",
    )
    time_to_escalation: Optional[int] = Field(
        default=None,
        description="Estimated seconds to escalation (null until ML is connected)",
    )

