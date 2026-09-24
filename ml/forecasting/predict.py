"""Inference and Prediction Pipeline for HEX HIVE Phase 6 Attack Forecasting.

Connects Phase 5 Binary Attack Detection with Phase 6 Stage Classification
and Transition Progression Forecasting:
Network Traffic -> Preprocessing -> Attack Detection -> Stage Classification -> Forecasting.
"""

from pathlib import Path
from typing import Dict, List, Any, Union, Optional
import json
import logging
import time
from datetime import datetime, timezone
import joblib
import numpy as np
import pandas as pd

from ml.forecasting.model import AttackForecastingModel
from ml.forecasting.preprocessing import (
    load_feature_metadata,
    format_input_features,
    STAGE_LABEL_MAPPING,
    STAGE_NAME_TO_CODE,
    STAGE_DESCRIPTIONS,
)
from ml.predictions.predict import predictor as binary_detector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HEX_HIVE.Forecasting.Predict")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = REPO_ROOT / "ml" / "models"
DATA_DIR = REPO_ROOT / "ml" / "data" / "processed"


class AttackForecaster:
    """Production runtime inference engine for real network attack forecasting."""

    def __init__(
        self,
        model_path: Optional[Path] = None,
        meta_path: Optional[Path] = None,
        features_csv: Optional[Path] = None,
        labels_csv: Optional[Path] = None,
    ):
        self.model_path = model_path or (MODELS_DIR / "forecast_stage_classifier.joblib")
        self.meta_path = meta_path or (DATA_DIR / "preprocessing_meta.json")
        self.features_csv = features_csv or (DATA_DIR / "train_features.csv")
        self.labels_csv = labels_csv or (DATA_DIR / "train_labels.csv")

        self.stage_classifier = None
        self.feature_names: List[str] = []
        self.forecasting_model = AttackForecastingModel()
        self.is_ready = False

        # Benchmark representative samples for interactive testing
        self._samples: Dict[str, np.ndarray] = {}

        self._load_artifacts()

    def _load_artifacts(self):
        """Load trained stage classifier weights, feature metadata, and benchmark samples."""
        try:
            self.feature_names = load_feature_metadata()

            if self.model_path.is_file():
                logger.info("Loading Stage Classifier from: %s", self.model_path)
                self.stage_classifier = joblib.load(self.model_path)
                self.forecasting_model.classifier = self.stage_classifier
                self.is_ready = True
            else:
                logger.warning("Stage classifier model file not found at: %s", self.model_path)
                self.is_ready = False

            # Cache benchmark samples for instant interactive UI testing
            if self.features_csv.is_file() and self.labels_csv.is_file():
                df_feat = pd.read_csv(self.features_csv)
                df_labels = pd.read_csv(self.labels_csv)
                y_vals = df_labels["Label"] if "Label" in df_labels.columns else df_labels.iloc[:, 0]

                if not self.feature_names:
                    self.feature_names = df_feat.columns.tolist()

                for code, name in STAGE_LABEL_MAPPING.items():
                    indices = np.where(y_vals == code)[0]
                    if len(indices) > 0:
                        self._samples[name.lower()] = df_feat.iloc[indices[0]].values.astype(float)
                        self._samples[name] = df_feat.iloc[indices[0]].values.astype(float)

            logger.info(
                "AttackForecaster initialized. Model ready: %s. Feature count: %d",
                self.is_ready,
                len(self.feature_names),
            )
        except Exception as e:
            logger.error("Failed to initialize AttackForecaster: %s", e)
            self.is_ready = False

    def predict(
        self,
        features: Union[Dict[str, float], List[float], np.ndarray, pd.DataFrame, None] = None,
        sample_type: str = "auto",
    ) -> Dict[str, Any]:
        """Perform end-to-end detection and forecasting on a network traffic flow.

        Flow:
            1. Preprocess & align 78 flow features.
            2. Phase 5 Binary Attack Detection (is it BENIGN or an ATTACK?).
            3. If ATTACK, run Phase 6 Multi-Class Stage Classifier to identify exact stage.
            4. Project possible next attack stage via empirical transition progression dynamics.
            5. Return structured forecast output with confidence, risk, and telemetry metrics.
        """
        start_time = time.perf_counter()

        if not self.is_ready or self.stage_classifier is None:
            self._load_artifacts()
            if not self.is_ready:
                return {
                    "forecast_available": False,
                    "status": "model_unavailable",
                    "current_state": "UNKNOWN",
                    "predicted_next_stage": "Forecasting unavailable",
                    "confidence": 0.0,
                    "risk_level": "LOW",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": "None",
                    "explanation": "Forecasting model weights not loaded or unavailable on host.",
                    "limitations": self.forecasting_model.limitations_note,
                }

        # Resolve input sample if sample_type specified
        features_vec = features
        normalized_sample_type = sample_type.strip().lower()
        if features_vec is None and normalized_sample_type in self._samples:
            features_vec = self._samples[normalized_sample_type]

        df_input = format_input_features(features_vec, self.feature_names)

        # STEP 1: Phase 5 Binary Detection
        binary_result = binary_detector.predict(features=df_input.values)
        is_attack = binary_result.get("is_attack", False)
        detection_confidence = binary_result.get("confidence", 95.0)

        # STEP 2: Phase 6 Stage Classification
        if not is_attack:
            current_stage = "BENIGN"
            stage_confidence = detection_confidence
            stage_probabilities = {"BENIGN": 100.0, "Bot": 0.0, "DDoS": 0.0, "PortScan": 0.0}
        else:
            # Multi-class stage prediction
            pred_code = int(self.stage_classifier.predict(df_input)[0])
            current_stage = STAGE_LABEL_MAPPING.get(pred_code, "PortScan")

            # Extract class probability distribution
            probs = self.stage_classifier.predict_proba(df_input)[0]
            stage_probabilities = {}
            for idx, p_val in enumerate(probs):
                c_name = STAGE_LABEL_MAPPING.get(idx, f"Class_{idx}")
                stage_probabilities[c_name] = round(float(p_val) * 100.0, 1)

            stage_confidence = stage_probabilities.get(current_stage, detection_confidence)

        # STEP 3: Phase 6 Transition Forecasting
        forecast_output = self.forecasting_model.predict_transition(
            current_stage=current_stage,
            current_confidence=stage_confidence,
            features_df=df_input,
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        # Merge with execution context
        forecast_output.update({
            "detection_stage": {
                "is_attack": is_attack,
                "detection_confidence": detection_confidence,
                "identified_stage": current_stage,
                "stage_probabilities": stage_probabilities,
            },
            "latency_ms": elapsed_ms,
            "sample_type": sample_type,
        })

        return forecast_output


# Global singleton instance for high-performance FastAPI route reuse
forecaster = AttackForecaster()
