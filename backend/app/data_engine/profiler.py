"""Automated exploratory data analysis (EDA) and profiling module."""

from typing import Dict, Any, List
import math


def profile_dataset(df: Any, sample_size: int = 10) -> Dict[str, Any]:
    """Generates comprehensive exploratory profiling metrics for a Pandas DataFrame.

    Args:
        df: Pandas DataFrame to profile.
        sample_size: Number of preview rows to include.

    Returns:
        Dictionary containing overview metrics, column summaries, numeric statistics, and sample rows.
    """
    try:
        import pandas as pd
        import numpy as np
    except ImportError as e:
        raise RuntimeError("Pandas and NumPy are required for profiling. Please install requirements.txt.") from e

    total_rows, total_cols = df.shape
    columns_info: List[Dict[str, Any]] = []

    for col in df.columns:
        col_series = df[col]
        null_count = int(col_series.isnull().sum())
        null_percentage = round((null_count / total_rows * 100), 2) if total_rows > 0 else 0.0
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
            valid_series = col_series.dropna()
            if not valid_series.empty:
                min_val = valid_series.min()
                max_val = valid_series.max()
                mean_val = valid_series.mean()
                median_val = valid_series.median()
                std_val = valid_series.std() if len(valid_series) > 1 else 0.0

                col_dict["stats"] = {
                    "min": float(min_val) if not pd.isna(min_val) else None,
                    "max": float(max_val) if not pd.isna(max_val) else None,
                    "mean": round(float(mean_val), 4) if not pd.isna(mean_val) else None,
                    "median": round(float(median_val), 4) if not pd.isna(median_val) else None,
                    "std": round(float(std_val), 4) if not pd.isna(std_val) else None,
                }
            else:
                col_dict["stats"] = None

        columns_info.append(col_dict)

    # Format JSON-serializable preview rows
    sample_df = df.head(sample_size).copy()
    sample_rows: List[Dict[str, Any]] = []
    for _, row in sample_df.iterrows():
        clean_row = {}
        for col_name, val in row.items():
            if pd.isna(val) or val is None:
                clean_row[str(col_name)] = None
            elif isinstance(val, (int, float)) and (math.isnan(val) or math.isinf(val)):
                clean_row[str(col_name)] = None
            elif hasattr(val, "item"):  # numpy scalars
                clean_row[str(col_name)] = val.item()
            else:
                clean_row[str(col_name)] = val
        sample_rows.append(clean_row)

    return {
        "rows": total_rows,
        "columns": total_cols,
        "total_cells": total_rows * total_cols,
        "total_nulls": int(df.isnull().sum().sum()),
        "column_names": [str(c) for c in df.columns],
        "columns_info": columns_info,
        "sample_rows": sample_rows,
    }
