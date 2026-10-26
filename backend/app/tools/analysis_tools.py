"""Statistical analysis tools for the DataSense AI agent."""

from typing import Dict, Any, List
import math


def _sanitize_dict_floats(data: Any) -> Any:
    """Recursively replaces NaN and Inf float values with None for clean JSON serialization."""
    if isinstance(data, dict):
        return {k: _sanitize_dict_floats(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_sanitize_dict_floats(v) for v in data]
    elif isinstance(data, float) and (math.isnan(data) or math.isinf(data)):
        return None
    return data


def calculate_summary_statistics(df: Any, columns: List[str] = None) -> Dict[str, Any]:
    """Computes descriptive statistics (count, mean, std, min, 25%, 50%, 75%, max) for numeric columns."""
    try:
        import pandas as pd
    except ImportError as e:
        raise RuntimeError("Pandas is required. Please install requirements.txt.") from e

    target_df = df[columns] if columns else df.select_dtypes(include=["number"])
    if target_df.empty or len(target_df.columns) == 0:
        return {"summary_statistics": {}}

    desc = target_df.describe().to_dict()
    sanitized_desc = _sanitize_dict_floats(desc)
    return {"summary_statistics": sanitized_desc}


def calculate_correlation_matrix(df: Any) -> Dict[str, Any]:
    """Calculates Pearson correlation coefficients among all numerical columns."""
    try:
        import pandas as pd
    except ImportError as e:
        raise RuntimeError("Pandas is required. Please install requirements.txt.") from e

    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty or numeric_df.shape[1] < 2:
        return {"correlation_matrix": {}}

    corr = numeric_df.corr().round(4).to_dict()
    sanitized_corr = _sanitize_dict_floats(corr)
    return {"correlation_matrix": sanitized_corr}
