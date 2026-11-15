"""LangGraph agent workflow nodes for DataSense AI.

Each node represents an autonomous step in the data analysis pipeline:
1. Plan: Understand user intent and outline analytical steps.
2. Code Generation: Generate safe Pandas and Matplotlib code.
3. Execution: Run generated code in a sandboxed execution context.
4. Synthesis: Translate execution results into clear natural language insights.
"""

import io
import re
import sys
import uuid
import math
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt

from app.config import settings
from app.agents.state import AgentState
from app.data_engine.loader import load_dataset
from app.data_engine.cleaner import clean_dataset


def _get_llm_client():
    """Returns a LangChain LLM or direct API client if configured, or None."""
    api_key = settings.LLM_API_KEY
    if not api_key or "your_" in api_key.lower():
        return None

    try:
        if settings.LLM_PROVIDER.lower() == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.LLM_MODEL,
                api_key=api_key,
                temperature=0.1,
            )
    except Exception:
        pass
    return None


def plan_analysis_node(state: AgentState) -> Dict[str, Any]:
    """Node: Formulates an analysis strategy based on user query and dataset schema."""
    user_query = state.get("user_query", "").strip()
    dataset_summary = state.get("dataset_summary") or {}
    columns = dataset_summary.get("column_names") or []

    llm = _get_llm_client()
    if llm:
        try:
            from langchain_core.messages import SystemMessage, HumanMessage
            prompt = (
                f"You are DataSense AI, an autonomous data analyst. "
                f"Dataset columns: {columns}. Total rows: {dataset_summary.get('rows')}. "
                f"Formulate a crisp 3-step analytical plan to answer this query: '{user_query}'."
                f"Return ONLY 3 numbered bullet points."
            )
            resp = llm.invoke([HumanMessage(content=prompt)])
            lines = [l.strip() for l in resp.content.split("\n") if l.strip() and l[0].isdigit()]
            if lines:
                return {"plan": lines}
        except Exception:
            pass

    # Heuristic Planning Engine
    query_lower = user_query.lower()
    plan: List[str] = [
        f"1. Parse user query '{user_query}' and map variables to dataset columns {columns[:6]}."
    ]

    if any(k in query_lower for k in ["chart", "plot", "histogram", "distribution", "graph", "heatmap", "trend"]):
        plan.append("2. Filter and aggregate the relevant metrics, then configure Matplotlib visualization.")
        plan.append("3. Render high-resolution chart and summarize visual insights.")
    elif any(k in query_lower for k in ["correlation", "relate", "relationship"]):
        plan.append("2. Compute Pearson correlation coefficients across numerical columns.")
        plan.append("3. Synthesize the strongest positive and negative linear relationships.")
    elif any(k in query_lower for k in ["top", "highest", "most", "lowest", "least", "bottom", "rank"]):
        plan.append("2. Group and aggregate target values, then sort to extract the top-ranked records.")
        plan.append("3. Formulate comparative ranking summary and key performance metrics.")
    elif any(k in query_lower for k in ["average", "mean", "median", "sum", "total", "count"]):
        plan.append("2. Compute statistical aggregations for requested numeric variables.")
        plan.append("3. Formulate descriptive statistical overview and narrative interpretation.")
    else:
        plan.append("2. Perform exploratory data aggregation and extract summary characteristics.")
        plan.append("3. Synthesize findings into clear executive insights.")

    return {"plan": plan}


def _match_columns(query: str, available_cols: List[str]) -> List[str]:
    """Fuzzy/substring matches query words against column names."""
    q_tokens = re.findall(r"\w+", query.lower())
    matched = []
    for col in available_cols:
        col_lower = col.lower()
        if col_lower in query.lower():
            matched.append(col)
        elif any(token in col_lower for token in q_tokens if len(token) > 2):
            matched.append(col)
    return list(dict.fromkeys(matched))


