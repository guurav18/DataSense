"""Integration tests for dynamic chart generation and image serving endpoints."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_demo_dataset_generates_charts():
    """Verify demo dataset automatically produces recommended starter charts."""
    response = client.get("/api/v1/datasets/demo")
    assert response.status_code == 200
    data = response.json()["data"]
    charts = data.get("charts", [])
    assert len(charts) > 0

    first_chart = charts[0]
    assert "url" in first_chart
    assert "filename" in first_chart

    # Verify chart image can be retrieved via HTTP
    img_resp = client.get(first_chart["url"])
    assert img_resp.status_code == 200
    assert img_resp.headers["content-type"] == "image/png"
    assert len(img_resp.content) > 500  # Non-empty PNG payload


def test_custom_histogram_generation():
    """Test on-demand histogram generation."""
    response = client.post(
        "/api/v1/charts/generate",
        json={
            "dataset_id": "demo",
            "chart_type": "histogram",
            "params": {"column": "units_sold", "bins": 15},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    chart = payload["chart"]
    assert chart["chart_type"] == "histogram"
    assert "units_sold" in chart["title"]

    # Verify image retrieval
    img_resp = client.get(chart["url"])
    assert img_resp.status_code == 200
    assert img_resp.headers["content-type"] == "image/png"


def test_custom_scatter_plot_generation():
    """Test on-demand scatter plot generation with trendline."""
    response = client.post(
        "/api/v1/charts/generate",
        json={
            "dataset_id": "demo",
            "chart_type": "scatter",
            "params": {
                "x_column": "units_sold",
                "y_column": "total_revenue",
                "add_trendline": True,
            },
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    chart = payload["chart"]
    assert chart["chart_type"] == "scatter"


def test_custom_bar_chart_generation():
    """Test on-demand categorical bar chart generation."""
    response = client.post(
        "/api/v1/charts/generate",
        json={
            "dataset_id": "demo",
            "chart_type": "bar",
            "params": {"column": "region", "top_n": 5},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    chart = payload["chart"]
    assert chart["chart_type"] == "bar"


def test_chart_not_found_and_traversal_protection():
    """Test invalid filename and path traversal attempts."""
    # Non-existent chart
    resp = client.get("/api/v1/charts/non_existent_chart_9999.png")
    assert resp.status_code == 404

    # Traversal attempt
    resp2 = client.get("/api/v1/charts/../../../app/main.py")
    assert resp2.status_code == 404
