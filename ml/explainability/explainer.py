"""Core Explainable AI (XAI) Engine for HEX HIVE Phase 11.

Uses SHAP (SHapley Additive exPlanations) TreeExplainer to produce exact Shapley values
for the trained Phase 5 binary RandomForestClassifier. Provides local sample explanations
and global model feature importance rankings with human-readable interpretation.
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import time
from typing import Dict, List, Any, Optional, Union
import joblib
import numpy as np
import pandas as pd
import shap

from ml.explainability.models import (
    FeatureContribution,
    LocalExplanationResult,
    GlobalFeatureImportance,
    GlobalExplanationResult,
)
from ml.explainability.formatter import (
    get_friendly_feature_meta,
    format_explanation_summary,
    format_technical_summary,
)

logger = logging.getLogger("HEX_HIVE.Explainability.Explainer")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = REPO_ROOT / "ml" / "models"
DATA_DIR = REPO_ROOT / "ml" / "data" / "processed"


class AttackExplainer:
    """Production runtime XAI engine for explaining Phase 5 Random Forest detections via SHAP."""

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
        self.feature_names: List[str] = []
        self.explainer: Optional[shap.TreeExplainer] = None
        self.is_ready = False
        self._benign_sample: Optional[np.ndarray] = None
        self._attack_sample: Optional[np.ndarray] = None
        self._global_cache: Optional[GlobalExplanationResult] = None

        self.limitations_note = (
            "SHAP (SHapley Additive exPlanations) identifies the mathematical feature contributions "
            "that pushed the Phase 5 Random Forest model toward or away from its classification. "
            "SHAP feature contributions reflect correlation and model decision boundaries on the "
            "CICIDS2017 continuous network flow telemetry; they describe the model's reasoning "
            "rather than absolute physical causation."
        )

        self._initialize()

    def _initialize(self):
        """Load model, metadata, and initialize TreeExplainer."""
        try:
            if not self.model_path.is_file():
                logger.warning("Phase 5 model not found at: %s", self.model_path)
                return

            logger.info("Initializing SHAP TreeExplainer with model: %s", self.model_path)
            self.model = joblib.load(self.model_path)
            self.explainer = shap.TreeExplainer(self.model)

            # Load feature column names
            if self.meta_path.is_file():
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    self.feature_names = meta.get("features", [])

            # Pre-cache benchmark representative test samples
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
            logger.info(
                "AttackExplainer initialized successfully with %d features. Base values: %s",
                len(self.feature_names),
                getattr(self.explainer, "expected_value", None),
            )
        except Exception as e:
            logger.error("Failed to initialize AttackExplainer: %s", e)
            self.is_ready = False

    @property
    def sample_attack(self) -> pd.DataFrame:
        """Returns benchmark Attack sample DataFrame."""
        return self._resolve_input_vector(sample_type="attack")

    @property
    def sample_benign(self) -> pd.DataFrame:
        """Returns benchmark Benign sample DataFrame."""
        return self._resolve_input_vector(sample_type="benign")

    def _resolve_input_vector(
        self,
        features: Union[Dict[str, float], List[float], np.ndarray, None] = None,
        sample_type: str = "auto",
    ) -> pd.DataFrame:
        """Align input into a 1x78 DataFrame matching the trained model feature sequence."""
        n_features = len(self.feature_names) if self.feature_names else 78

        if features is None:
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
            vec = [float(features.get(col, 0.0)) for col in self.feature_names]
            x_vec = np.array(vec).reshape(1, -1)
        elif isinstance(features, (list, tuple)):
            arr = np.array(features, dtype=float)
            if len(arr) != n_features:
                padded = np.zeros(n_features)
                padded[: min(len(arr), n_features)] = arr[: min(len(arr), n_features)]
                x_vec = padded.reshape(1, -1)
            else:
                x_vec = arr.reshape(1, -1)
        elif isinstance(features, np.ndarray):
            x_vec = features.reshape(1, -1)
        else:
            raise ValueError(f"Unsupported features payload type: {type(features)}")

        if self.feature_names and len(self.feature_names) == x_vec.shape[1]:
            return pd.DataFrame(x_vec, columns=self.feature_names)
        return pd.DataFrame(x_vec)

    def explain_instance(
        self,
        features: Union[Dict[str, float], List[float], np.ndarray, None] = None,
        sample_type: str = "auto",
        top_n: int = 5,
    ) -> LocalExplanationResult:
        """Generate a local SHAP explanation for an individual network traffic observation.

        Args:
            features: Custom feature dictionary or continuous numerical list.
            sample_type: 'auto', 'benign', or 'attack' if features is None.
            top_n: Number of top contributing features to rank and return.

        Returns:
            LocalExplanationResult containing prediction, base value, top features, and summary.
        """
        if not self.is_ready or self.explainer is None:
            self._initialize()
            if not self.is_ready or self.explainer is None:
                raise RuntimeError("SHAP TreeExplainer is not ready or model artifact missing.")

        x_df = self._resolve_input_vector(features=features, sample_type=sample_type)

        # 1. Real Model Prediction
        raw_pred = int(self.model.predict(x_df)[0])  # 0: BENIGN, 1: ATTACK
        raw_proba = self.model.predict_proba(x_df)[0]
        prediction_label = "ATTACK" if raw_pred == 1 else "BENIGN"
        confidence = float(raw_proba[raw_pred] * 100)

        # 2. Compute exact SHAP values via TreeExplainer
        sv = self.explainer.shap_values(x_df)

        # Handle binary classification shapes: (1, 78, 2) or list of [arr_0, arr_1]
        if isinstance(sv, list):
            class_shap = sv[raw_pred][0]
        elif isinstance(sv, np.ndarray) and len(sv.shape) == 3:
            class_shap = sv[0, :, raw_pred]
        elif isinstance(sv, np.ndarray) and len(sv.shape) == 2:
            class_shap = sv[0] if raw_pred == 1 else -sv[0]
        else:
            class_shap = np.array(sv).flatten()

        # Expected value for predicted class
        expected_val = self.explainer.expected_value
        if isinstance(expected_val, (list, np.ndarray)):
            base_value = float(expected_val[raw_pred])
        else:
            base_value = float(expected_val) if raw_pred == 1 else (1.0 - float(expected_val))

        predicted_value = base_value + float(np.sum(class_shap))

        # 3. Rank features by absolute SHAP impact
        abs_contributions = np.abs(class_shap)
        sorted_indices = np.argsort(abs_contributions)[::-1]

        contributions: List[FeatureContribution] = []
        n_to_extract = min(top_n, len(sorted_indices))

        for rank_idx in range(n_to_extract):
            col_idx = sorted_indices[rank_idx]
            feat_name = self.feature_names[col_idx] if col_idx < len(self.feature_names) else f"feature_{col_idx}"
            friendly_name, desc = get_friendly_feature_meta(feat_name)
            raw_val = float(x_df.iloc[0, col_idx])
            shap_val = float(class_shap[col_idx])
            abs_val = float(abs_contributions[col_idx])

            # Direction: does it push toward the predicted class or away from it?
            if shap_val > 0.00001:
                direction = "toward_prediction"
            elif shap_val < -0.00001:
                direction = "away_from_prediction"
            else:
                direction = "neutral"

            contributions.append(
                FeatureContribution(
                    name=feat_name,
                    friendly_name=friendly_name,
                    value=raw_val,
                    shap_value=shap_val,
                    abs_shap=abs_val,
                    direction=direction,
                    rank=rank_idx + 1,
                    description=desc,
                )
            )

        # 4. Synthesize human-readable and technical summaries
        human_summary = format_explanation_summary(
            prediction=prediction_label,
            confidence=confidence,
            top_features=contributions,
        )
        tech_summary = format_technical_summary(
            base_value=base_value,
            predicted_value=predicted_value,
            top_features=contributions,
        )

        return LocalExplanationResult(
            available=True,
            prediction=prediction_label,
            confidence=confidence,
            base_value=base_value,
            predicted_value=predicted_value,
            features=contributions,
            summary=human_summary,
            technical_summary=tech_summary,
            method="SHAP (TreeExplainer)",
            model="RandomForestClassifier",
            features_evaluated=x_df.shape[1],
            timestamp=datetime.now(timezone.utc).isoformat(),
            limitations=self.limitations_note,
        )

    def get_global_importance(self, top_n: int = 10) -> GlobalExplanationResult:
        """Compute or retrieve cached global feature importance across evaluation data.

        Args:
            top_n: Number of top global features to return.

        Returns:
            GlobalExplanationResult with ranked mean absolute SHAP values.
        """
        if self._global_cache is not None:
            return GlobalExplanationResult(
                available=self._global_cache.available,
                method=self._global_cache.method,
                model=self._global_cache.model,
                dataset_source=self._global_cache.dataset_source,
                samples_evaluated=self._global_cache.samples_evaluated,
                top_features=self._global_cache.top_features[:top_n],
                generated_at=self._global_cache.generated_at,
                limitations=self._global_cache.limitations,
            )

        if not self.is_ready or self.explainer is None:
            self._initialize()

        if not self.features_csv.is_file():
            raise FileNotFoundError(f"Evaluation features dataset not found at: {self.features_csv}")

        df_feat = pd.read_csv(self.features_csv)
        sv = self.explainer.shap_values(df_feat)

        # Class 1 (ATTACK) impact
        if isinstance(sv, list):
            attack_shap = sv[1]
        elif isinstance(sv, np.ndarray) and len(sv.shape) == 3:
            attack_shap = sv[:, :, 1]
        else:
            attack_shap = sv

        mean_abs_shap = np.mean(np.abs(attack_shap), axis=0)
        sorted_indices = np.argsort(mean_abs_shap)[::-1]

        global_features: List[GlobalFeatureImportance] = []

        for rank_idx, col_idx in enumerate(sorted_indices):
            feat_name = self.feature_names[col_idx] if col_idx < len(self.feature_names) else f"feature_{col_idx}"
            friendly_name, desc = get_friendly_feature_meta(feat_name)
            val = float(mean_abs_shap[col_idx])

            global_features.append(
                GlobalFeatureImportance(
                    name=feat_name,
                    friendly_name=friendly_name,
                    mean_abs_shap=val,
                    rank=rank_idx + 1,
                    description=desc,
                )
            )

        self._global_cache = GlobalExplanationResult(
            available=True,
            method="Mean Absolute SHAP (TreeExplainer)",
            model="RandomForestClassifier",
            dataset_source="CICIDS2017 Benchmark (500 Samples)",
            samples_evaluated=len(df_feat),
            top_features=global_features,
            generated_at=datetime.now(timezone.utc).isoformat(),
            limitations=(
                "Global importance represents the mean absolute SHAP value across all 500 evaluation "
                "flows in the CICIDS2017 dataset. Features with higher mean |SHAP| exert greater average "
                "leverage across the model's tree split paths."
            ),
        )

        return GlobalExplanationResult(
            available=self._global_cache.available,
            method=self._global_cache.method,
            model=self._global_cache.model,
            dataset_source=self._global_cache.dataset_source,
            samples_evaluated=self._global_cache.samples_evaluated,
            top_features=self._global_cache.top_features[:top_n],
            generated_at=self._global_cache.generated_at,
            limitations=self._global_cache.limitations,
        )


# Global singleton instance for performance optimization and cache reuse
attack_explainer = AttackExplainer()
