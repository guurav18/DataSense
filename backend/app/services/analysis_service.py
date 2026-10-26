"""Analysis service orchestrating data ingestion, EDA, visualization, and agent interaction."""

from pathlib import Path
from typing import Dict, Any, Optional, Union, List

from app.data_engine.loader import load_dataset
from app.data_engine.cleaner import clean_dataset
from app.data_engine.profiler import profile_dataset
from app.tools.analysis_tools import calculate_summary_statistics, calculate_correlation_matrix
from app.tools.visualization_tools import (
    generate_histogram,
    generate_correlation_heatmap,
    generate_scatter_plot,
    generate_bar_chart,
    generate_recommended_charts,
)
from app.agents.graph import create_analysis_graph


class AnalysisService:
    """Coordinates data workflows between the processing engine and the LangGraph agent."""

    def __init__(self):
        self.graph = create_analysis_graph()

    def inspect_dataset(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Loads and profiles a dataset, returning baseline exploratory metrics."""
        df = load_dataset(file_path)
        profile = profile_dataset(df)
        return {
            "file_path": str(file_path),
            "profile": profile,
        }

    def clean_and_profile(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Cleans and generates an updated profile of the dataset."""
        df = load_dataset(file_path)
        cleaned_df, clean_report = clean_dataset(df)
        updated_profile = profile_dataset(cleaned_df)

        return {
            "cleaning_report": clean_report,
            "profile": updated_profile,
        }

    def process_uploaded_dataset(
        self,
        file_path: Union[str, Path],
        auto_clean: bool = True,
        generate_charts: bool = True,
    ) -> Dict[str, Any]:
        """Complete ingestion pipeline: loads, cleans, profiles, and analyzes correlations.

        Args:
            file_path: Path to the uploaded dataset.
            auto_clean: Whether to apply automated cleaning.
            generate_charts: Whether to automatically generate starter visualizations.

        Returns:
            Dictionary containing metadata, profile, cleaning report, summary stats, sample rows, and charts.
        """
        raw_df = load_dataset(file_path)
        clean_report = None

        if auto_clean:
            active_df, clean_report = clean_dataset(raw_df)
        else:
            active_df = raw_df

        profile = profile_dataset(active_df)
        summary_stats = calculate_summary_statistics(active_df)
        corr_matrix = calculate_correlation_matrix(active_df)

        charts: List[Dict[str, Any]] = []
        if generate_charts:
            charts = generate_recommended_charts(active_df)

        return {
            "file_path": str(file_path),
            "file_name": Path(file_path).name,
            "auto_cleaned": auto_clean,
            "cleaning_report": clean_report,
            "profile": profile,
            "summary_statistics": summary_stats.get("summary_statistics", {}),
            "correlation_matrix": corr_matrix.get("correlation_matrix", {}),
            "charts": charts,
        }

    def generate_custom_chart(
        self,
        file_path: Union[str, Path],
        chart_type: str,
        params: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Generates a custom visualization on demand for a dataset."""
        df = load_dataset(file_path)
        cleaned_df, _ = clean_dataset(df)

        if chart_type == "histogram":
            column = params.get("column")
            bins = int(params.get("bins", 20))
            return generate_histogram(cleaned_df, column, bins=bins)
        elif chart_type == "heatmap":
            return generate_correlation_heatmap(cleaned_df)
        elif chart_type == "scatter":
            x_col = params.get("x_column")
            y_col = params.get("y_column")
            add_trendline = bool(params.get("add_trendline", True))
            return generate_scatter_plot(cleaned_df, x_col, y_col, add_trendline=add_trendline)
        elif chart_type == "bar":
            column = params.get("column")
            top_n = int(params.get("top_n", 10))
            return generate_bar_chart(cleaned_df, column, top_n=top_n)
        else:
            raise ValueError(f"Unsupported chart type '{chart_type}'. Choose histogram, heatmap, scatter, or bar.")

    def run_agent_query(self, user_query: str, dataset_path: Optional[str] = None) -> Dict[str, Any]:
        """Dispatches user prompt to LangGraph agent execution graph."""
        if not self.graph:
            return {
                "user_query": user_query,
                "response": (
                    "LangGraph agent workflow compiled in stub mode. "
                    "Activate Python virtual environment with full dependencies to execute graph."
                ),
            }

        initial_state = {
            "user_query": user_query,
            "dataset_path": dataset_path,
            "messages": [],
            "chart_paths": [],
        }

        # Invocation will be connected in feature integration phase
        return {
            "user_query": user_query,
            "status": "ready",
            "state_initialized": True,
        }
