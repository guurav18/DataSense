"""Statistical analysis tools for the DataSense AI agent."""

from typing import Dict, Any, List


def calculate_summary_statistics(df: Any, columns: List[str] = None) -> Dict[str, Any]:
    """Computes descriptive statistics (count, mean, std, min, 25%, 50%, 75%, max) for numeric columns."""
    try:
        import pandas as pd
    except ImportError as e:
        raise RuntimeError("Pandas is required. Please install requirements.txt.") from e

    target_df = df[columns] if columns else df.select_dtypes(include=["number"])
    if target_df.empty:
        return {"error": "No numeric columns found for summary statistics."}

    desc = target_df.describe().to_dict()
    return {"summary_statistics": desc}


def calculate_correlation_matrix(df: Any) -> Dict[str, Any]:
    """Calculates Pearson correlation coefficients among all numerical columns."""
    try:
        import pandas as pd
    except ImportError as e:
        raise RuntimeError("Pandas is required. Please install requirements.txt.") from e

    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty or numeric_df.shape[1] < 2:
        return {"error": "At least two numeric columns are required to calculate correlation."}

    corr = numeric_df.corr().round(4).to_dict()
    return {"correlation_matrix": corr}
