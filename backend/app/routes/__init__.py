"""API Route Registry for HEX HIVE.

Organized modularly to support Phase 1 health checks and future phase routing:
- /traffic (Network traffic telemetry ingestion)
- /anomalies (Unsupervised anomaly detection)
- /classification (Multi-class attack classification)
- /forecasting (Temporal attack sequence prediction)
- /escalation (Time-to-escalation estimation)
- /story (Attack story graph correlation)
- /explainability (SHAP & feature attributions)
- /alerts (Early warning notifications)
- /recommendations (Mitigation advisories)
"""

from fastapi import APIRouter
from app.routes.health import router as health_router

api_router = APIRouter()

# Phase 1 active route
api_router.include_router(health_router)

__all__ = ["api_router"]

