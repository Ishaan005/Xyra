import pytest

USER_DATA = {
    "email": "user1@example.com",
    "full_name": "User One",
    "password": "userpass",
    "organization_id": None
}
UPDATED_NAME = "Updated User"


@pytest.fixture()
def created_user(client, token):
    """Create a user for testing and return its ID"""
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/users/",
        json=USER_DATA,
        headers=headers
    )
    if response.status_code == 200:
        user = response.json()
        assert user["email"] == USER_DATA["email"]
        return user["id"]
    
    # If already exists, fetch existing user
    list_response = client.get("/api/v1/users/", headers=headers)
    assert list_response.status_code == 200, f"Failed to list users: {list_response.status_code}, {list_response.text}"
    users = list_response.json()
    for user in users:
        if user.get("email") == USER_DATA["email"]:
            return user["id"]
    
    # If we get here, there was an unexpected error
    pytest.fail(f"User '{USER_DATA['email']}' not found and could not be created. Response: {response.status_code}, {response.text}")


def test_read_users(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    # Should at least contain the superuser
    assert any(u["email"] == "admin@example.com" for u in data)


def test_create_user(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/users/",
        json=USER_DATA,
        headers=headers
    )
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == USER_DATA["email"]


def test_get_user_by_id(client, token, created_user):
    headers = {"Authorization": f"Bearer {token}"}
    user_id = created_user
    response = client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == user_id


def test_update_user(client, token, created_user):
    headers = {"Authorization": f"Bearer {token}"}
    user_id = created_user
    response = client.put(
        f"/api/v1/users/{user_id}",
        json={"full_name": UPDATED_NAME},
        headers=headers
    )
    assert response.status_code == 200
    user = response.json()
    assert user["full_name"] == UPDATED_NAME


def test_delete_user(client, token, created_user):
    headers = {"Authorization": f"Bearer {token}"}
    user_id = created_user
    response = client.delete(f"/api/v1/users/{user_id}", headers=headers)
    assert response.status_code == 200
    # subsequent get should 404
    response = client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert response.status_code == 404
