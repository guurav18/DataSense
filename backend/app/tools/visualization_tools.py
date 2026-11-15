"""Matplotlib visualization tools for generating charts and statistical plots."""

import uuid
from pathlib import Path
from typing import Any, Optional, Dict, List
import numpy as np

from app.config import settings

# Common modern styling constants
PLOT_STYLE = {
    "primary_color": "#4f46e5",    # Indigo
    "secondary_color": "#06b6d4",  # Cyan
    "accent_color": "#10b981",     # Emerald
    "grid_color": "#e2e8f0",
    "text_color": "#1e293b",
    "background_color": "#ffffff",
}


def _get_chart_metadata(filename: str, filepath: Path, chart_type: str, title: str) -> Dict[str, Any]:
    """Helper to return consistent chart metadata across all generator functions."""
    return {
        "chart_id": filename.split(".")[0],
        "chart_type": chart_type,
        "title": title,
        "filename": filename,
        "filepath": str(filepath),
        "url": f"/api/v1/charts/{filename}",
    }


def generate_histogram(df: Any, column: str, bins: int = 20) -> Optional[Dict[str, Any]]:
    """Generates a distribution histogram for a numeric column and saves it to disk."""
    try:
        import matplotlib
        matplotlib.use("Agg")  # Non-interactive headless backend
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise RuntimeError("Matplotlib is required for visualization tools.") from e

    if column not in df.columns:
        return None

    series = df[column].dropna()
    if series.empty:
        return None

    filename = f"hist_{column}_{uuid.uuid4().hex[:8]}.png"
    filepath = settings.CHARTS_DIR / filename

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(
        series,
        bins=bins,
        color=PLOT_STYLE["primary_color"],
        edgecolor="#ffffff",
        alpha=0.85,
        rwidth=0.9,
    )

    # Add mean and median dashed reference lines
    mean_val = series.mean()
    median_val = series.median()
    ax.axvline(mean_val, color="#ef4444", linestyle="--", linewidth=1.5, label=f"Mean: {mean_val:.2f}")
    ax.axvline(median_val, color="#f59e0b", linestyle=":", linewidth=1.5, label=f"Median: {median_val:.2f}")

    title = f"Distribution of {column}"
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12, color=PLOT_STYLE["text_color"])
    ax.set_xlabel(column, fontsize=11, labelpad=8)
    ax.set_ylabel("Frequency", fontsize=11, labelpad=8)
    ax.grid(True, linestyle="--", alpha=0.5, color=PLOT_STYLE["grid_color"])
    ax.legend(frameon=True, facecolor="white", edgecolor="#e2e8f0")

    plt.tight_layout()
    plt.savefig(filepath, dpi=150)
    plt.close(fig)

    return _get_chart_metadata(filename, filepath, "histogram", title)


