"""Feature Preprocessor Module for HEX HIVE Preprocessing Pipeline.

Normalizes continuous numeric network features using StandardScaler
and encodes categorical attack classification labels with LabelEncoder.
Exports full preprocessing metadata to JSON for reproducible inference.
"""

from pathlib import Path
from typing import Tuple, Dict, Any, Union
import json
import logging
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder

logger = logging.getLogger("HEX_HIVE.Preprocessor")


class NetworkFlowPreprocessor:
    """Preprocesses network flow features and attack labels for machine learning."""

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.label_mapping = {}
        self.is_fitted = False

    def fit_transform(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Fit scaler on feature matrix and encoder on labels, then transform.

        Args:
            X: Cleaned numeric feature DataFrame.
            y: Target label Series.

        Returns:
            Tuple of:
                - X_scaled: Scaled feature DataFrame preserving column names.
                - y_encoded: Encoded integer target Series.
        """
        logger.info("Fitting StandardScaler on %d features and %d samples.", X.shape[1], X.shape[0])
        self.feature_names = X.columns.tolist()

        # Fit and transform features
        scaled_array = self.scaler.fit_transform(X)
        X_scaled = pd.DataFrame(scaled_array, columns=self.feature_names, index=X.index)

        # Fit and transform labels
        logger.info("Encoding attack classification labels.")
        encoded_labels = self.label_encoder.fit_transform(y)
        y_encoded = pd.Series(encoded_labels, name="Label", index=y.index)

        # Store label mappings
        self.label_mapping = {
            str(cls_name): int(idx)
            for idx, cls_name in enumerate(self.label_encoder.classes_)
        }
        self.is_fitted = True

        logger.info("Label mapping established: %s", self.label_mapping)
        return X_scaled, y_encoded

    def export_metadata(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """Export preprocessing parameters, feature list, and label encodings to JSON.

        Args:
            filepath: Destination path for the metadata JSON file.

        Returns:
            Dictionary of exported metadata.
        """
        if not self.is_fitted:
            raise RuntimeError("Cannot export metadata before fitting preprocessor.")

        meta = {
            "dataset_name": "CICIDS2017",
            "mode": "demo",
            "feature_count": len(self.feature_names),
            "features": self.feature_names,
            "classes": [str(c) for c in self.label_encoder.classes_],
            "label_mapping": self.label_mapping,
            "scaler_mean": [float(m) for m in self.scaler.mean_],
            "scaler_scale": [float(s) for s in self.scaler.scale_],
            "scaler_variance": [float(v) for v in self.scaler.var_],
        }

        dest = Path(filepath)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        logger.info("Preprocessing metadata exported to %s", dest)
        return meta

