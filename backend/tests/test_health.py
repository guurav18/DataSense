"""Unit tests for FastAPI root and health check endpoints."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify root endpoint returns welcome payload."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "DataSense AI" in data["message"]


def test_health_endpoint():
    """Verify health endpoint reports healthy without external DB or LLM dependencies."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "DataSense AI"
