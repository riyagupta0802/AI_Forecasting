"""Inference and Prediction Pipeline for HEX HIVE Phase 7 Time-to-Escalation.

Chains Phase 5 Binary Attack Detection and Phase 6 Stage Forecasting directly into
Phase 7 Time-to-Escalation estimation:
Traffic Telemetry -> Detection -> Forecasting -> Time-to-Escalation Estimation.
"""

from pathlib import Path
from typing import Dict, List, Any, Union, Optional
import time
import logging
import joblib
import pandas as pd
import numpy as np

from ml.escalation.model import TimeToEscalationEngine
from ml.forecasting.predict import forecaster
from ml.forecasting.preprocessing import load_feature_metadata, format_input_features

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HEX_HIVE.Escalation.Predict")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = REPO_ROOT / "ml" / "models"


class EscalationPredictor:
    """Production runtime inference engine for real-time attack escalation timing."""

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or (MODELS_DIR / "escalation_model.joblib")
        self.regressor = None
        self.feature_names = load_feature_metadata()
        self.engine = TimeToEscalationEngine()
        self.is_ready = False

        self._load_artifacts()

    def _load_artifacts(self):
        """Load trained regression model if available."""
        try:
            if self.model_path.is_file():
                logger.info("Loading Escalation Regressor from: %s", self.model_path)
                self.regressor = joblib.load(self.model_path)
                self.engine.model = self.regressor
                self.is_ready = True
            else:
                logger.warning("Escalation model file not found at: %s", self.model_path)
                self.is_ready = True  # Analytical engine can still operate on empirical velocity baseline
        except Exception as e:
            logger.error("Failed to load escalation artifacts: %s", e)
            self.is_ready = False

    def predict(
        self,
        features: Union[Dict[str, float], List[float], np.ndarray, pd.DataFrame, None] = None,
        sample_type: str = "auto",
    ) -> Dict[str, Any]:
        """Perform end-to-end detection, forecasting, and time-to-escalation estimation.

        Flow:
            1. Run Phase 6 forecaster (which runs Phase 5 detector).
            2. Extract current state, forecasted next stage, and confidence.
            3. Apply velocity-calibrated escalation engine.
            4. Return unified multi-phase telemetry response.
        """
        start_time = time.perf_counter()

        # Step 1 & 2: Execute upstream Detection & Forecasting
        forecast_result = forecaster.predict(features=features, sample_type=sample_type)

        current_state = forecast_result.get("current_state", "BENIGN")
        predicted_stage = forecast_result.get("predicted_next_stage", "BENIGN")
        confidence = forecast_result.get("confidence", 85.0)

        # Format features DataFrame for velocity computation
        df_features = None
        if features is not None or sample_type != "auto":
            try:
                # Use cached sample from forecaster if sample_type specified
                feat_input = features
                if feat_input is None and sample_type.lower() in forecaster._samples:
                    feat_input = forecaster._samples[sample_type.lower()]
                df_features = format_input_features(feat_input, self.feature_names)
            except Exception as e:
                logger.warning("Could not format feature DataFrame: %s", e)

        # Step 3: Run Phase 7 Time-to-Escalation Engine
        escalation_result = self.engine.estimate(
            current_state=current_state,
            predicted_state=predicted_stage,
            confidence=confidence,
            features_df=df_features,
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        # Merge with execution metadata
        escalation_result.update({
            "latency_ms": elapsed_ms,
            "sample_type": sample_type,
            "detection_stage": forecast_result.get("detection_stage", {}),
            "forecast_context": {
                "forecast_available": forecast_result.get("forecast_available", True),
                "predicted_next_stage_display": forecast_result.get("predicted_next_stage_display"),
                "forecast_confidence": confidence,
                "trajectory": forecast_result.get("trajectory", []),
            },
        })

        return escalation_result


# Global singleton instance
escalation_predictor = EscalationPredictor()

