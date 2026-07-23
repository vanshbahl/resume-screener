import pytest
from fastapi.testclient import TestClient

def test_create_and_get_interview(client: TestClient):
    payload = {
        "candidate_id": "cand_123",
        "job_id": "job_456",
        "title": "Technical Screen",
        "interview_type": "Technical"
    }
    
    # Create
    response = client.post("/interviews", json=payload)
    assert response.status_code == 200
    interview_id = response.json()["id"]
    
    # Get
    response = client.get(f"/interviews/{interview_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Technical Screen"
    
def test_schedule_interview(client: TestClient):
    # Setup interview
    payload = {
        "candidate_id": "cand_123",
        "job_id": "job_456",
        "title": "Behavioral",
        "interview_type": "Behavioral"
    }
    response = client.post("/interviews", json=payload)
    interview_id = response.json()["id"]
    
    # Schedule
    schedule_payload = {
        "start_time": "2026-08-01T10:00:00Z",
        "end_time": "2026-08-01T11:00:00Z",
        "timezone": "UTC",
        "location": "Zoom"
    }
    response = client.post(f"/interviews/{interview_id}/schedule", json=schedule_payload)
    assert response.status_code == 200
    assert response.json()["location"] == "Zoom"
    
def test_panel_management(client: TestClient):
    payload = {
        "candidate_id": "cand_123",
        "job_id": "job_456",
        "title": "Managerial",
        "interview_type": "Managerial"
    }
    response = client.post("/interviews", json=payload)
    interview_id = response.json()["id"]
    
    # Add panel
    panel_payload = {"user_id": "user_789", "role": "Lead"}
    response = client.post(f"/interviews/{interview_id}/panel", json=panel_payload)
    assert response.status_code == 200
    
    # Remove panel
    response = client.delete(f"/interviews/{interview_id}/panel/user_789")
    assert response.status_code == 200

def test_feedback_and_complete(client: TestClient):
    payload = {
        "candidate_id": "cand_123",
        "job_id": "job_456",
        "title": "Final Round",
        "interview_type": "Final"
    }
    response = client.post("/interviews", json=payload)
    interview_id = response.json()["id"]
    
    # Submit feedback
    feedback_payload = {
        "overall_recommendation": "STRONG_PASS",
        "strengths": "Great communication",
        "scorecard": {
            "criteria": {
                "Architecture": {"score": 5}
            }
        }
    }
    response = client.post(f"/interviews/{interview_id}/feedback", json=feedback_payload)
    assert response.status_code == 200
    
    # Complete interview
    response = client.post(f"/interviews/{interview_id}/complete?outcome=STRONG_PASS")
    assert response.status_code == 200
    assert response.json()["outcome"] == "STRONG_PASS"
    assert response.json()["status"] == "COMPLETED"
