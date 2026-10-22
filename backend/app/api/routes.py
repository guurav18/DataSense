"""API routes for DataSense AI."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/api/v1", tags=["DataSense AI API"])


@router.get("/status")
def get_api_status() -> Dict[str, Any]:
    """Retrieve detailed backend status and identify implemented vs pending major features."""
    return {
        "status": "online",
        "service": "DataSense AI REST API",
        "version": "0.1.0",
        "current_stage": "Step 2 — Backend Configuration & Testing",
        "implemented_features": [
            "FastAPI Application Scaffolding",
            "Root Welcome Endpoint (GET /)",
            "Health Check Endpoint (GET /health)",
            "API Status & Feature Matrix (GET /api/v1/status)",
            "CORS Middleware for React/Vite Dev Server (http://localhost:5173)",
            "Swagger / OpenAPI Interactive Documentation (/docs)",
        ],
        "unimplemented_features": [
            {
                "name": "Dataset Ingestion Pipeline",
                "description": "Multipart CSV and Excel dataset uploads with format validation and secure storage",
                "status": "pending_implementation",
            },
            {
                "name": "Automated Data Cleaning",
                "description": "Automated duplicate removal, whitespace stripping, and missing-value imputation",
                "status": "pending_implementation",
            },
            {
                "name": "Exploratory Data Analysis (EDA) Profiler",
                "description": "Comprehensive statistical distributions, column profiling, and schema inference",
                "status": "pending_implementation",
            },
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
        ],
    }


@router.post("/datasets/upload")
async def upload_dataset_stub(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Placeholder endpoint for uploading CSV/Excel datasets.

    Full parsing, validation, and storage pipeline will be implemented in subsequent phases.
    """
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a .csv, .xlsx, or .xls file.",
        )

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "File received (scaffold placeholder). Full processing pipeline pending feature implementation.",
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
