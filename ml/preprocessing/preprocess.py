"""Main Preprocessing Pipeline Runner for HEX HIVE Phase 4.

Coordinates:
    Data Loading -> Cleaning -> Preprocessing / Scaling -> Processed Output Generation

Usage:
    python ml/preprocessing/preprocess.py
"""

import sys
from pathlib import Path

# Add project root to sys.path so ml.preprocessing imports work reliably
current_dir = Path(__file__).resolve().parent
repo_root = current_dir.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from ml.preprocessing.data_loader import load_dataset
from ml.preprocessing.cleaner import clean_network_data
from ml.preprocessing.preprocessor import NetworkFlowPreprocessor


def run_pipeline(
    input_csv: Path = None,
    output_dir: Path = None,
) -> bool:
    """Execute the end-to-end dataset preprocessing pipeline.

    Args:
        input_csv: Path to the raw/sample CSV dataset.
        output_dir: Destination folder for processed datasets.

    Returns:
        True if pipeline succeeded, False otherwise.
    """
    if input_csv is None:
        # Default to sample dataset
        input_csv = repo_root / "ml" / "data" / "sample" / "cicids2017_sample.csv"

    if output_dir is None:
        output_dir = repo_root / "ml" / "data" / "processed"

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("HEX HIVE — Phase 4 Network Traffic Preprocessing Pipeline")
    print("=" * 60)
    print(f"Input Dataset:  {input_csv}")
    print(f"Output Directory: {output_dir}")
    print("-" * 60)

    # 1. Load Data
    try:
        raw_df = load_dataset(input_csv)
    except Exception as e:
        print(f"[ERROR] Failed to load dataset: {e}")
        return False

    # 2. Clean Data
    try:
        X_clean, y_clean, stats = clean_network_data(raw_df, target_column="Label")
    except Exception as e:
        print(f"[ERROR] Failed during data cleaning: {e}")
        return False

    print(f"Initial Records:        {stats['initial_rows']}")
    print(f"Duplicates Removed:     {stats['duplicates_removed']}")
    print(f"Infinite Values Fixed:  {stats['inf_values_replaced']}")
    print(f"Missing Values Imputed: {stats['nan_values_imputed']}")
    print(f"Final Retained Records: {stats['final_rows']}")
    print(f"Total Clean Features:   {stats['feature_count']}")
    print("-" * 60)

    # 3. Preprocess & Scale
    try:
        preprocessor = NetworkFlowPreprocessor()
        X_scaled, y_encoded = preprocessor.fit_transform(X_clean, y_clean)
    except Exception as e:
        print(f"[ERROR] Failed during feature scaling: {e}")
        return False

    # 4. Save Processed Artifacts
    features_path = output_dir / "train_features.csv"
    labels_path = output_dir / "train_labels.csv"
    meta_path = output_dir / "preprocessing_meta.json"

    print("Saving processed data artifacts:")
    X_scaled.to_csv(features_path, index=False)
    print(f"  [OK] Features saved to: {features_path} ({len(X_scaled)} rows, {len(X_scaled.columns)} cols)")

    y_encoded.to_frame().to_csv(labels_path, index=False)
    print(f"  [OK] Labels saved to:   {labels_path} ({len(y_encoded)} rows)")

    meta = preprocessor.export_metadata(meta_path)
    print(f"  [OK] Metadata saved to: {meta_path}")

    print("-" * 60)
    print("Detected Classes & Encoding:")
    for cls_name, code in meta["label_mapping"].items():
        count = int((y_clean == cls_name).sum())
        print(f"  - {cls_name:<12} (Code: {code}) -> {count} instances")

    print("=" * 60)
    print("Phase 4 Preprocessing Pipeline COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)