def generate_code_node(state: AgentState) -> Dict[str, Any]:
    """Node: Synthesizes Python code for data transformation and visualization."""
    user_query = state.get("user_query", "").strip()
    dataset_summary = state.get("dataset_summary") or {}
    columns_info = dataset_summary.get("columns_info") or []
    column_names = dataset_summary.get("column_names") or []

    llm = _get_llm_client()
    if llm:
        try:
            from langchain_core.messages import SystemMessage, HumanMessage
            prompt = (
                f"Write executable Python code to analyze a pandas DataFrame named `df`.\n"
                f"Columns available: {column_names}.\n"
                f"User request: {user_query}\n"
                f"Rules:\n"
                f"- Assign the main textual/numeric/table result to variable `result`.\n"
                f"- If plotting a chart, use `matplotlib.pyplot` as `plt`. Save the figure to `CHARTS_DIR / f'agent_chart_{uuid.uuid4().hex[:8]}.png'` and assign its string path to `generated_chart_path`.\n"
                f"- `pd`, `np`, `plt`, `CHARTS_DIR`, `uuid` are already imported and in scope.\n"
                f"- Do NOT wrap code in markdown fences. Return ONLY raw Python code."
            )
            resp = llm.invoke([HumanMessage(content=prompt)])
            code = resp.content.strip()
            # Clean markdown code fences if present
            if code.startswith("```"):
                code = re.sub(r"^```python\s*|^```\s*", "", code)
                code = re.sub(r"\s*```$", "", code)
            return {"generated_code": code}
        except Exception:
            pass

    # Intelligent Heuristic Code Generator
    query_lower = user_query.lower()
    matched_cols = _match_columns(user_query, column_names)

    numeric_cols = [c["name"] for c in columns_info if c.get("stats")]
    cat_cols = [c["name"] for c in columns_info if not c.get("stats")]

    # Default fallback numerical and categorical columns
    target_num = next((c for c in matched_cols if c in numeric_cols), numeric_cols[0] if numeric_cols else None)
    target_cat = next((c for c in matched_cols if c in cat_cols), cat_cols[0] if cat_cols else None)

    code_lines = []

    # 1. Correlation query
    if any(k in query_lower for k in ["correlation", "heatmap", "relate", "relationship"]):
        code_lines = [
            "num_df = df.select_dtypes(include=['number'])",
            "corr = num_df.corr().round(4)",
            "result = corr.to_dict()",
            "",
            "# Render correlation heatmap",
            "fig, ax = plt.subplots(figsize=(8, 6))",
            "cax = ax.matshow(corr.values, cmap='coolwarm', vmin=-1, vmax=1)",
            "fig.colorbar(cax)",
            "ax.set_xticks(range(len(corr.columns)))",
            "ax.set_yticks(range(len(corr.columns)))",
            "ax.set_xticklabels(corr.columns, rotation=45, ha='left', fontsize=9)",
            "ax.set_yticklabels(corr.columns, fontsize=9)",
            "ax.set_title('Correlation Analysis', pad=20, fontsize=14, fontweight='bold')",
            "plt.tight_layout()",
            "chart_file = CHARTS_DIR / f'agent_corr_{uuid.uuid4().hex[:8]}.png'",
            "plt.savefig(chart_file, dpi=150)",
            "plt.close(fig)",
            "generated_chart_path = str(chart_file)",
        ]

    # 2. Distribution / Histogram
    elif any(k in query_lower for k in ["distribution", "histogram", "spread", "bins"]) and target_num:
        code_lines = [
            f"series = df['{target_num}'].dropna()",
            f"stats = series.describe().round(2).to_dict()",
            f"result = {{'metric': '{target_num}', 'statistics': stats}}",
            "",
            "# Render histogram",
            "fig, ax = plt.subplots(figsize=(8, 5))",
            f"series.hist(bins=20, ax=ax, color='#4f46e5', edgecolor='white', alpha=0.85)",
            f"ax.axvline(series.mean(), color='#ef4444', linestyle='--', label=f'Mean: {{series.mean():.2f}}')",
            f"ax.axvline(series.median(), color='#f59e0b', linestyle=':', label=f'Median: {{series.median():.2f}}')",
            f"ax.set_title('Distribution of {target_num}', fontsize=14, fontweight='bold')",
            f"ax.set_xlabel('{target_num}')",
            "ax.set_ylabel('Frequency')",
            "ax.grid(True, linestyle='--', alpha=0.5)",
            "ax.legend()",
            "plt.tight_layout()",
            "chart_file = CHARTS_DIR / f'agent_hist_{uuid.uuid4().hex[:8]}.png'",
            "plt.savefig(chart_file, dpi=150)",
            "plt.close(fig)",
            "generated_chart_path = str(chart_file)",
        ]

    # 3. Aggregation by Category (e.g. revenue by product, units by region)
    elif target_cat and target_num and any(k in query_lower for k in ["by", "group", "highest", "top", "per", "most"]):
        agg_func = "mean" if "average" in query_lower or "mean" in query_lower else "sum"
        code_lines = [
            f"grouped = df.groupby('{target_cat}')['{target_num}'].{agg_func}().round(2).sort_values(ascending=False)",
            f"result = {{'dimension': '{target_cat}', 'metric': '{target_num}', 'aggregation': '{agg_func}', 'data': grouped.head(10).to_dict()}}",
            "",
            "# Render comparative bar chart",
            "fig, ax = plt.subplots(figsize=(8, 5))",
            "top_data = grouped.head(8)",
            "bars = ax.bar([str(x) for x in top_data.index], top_data.values, color='#4f46e5', width=0.6, edgecolor='white')",
            f"ax.set_title(f'{target_num.title()} by {target_cat.title()} ({agg_func.title()})', fontsize=14, fontweight='bold')",
            f"ax.set_xlabel('{target_cat}')",
            f"ax.set_ylabel('{target_num}')",
            "ax.set_xticks(range(len(top_data)))",
            "ax.set_xticklabels([str(x) for x in top_data.index], rotation=30, ha='right', fontsize=9)",
            "ax.grid(axis='y', linestyle='--', alpha=0.5)",
            "plt.tight_layout()",
            "chart_file = CHARTS_DIR / f'agent_bar_{uuid.uuid4().hex[:8]}.png'",
            "plt.savefig(chart_file, dpi=150)",
            "plt.close(fig)",
            "generated_chart_path = str(chart_file)",
        ]

    # 4. Scatter plot (e.g. relation between two numeric variables)
    elif len(numeric_cols) >= 2 and any(k in query_lower for k in ["scatter", "versus", "vs", "against"]):
        x_col = matched_cols[0] if len(matched_cols) > 0 and matched_cols[0] in numeric_cols else numeric_cols[0]
        y_col = matched_cols[1] if len(matched_cols) > 1 and matched_cols[1] in numeric_cols else numeric_cols[1]
        code_lines = [
            f"clean_pts = df[['{x_col}', '{y_col}']].dropna()",
            f"corr_val = clean_pts['{x_col}'].corr(clean_pts['{y_col}'])",
            f"result = {{'x': '{x_col}', 'y': '{y_col}', 'pearson_correlation': round(corr_val, 4)}}",
            "",
            "# Render scatter plot",
            "fig, ax = plt.subplots(figsize=(8, 5))",
            f"ax.scatter(clean_pts['{x_col}'], clean_pts['{y_col}'], color='#06b6d4', alpha=0.7, edgecolors='none')",
            f"ax.set_title('{y_col} vs {x_col}', fontsize=14, fontweight='bold')",
            f"ax.set_xlabel('{x_col}')",
            f"ax.set_ylabel('{y_col}')",
            "ax.grid(True, linestyle='--', alpha=0.5)",
            "plt.tight_layout()",
            "chart_file = CHARTS_DIR / f'agent_scatter_{uuid.uuid4().hex[:8]}.png'",
            "plt.savefig(chart_file, dpi=150)",
            "plt.close(fig)",
            "generated_chart_path = str(chart_file)",
        ]

    # 5. General Summary & Exploration
    else:
        code_lines = [
            "num_cols = df.select_dtypes(include=['number']).columns",
            "stats = df[num_cols].describe().round(2).to_dict() if len(num_cols) > 0 else {}",
            "row_count = len(df)",
            "col_count = len(df.columns)",
            "result = {'shape': [row_count, col_count], 'summary': stats}",
        ]

    generated_code = "\n".join(code_lines)
    return {"generated_code": generated_code}


