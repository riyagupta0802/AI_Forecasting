"""Dataset Ingestion, Validation, and Multi-Phase Analysis Routes for NETORACLE.

Provides endpoints for:
- POST /api/analyze          (Upload and analyze CSV dataset through Phase 5–11)
- POST /api/analyze/validate (Validate dataset column schema without running full pipeline)
- GET  /api/analyze/sample-csv (Download compatible local test dataset for user testing)
"""

import io
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
import pandas as pd

from app.schemas.analyze import (
    AnalyzeResponse,
    AnalyzeJsonRequest,
    DatasetValidationResult,
)
from app.services.dataset_analyzer import dataset_analyzer

logger = logging.getLogger("NETORACLE.Routes.Analyze")
router = APIRouter(prefix="/analyze", tags=["Dataset Analysis"])

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEMO_DATASET_PATH = REPO_ROOT / "datasets" / "netoracle_demo_traffic.csv"
SAMPLE_CSV_PATH = DEMO_DATASET_PATH if DEMO_DATASET_PATH.is_file() else (REPO_ROOT / "ml" / "data" / "sample" / "cicids2017_sample.csv")


@router.post(
    "/validate",
    response_model=DatasetValidationResult,
    summary="Validate Network Traffic Dataset Columns",
    description="Inspects CSV columns, checks compatibility against the 78 required Phase 5 model features, and reports missing/extra columns.",
)
async def validate_dataset(
    request: Request,
    file: Optional[UploadFile] = File(None),
    use_local_test: bool = Form(False),
) -> DatasetValidationResult:
    """Validate dataset headers against required feature schema."""
    try:
        is_local = use_local_test or request.query_params.get("use_local_test", "").lower() in ("true", "1")
        if is_local:
            if not SAMPLE_CSV_PATH.is_file():
                raise HTTPException(status_code=404, detail="Local sample dataset not found.")
            df = pd.read_csv(SAMPLE_CSV_PATH, nrows=5)
            filename = SAMPLE_CSV_PATH.name
        elif file is not None:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Uploaded file is empty.")
            df = pd.read_csv(io.BytesIO(content), nrows=5)
            filename = file.filename or "uploaded_dataset.csv"
        else:
            raise HTTPException(
                status_code=400,
                detail="No dataset provided. Please upload a CSV file or set use_local_test=true.",
            )

        res = dataset_analyzer.validate_columns(df, filename=filename)
        return DatasetValidationResult(**res)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Dataset validation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse and validate CSV: {str(e)}",
        )


@router.post(
    "",
    response_model=AnalyzeResponse,
    summary="Ingest and Analyze Network Traffic Dataset",
    description="Accepts an uploaded CSV dataset or local test flag, validates schema, standardizes features, executes Phase 5 Random Forest classification, Phase 6 forecasting, Phase 7 escalation, Phase 8 story, Phase 9 early warnings, Phase 10 recommendations, and Phase 11 SHAP explainability.",
)
async def analyze_traffic_dataset(
    request: Request,
    file: Optional[UploadFile] = File(None),
    use_local_test: bool = Form(False),
) -> AnalyzeResponse:
    """Run full Phase 5–11 analysis pipeline on uploaded dataset."""
    try:
        is_local = use_local_test or request.query_params.get("use_local_test", "").lower() in ("true", "1")
        if is_local:
            if not SAMPLE_CSV_PATH.is_file():
                raise HTTPException(status_code=404, detail="Local sample dataset not found on server.")
            df = pd.read_csv(SAMPLE_CSV_PATH)
            filename = SAMPLE_CSV_PATH.name
            source_type = "Local Test Dataset"
        elif file is not None:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Uploaded file is empty.")
            try:
                df = pd.read_csv(io.BytesIO(content))
            except Exception as pe:
                raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(pe)}")
            filename = file.filename or "uploaded_dataset.csv"
            source_type = "Uploaded Dataset"
        else:
            raise HTTPException(
                status_code=400,
                detail="No dataset supplied. Upload a CSV file or set use_local_test=true.",
            )

        # Validate columns
        val = dataset_analyzer.validate_columns(df, filename=filename)
        if not val["is_compatible"]:
            missing_list = val["missing_features"]
            missing_preview = ", ".join(missing_list[:8])
            if len(missing_list) > 8:
                missing_preview += f" ... (+{len(missing_list) - 8} more)"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dataset is not compatible with the current model. Missing {len(missing_list)} required features: {missing_preview}",
            )

        # Run complete real multi-phase analysis
        analysis_result = dataset_analyzer.analyze_dataset(
            df_or_path=df,
            filename=filename,
            source_type=source_type,
        )

        return AnalyzeResponse(**analysis_result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Dataset analysis failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dataset analysis pipeline failed: {str(e)}",
        )


@router.post(
    "/json",
    response_model=AnalyzeResponse,
    summary="Analyze Dataset via Raw JSON/Text Payload",
    description="Alternative endpoint accepting raw CSV text or triggering local test analysis via JSON body.",
)
async def analyze_traffic_json(payload: AnalyzeJsonRequest) -> AnalyzeResponse:
    """Analyze dataset passed via JSON payload."""
    try:
        if payload.use_local_test or not payload.csv_text:
            if not SAMPLE_CSV_PATH.is_file():
                raise HTTPException(status_code=404, detail="Local sample dataset not found on server.")
            df = pd.read_csv(SAMPLE_CSV_PATH)
            filename = "cicids2017_sample.csv"
            source_type = "Local Test Dataset"
        else:
            df = pd.read_csv(io.StringIO(payload.csv_text))
            filename = payload.filename or "uploaded_dataset.csv"
            source_type = "Uploaded Dataset"

        analysis_result = dataset_analyzer.analyze_dataset(
            df_or_path=df,
            filename=filename,
            source_type=source_type,
        )
        return AnalyzeResponse(**analysis_result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("JSON dataset analysis failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dataset analysis failed: {str(e)}",
        )


@router.get(
    "/sample-csv",
    summary="Download Local Test Dataset (CICIDS2017 Sample)",
    description="Provides direct download of the compatible 500-sample test CSV with 78 numerical features for live testing.",
)
async def download_sample_csv():
    """Download the compatible test dataset CSV."""
    if not SAMPLE_CSV_PATH.is_file():
        raise HTTPException(status_code=404, detail="Sample dataset not found.")
    return FileResponse(
        path=SAMPLE_CSV_PATH,
        filename="cicids2017_sample.csv",
        media_type="text/csv",
    )
