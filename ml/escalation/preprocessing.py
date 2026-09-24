"""Temporal Preprocessing and Velocity Extraction Utilities for HEX HIVE Phase 7.

Extracts flow duration, packet arrival rates, and inter-arrival time metrics
to construct flow velocity indexes for time-to-escalation regression and modeling.
"""

from pathlib import Path
from typing import Dict, List, Any, Union, Tuple, Optional
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "ml" / "data" / "processed"

# Primary flow timing and velocity columns from CICIDS2017 schema
TEMPORAL_FEATURE_COLUMNS = [
    "Flow Duration",
    "Flow IAT Mean",
    "Flow IAT Std",
    "Flow IAT Max",
    "Flow IAT Min",
    "Fwd IAT Total",
    "Fwd IAT Mean",
    "Bwd IAT Total",
    "Bwd IAT Mean",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Active Mean",
    "Idle Mean",
]


def extract_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and validate temporal flow duration and velocity features.

    Args:
        df: Input DataFrame with normalized column names.

    Returns:
        DataFrame containing available numeric temporal features with finite values.
    """
    available_cols = [c for c in TEMPORAL_FEATURE_COLUMNS if c in df.columns]
    if not available_cols:
        # Fallback to whatever numeric columns match duration/rate patterns
        available_cols = [
            c for c in df.columns
            if any(k in c.lower() for k in ["dur", "iat", "pkt", "byte", "act", "idl"])
        ]

    temp_df = df[available_cols].copy()

    # Replace infinities and NaNs with robust statistical medians
    for col in temp_df.columns:
        temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
        temp_df[col] = temp_df[col].replace([np.inf, -np.inf], np.nan)
        median_val = temp_df[col].median()
        if pd.isna(median_val):
            median_val = 0.0
        temp_df[col] = temp_df[col].fillna(median_val)

    return temp_df


def compute_velocity_index(row: Union[pd.Series, Dict[str, float]]) -> float:
    """Calculate normalized telemetry velocity index V in range [0.5, 2.5].

    Higher packet velocity and byte rates indicate aggressive attack execution,
    compressing the time until full escalation occurs.
    """
    try:
        pkts_sec = float(row.get("Flow Packets/s", 1.0))
        duration = float(row.get("Flow Duration", 1000.0))
        fwd_pkts = float(row.get("Total Fwd Packets", 1.0))

        # Base logarithmic scaling of packet intensity
        intensity = np.log1p(max(0.0, pkts_sec)) + np.log1p(max(0.0, fwd_pkts))
        norm_velocity = np.clip(1.0 + (intensity - 3.0) * 0.25, 0.5, 2.5)
        return float(norm_velocity)
    except Exception:
        return 1.0

