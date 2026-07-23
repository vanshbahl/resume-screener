import pytest
from fastapi.testclient import TestClient
import time

def test_get_kpis(client: TestClient):
    response = client.get("/analytics/kpis")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    # Verify the specific KPIs exist
    kpi_names = [kpi["name"] for kpi in data["kpis"]]
    assert "Total Candidates" in kpi_names
    assert "Active Jobs" in kpi_names
    assert "Avg Time To Hire" in kpi_names

def test_get_trends(client: TestClient):
    response = client.get("/analytics/trends?days=7")
    assert response.status_code == 200
    data = response.json()
    assert data["metric_name"] == "Hires Over Time"
    assert len(data["data_points"]) == 7

def test_dashboard_config(client: TestClient):
    # Create config
    payload = {
        "dashboard_type": "recruiter",
        "widgets": [{"id": "kpi_widget_1", "type": "kpi"}]
    }
    response = client.post("/analytics/dashboard", json=payload)
    assert response.status_code == 200
    assert response.json()["dashboard_type"] == "recruiter"
    
    # Get config
    response = client.get("/analytics/dashboard/recruiter")
    assert response.status_code == 200
    assert response.json()["widgets"][0]["id"] == "kpi_widget_1"

def test_report_generation_and_export(client: TestClient):
    # Setup some test candidates
    client.post("/candidates", json={
        "first_name": "Alice", "last_name": "Smith", "email": "alice@test.com"
    })
    
    payload = {"status": "NEW"}
    # Test JSON generation
    response = client.post("/analytics/reports/candidate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["report_name"] == "Candidate Summary"
    assert len(data["columns"]) == 4
    
    # Test CSV Export
    csv_response = client.post("/analytics/reports/candidate/export", json=payload)
    assert csv_response.status_code == 200
    assert csv_response.headers["content-type"].startswith("text/csv")
    csv_text = csv_response.text
    assert "id,name,email,status" in csv_text
