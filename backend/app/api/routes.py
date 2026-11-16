"""API routes for DataSense AI."""

import os
import uuid
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
import pandas as pd
import numpy as np

from app.config import settings
from app.data_engine.loader import load_dataset
from app.data_engine.cleaner import clean_dataset
from app.data_engine.profiler import profile_dataset
from app.tools.visualization_tools import generate_histogram, generate_correlation_heatmap
from app.tools.analysis_tools import calculate_summary_statistics, calculate_correlation_matrix

router = APIRouter(prefix="/api/v1", tags=["DataSense AI API"])

# In-memory session store for datasets
DATASETS: Dict[str, Dict[str, Any]] = {}


class QueryPayload(BaseModel):
    query: str
    dataset_id: Optional[str] = None


def _format_preview(df: pd.DataFrame, n: int = 15) -> List[Dict[str, Any]]:
    """Sanitize and format DataFrame head for JSON serialization."""
    preview_df = df.head(n).copy()
    records = []
    for row in preview_df.to_dict(orient="records"):
        clean_row = {}
        for k, v in row.items():
            if pd.isna(v):
                clean_row[k] = None
            elif isinstance(v, (np.integer, int)):
                clean_row[k] = int(v)
            elif isinstance(v, (np.floating, float)):
                clean_row[k] = round(float(v), 4)
            else:
                clean_row[k] = str(v)
        records.append(clean_row)
    return records


@router.get("/status")
def get_api_status() -> Dict[str, Any]:
    """Retrieve detailed backend status and identify implemented vs pending features."""
    return {
        "status": "online",
        "service": "DataSense AI REST API",
        "version": "0.1.0",
        "current_stage": "Step 3 — Interactive Ingestion & EDA Engine",
        "loaded_datasets_count": len(DATASETS),
        "implemented_features": [
            "FastAPI Application Scaffolding",
            "Root Welcome Endpoint (GET /)",
            "Health Check Endpoint (GET /health)",
            "Live Dataset Ingestion (.csv, .xlsx, .xls) (POST /api/v1/datasets/upload)",
            "Automated EDA Profiler & Summary Statistics",
            "Automated Data Cleaning (POST /api/v1/datasets/{id}/clean)",
            "Dynamic Chart Generation (Histograms & Correlation Heatmaps)",
            "Conversational Data Agent Queries (POST /api/v1/agent/query)",
            "Swagger / OpenAPI Interactive Documentation (/docs)",
        ],
    }


