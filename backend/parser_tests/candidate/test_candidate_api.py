import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import tempfile

from app.main import app
from app.core.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_candidate.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_create_candidate():
    response = client.post("/candidates/", json={
        "custom_fields": {"expected_salary": 120000},
        "tags": ["tag_backend", "tag_urgent"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "applied"
    assert "tag_urgent" in data["tags"]
    assert data["custom_fields"]["expected_salary"] == 120000
    return data["id"]

def test_update_candidate_status():
    candidate_id = test_create_candidate()
    response = client.post(f"/candidates/{candidate_id}/status", json={
        "status": "screening",
        "reason": "Resume looks good"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "screening"
    
    # Check timeline
    timeline_res = client.get(f"/candidates/{candidate_id}/timeline")
    assert timeline_res.status_code == 200
    events = timeline_res.json()
    assert any(e["event_type"] == "status_changed" and e["details"]["new_status"] == "screening" for e in events)

def test_add_candidate_note():
    candidate_id = test_create_candidate()
    response = client.post(f"/candidates/{candidate_id}/notes", json={
        "content": "Candidate has great communication skills.",
        "visibility": "public"
    })
    assert response.status_code == 200
    assert response.json()["content"] == "Candidate has great communication skills."
    
    # Check timeline
    timeline_res = client.get(f"/candidates/{candidate_id}/timeline")
    assert timeline_res.status_code == 200
    events = timeline_res.json()
    assert any(e["event_type"] == "note_added" for e in events)

def test_upload_resume():
    candidate_id = test_create_candidate()
    
    # Create a dummy PDF
    fd, path = tempfile.mkstemp(suffix=".pdf")
    with os.fdopen(fd, 'w') as f:
        f.write("%PDF-1.4 Dummy PDF Content")
        
    with open(path, "rb") as f:
        response = client.post(f"/candidates/{candidate_id}/resume", files={"file": ("test.pdf", f, "application/pdf")})
    
    os.remove(path)
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] == True
    assert data["filename"].endswith(".pdf")
