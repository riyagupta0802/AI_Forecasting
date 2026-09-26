import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent.parent
_backend_root = Path(__file__).resolve().parent.parent
for p in (str(_repo_root), str(_backend_root)):
    if p not in sys.path:
        sys.path.insert(0, p)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.mongodb import db_manager
from app.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events for startup and shutdown."""
    # Startup: Initialize hooks (DB, future ML models)
    await db_manager.connect()
    yield
    # Shutdown: Clean up resources
    await db_manager.disconnect()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="NETORACLE - AI-based Network Attack Forecasting & Early Warning System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration for React frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount primary API router under configured prefix (/api)
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    """Root entry point providing basic project info."""
    return {
        "project": settings.PROJECT_NAME,
        "phase": "Phase 1–11 Full Operational System",
        "docs": "/docs",
        "health": f"{settings.API_PREFIX}/health",
    }

