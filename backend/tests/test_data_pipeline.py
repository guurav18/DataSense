"""Integration tests for dataset ingestion, cleaning, and EDA profiling endpoints."""

import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_status_endpoint():
    """Verify status endpoint lists implemented features."""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Dataset Ingestion Pipeline" in "".join(data["implemented_features"])


def test_upload_csv_dataset():
    """Test uploading a CSV dataset and verifying automated cleaning & profiling."""
    csv_content = (
        "  User ID , Age , Salary , Department \n"
        "101 , 28 , 65000.0 , Engineering \n"
        "102 , 35 , 85000.0 , Marketing \n"
        "103 , 42 , 110000.0 , Management \n"
        "101 , 28 , 65000.0 , Engineering \n"  # Duplicate row
        "104 ,  , 72000.0 , Engineering \n"     # Missing Age
    )
    file_bytes = io.BytesIO(csv_content.encode("utf-8"))

    response = client.post(
        "/api/v1/datasets/upload?auto_clean=true",
        files={"file": ("test_employees.csv", file_bytes, "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["original_name"] == "test_employees.csv"

    data = payload["data"]
    # Check cleaning report
    report = data["cleaning_report"]
    assert report["initial_shape"] == [5, 4]
    assert report["final_shape"] == [4, 4]  # 1 duplicate removed
    assert report["duplicates_removed"] == 1

    # Check profile
    profile = data["profile"]
    assert profile["rows"] == 4
    assert profile["columns"] == 4
    assert "user_id" in profile["column_names"]
    assert "age" in profile["column_names"]
    assert "salary" in profile["column_names"]

    # Verify preview sample rows
    assert len(profile["sample_rows"]) == 4

    # Verify summary statistics & correlation
    assert "salary" in data["summary_statistics"]


def test_upload_invalid_file_extension():
    """Test rejecting unsupported file types."""
    invalid_content = io.BytesIO(b"Hello world")
    response = client.post(
        "/api/v1/datasets/upload",
        files={"file": ("notes.txt", invalid_content, "text/plain")},
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_demo_dataset_endpoint():
    """Test demo dataset generation and retrieval."""
    response = client.get("/api/v1/datasets/demo")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["dataset_id"] == "demo"
    assert payload["data"]["profile"]["rows"] == 100
    assert "total_revenue" in payload["data"]["profile"]["column_names"]
    assert len(payload["data"]["profile"]["sample_rows"]) == 10


def test_preview_dataset_endpoint():
    """Test previewing an existing dataset."""
    # First ensure demo dataset exists
    client.get("/api/v1/datasets/demo")

    response = client.get("/api/v1/datasets/preview?dataset_id=demo")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["dataset_id"] == "demo"
    assert "profile" in payload["data"]
