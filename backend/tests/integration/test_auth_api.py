"""Integration tests for the authentication API endpoints."""


def test_register_and_login_flow(client):
    register_resp = client.post(
        "/api/v1/auth/register",
        json={"email": "integration@example.com", "full_name": "Integration Test", "password": "Password123"},
    )
    assert register_resp.status_code == 201

    login_resp = client.post(
        "/api/v1/auth/login", json={"email": "integration@example.com", "password": "Password123"}
    )
    assert login_resp.status_code == 200
    body = login_resp.json()
    assert "tokens" in body
    assert body["user"]["email"] == "integration@example.com"


def test_login_wrong_password_returns_401(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpw@example.com", "full_name": "Test", "password": "Password123"},
    )
    resp = client.post("/api/v1/auth/login", json={"email": "wrongpw@example.com", "password": "WrongPass1"})
    assert resp.status_code == 401


def test_me_requires_authentication(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
