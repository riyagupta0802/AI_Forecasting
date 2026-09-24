"""HEX HIVE Phase 7 — Time-to-Escalation Module Package.

Provides scientifically defensible estimation of time until network security threats
escalate into higher-severity stages, driven by flow velocity telemetry and Kill Chain dynamics.
"""

from ml.escalation.model import TimeToEscalationEngine
from ml.escalation.predict import EscalationPredictor, escalation_predictor

__all__ = [
    "TimeToEscalationEngine",
    "EscalationPredictor",
    "escalation_predictor",
]

