"""API routes for DataSense AI."""

import uuid
from pathlib import Path
from typing import Dict, Any, Optional

import aiofiles
from fastapi import APIRouter, UploadFile, File, Query, HTTPException

from app.config import settings
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/v1", tags=["DataSense AI API"])
analysis_service = AnalysisService()


@router.get("/status")
def get_api_status() -> Dict[str, Any]:
    """Retrieve detailed backend status and identify implemented vs pending features."""
    return {
        "status": "online",
        "service": "DataSense AI REST API",
        "version": "0.2.0",
        "current_stage": "Step 2 Complete — Ingestion, Cleaning & EDA Engine Integrated",
        "implemented_features": [
            "FastAPI Application Scaffolding & CORS Protection",
            "Root Welcome Endpoint (GET /) & Health Check (GET /health)",
            "Dataset Ingestion Pipeline (POST /api/v1/datasets/upload for CSV, XLSX, XLS)",
            "Automated Data Cleaning (Whitespace stripping, duplicate removal, column normalization)",
            "Exploratory Data Analysis Profiler (Dtypes, null metrics, stats & JSON preview samples)",
            "Statistical Analysis Tools (Descriptive metrics & Pearson correlation matrix)",
            "Demo Dataset Generator & Inspection Endpoint (GET /api/v1/datasets/demo)",
            "Swagger / OpenAPI Interactive Documentation (/docs)",
        ],
        "unimplemented_features": [
            {
                "name": "Dynamic Matplotlib Visualizations",
                "description": "Headless generation of distribution plots, correlation heatmaps, and chart exports",
                "status": "pending_implementation",
            },
            {
                "name": "LangGraph Autonomous Agent Orchestrator",
                "description": "Cyclic state machine for multi-step data reasoning, Python code generation, and result synthesis",
                "status": "pending_implementation",
            },
            {
                "name": "PostgreSQL Database Persistence",
                "description": "SQLAlchemy session management, dataset registry, and analysis history persistence",
                "status": "pending_implementation",
            },
            {
                "name": "Interactive React Dashboard",
                "description": "Dataset table preview, visual charts gallery, and conversational agent chat interface",
                "status": "pending_implementation",
            },
        ],
    }


@router.post("/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    auto_clean: bool = Query(True, description="Automatically clean column names, strip whitespace, and drop duplicate rows"),
) -> Dict[str, Any]:
    """Uploads a CSV or Excel dataset, executes automated cleaning, and computes full EDA profiling."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a valid filename.")

    filename_lower = file.filename.lower()
    if not filename_lower.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a .csv, .xlsx, or .xls file.",
        )

    # Generate a unique storage identifier
    file_id = uuid.uuid4().hex[:12]
    safe_name = "".join(c for c in file.filename if c.isalnum() or c in (".", "_", "-")).strip()
    stored_filename = f"{file_id}_{safe_name}"
    stored_path = settings.UPLOAD_DIR / stored_filename

    # Stream file to disk
    try:
        async with aiofiles.open(stored_path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):  # 1MB buffer
                await out_file.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    # Process dataset through the engine
    try:
        result = analysis_service.process_uploaded_dataset(stored_path, auto_clean=auto_clean)
        file_size = stored_path.stat().st_size
    except Exception as e:
        # Clean up temporary file on failure
        if stored_path.exists():
            stored_path.unlink()
        raise HTTPException(status_code=422, detail=f"Failed to process and profile dataset: {str(e)}")

    return {
        "status": "success",
        "dataset_id": file_id,
        "filename": stored_filename,
        "original_name": file.filename,
        "file_size_bytes": file_size,
        "dataset_path": str(stored_path),
        "data": result,
    }


@router.get("/datasets/demo")
def get_demo_dataset() -> Dict[str, Any]:
    """Creates or returns a pre-configured sales demonstration dataset for instant testing."""
    import pandas as pd
    import numpy as np

    demo_path = settings.UPLOAD_DIR / "demo_sales_dataset.csv"
    if not demo_path.exists():
        np.random.seed(42)
        n = 100
        products = ["Enterprise Cloud", "Standard SaaS", "Analytics Add-on", "Security Suite", "Premium Support"]
        regions = ["North America", "Europe", "Asia-Pacific", "Latin America"]

        demo_df = pd.DataFrame({
            "Transaction ID": [f"TX-{1000 + i}" for i in range(n)],
            "Product": np.random.choice(products, size=n),
            "Region": np.random.choice(regions, size=n),
            "Units Sold": np.random.randint(1, 50, size=n),
            "Unit Price": np.random.choice([99.0, 199.0, 499.0, 999.0, 1499.0], size=n),
            "Discount Pct": np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20], size=n),
            "Customer Rating": np.random.choice([3.5, 4.0, 4.5, 5.0, np.nan], size=n),
        })
        demo_df["Total Revenue"] = demo_df["Units Sold"] * demo_df["Unit Price"] * (1 - demo_df["Discount Pct"])
        demo_df.to_csv(demo_path, index=False)

    result = analysis_service.process_uploaded_dataset(demo_path, auto_clean=True)
    return {
        "status": "success",
        "dataset_id": "demo",
        "filename": demo_path.name,
        "original_name": "demo_sales_dataset.csv",
        "file_size_bytes": demo_path.stat().st_size,
        "dataset_path": str(demo_path),
        "data": result,
    }


@router.get("/datasets/preview")
def preview_dataset(dataset_id: str) -> Dict[str, Any]:
    """Retrieves profiling metadata and sample rows for an existing uploaded dataset."""
    matching_files = list(settings.UPLOAD_DIR.glob(f"{dataset_id}*"))
    if not matching_files:
        raise HTTPException(status_code=404, detail=f"Dataset with ID '{dataset_id}' not found.")

    target_file = matching_files[0]
    result = analysis_service.inspect_dataset(target_file)
    return {
        "status": "success",
        "dataset_id": dataset_id,
        "filename": target_file.name,
        "dataset_path": str(target_file),
        "data": result,
    }


@router.post("/agent/query")
def agent_query_stub(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Placeholder endpoint for conversational queries to the LangGraph agent."""
    query = payload.get("query", "")
    return {
        "query": query,
        "status": "received",
        "message": "Agent orchestration workflow initialized. LangGraph execution node pending integration.",
    }
