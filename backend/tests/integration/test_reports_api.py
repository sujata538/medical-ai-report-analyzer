"""Integration tests for report listing/search (requires authentication)."""


def _register_and_login(client, email="reports@example.com"):
    client.post("/api/v1/auth/register", json={"email": email, "full_name": "Reports User", "password": "Password123"})
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123"})
    return resp.json()["tokens"]["access_token"]


def test_list_reports_empty_for_new_user(client):
    token = _register_and_login(client)
    resp = client.get("/api/v1/reports", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_dashboard_stats_for_new_user(client):
    token = _register_and_login(client, email="dashboard@example.com")
    resp = client.get("/api/v1/dashboard/stats", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_reports"] == 0
    assert body["average_health_score"] is None
