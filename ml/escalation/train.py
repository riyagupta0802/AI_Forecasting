"""Supervised Training Script for HEX HIVE Phase 7 Time-to-Escalation Model.

Trains a regression model on network flow duration, arrival rates, and telemetry velocities
to predict the continuous escalation window (in seconds) toward the next attack stage.

Usage:
    python ml/escalation/train.py
"""

from pathlib import Path
import json
import logging
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Ensure project root is in sys.path
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.escalation.preprocessing import compute_velocity_index

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HEX_HIVE.Escalation.Train")

DATA_DIR = REPO_ROOT / "ml" / "data" / "processed"
MODELS_DIR = REPO_ROOT / "ml" / "models"


def construct_escalation_targets(X_df: pd.DataFrame, y_series: pd.Series) -> np.ndarray:
    """Construct velocity-calibrated continuous escalation targets in seconds.

    Classes:
        0 (BENIGN): 0 seconds (not escalating / baseline)
        1 (Bot): ~60 to 180 seconds based on C2 beacon velocity
        2 (DDoS): 0 seconds (already at peak saturation)
        3 (PortScan): ~120 to 360 seconds based on scan velocity
    """
    targets = []
    for idx in range(len(X_df)):
        label_code = int(y_series.iloc[idx])
        row = X_df.iloc[idx]
        v_idx = compute_velocity_index(row)

        if label_code == 0:  # BENIGN
            targets.append(0.0)
        elif label_code == 1:  # Bot
            # Nominal 120s modulated by velocity
            sec = float(np.clip(120.0 / v_idx, 30.0, 300.0))
            targets.append(sec)
        elif label_code == 2:  # DDoS
            targets.append(0.0)  # Already escalated
        elif label_code == 3:  # PortScan
            # Nominal 240s modulated by velocity
            sec = float(np.clip(240.0 / v_idx, 60.0, 600.0))
            targets.append(sec)
        else:
            targets.append(0.0)

    return np.array(targets, dtype=float)


def train_escalation_model() -> bool:
    """Train and evaluate the Time-to-Escalation regression model."""
    features_path = DATA_DIR / "train_features.csv"
    labels_path = DATA_DIR / "train_labels.csv"

    if not features_path.is_file() or not labels_path.is_file():
        logger.error("Required processed data files not found in %s", DATA_DIR)
        return False

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_output_path = MODELS_DIR / "escalation_model.joblib"
    metrics_output_path = MODELS_DIR / "escalation_metrics.json"

    logger.info("Loading processed dataset...")
    X = pd.read_csv(features_path)
    y_df = pd.read_csv(labels_path)
    y = y_df["Label"] if "Label" in y_df.columns else y_df.iloc[:, 0]

    feature_names = X.columns.tolist()
    y_targets = construct_escalation_targets(X, y)

    # Stratified 80/20 train/test split based on categorical label
    logger.info("Performing 80/20 train-test split (random_state=42)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_targets,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )
    logger.info("Training set: %d samples | Test set: %d samples", len(X_train), len(X_test))

    # Initialize and fit RandomForestRegressor
    logger.info("Fitting RandomForestRegressor for escalation window estimation...")
    regressor = RandomForestRegressor(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        n_jobs=-1,
    )
    regressor.fit(X_train, y_train)

    # Evaluate on held-out test split
    y_pred = regressor.predict(X_test)
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2 = float(r2_score(y_test, y_pred))

    logger.info("Held-out Test MAE: %.2f seconds | RMSE: %.2f seconds | R²: %.4f", mae, rmse, r2)

    # Save model artifact
    logger.info("Saving trained escalation model to: %s", model_output_path)
    joblib.dump(regressor, model_output_path)

    # Top feature importances
    importances = regressor.feature_importances_
    sorted_idx = np.argsort(importances)[::-1][:10]
    top_features = [
        {"feature": feature_names[i], "importance": round(float(importances[i]), 4)}
        for i in sorted_idx
    ]

    metrics_payload = {
        "model_type": "RandomForestRegressor (Escalation Window Regressor)",
        "task": "Time-to-Escalation Window Estimation",
        "random_state": 42,
        "n_estimators": 100,
        "max_depth": 8,
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "target_unit": "seconds",
        "mean_absolute_error": round(mae, 2),
        "root_mean_squared_error": round(rmse, 2),
        "r2_score": round(r2, 4),
        "top_features": top_features,
        "risk_thresholds": {
            "CRITICAL": "<= 60s",
            "HIGH": "61s - 180s",
            "MODERATE": "181s - 360s",
            "LOW": "> 360s or Not Escalating",
        },
        "limitations": (
            "Current dataset consists of 500 flow-level summary records without wall-clock timestamps. "
            "Escalation targets are modeled via flow velocity calibration (packet arrival rate, byte volume, "
            "and flow duration) combined with empirical Kill Chain progression baselines. "
            "Future iterations with continuous multi-hour PCAPs can ingest chronological sequence timestamps."
        ),
    }

    logger.info("Writing escalation metrics to: %s", metrics_output_path)
    with open(metrics_output_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    logger.info("Phase 7 Escalation Model Training COMPLETED SUCCESSFULLY.")
    return True


if __name__ == "__main__":
    success = train_escalation_model()
    sys.exit(0 if success else 1)

