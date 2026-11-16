"""Integration tests for LangGraph autonomous data analysis agent workflow."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_agent_query_on_demo_dataset():
    """Verify conversational agent query executes plan, generates code, computes results, and creates charts."""
    # Ensure demo dataset exists
    demo_resp = client.get("/api/v1/datasets/demo")
    assert demo_resp.status_code == 200

    # Ask the agent an aggregation query
    query_resp = client.post(
        "/api/v1/agent/query",
        json={
            "query": "What is the total revenue by product?",
            "dataset_id": "demo",
        },
    )
    assert query_resp.status_code == 200
    payload = query_resp.json()

    assert payload["status"] == "completed"
    assert len(payload["plan"]) >= 2
    assert "df.groupby" in payload["generated_code"] or "result" in payload["generated_code"]
    assert "total_revenue" in payload["final_response"].lower() or "revenue" in payload["final_response"].lower()

    # Verify chart URL was produced and is downloadable
    assert len(payload["chart_urls"]) > 0
    chart_url = payload["chart_urls"][0]
    chart_resp = client.get(chart_url)
    assert chart_resp.status_code == 200
    assert chart_resp.headers["content-type"] == "image/png"


def test_agent_distribution_query():
    """Verify distribution and histogram generation via natural language query."""
    resp = client.post(
        "/api/v1/agent/query",
        json={
            "query": "Show distribution of units sold",
            "dataset_id": "demo",
        },
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["status"] == "completed"
    assert "units_sold" in payload["final_response"] or "Mean" in payload["final_response"]
    assert len(payload["chart_urls"]) > 0


def test_agent_correlation_query():
    """Verify correlation matrix and heatmap generation via agent query."""
    resp = client.post(
        "/api/v1/agent/query",
        json={
            "query": "What is the correlation between numerical variables?",
            "dataset_id": "demo",
        },
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["status"] == "completed"
    assert "correlation" in payload["generated_code"].lower()
    assert len(payload["chart_urls"]) > 0


def test_agent_empty_query_rejected():
    """Verify empty prompt is rejected with 400 Bad Request."""
    resp = client.post(
        "/api/v1/agent/query",
        json={"query": "   ", "dataset_id": "demo"},
    )
    assert resp.status_code == 400
