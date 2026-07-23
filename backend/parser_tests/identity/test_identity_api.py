from app.main import app
import pytest

@pytest.fixture
def setup_identity(client):
    # Setup test org
    org_res = client.post("/identity/organizations", json={
        "name": "Test Org",
        "slug": "test-org-123"
    })
    org_id = org_res.json()["id"]

    # Setup test user
    user_res = client.post("/identity/users", json={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.identity@example.com",
        "password": "strongpassword123",
        "organization_id": org_id
    })
    
    return {
        "org_id": org_id,
        "user": user_res.json()
    }

def test_organization_creation(setup_identity):
    assert setup_identity["org_id"] is not None

def test_user_creation(setup_identity):
    user = setup_identity["user"]
    assert user["email"] == "john.identity@example.com"
    assert user["is_active"] is True
    
def test_user_login(client, setup_identity):
    res = client.post("/identity/auth/login", json={
        "email": "john.identity@example.com",
        "password": "strongpassword123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    
def test_get_me(client, setup_identity):
    # Login first
    login_res = client.post("/identity/auth/login", json={
        "email": "john.identity@example.com",
        "password": "strongpassword123"
    })
    token = login_res.json()["access_token"]
    
    # Use token
    res = client.get("/identity/users/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "john.identity@example.com"

def test_get_me_unauthorized(client):
    res = client.get("/identity/users/me", headers={"Authorization": "Bearer invalidtoken"})
    assert res.status_code == 401
