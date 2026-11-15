"""API routes for DataSense AI."""

import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List

import aiofiles
from fastapi import APIRouter, UploadFile, File, Query, HTTPException, Body, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.services.analysis_service import AnalysisService
from app.database.connection import get_db
from app.database.models import DatasetRecord, AnalysisSession

router = APIRouter(prefix="/api/v1", tags=["DataSense AI API"])
analysis_service = AnalysisService()


@router.get("/status")
def get_api_status() -> Dict[str, Any]:
    """Retrieve detailed backend status and identify implemented feature matrix."""
    return {
        "status": "online",
        "service": "DataSense AI REST API",
        "version": "1.0.0",
        "current_stage": "All Milestones Operational (100% Complete)",
        "implemented_features": [
            "FastAPI Application Scaffolding & CORS Protection",
            "Root Welcome Endpoint (GET /) & Health Check (GET /health)",
            "Dataset Ingestion Pipeline (POST /api/v1/datasets/upload for CSV, XLSX, XLS)",
            "Automated Data Cleaning (Whitespace stripping, duplicate removal, column normalization)",
            "Exploratory Data Analysis Profiler (Dtypes, null metrics, stats & JSON preview samples)",
            "Statistical Analysis Tools (Descriptive metrics & Pearson correlation matrix)",
            "Dynamic Matplotlib Visualizations (Distribution histograms, heatmaps, scatter, bar charts)",
            "Headless Image Serving Engine (GET /api/v1/charts/{filename})",
            "On-Demand Custom Chart Generation (POST /api/v1/charts/generate)",
            "Demo Dataset Generator with Auto-Charts (GET /api/v1/datasets/demo)",
            "LangGraph Autonomous Agent Orchestrator (Planning, Code Gen, Sandbox Exec, Synthesis)",
            "Conversational Agent Query Endpoint (POST /api/v1/agent/query)",
            "Relational Database Persistence (SQLAlchemy & SQLite/PostgreSQL Fallback)",
            "Dataset & Session History Endpoints (GET /api/v1/datasets, GET /api/v1/sessions)",
            "Interactive Studio React Dashboard (File Ingestion, Table Preview, Visuals, Agent Chat)",
            "Swagger / OpenAPI Interactive Documentation (/docs)",
        ],
        "unimplemented_features": [],
    }


