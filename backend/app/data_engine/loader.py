"""Dataset loader for CSV and Excel formats."""

from pathlib import Path
from typing import Any, Union


def load_dataset(file_path: Union[str, Path]) -> Any:
    """Loads a CSV or Excel dataset into a Pandas DataFrame.

    Args:
        file_path: Path to the dataset file (.csv, .xlsx, .xls).

    Returns:
        pd.DataFrame containing the dataset.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If file format is not supported.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()

    try:
        import pandas as pd
    except ImportError as e:
        raise RuntimeError("Pandas is required to load datasets. Please install requirements.txt.") from e

    if suffix == ".csv":
        return pd.read_csv(path)
    elif suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file format '{suffix}'. Expected .csv, .xlsx, or .xls")
