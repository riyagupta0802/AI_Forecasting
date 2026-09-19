"""Data Cleaning Module for HEX HIVE Preprocessing Pipeline.

Handles deduplication, infinite value correction (e.g. division by zero in Flow Bytes/s),
missing value imputation, and feature/label separation without data leakage.
"""

from typing import Tuple, Dict, Any
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger("HEX_HIVE.Cleaner")


def clean_network_data(
    df: pd.DataFrame,
    target_column: str = "Label"
) -> Tuple[pd.DataFrame, pd.Series, Dict[str, Any]]:
    """Clean raw network traffic dataset and split into features and targets.

    Args:
        df: Input DataFrame with normalized column names.
        target_column: Name of the classification label column.

    Returns:
        Tuple containing:
            - X: Cleaned numeric feature DataFrame.
            - y: Cleaned target Series.
            - stats: Dictionary with cleaning metrics for auditability.
    """
    initial_rows = len(df)
    stats: Dict[str, Any] = {
        "initial_rows": initial_rows,
        "duplicates_removed": 0,
        "inf_values_replaced": 0,
        "nan_values_imputed": 0,
        "final_rows": 0,
    }

    # 1. Deduplication
    df_clean = df.drop_duplicates().copy()
    stats["duplicates_removed"] = initial_rows - len(df_clean)
    if stats["duplicates_removed"] > 0:
        logger.info("Removed %d duplicate rows.", stats["duplicates_removed"])

    # 2. Separate target label if present to avoid data leakage
    if target_column in df_clean.columns:
        # Drop rows where target itself is null
        valid_labels = df_clean[target_column].notna()
        df_clean = df_clean[valid_labels].copy()
        y = df_clean[target_column].astype(str)
        X = df_clean.drop(columns=[target_column]).copy()
    else:
        logger.warning("Target column '%s' not found. Returning None for targets.", target_column)
        y = pd.Series(["UNKNOWN"] * len(df_clean), index=df_clean.index)
        X = df_clean.copy()

    # 3. Handle infinite values in numeric columns (common in CICIDS2017 Flow Bytes/s)
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    inf_count = 0
    for col in numeric_cols:
        is_inf = np.isinf(X[col])
        count = int(is_inf.sum())
        if count > 0:
            inf_count += count
            X.loc[is_inf, col] = np.nan
    stats["inf_values_replaced"] = inf_count
    if inf_count > 0:
        logger.info("Replaced %d infinite values with NaN across numeric features.", inf_count)

    # 4. Handle missing values (NaN) with median imputation per feature column
    nan_count = int(X[numeric_cols].isna().sum().sum())
    stats["nan_values_imputed"] = nan_count
    if nan_count > 0:
        logger.info("Imputing %d NaN values using column medians.", nan_count)
        for col in numeric_cols:
            if X[col].isna().any():
                median_val = X[col].median()
                if pd.isna(median_val):
                    median_val = 0.0
                X[col] = X[col].fillna(median_val)

    # Drop any non-numeric leftover metadata features (e.g. flow IDs or timestamps if present)
    non_numeric_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()
    if non_numeric_cols:
        logger.info("Dropping non-numeric flow identifier columns: %s", non_numeric_cols)
        X = X.drop(columns=non_numeric_cols)

    stats["final_rows"] = len(X)
    stats["feature_count"] = len(X.columns)

    logger.info(
        "Data cleaning completed. Rows: %d -> %d | Features retained: %d",
        initial_rows,
        len(X),
        len(X.columns),
    )

    return X, y, stats