@router.post("/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    auto_clean: bool = Query(True, description="Automatically clean column names, strip whitespace, and drop duplicate rows"),
    generate_charts: bool = Query(True, description="Automatically generate initial starter charts"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Uploads a CSV or Excel dataset, executes automated cleaning, computes EDA profiling, and saves to database."""
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
        result = analysis_service.process_uploaded_dataset(
            stored_path,
            auto_clean=auto_clean,
            generate_charts=generate_charts,
        )
        file_size = stored_path.stat().st_size
    except Exception as e:
        if stored_path.exists():
            stored_path.unlink()
        raise HTTPException(status_code=422, detail=f"Failed to process and profile dataset: {str(e)}")

    # Persist in Database
    try:
        file_ext = stored_path.suffix.lstrip(".").lower()
        record = DatasetRecord(
            dataset_uid=file_id,
            filename=stored_filename,
            original_name=file.filename,
            file_type=file_ext,
            file_size_bytes=file_size,
            row_count=result.get("profile", {}).get("rows"),
            column_count=result.get("profile", {}).get("columns"),
            storage_path=str(stored_path),
            profile_summary=result.get("profile"),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        record_id = record.id
    except Exception:
        db.rollback()
        record_id = None

    return {
        "status": "success",
        "dataset_id": file_id,
        "database_id": record_id,
        "filename": stored_filename,
        "original_name": file.filename,
        "file_size_bytes": file_size,
        "dataset_path": str(stored_path),
        "data": result,
    }


@router.get("/datasets")
def list_datasets(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Retrieves all registered datasets from database persistence."""
    try:
        records = db.query(DatasetRecord).order_by(DatasetRecord.created_at.desc()).all()
        datasets_list = [
            {
                "id": r.id,
                "dataset_uid": r.dataset_uid,
                "filename": r.filename,
                "original_name": r.original_name,
                "file_type": r.file_type,
                "file_size_bytes": r.file_size_bytes,
                "row_count": r.row_count,
                "column_count": r.column_count,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ]
        return {"status": "success", "count": len(datasets_list), "datasets": datasets_list}
    except Exception as e:
        return {"status": "success", "count": 0, "datasets": [], "error": str(e)}


@router.get("/datasets/demo")
def get_demo_dataset(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Creates or returns a pre-configured sales demonstration dataset with auto-generated charts."""
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

    result = analysis_service.process_uploaded_dataset(demo_path, auto_clean=True, generate_charts=True)

    # Persist or update Demo record in database
    try:
        existing = db.query(DatasetRecord).filter(DatasetRecord.dataset_uid == "demo").first()
        if not existing:
            demo_record = DatasetRecord(
                dataset_uid="demo",
                filename=demo_path.name,
                original_name="demo_sales_dataset.csv",
                file_type="csv",
                file_size_bytes=demo_path.stat().st_size,
                row_count=result.get("profile", {}).get("rows"),
                column_count=result.get("profile", {}).get("columns"),
                storage_path=str(demo_path),
                profile_summary=result.get("profile"),
            )
            db.add(demo_record)
            db.commit()
    except Exception:
        db.rollback()

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


@router.get("/charts/{filename}")
def get_chart_image(filename: str):
    """Serves generated Matplotlib visualization images with path traversal protection."""
    safe_filename = Path(filename).name
    filepath = settings.CHARTS_DIR / safe_filename

    if not filepath.exists() or not filepath.is_file():
        raise HTTPException(status_code=404, detail=f"Chart '{safe_filename}' not found.")

    return FileResponse(filepath, media_type="image/png")


@router.post("/charts/generate")
def generate_custom_chart(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """Generates custom on-demand chart (histogram, heatmap, scatter, bar) for an existing dataset."""
    dataset_id = payload.get("dataset_id")
    chart_type = payload.get("chart_type")
    params = payload.get("params", {})

    if not dataset_id or not chart_type:
        raise HTTPException(status_code=400, detail="Missing required fields: dataset_id and chart_type are required.")

    matching_files = list(settings.UPLOAD_DIR.glob(f"{dataset_id}*"))
    if not matching_files:
        raise HTTPException(status_code=404, detail=f"Dataset with ID '{dataset_id}' not found.")

    target_file = matching_files[0]
    try:
        chart_info = analysis_service.generate_custom_chart(target_file, chart_type, params)
        if not chart_info:
            raise HTTPException(
                status_code=422,
                detail=f"Could not generate chart of type '{chart_type}' with specified parameters.",
            )
        return {
            "status": "success",
            "dataset_id": dataset_id,
            "chart": chart_info,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate visualization: {str(e)}")


@router.post("/agent/query")
def agent_query(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Dispatches a natural-language query to the autonomous LangGraph data analysis agent."""
    query = payload.get("query", "").strip()
    dataset_id = payload.get("dataset_id")

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    target_file = None
    db_dataset_id = None

    if dataset_id:
        matching_files = list(settings.UPLOAD_DIR.glob(f"{dataset_id}*"))
        if matching_files:
            target_file = matching_files[0]

        # Lookup database record if exists
        try:
            d_rec = db.query(DatasetRecord).filter(
                (DatasetRecord.dataset_uid == dataset_id) | (DatasetRecord.id == int(dataset_id) if str(dataset_id).isdigit() else False)
            ).first()
            if d_rec:
                db_dataset_id = d_rec.id
                if not target_file and Path(d_rec.storage_path).exists():
                    target_file = Path(d_rec.storage_path)
        except Exception:
            pass

    # Fallback to demo file if no dataset provided or found
    if not target_file:
        demo_candidate = settings.UPLOAD_DIR / "demo_sales_dataset.csv"
        if demo_candidate.exists():
            target_file = demo_candidate

    response = analysis_service.run_agent_query(
        user_query=query,
        dataset_path=str(target_file) if target_file else None,
    )

    # Persist analysis session to database
    session_id = None
    try:
        session_record = AnalysisSession(
            dataset_id=db_dataset_id,
            dataset_uid=dataset_id or "demo",
            user_query=query,
            agent_plan=response.get("plan"),
            generated_code=response.get("generated_code"),
            status=response.get("status", "completed"),
            response_summary=response.get("final_response"),
            chart_path=response.get("chart_paths")[0] if response.get("chart_paths") else None,
            chart_paths=response.get("chart_urls"),
        )
        db.add(session_record)
        db.commit()
        db.refresh(session_record)
        session_id = session_record.id
    except Exception:
        db.rollback()

    return {
        "status": response.get("status", "completed"),
        "session_id": session_id,
        "dataset_id": dataset_id,
        "query": query,
        "plan": response.get("plan", []),
        "generated_code": response.get("generated_code", ""),
        "execution_result": response.get("execution_result"),
        "stdout_output": response.get("stdout_output", ""),
        "chart_urls": response.get("chart_urls", []),
        "final_response": response.get("final_response", ""),
        "error": response.get("error"),
    }


@router.get("/sessions")
def list_sessions(
    dataset_id: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieves previous agent analysis sessions from database persistence."""
    try:
        q = db.query(AnalysisSession)
        if dataset_id:
            q = q.filter(AnalysisSession.dataset_uid == dataset_id)
        records = q.order_by(AnalysisSession.created_at.desc()).limit(50).all()

        sessions = [
            {
                "id": s.id,
                "dataset_uid": s.dataset_uid,
                "user_query": s.user_query,
                "agent_plan": s.agent_plan,
                "generated_code": s.generated_code,
                "status": s.status,
                "response_summary": s.response_summary,
                "chart_paths": s.chart_paths or [],
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in records
        ]
        return {"status": "success", "count": len(sessions), "sessions": sessions}
    except Exception as e:
        return {"status": "success", "count": 0, "sessions": [], "error": str(e)}
