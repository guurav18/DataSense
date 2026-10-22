"""Automated exploratory data analysis (EDA) and profiling module."""

from typing import Dict, Any


def profile_dataset(df: Any) -> Dict[str, Any]:
    """Generates comprehensive exploratory profiling metrics for a Pandas DataFrame.

    Returns:
        Dictionary containing overview metrics, column summaries, and numeric statistics.
    """
    try:
        import pandas as pd
    except ImportError as e:
        raise RuntimeError("Pandas is required for profiling. Please install requirements.txt.") from e

    total_rows, total_cols = df.shape
    columns_info = []

    for col in df.columns:
        col_series = df[col]
        null_count = int(col_series.isnull().sum())
        null_percentage = round((null_count / total_rows * 100), 2) if total_rows > 0 else 0
        unique_count = int(col_series.nunique())

        col_dict: Dict[str, Any] = {
            "name": str(col),
            "dtype": str(col_series.dtype),
            "null_count": null_count,
            "null_percentage": null_percentage,
            "unique_count": unique_count,
        }

        # Include basic stats if numeric
        if pd.api.types.is_numeric_dtype(col_series):
            col_dict["stats"] = {
                "min": float(col_series.min()) if not col_series.empty and not pd.isna(col_series.min()) else None,
                "max": float(col_series.max()) if not col_series.empty and not pd.isna(col_series.max()) else None,
                "mean": round(float(col_series.mean()), 4) if not col_series.empty and not pd.isna(col_series.mean()) else None,
            }

        columns_info.append(col_dict)

    return {
        "rows": total_rows,
        "columns": total_cols,
        "total_cells": total_rows * total_cols,
        "total_nulls": int(df.isnull().sum().sum()),
        "columns_info": columns_info,
    }
