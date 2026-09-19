"""Inference and Prediction Module for HEX HIVE Phase 5.

Loads the trained Random Forest classifier and preprocessing metadata to perform
real ML-based binary classification (BENIGN vs ATTACK) on network traffic telemetry.
"""

from pathlib import Path
from typing import Dict, List, Any, Union
import json
import logging
import time
import joblib
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HEX_HIVE.Predictor")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = REPO_ROOT / "ml" / "models"
DATA_DIR = REPO_ROOT / "ml" / "data" / "processed"


class AttackPredictor:
    """Production runtime inference engine for binary network attack classification."""

    def __init__(
        self,
        model_path: Path = None,
        meta_path: Path = None,
        features_csv: Path = None,
    ):
        self.model_path = model_path or (MODELS_DIR / "attack_classifier.joblib")
        self.meta_path = meta_path or (DATA_DIR / "preprocessing_meta.json")
        self.features_csv = features_csv or (DATA_DIR / "train_features.csv")

        self.model = None
        self.feature_names = []
        self.is_ready = False
        self._benign_sample = None
        self._attack_sample = None

        self._load_artifacts()

    def _load_artifacts(self):
        """Load trained model weights and metadata into memory."""
        try:
            if not self.model_path.is_file():
                logger.warning("Trained model not found at: %s", self.model_path)
                return

            logger.info("Loading Random Forest model from: %s", self.model_path)
            self.model = joblib.load(self.model_path)

            if self.meta_path.is_file():
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    self.feature_names = meta.get("features", [])

            # Pre-cache benchmark representative test samples for interactive UI testing
            if self.features_csv.is_file():
                df_feat = pd.read_csv(self.features_csv)
                if not self.feature_names:
                    self.feature_names = df_feat.columns.tolist()

                labels_path = DATA_DIR / "train_labels.csv"
                if labels_path.is_file():
                    df_labels = pd.read_csv(labels_path)
                    y_vals = df_labels["Label"] if "Label" in df_labels.columns else df_labels.iloc[:, 0]
                    benign_indices = np.where(y_vals == 0)[0]
                    attack_indices = np.where(y_vals > 0)[0]

                    if len(benign_indices) > 0:
                        self._benign_sample = df_feat.iloc[benign_indices[0]].values.astype(float)
                    if len(attack_indices) > 0:
                        self._attack_sample = df_feat.iloc[attack_indices[0]].values.astype(float)

            self.is_ready = True
            logger.info("AttackPredictor initialized successfully with %d features.", len(self.feature_names))
        except Exception as e:
            logger.error("Failed to initialize AttackPredictor: %s", e)
            self.is_ready = False

    def predict(
        self,
        features: Union[Dict[str, float], List[float], np.ndarray, None] = None,
        sample_type: str = "auto",
    ) -> Dict[str, Any]:
        """Perform real ML prediction on a traffic sample.

        Args:
            features: Dictionary of feature name-values, list of numeric values, or None.
            sample_type: 'auto', 'benign', or 'attack' (used when features is None).

        Returns:
            Dictionary containing prediction label, confidence, probabilities, and latency.
        """
        if not self.is_ready or self.model is None:
            self._load_artifacts()
            if not self.is_ready or self.model is None:
                raise RuntimeError("Random Forest model is not trained or loaded.")

        start_time = time.perf_counter()
        n_features = len(self.feature_names) if self.feature_names else 78

        # 1. Resolve feature vector
        if features is None:
            # Use representative sample
            if sample_type == "benign" and self._benign_sample is not None:
                x_vec = self._benign_sample.reshape(1, -1)
            elif sample_type == "attack" and self._attack_sample is not None:
                x_vec = self._attack_sample.reshape(1, -1)
            else:
                x_vec = (
                    self._attack_sample.reshape(1, -1)
                    if (self._attack_sample is not None and np.random.rand() > 0.5)
                    else (self._benign_sample.reshape(1, -1) if self._benign_sample is not None else np.zeros((1, n_features)))
                )
        elif isinstance(features, dict):
            # Map dictionary to expected column sequence
            vec = []
            for col in self.feature_names:
                vec.append(float(features.get(col, 0.0)))
            x_vec = np.array(vec).reshape(1, -1)
        elif isinstance(features, (list, tuple)):
            arr = np.array(features, dtype=float)
            if len(arr) != n_features:
                logger.warning("Feature list length %d does not match expected %d. Padding/truncating.", len(arr), n_features)
                padded = np.zeros(n_features)
                padded[: min(len(arr), n_features)] = arr[: min(len(arr), n_features)]
                x_vec = padded.reshape(1, -1)
            else:
                x_vec = arr.reshape(1, -1)
        elif isinstance(features, np.ndarray):
            x_vec = features.reshape(1, -1)
        else:
            raise ValueError(f"Unsupported features payload type: {type(features)}")

        # 2. Execute Real Model Inference
        # Wrap as DataFrame with feature names to maintain feature alignment
        if self.feature_names and len(self.feature_names) == x_vec.shape[1]:
            x_df = pd.DataFrame(x_vec, columns=self.feature_names)
        else:
            x_df = x_vec

        raw_pred = int(self.model.predict(x_df)[0])
        raw_proba = self.model.predict_proba(x_df)[0]

        benign_prob = float(raw_proba[0])
        attack_prob = float(raw_proba[1]) if len(raw_proba) > 1 else 0.0

        label = "ATTACK" if raw_pred == 1 else "BENIGN"
        confidence = round(max(benign_prob, attack_prob) * 100, 1)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "prediction": label,
            "is_attack": bool(raw_pred == 1),
            "confidence": confidence,
            "probabilities": {
                "BENIGN": round(benign_prob, 4),
                "ATTACK": round(attack_prob, 4),
            },
            "inference_latency_ms": latency_ms,
            "model_type": "Random Forest",
            "features_evaluated": x_vec.shape[1],
        }


# Global singleton instance for high-performance reuse
predictor = AttackPredictor()


if __name__ == "__main__":
    p = AttackPredictor()
    print("Testing Benign prediction:")
    print(p.predict(sample_type="benign"))
    print("\nTesting Attack prediction:")
    print(p.predict(sample_type="attack"))
