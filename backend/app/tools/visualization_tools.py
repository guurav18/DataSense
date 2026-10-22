"""Matplotlib visualization tools for generating charts and statistical plots."""

import uuid
from pathlib import Path
from typing import Any, Optional
from app.config import settings


def generate_histogram(df: Any, column: str, bins: int = 20) -> Optional[str]:
    """Generates a distribution histogram for a numeric column and saves it to disk.

    Returns:
        Absolute or relative filepath of the saved chart image, or None on failure.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")  # Non-interactive headless backend for server execution
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise RuntimeError("Matplotlib is required for visualization tools.") from e

    if column not in df.columns:
        return None

    filename = f"hist_{column}_{uuid.uuid4().hex[:8]}.png"
    filepath = settings.CHARTS_DIR / filename

    fig, ax = plt.subplots(figsize=(8, 5))
    df[column].dropna().hist(bins=bins, ax=ax, color="#3b82f6", edgecolor="black", alpha=0.7)
    ax.set_title(f"Distribution of {column}", fontsize=14, fontweight="bold")
    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")
    ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(filepath, dpi=150)
    plt.close(fig)

    return str(filepath)


def generate_correlation_heatmap(df: Any) -> Optional[str]:
    """Generates a correlation matrix heatmap for numeric features and saves it to disk."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError as e:
        raise RuntimeError("Matplotlib & NumPy are required for heatmaps.") from e

    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty or numeric_df.shape[1] < 2:
        return None

    corr = numeric_df.corr().values
    columns = list(numeric_df.columns)

    filename = f"corr_heatmap_{uuid.uuid4().hex[:8]}.png"
    filepath = settings.CHARTS_DIR / filename

    fig, ax = plt.subplots(figsize=(8, 6))
    cax = ax.matshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    fig.colorbar(cax)

    ax.set_xticks(range(len(columns)))
    ax.set_yticks(range(len(columns)))
    ax.set_xticklabels(columns, rotation=45, ha="left")
    ax.set_yticklabels(columns)
    ax.set_title("Correlation Heatmap", pad=20, fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.savefig(filepath, dpi=150)
    plt.close(fig)

    return str(filepath)
