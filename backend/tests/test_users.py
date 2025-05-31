import pytest

USER_DATA = {
    "email": "user1@example.com",
    "full_name": "User One",
    "password": "userpass",
    "organization_id": None
}
UPDATED_NAME = "Updated User"


def test_read_users(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    # Should at least contain the superuser
    assert any(u["email"] == "admin@example.com" for u in data)


class TestUserLifecycle:
    """Test user CRUD operations in sequence."""
    
    user_id = None
    
    def test_create_user(self, client, token):
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            "/api/v1/users/",
            json=USER_DATA,
            headers=headers
        )
        assert response.status_code == 200
        user = response.json()
        assert user["email"] == USER_DATA["email"]
        TestUserLifecycle.user_id = user["id"]

    def test_get_user_by_id(self, client, token):
        headers = {"Authorization": f"Bearer {token}"}
        user_id = TestUserLifecycle.user_id
        assert user_id is not None, "User must be created first"
        response = client.get(f"/api/v1/users/{user_id}", headers=headers)
        assert response.status_code == 200
        user = response.json()
        assert user["id"] == user_id

    def test_update_user(self, client, token):
        headers = {"Authorization": f"Bearer {token}"}
        user_id = TestUserLifecycle.user_id
        assert user_id is not None, "User must be created first"
        response = client.put(
            f"/api/v1/users/{user_id}",
            json={"full_name": UPDATED_NAME},
            headers=headers
        )
        assert response.status_code == 200
        user = response.json()
        assert user["full_name"] == UPDATED_NAME

    def test_delete_user(self, client, token):
        headers = {"Authorization": f"Bearer {token}"}
        user_id = TestUserLifecycle.user_id
        assert user_id is not None, "User must be created first"
        response = client.delete(f"/api/v1/users/{user_id}", headers=headers)
        assert response.status_code == 200
        # subsequent get should 404
        response = client.get(f"/api/v1/users/{user_id}", headers=headers)
        assert response.status_code == 404
