import os
import tempfile



def test_create_candidate(client):
    response = client.post(
        "/candidates/",
        json={
            "custom_fields": {"expected_salary": 120000},
            "tags": ["tag_backend", "tag_urgent"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "applied"
    assert "tag_urgent" in data["tags"]
    assert data["custom_fields"]["expected_salary"] == 120000
    return data["id"]


def test_update_candidate_status(client):
    candidate_id = test_create_candidate(client)
    response = client.post(
        f"/candidates/{candidate_id}/status",
        json={"status": "screening", "reason": "Resume looks good"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "screening"

    # Check timeline
    timeline_res = client.get(f"/candidates/{candidate_id}/timeline")
    assert timeline_res.status_code == 200
    events = timeline_res.json()
    assert any(
        e["event_type"] == "status_changed"
        and e["details"]["new_status"] == "screening"
        for e in events
    )


def test_add_candidate_note(client):
    candidate_id = test_create_candidate(client)
    response = client.post(
        f"/candidates/{candidate_id}/notes",
        json={
            "content": "Candidate has great communication skills.",
            "visibility": "public",
        },
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Candidate has great communication skills."

    # Check timeline
    timeline_res = client.get(f"/candidates/{candidate_id}/timeline")
    assert timeline_res.status_code == 200
    events = timeline_res.json()
    assert any(e["event_type"] == "note_added" for e in events)


def test_upload_candidate_resume(client):
    candidate_id = test_create_candidate(client)

    # Create a dummy PDF
    fd, path = tempfile.mkstemp(suffix=".pdf")
    with os.fdopen(fd, "w") as f:
        f.write("%PDF-1.4 Dummy PDF Content")

    with open(path, "rb") as f:
        response = client.post(
            f"/candidates/{candidate_id}/resume",
            files={"file": ("test.pdf", f, "application/pdf")},
        )

    os.remove(path)

    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] == True
    assert data["filename"].endswith(".pdf")
