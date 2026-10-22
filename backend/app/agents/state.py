"""State definition for DataSense AI LangGraph agent."""

from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict, total=False):
    """Represents the mutable state shared across all LangGraph nodes during data analysis.

    Attributes:
        messages: Conversation history between the user and the agent.
        dataset_path: Path to the currently loaded dataset file.
        dataset_summary: High-level overview of columns, shapes, and null counts.
        user_query: The natural language question or request from the user.
        plan: Steps formulated by the agent to satisfy the query.
        generated_code: Python code synthesized to query pandas or generate charts.
        execution_result: Raw outputs, tables, or numeric results from code execution.
        chart_paths: File paths to generated Matplotlib charts/visualizations.
        final_response: Natural language answer synthesized for the user.
        error: Any error encountered during data processing or code execution.
    """

    messages: List[Dict[str, Any]]
    dataset_path: Optional[str]
    dataset_summary: Optional[Dict[str, Any]]
    user_query: str
    plan: Optional[List[str]]
    generated_code: Optional[str]
    execution_result: Optional[Any]
    chart_paths: List[str]
    final_response: Optional[str]
    error: Optional[str]
