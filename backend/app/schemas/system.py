from pydantic import BaseModel, Field


class SystemStatusResponse(BaseModel):
    """Schema for overall system architectural component status.

    Clearly discloses that ML models and MongoDB databases are not loaded/connected
    in this prototype phase.
    """

    status: str = Field(default="online", description="Overall gateway status")
    backend: str = Field(default="running", description="FastAPI service status")
    ml_model: str = Field(default="not_loaded", description="ML inference engine status")
    database: str = Field(default="not_connected", description="MongoDB database status")

