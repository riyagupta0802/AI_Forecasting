"""HEX HIVE Phase 6 — Forecasting Module Package.

Provides real machine-learning attack stage classification, progression modeling,
and predictive transition forecasting based on CICIDS2017 network flow telemetry.
"""

from ml.forecasting.model import AttackForecastingModel
from ml.forecasting.predict import AttackForecaster, forecaster

__all__ = [
    "AttackForecastingModel",
    "AttackForecaster",
    "forecaster",
]

