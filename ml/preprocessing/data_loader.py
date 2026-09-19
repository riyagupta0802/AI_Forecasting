"""Data Loader Module for HEX HIVE Preprocessing Pipeline.

Loads raw or sample network traffic datasets (e.g. CICIDS2017 flow captures)
with path validation, schema normalization, and whitespace cleanup.
"""

from pathlib import Path
from typing import Union
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HEX_HIVE.DataLoader")


def load_dataset(filepath: Union[str, Path]) -> pd.DataFrame:
    """Load a network traffic CSV dataset safely.

    Args:
        filepath: Path to the CSV dataset.

    Returns:
        pd.DataFrame with cleaned column headers.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file is empty or missing required flow data.
    """
    path = Path(filepath)
    if not path.is_file():
        logger.error("Dataset file not found at: %s", path)
        raise FileNotFoundError(f"Dataset file does not exist: {path}")

    logger.info("Loading network traffic dataset from: %s", path)
    df = pd.read_csv(path)

    if df.empty:
        logger.error("Loaded dataset is empty: %s", path)
        raise ValueError(f"Dataset at {path} contains no records.")

    # Strip whitespaces from column headers (critical for CICIDS2017 compatibility)
    original_cols = len(df.columns)
    df.columns = df.columns.str.strip()

    logger.info(
        "Successfully loaded %d records and %d columns. Cleaned column names.",
        len(df),
        original_cols,
    )

    if "Label" in df.columns:
        class_dist = df["Label"].value_counts().to_dict()
        logger.info("Target class distribution: %s", class_dist)
    else:
        logger.warning("No 'Label' column detected in dataset schema.")

    return df

