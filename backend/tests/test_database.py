"""Unit and integration tests for database persistence of datasets and analysis sessions."""

import io
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import get_db, check_db_connection
from app.database.models import DatasetRecord, AnalysisSession

client = TestClient(app)


def test_database_connection_probe():
    """Verify database connection probe reports healthy status with fallback."""
    assert check_db_connection() is True


def test_dataset_upload_persists_in_database():
    """Verify uploaded dataset is recorded in relational database."""
    csv_data = "col_a,col_b,col_c\n1,10.5,alpha\n2,20.0,beta\n"
    file_bytes = io.BytesIO(csv_data.encode("utf-8"))

    upload_resp = client.post(
        "/api/v1/datasets/upload",
        files={"file": ("db_test_upload.csv", file_bytes, "text/csv")},
    )
    assert upload_resp.status_code == 200
    dataset_id = upload_resp.json()["dataset_id"]

    # Verify dataset appears in /datasets endpoint
    list_resp = client.get("/api/v1/datasets")
    assert list_resp.status_code == 200
    datasets = list_resp.json()["datasets"]
    assert any(d["dataset_uid"] == dataset_id for d in datasets)


def test_analysis_session_persists_in_database():
    """Verify conversational queries create persistent AnalysisSession records."""
    # Ensure demo dataset exists
    client.get("/api/v1/datasets/demo")

    query_resp = client.post(
        "/api/v1/agent/query",
        json={
            "query": "Show average unit price",
            "dataset_id": "demo",
        },
    )
    assert query_resp.status_code == 200

    # Retrieve sessions from endpoint
    sessions_resp = client.get("/api/v1/sessions?dataset_id=demo")
    assert sessions_resp.status_code == 200
    sessions = sessions_resp.json()["sessions"]
    assert len(sessions) > 0
    assert any("average unit price" in s["user_query"].lower() for s in sessions)
