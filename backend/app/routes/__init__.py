"""API Route Registry for HEX HIVE.

Mounts modular endpoint routers under /api:
- GET /api/health           (Health check)
- GET /api/system/status    (Component architecture status)
- GET /api/network/summary  (Network security summary metrics - Demo)
- GET /api/forecast/status  (Attack forecasting status placeholder)
- GET /api/traffic/sample   (Sample network traffic dataset - Demo)
"""

from fastapi import APIRouter
from app.routes.health import router as health_router
from app.routes.system import router as system_router
from app.routes.network import router as network_router
from app.routes.forecast import router as forecast_router
from app.routes.traffic import router as traffic_router

api_router = APIRouter()

# Phase 1 & Phase 3 active routes
api_router.include_router(health_router)
api_router.include_router(system_router)
api_router.include_router(network_router)
api_router.include_router(forecast_router)
api_router.include_router(traffic_router)

__all__ = ["api_router"]
