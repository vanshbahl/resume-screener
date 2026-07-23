from fastapi.testclient import TestClient
from app.main import app
import traceback

client = TestClient(app, raise_server_exceptions=False)

response = client.get("/jobs/")
print("Status Code:", response.status_code)
print("Response:", response.text)

try:
    # Trigger exception directly to get traceback
    from app.core.database import SessionLocal
    from app.models.domain import Job
    db = SessionLocal()
    db.query(Job).all()
except Exception as e:
    traceback.print_exc()