@router.post("/datasets/upload")
async def upload_dataset_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload and process CSV or Excel datasets with automated profiling and chart generation."""
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a .csv, .xlsx, or .xls file.",
        )

    dataset_id = uuid.uuid4().hex[:12]
    safe_filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", file.filename)
    saved_path = settings.UPLOAD_DIR / f"{dataset_id}_{safe_filename}"

    # Save uploaded file
    try:
        content = await file.read()
        with open(saved_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Load into Pandas
    try:
        df = load_dataset(saved_path)
    except Exception as e:
        if saved_path.exists():
            saved_path.unlink()
        raise HTTPException(status_code=400, detail=f"Could not parse tabular dataset: {str(e)}")

    # Perform EDA Profiling
    profile = profile_dataset(df)
    preview = _format_preview(df, 15)

    # Generate visualizations
    charts = []
    numeric_cols = list(df.select_dtypes(include=["number"]).columns)

    # Correlation Heatmap
    if len(numeric_cols) >= 2:
        heatmap_path = generate_correlation_heatmap(df)
        if heatmap_path:
            charts.append({
                "type": "correlation_heatmap",
                "title": "Feature Correlation Heatmap",
                "url": f"/charts/{Path(heatmap_path).name}",
            })

    # Distribution Histograms for top 3 numeric columns
    for col in numeric_cols[:3]:
        hist_path = generate_histogram(df, col)
        if hist_path:
            charts.append({
                "type": "histogram",
                "column": col,
                "title": f"Distribution of {col}",
                "url": f"/charts/{Path(hist_path).name}",
            })

    # Store in memory
    DATASETS[dataset_id] = {
        "dataset_id": dataset_id,
        "filename": file.filename,
        "file_path": str(saved_path),
        "df": df,
        "profile": profile,
        "preview": preview,
        "charts": charts,
        "numeric_columns": numeric_cols,
        "all_columns": list(df.columns),
    }

    return {
        "success": True,
        "dataset_id": dataset_id,
        "filename": file.filename,
        "shape": [int(df.shape[0]), int(df.shape[1])],
        "columns": list(df.columns),
        "profile": profile,
        "preview": preview,
        "charts": charts,
        "message": f"Successfully ingested {file.filename} with {df.shape[0]} rows and {df.shape[1]} columns.",
    }


@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: str) -> Dict[str, Any]:
    """Retrieve metadata, profile, and preview of an uploaded dataset."""
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Dataset with ID '{dataset_id}' not found.")

    ds = DATASETS[dataset_id]
    df = ds["df"]
    return {
        "dataset_id": dataset_id,
        "filename": ds["filename"],
        "shape": [int(df.shape[0]), int(df.shape[1])],
        "columns": ds["all_columns"],
        "numeric_columns": ds["numeric_columns"],
        "profile": ds["profile"],
        "preview": ds["preview"],
        "charts": ds["charts"],
    }


@router.post("/datasets/{dataset_id}/clean")
def clean_dataset_endpoint(dataset_id: str) -> Dict[str, Any]:
    """Clean the specified dataset (deduplicate, strip whitespace, normalize headers)."""
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Dataset with ID '{dataset_id}' not found.")

    ds = DATASETS[dataset_id]
    cleaned_df, report = clean_dataset(ds["df"])

    # Update stored dataset
    ds["df"] = cleaned_df
    ds["profile"] = profile_dataset(cleaned_df)
    ds["preview"] = _format_preview(cleaned_df, 15)
    ds["all_columns"] = list(cleaned_df.columns)
    ds["numeric_columns"] = list(cleaned_df.select_dtypes(include=["number"]).columns)

    return {
        "success": True,
        "dataset_id": dataset_id,
        "cleaning_report": report,
        "new_shape": [int(cleaned_df.shape[0]), int(cleaned_df.shape[1])],
        "profile": ds["profile"],
        "preview": ds["preview"],
        "message": "Dataset successfully cleaned and normalized.",
    }


@router.post("/agent/query")
def agent_query(payload: QueryPayload) -> Dict[str, Any]:
    """Answer natural language and analytical questions about the active dataset."""
    query = payload.query.strip()
    dataset_id = payload.dataset_id

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # If no dataset specified, pick the most recent one if available
    if not dataset_id and DATASETS:
        dataset_id = list(DATASETS.keys())[-1]

    q_lower = query.lower()

    if not dataset_id or dataset_id not in DATASETS:
        # Conversational fallback when no dataset is loaded
        if any(w in q_lower for w in ["hi", "hello", "hey", "namaste", "halo"]):
            resp = (
                "👋 Hello! I am your **DataSense AI Assistant**.\n\n"
                "I can help you analyze CSV and Excel datasets, clean data, create charts (histograms, correlation heatmaps), "
                "and answer deep statistical questions.\n\n"
                "👉 *Upload a CSV or Excel file using the uploader below to begin analyzing!*"
            )
        elif any(w in q_lower for w in ["help", "what can you do", "features", "kaam", "kya kar"]):
            resp = (
                "Here is what DataSense AI can do for you:\n"
                "1. 📥 **Automated Ingestion:** Fast loading of `.csv`, `.xlsx`, and `.xls` files.\n"
                "2. 🧹 **Data Cleaning:** Removing duplicates, trimming whitespace, normalizing columns.\n"
                "3. 📊 **Exploratory Data Analysis:** Profiling null counts, unique frequencies, min/mean/max stats.\n"
                "4. 📈 **Headless Visualizations:** Generating correlation heatmaps and distribution histograms.\n"
                "5. 💬 **Conversational Queries:** Answering complex questions about your data in plain English or Hinglish!\n\n"
                "Try uploading a dataset to see it in action."
            )
        elif any(w in q_lower for w in ["sample", "demo", "test"]):
            resp = (
                "💡 You can test the platform with sample data right now! "
                "A sample sales dataset is located at `sample_data/sample_sales_dataset.csv`. "
                "Upload it using the drag & drop area to explore instant charts and metrics."
            )
        else:
            resp = (
                f"I received your question: \"{query}\".\n\n"
                "To give you exact calculations, please upload a CSV or Excel file using the workspace below. "
                "Once loaded, I will profile every column and answer your questions directly!"
            )
        return {
            "query": query,
            "status": "assistant_guidance",
            "response": resp,
        }

    # Intelligent analytical rules and insights
    insights = []
    numeric_df = df.select_dtypes(include=["number"])

    if any(k in q_lower for k in ["row", "size", "shape", "length", "how many", "count"]):
        insights.append(f"The dataset contains **{len(df):,} rows** and **{len(df.columns)} columns**.")

    if any(k in q_lower for k in ["null", "missing", "na", "empty"]):
        null_counts = df.isnull().sum()
        total_nulls = int(null_counts.sum())
        if total_nulls == 0:
            insights.append("Good news! There are **0 missing values** across all columns in this dataset.")
        else:
            cols_with_nulls = {k: int(v) for k, v in null_counts.items() if v > 0}
            insights.append(f"Found a total of **{total_nulls:,} missing values**. Affected columns: {cols_with_nulls}")

    if any(k in q_lower for k in ["average", "mean", "avg"]):
        if not numeric_df.empty:
            means = {col: round(float(numeric_df[col].mean()), 2) for col in numeric_df.columns[:5]}
            insights.append(f"Averages for key numeric features: {means}")

    if any(k in q_lower for k in ["highest", "maximum", "max"]):
        if not numeric_df.empty:
            maxes = {col: round(float(numeric_df[col].max()), 2) for col in numeric_df.columns[:5]}
            insights.append(f"Maximum values for numeric columns: {maxes}")

    if any(k in q_lower for k in ["lowest", "minimum", "min"]):
        if not numeric_df.empty:
            mins = {col: round(float(numeric_df[col].min()), 2) for col in numeric_df.columns[:5]}
            insights.append(f"Minimum values for numeric columns: {mins}")

    if any(k in q_lower for k in ["column", "feature", "attribute", "header"]):
        insights.append(f"Available columns ({len(df.columns)}): `{', '.join(list(df.columns))}`")

    if any(k in q_lower for k in ["corr", "relationship", "relation"]):
        if len(numeric_df.columns) >= 2:
            corr = numeric_df.corr()
            top_pairs = []
            for i in range(len(corr.columns)):
                for j in range(i + 1, len(corr.columns)):
                    c1, c2 = corr.columns[i], corr.columns[j]
                    val = corr.iloc[i, j]
                    if not pd.isna(val):
                        top_pairs.append((c1, c2, float(val)))
            top_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
            if top_pairs:
                c1, c2, val = top_pairs[0]
                insights.append(f"Strongest feature correlation: **{c1}** & **{c2}** with Pearson r = **{val:.3f}**.")

    if not insights:
        # General summary response
        num_cols_str = ", ".join(list(df.columns[:6])) + ("..." if len(df.columns) > 6 else "")
        insights.append(
            f"Dataset Summary for '{ds['filename']}':\n"
            f"- Total records: {len(df):,}\n"
            f"- Features ({len(df.columns)}): {num_cols_str}\n"
            f"- Numeric features: {len(numeric_df.columns)}\n"
            f"- Missing values: {int(df.isnull().sum().sum()):,}\n"
            "You can ask me about specific columns, averages, correlations, missing values, or highest/lowest values!"
        )

    response_text = "\n\n".join(insights)

    return {
        "query": query,
        "dataset_id": dataset_id,
        "filename": ds["filename"],
        "status": "completed",
        "response": response_text,
    }
