import os
import tempfile



def test_create_job(client):
    response = client.post(
        "/jobs/",
        json={
            "title": "Senior Backend Engineer",
            "department": "Engineering",
            "employment_type": "full_time",
            "location": "Remote",
            "salary_range": "$140k - $180k",
            "custom_fields": {"budget_code": "ENG-2026-Q3"},
            "tags": ["tag_urgent", "tag_remote"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "draft"
    assert "tag_remote" in data["tags"]
    assert data["custom_fields"]["budget_code"] == "ENG-2026-Q3"
    return data["id"]


def test_update_job_status(client):
    job_id = test_create_job(client)
    response = client.post(
        f"/jobs/{job_id}/status",
        json={"status": "open", "reason": "Headcount approved"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "open"

    # Check timeline
    timeline_res = client.get(f"/jobs/{job_id}/timeline")
    assert timeline_res.status_code == 200
    events = timeline_res.json()
    assert any(
        e["event_type"] == "status_changed" and e["details"]["new_status"] == "open"
        for e in events
    )


def test_add_job_note(client):
    job_id = test_create_job(client)
    response = client.post(
        f"/jobs/{job_id}/notes",
        json={
            "content": "Make sure we prioritize Python experience.",
            "visibility": "public",
        },
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Make sure we prioritize Python experience."

    # Check timeline
    timeline_res = client.get(f"/jobs/{job_id}/timeline")
    assert timeline_res.status_code == 200
    events = timeline_res.json()
    assert any(e["event_type"] == "note_added" for e in events)


def test_upload_job_description(client):
    job_id = test_create_job(client)

    # Create a dummy PDF
    fd, path = tempfile.mkstemp(suffix=".pdf")
    with os.fdopen(fd, "w") as f:
        f.write("%PDF-1.4 Dummy JD PDF Content")

    with open(path, "rb") as f:
        response = client.post(
            f"/jobs/{job_id}/description",
            files={"file": ("jd.pdf", f, "application/pdf")},
        )

    os.remove(path)

    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] == True
    assert data["filename"].endswith(".pdf")
