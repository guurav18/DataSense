"""LangGraph workflow definition for DataSense AI agent."""

from typing import Any
from app.agents.state import AgentState
from app.agents.nodes import (
    plan_analysis_node,
    generate_code_node,
    execute_code_node,
    synthesize_response_node,
)


def create_analysis_graph() -> Any:
    """Constructs and compiles the LangGraph StateGraph for autonomous data analysis.

    Workflow topology:
      START -> plan_analysis -> generate_code -> execute_code -> synthesize_response -> END
    """
    try:
        from langgraph.graph import StateGraph, START, END

        builder = StateGraph(AgentState)

        # Register workflow nodes
        builder.add_node("plan_analysis", plan_analysis_node)
        builder.add_node("generate_code", generate_code_node)
        builder.add_node("execute_code", execute_code_node)
        builder.add_node("synthesize_response", synthesize_response_node)

        # Wire graph edges
        builder.add_edge(START, "plan_analysis")
        builder.add_edge("plan_analysis", "generate_code")
        builder.add_edge("generate_code", "execute_code")
        builder.add_edge("execute_code", "synthesize_response")
        builder.add_edge("synthesize_response", END)

        return builder.compile()
    except ImportError:
        # Fallback when dependencies have not yet been installed in the local environment
        return None
