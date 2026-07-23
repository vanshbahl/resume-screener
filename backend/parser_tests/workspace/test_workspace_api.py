import pytest
from fastapi.testclient import TestClient

def test_get_dashboard(client: TestClient):
    response = client.get("/workspace/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "open_jobs" in data
    assert "assigned_candidates" in data

def test_get_activity_feed(client: TestClient):
    response = client.get("/workspace/activity")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_candidate_queue(client: TestClient):
    response = client.get("/workspace/queue/candidates")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_saved_searches(client: TestClient):
    # Create
    create_payload = {
        "name": "Frontend Engineers",
        "search_type": "candidate",
        "criteria": {"skills": ["React", "TypeScript"]}
    }
    response = client.post("/workspace/searches", json=create_payload)
    assert response.status_code == 200
    search_id = response.json()["id"]

    # Get
    response = client.get("/workspace/searches")
    assert response.status_code == 200
    searches = response.json()
    assert len(searches) >= 1
    assert any(s["id"] == search_id for s in searches)

    # Delete
    response = client.delete(f"/workspace/searches/{search_id}")
    assert response.status_code == 200

def test_preferences(client: TestClient):
    payload = {"settings": {"theme": "dark"}}
    response = client.patch("/workspace/preferences", json=payload)
    assert response.status_code == 200
    assert response.json()["settings"]["theme"] == "dark"

def test_favorites(client: TestClient):
    payload = {
        "entity_type": "job",
        "entity_id": "job_123",
        "folder": "Urgent"
    }
    response = client.post("/workspace/favorites", json=payload)
    assert response.status_code == 200
    
    response = client.get("/workspace/favorites?entity_type=job")
    assert response.status_code == 200
    assert len(response.json()) >= 1