def _resolve_dataset_path(path_str: Optional[str]) -> Optional[Path]:
    if not path_str:
        return None
    p = Path(path_str)
    if p.exists() and p.is_file():
        return p
    p_upload = settings.UPLOAD_DIR / p.name
    if p_upload.exists() and p_upload.is_file():
        return p_upload
    return None


def execute_code_node(state: AgentState) -> Dict[str, Any]:
    """Node: Safely executes generated code against the dataset DataFrame."""
    code = state.get("generated_code", "")
    dataset_path_str = state.get("dataset_path")

    chart_paths = list(state.get("chart_paths") or [])
    chart_urls = list(state.get("chart_urls") or [])

    resolved_path = _resolve_dataset_path(dataset_path_str)
    if not resolved_path:
        return {
            "execution_result": "Dataset file not found for code execution.",
            "error": "Dataset path missing or invalid.",
            "chart_paths": chart_paths,
            "chart_urls": chart_urls,
        }

    try:
        raw_df = load_dataset(resolved_path)
        df, _ = clean_dataset(raw_df)
    except Exception as e:
        return {
            "execution_result": None,
            "error": f"Failed to load dataset: {str(e)}",
            "chart_paths": chart_paths,
            "chart_urls": chart_urls,
        }

    # Sandboxed execution context
    sandbox_globals = {
        "__builtins__": __builtins__,
        "df": df,
        "pd": pd,
        "np": np,
        "plt": plt,
        "CHARTS_DIR": settings.CHARTS_DIR,
        "uuid": uuid,
        "math": math,
        "result": None,
        "generated_chart_path": None,
    }

    stdout_capture = io.StringIO()
    old_stdout = sys.stdout

    try:
        sys.stdout = stdout_capture
        exec(code, sandbox_globals)
    except Exception as e:
        err_msg = traceback.format_exc()
        return {
            "execution_result": None,
            "stdout_output": stdout_capture.getvalue(),
            "error": f"Execution Error: {str(e)}\n{err_msg}",
            "chart_paths": chart_paths,
            "chart_urls": chart_urls,
        }
    finally:
        sys.stdout = old_stdout

    raw_result = sandbox_globals.get("result")
    chart_path = sandbox_globals.get("generated_chart_path")

    # Serialize raw_result if it's a pandas object
    if isinstance(raw_result, pd.DataFrame):
        clean_result = raw_result.to_dict(orient="records")
    elif isinstance(raw_result, pd.Series):
        clean_result = raw_result.to_dict()
    else:
        clean_result = raw_result

    # Register chart if one was produced
    if chart_path and Path(chart_path).exists():
        chart_paths.append(str(chart_path))
        chart_urls.append(f"/api/v1/charts/{Path(chart_path).name}")

    return {
        "execution_result": clean_result,
        "stdout_output": stdout_capture.getvalue(),
        "chart_paths": chart_paths,
        "chart_urls": chart_urls,
        "error": None,
    }


