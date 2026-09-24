"""Preprocessing and Feature Alignment Utilities for HEX HIVE Phase 6 Forecasting.

Standardizes input network flow features and prepares stage transition sequences,
reusing the Phase 4 preprocessing metadata and scaler specifications.
Designed with a modular architecture so it can adapt to LSTM 3D sequence tensors
(batch_size, timesteps, features) or tabular feature vectors.
"""

from pathlib import Path
from typing import Dict, List, Any, Union, Tuple, Optional
import json
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger("HEX_HIVE.Forecasting.Preprocessing")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "ml" / "data" / "processed"
META_PATH = DATA_DIR / "preprocessing_meta.json"

STAGE_LABEL_MAPPING = {
    0: "BENIGN",
    1: "Bot",
    2: "DDoS",
    3: "PortScan",
}

STAGE_NAME_TO_CODE = {
    "BENIGN": 0,
    "Bot": 1,
    "DDoS": 2,
    "PortScan": 3,
}

# Real attack stages mapped to standardized cybersecurity lifecycle descriptions
STAGE_DESCRIPTIONS = {
    "BENIGN": "Normal Baseline Traffic",
    "PortScan": "Reconnaissance / Probe Phase",
    "Bot": "C2 Botnet Infection / Staging Phase",
    "DDoS": "Volumetric Denial of Service Attack",
}


def load_feature_metadata() -> List[str]:
    """Load the canonical 78 feature names from Phase 4 metadata."""
    if META_PATH.is_file():
        try:
            with open(META_PATH, "r", encoding="utf-8") as f:
                meta = json.load(f)
                return meta.get("features", [])
        except Exception as e:
            logger.warning("Could not read feature metadata: %s", e)
    return []


def format_input_features(
    features: Union[Dict[str, float], List[float], np.ndarray, pd.DataFrame, None],
    feature_names: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Format diverse feature representations into a canonical 78-feature DataFrame.

    Args:
        features: Dictionary, list, array, or DataFrame.
        feature_names: Expected list of feature column names.

    Returns:
        pd.DataFrame with exact feature column alignment.
    """
    if feature_names is None:
        feature_names = load_feature_metadata()

    num_features = len(feature_names) if feature_names else 78

    if features is None:
        # Default zeros vector
        return pd.DataFrame(np.zeros((1, num_features)), columns=feature_names)

    if isinstance(features, pd.DataFrame):
        # Align columns
        for col in feature_names:
            if col not in features.columns:
                features[col] = 0.0
        return features[feature_names].copy()

    if isinstance(features, dict):
        row = {col: float(features.get(col, 0.0)) for col in feature_names}
        return pd.DataFrame([row], columns=feature_names)

    if isinstance(features, (list, np.ndarray)):
        arr = np.array(features, dtype=float).ravel()
        if len(arr) < num_features:
            padded = np.zeros(num_features, dtype=float)
            padded[: len(arr)] = arr
            arr = padded
        elif len(arr) > num_features:
            arr = arr[:num_features]
        return pd.DataFrame(arr.reshape(1, -1), columns=feature_names)

    raise ValueError(f"Unsupported features format: {type(features)}")


def build_sequence_windows(
    X: np.ndarray,
    y: np.ndarray,
    timesteps: int = 5,
) -> Tuple[np.ndarray, np.ndarray]:
    """Construct sliding temporal windows for sequence/LSTM model training.

    Args:
        X: 2D feature matrix (samples, features).
        y: 1D target array.
        timesteps: Window length.

    Returns:
        Tuple of (X_seq, y_next):
            - X_seq: 3D array of shape (samples - timesteps, timesteps, features)
            - y_next: 1D array of shape (samples - timesteps,) representing next state
    """
    num_samples = len(X)
    if num_samples <= timesteps:
        raise ValueError(f"Insufficient samples ({num_samples}) for timesteps={timesteps}")

    X_seq = []
    y_next = []
    for i in range(num_samples - timesteps):
        X_seq.append(X[i : i + timesteps])
        y_next.append(y[i + timesteps])

    return np.array(X_seq), np.array(y_next)

