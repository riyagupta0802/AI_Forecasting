"""API Route Registry for HEX HIVE.

Mounts modular endpoint routers under /api:
- GET /api/health           (Health check)
- GET /api/system/status    (Component architecture status)
- GET /api/network/summary  (Network security summary metrics - Demo)
- GET /api/forecast/status  (Attack forecasting status placeholder)
- GET /api/traffic/sample   (Sample network traffic dataset - Demo)
- GET /api/data/status      (Dataset & preprocessing status - Phase 4)
- GET /api/ml/status        (Random Forest model status - Phase 5)
- GET /api/ml/metrics       (Test evaluation performance metrics - Phase 5)
- POST /api/ml/predict      (Real binary attack detection inference - Phase 5)
"""

from fastapi import APIRouter
from app.routes.health import router as health_router
from app.routes.system import router as system_router
from app.routes.network import router as network_router
from app.routes.forecast import router as forecast_router
from app.routes.traffic import router as traffic_router
from app.routes.data import router as data_router
from app.routes.ml import router as ml_router
from app.routes.escalation import router as escalation_router
from app.routes.attack_story import router as attack_story_router
from app.routes.warning import router as warning_router
from app.routes.recommendations import router as recommendations_router
from app.routes.explainability import router as explainability_router

api_router = APIRouter()

# Active routes across Phases 1 through 11
api_router.include_router(health_router)
api_router.include_router(system_router)
api_router.include_router(network_router)
api_router.include_router(forecast_router)
api_router.include_router(traffic_router)
api_router.include_router(data_router)
api_router.include_router(ml_router)
api_router.include_router(escalation_router)
api_router.include_router(attack_story_router)
api_router.include_router(warning_router)
api_router.include_router(recommendations_router)
api_router.include_router(explainability_router)

__all__ = ["api_router"]




