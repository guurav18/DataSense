"""Automated data cleaning module for DataSense AI."""

from typing import Dict, Any, Tuple


def clean_dataset(df: Any, drop_duplicates: bool = True, strip_whitespace: bool = True) -> Tuple[Any, Dict[str, Any]]:
    """Performs foundational data cleaning on a Pandas DataFrame.

    Operations:
    1. Standardizes column names (stripped, lowercase, spaces replaced with underscores).
    2. Strips leading/trailing whitespace from string columns.
    3. Removes exact duplicate rows if requested.
    4. Computes a summary of cleaning operations performed.

    Returns:
        Tuple containing the cleaned DataFrame and a report dictionary.
    """
    try:
        import pandas as pd
    except ImportError as e:
        raise RuntimeError("Pandas is required for data cleaning. Please install requirements.txt.") from e

    cleaned_df = df.copy()
    initial_rows = len(cleaned_df)
    initial_cols = len(cleaned_df.columns)

    # 1. Clean column names
    cleaned_df.columns = [
        str(col).strip().lower().replace(" ", "_")
        for col in cleaned_df.columns
    ]

    # 2. Strip whitespace from string objects
    if strip_whitespace:
        for col in cleaned_df.select_dtypes(include=["object"]).columns:
            cleaned_df[col] = cleaned_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

    # 3. Handle duplicates
    duplicates_removed = 0
    if drop_duplicates:
        duplicates_removed = int(cleaned_df.duplicated().sum())
        cleaned_df = cleaned_df.drop_duplicates()

    report = {
        "initial_shape": [initial_rows, initial_cols],
        "final_shape": [len(cleaned_df), len(cleaned_df.columns)],
        "duplicates_removed": duplicates_removed,
        "remaining_null_count": int(cleaned_df.isnull().sum().sum()),
    }

    return cleaned_df, report