def synthesize_response_node(state: AgentState) -> Dict[str, Any]:
    """Node: Converts raw computational findings into user-friendly natural language insights."""
    query = state.get("user_query", "data query")
    result = state.get("execution_result")
    error = state.get("error")
    chart_urls = state.get("chart_urls") or []
    plan = state.get("plan") or []

    if error:
        return {
            "final_response": f"I encountered an error during analysis of '{query}':\n\n```\n{error}\n```\n"
                              f"Please review the dataset columns or rephrase your query."
        }

    llm = _get_llm_client()
    if llm:
        try:
            from langchain_core.messages import SystemMessage, HumanMessage
            prompt = (
                f"You are DataSense AI, an expert autonomous data analyst.\n"
                f"User Query: '{query}'\n"
                f"Computational Execution Output: {result}\n"
                f"Charts generated: {len(chart_urls)}\n"
                f"Provide a clear, professional analytical response summarizing the findings, "
                f"key metrics, and insights in Markdown."
            )
            resp = llm.invoke([HumanMessage(content=prompt)])
            return {"final_response": resp.content.strip()}
        except Exception:
            pass

    # Heuristic Response Synthesis
    lines = [
        f"### Analysis for: *\"{query}\"*\n",
    ]

    if isinstance(result, dict):
        if "dimension" in result and "metric" in result:
            dim = result["dimension"]
            metric = result["metric"]
            agg = result.get("aggregation", "sum")
            data = result.get("data", {})
            lines.append(f"**Key Findings for {metric.title()} by {dim.title()} ({agg.title()}):**\n")
            for k, v in list(data.items())[:8]:
                formatted_v = f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)
                lines.append(f"- **{k}**: {formatted_v}")
        elif "metric" in result and "statistics" in result:
            metric = result["metric"]
            stats = result["statistics"]
            lines.append(f"**Statistical Distribution for `{metric}`:**\n")
            lines.append(f"- **Count**: {stats.get('count', 'N/A')}")
            lines.append(f"- **Mean**: {stats.get('mean', 'N/A')}")
            lines.append(f"- **Std Dev**: {stats.get('std', 'N/A')}")
            lines.append(f"- **Median (50%)**: {stats.get('50%', 'N/A')}")
            lines.append(f"- **Range**: {stats.get('min', 'N/A')} to {stats.get('max', 'N/A')}")
        elif "pearson_correlation" in result:
            x = result.get("x")
            y = result.get("y")
            corr_val = result.get("pearson_correlation")
            lines.append(f"- Pearson correlation between **{x}** and **{y}** is **{corr_val}**.")
            if abs(corr_val) > 0.7:
                lines.append("  - This indicates a **strong** linear association.")
            elif abs(corr_val) > 0.4:
                lines.append("  - This indicates a **moderate** linear association.")
            else:
                lines.append("  - This indicates a **weak** linear association.")
        else:
            lines.append("Here are the computed results from the dataset:")
            for k, v in list(result.items())[:10]:
                if isinstance(v, dict):
                    v_str = ", ".join(f"{sub_k}: {sub_v}" for sub_k, sub_v in list(v.items())[:4])
                    lines.append(f"- **{k}**: {v_str}")
                else:
                    lines.append(f"- **{k}**: {v}")
    elif isinstance(result, list):
        lines.append(f"Retrieved **{len(result)}** matching records:")
        for idx, item in enumerate(result[:5], 1):
            lines.append(f"{idx}. {item}")
    elif result is not None:
        lines.append(f"**Result**: {result}")

    if chart_urls:
        lines.append(f"\n*A visual chart was automatically generated and is attached below.*")

    return {"final_response": "\n".join(lines)}
