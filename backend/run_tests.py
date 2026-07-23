import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api():
    print("Testing GET /")
    res = client.get("/")
    assert res.status_code == 200, f"GET / failed: {res.status_code} {res.text}"
    print("✓ GET / passed")

    print("Testing GET /jobs/")
    res = client.get("/jobs/")
    assert res.status_code == 200, f"GET /jobs/ failed: {res.status_code} {res.text}"
    print("✓ GET /jobs/ passed")
    
    print("Testing POST /jobs/")
    job_payload = {"title": "Software Engineer", "description": "Python dev", "required_skills": ["python", "fastapi"]}
    res = client.post("/jobs/", json=job_payload)
    assert res.status_code == 201, f"POST /jobs/ failed: {res.status_code} {res.text}"
    job_id = res.json()["id"]
    print(f"✓ POST /jobs/ passed (Job ID: {job_id})")

    print(f"Testing GET /jobs/{job_id}")
    res = client.get(f"/jobs/{job_id}")
    assert res.status_code == 200, f"GET /jobs/{job_id} failed: {res.status_code} {res.text}"
    print(f"✓ GET /jobs/{job_id} passed")

    print(f"Testing PUT /jobs/{job_id}")
    res = client.put(f"/jobs/{job_id}", json={"title": "Senior Software Engineer"})
    assert res.status_code == 200, f"PUT /jobs/{job_id} failed: {res.status_code} {res.text}"
    assert res.json()["title"] == "Senior Software Engineer"
    print(f"✓ PUT /jobs/{job_id} passed")

    print(f"Testing POST /jobs/{job_id}/resumes/ (Success Case)")
    with open("dummy.pdf", "wb") as f:
        f.write(b"%PDF-1.4 dummy content")
    with open("dummy.pdf", "rb") as f:
        res = client.post(
            f"/jobs/{job_id}/resumes/", 
            files={"file": ("dummy.pdf", f, "application/pdf")}
        )
    assert res.status_code == 201, f"POST /jobs/{job_id}/resumes/ failed: {res.status_code} {res.text}"
    resume_id = res.json()["id"]
    print(f"✓ POST /jobs/{job_id}/resumes/ passed (Resume ID: {resume_id})")

    print(f"Testing POST /jobs/{job_id}/resumes/ (Invalid Type)")
    with open("dummy.txt", "wb") as f:
        f.write(b"text content")
    with open("dummy.txt", "rb") as f:
        res = client.post(
            f"/jobs/{job_id}/resumes/", 
            files={"file": ("dummy.txt", f, "text/plain")}
        )
    assert res.status_code == 400, f"Expected 400, got: {res.status_code} {res.text}"
    print(f"✓ POST invalid type passed")

    print(f"Testing GET /jobs/{job_id}/rankings/")
    res = client.get(f"/jobs/{job_id}/rankings/")
    assert res.status_code == 200, f"GET /jobs/{job_id}/rankings/ failed: {res.status_code} {res.text}"
    print(f"✓ GET /jobs/{job_id}/rankings/ passed")

    print(f"Testing GET /resumes/{resume_id}")
    res = client.get(f"/resumes/{resume_id}")
    assert res.status_code == 200, f"GET /resumes/{resume_id} failed: {res.status_code} {res.text}"
    print(f"✓ GET /resumes/{resume_id} passed")

    print(f"Testing DELETE /jobs/{job_id}")
    res = client.delete(f"/jobs/{job_id}")
    assert res.status_code == 204, f"DELETE /jobs/{job_id} failed: {res.status_code} {res.text}"
    print(f"✓ DELETE /jobs/{job_id} passed")
    
    res = client.get(f"/jobs/{job_id}")
    assert res.status_code == 404, f"Expected 404 after delete, got {res.status_code}"
    
    print("\n✅ All endpoints tested successfully! Zero 500 Internal Server Errors detected.")

if __name__ == "__main__":
    test_api()
