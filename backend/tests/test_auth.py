import pytest


def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={"username": "admin@example.com", "password": "adminpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data and data["token_type"] == "bearer"


def test_login_failure(client):
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={"username": "admin@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401


def test_read_users_me(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        "/api/v1/auth/me",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@example.com"
