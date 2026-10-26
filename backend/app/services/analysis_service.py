"""Analysis service orchestrating data ingestion, EDA, and agent interaction."""

from pathlib import Path
from typing import Dict, Any, Optional, Union

from app.data_engine.loader import load_dataset
from app.data_engine.cleaner import clean_dataset
from app.data_engine.profiler import profile_dataset
from app.tools.analysis_tools import calculate_summary_statistics, calculate_correlation_matrix
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
    ) -> Dict[str, Any]:
        """Complete ingestion pipeline: loads, cleans, profiles, and analyzes correlations.

        Args:
            file_path: Path to the uploaded dataset.
            auto_clean: Whether to apply automated cleaning (dedup, whitespace strip, column normalization).

        Returns:
            Dictionary containing metadata, profile, cleaning report, summary stats, and sample rows.
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

        return {
            "file_path": str(file_path),
            "file_name": Path(file_path).name,
            "auto_cleaned": auto_clean,
            "cleaning_report": clean_report,
            "profile": profile,
            "summary_statistics": summary_stats.get("summary_statistics", {}),
            "correlation_matrix": corr_matrix.get("correlation_matrix", {}),
        }

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