def generate_correlation_heatmap(df: Any) -> Optional[Dict[str, Any]]:
    """Generates an annotated correlation matrix heatmap for numerical columns."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise RuntimeError("Matplotlib is required for heatmaps.") from e

    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty or numeric_df.shape[1] < 2:
        return None

    corr_df = numeric_df.corr().round(2)
    columns = list(numeric_df.columns)
    n = len(columns)

    # Dynamic figure sizing based on column count
    fig_size = max(6, min(12, n * 1.2))
    filename = f"corr_heatmap_{uuid.uuid4().hex[:8]}.png"
    filepath = settings.CHARTS_DIR / filename

    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    cax = ax.matshow(corr_df.values, cmap="coolwarm", vmin=-1, vmax=1)
    fig.colorbar(cax, shrink=0.8)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(columns, rotation=45, ha="left", fontsize=9)
    ax.set_yticklabels(columns, fontsize=9)

    # Annotate numeric values inside each cell
    for i in range(n):
        for j in range(n):
            val = corr_df.values[i, j]
            if not np.isnan(val):
                text_color = "white" if abs(val) > 0.5 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=text_color, fontsize=8, fontweight="bold")

    title = "Pearson Correlation Matrix"
    ax.set_title(title, pad=25, fontsize=14, fontweight="bold", color=PLOT_STYLE["text_color"])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150)
    plt.close(fig)

    return _get_chart_metadata(filename, filepath, "heatmap", title)


def generate_scatter_plot(
    df: Any,
    x_column: str,
    y_column: str,
    add_trendline: bool = True,
) -> Optional[Dict[str, Any]]:
    """Generates a scatter plot of two numerical features with an optional linear trendline."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise RuntimeError("Matplotlib is required for scatter plots.") from e

    if x_column not in df.columns or y_column not in df.columns:
        return None

    clean_data = df[[x_column, y_column]].dropna()
    if clean_data.empty or len(clean_data) < 2:
        return None

    x = clean_data[x_column].values
    y = clean_data[y_column].values

    filename = f"scatter_{x_column}_vs_{y_column}_{uuid.uuid4().hex[:8]}.png"
    filepath = settings.CHARTS_DIR / filename

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(x, y, color=PLOT_STYLE["secondary_color"], alpha=0.7, edgecolors="none", s=50, label="Data Points")

    # Linear trendline
    if add_trendline and len(clean_data) >= 2:
        try:
            poly_fit = np.polyfit(x, y, 1)
            poly_fn = np.poly1d(poly_fit)
            x_line = np.linspace(x.min(), x.max(), 100)
            ax.plot(x_line, poly_fn(x_line), color="#ef4444", linestyle="-", linewidth=2, label="Trendline")
        except Exception:
            pass

    title = f"{y_column} vs {x_column}"
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12, color=PLOT_STYLE["text_color"])
    ax.set_xlabel(x_column, fontsize=11, labelpad=8)
    ax.set_ylabel(y_column, fontsize=11, labelpad=8)
    ax.grid(True, linestyle="--", alpha=0.5, color=PLOT_STYLE["grid_color"])
    ax.legend(frameon=True, facecolor="white", edgecolor="#e2e8f0")

    plt.tight_layout()
    plt.savefig(filepath, dpi=150)
    plt.close(fig)

    return _get_chart_metadata(filename, filepath, "scatter", title)


def generate_bar_chart(df: Any, column: str, top_n: int = 10) -> Optional[Dict[str, Any]]:
    """Generates a bar chart showing frequency counts of categorical columns."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise RuntimeError("Matplotlib is required for bar charts.") from e

    if column not in df.columns:
        return None

    counts = df[column].dropna().value_counts().head(top_n)
    if counts.empty:
        return None

    filename = f"bar_{column}_{uuid.uuid4().hex[:8]}.png"
    filepath = settings.CHARTS_DIR / filename

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        [str(idx) for idx in counts.index],
        counts.values,
        color=PLOT_STYLE["accent_color"],
        edgecolor="#ffffff",
        alpha=0.85,
        width=0.6,
    )

    # Bar label values on top
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{int(height)}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    title = f"Top {len(counts)} Frequency Counts for {column}"
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12, color=PLOT_STYLE["text_color"])
    ax.set_xlabel(column, fontsize=11, labelpad=8)
    ax.set_ylabel("Count", fontsize=11, labelpad=8)
    ax.set_xticks(range(len(counts)))
    ax.set_xticklabels([str(idx) for idx in counts.index], rotation=30, ha="right", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.5, color=PLOT_STYLE["grid_color"])

    plt.tight_layout()
    plt.savefig(filepath, dpi=150)
    plt.close(fig)

    return _get_chart_metadata(filename, filepath, "bar", title)


def generate_recommended_charts(df: Any) -> List[Dict[str, Any]]:
    """Automatically produces an initial curated set of starter charts for a dataset."""
    recommended: List[Dict[str, Any]] = []

    # 1. Correlation heatmap if at least 2 numerical columns
    heatmap = generate_correlation_heatmap(df)
    if heatmap:
        recommended.append(heatmap)

    # 2. Histogram for up to 2 numerical columns
    numeric_cols = list(df.select_dtypes(include=["number"]).columns)
    for num_col in numeric_cols[:2]:
        hist = generate_histogram(df, num_col)
        if hist:
            recommended.append(hist)

    # 3. Bar chart for 1 categorical column
    categorical_cols = list(df.select_dtypes(include=["object", "category"]).columns)
    for cat_col in categorical_cols[:1]:
        bar = generate_bar_chart(df, cat_col)
        if bar:
            recommended.append(bar)

    return recommended
