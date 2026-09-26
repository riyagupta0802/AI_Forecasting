"""Data and Preprocessing Status API Route for NETORACLE Phase 4.

Provides dynamic inspection of dataset ingestion and preprocessing pipeline outputs.
"""

from pathlib import Path
import json
from fastapi import APIRouter
from app.schemas.data import DataStatusResponse

router = APIRouter(prefix="/data", tags=["Dataset & Preprocessing"])

# Resolve path to ml/data relative to repository root
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = BACKEND_DIR.parent
DATA_DIR = REPO_ROOT / "ml" / "data"


def _count_csv_records(file_path: Path) -> int:
    """Count non-empty data lines in a CSV file excluding header."""
    if not file_path.is_file():
        return 0
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.strip() for line in f if line.strip()]
        return max(0, len(lines) - 1)
    except Exception:
        return 0


@router.get(
    "/status",
    response_model=DataStatusResponse,
    summary="Get Dataset & Preprocessing Pipeline Status",
    description="Returns dynamic dataset inventory, preprocessing state, and detected attack classes.",
)
async def get_data_status() -> DataStatusResponse:
    """Dynamically check dataset presence, preprocessing output, and return status."""
    sample_file = DATA_DIR / "sample" / "cicids2017_sample.csv"
    processed_features = DATA_DIR / "processed" / "train_features.csv"
    meta_file = DATA_DIR / "processed" / "preprocessing_meta.json"

    records_available = _count_csv_records(sample_file)
    processed_records = _count_csv_records(processed_features)

    classes_detected = []
    if meta_file.is_file():
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
                classes_detected = meta.get("classes", [])
        except Exception:
            pass

    if not classes_detected and records_available > 0:
        classes_detected = ["BENIGN", "DDoS", "PortScan", "Bot"]

    preprocessing_status = "ready" if processed_records > 0 else "pending"
    overall_status = "ready" if records_available > 0 else "pending"

    return DataStatusResponse(
        status=overall_status,
        dataset="CICIDS2017",
        mode="demo",
        records_available=records_available,
        preprocessing=preprocessing_status,
        processed_records=processed_records,
        classes_detected=classes_detected,
    )

