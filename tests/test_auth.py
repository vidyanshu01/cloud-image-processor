from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "auth_test_user",
            "email": "auth_test@example.com",
            "password": "StrongPassword123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    # Registration returns JWT + user
    assert "access_token" in data
    assert data["access_token"]

    assert data["token_type"].lower() == "bearer"

    # User information is nested under "user"
    assert "user" in data

    user = data["user"]

    assert "id" in user
    assert user["username"] == "auth_test_user"
    assert user["email"] == "auth_test@example.com"

    # Password must never be returned
    assert "password" not in user
    assert "hashed_password" not in user
    
def test_login_user(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "login_test_user",
            "email": "login_test@example.com",
            "password": "StrongPassword123",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "login_test_user",
            "password": "StrongPassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["access_token"]
    assert data["token_type"].lower() == "bearer"

    assert "user" in data
    assert data["user"]["username"] == "login_test_user"


def test_jwt_token_is_returned(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "jwt_test_user",
            "email": "jwt_test@example.com",
            "password": "StrongPassword123",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "jwt_test_user",
            "password": "StrongPassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()
    token = data["access_token"]

    # JWT consists of three dot-separated sections
    parts = token.split(".")

    assert len(parts) == 3
    assert all(parts)


def test_me_with_valid_jwt(client: TestClient):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "me_test_user",
            "email": "me_test@example.com",
            "password": "StrongPassword123",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "me_test_user",
            "password": "StrongPassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "me_test_user"
    assert data["email"] == "me_test@example.com"


def test_duplicate_username(client: TestClient):
    payload = {
        "username": "duplicate_user",
        "email": "duplicate1@example.com",
        "password": "StrongPassword123",
    }

    first_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicate_user",
            "email": "duplicate2@example.com",
            "password": "StrongPassword123",
        },
    )

    assert second_response.status_code in (400, 409)


def test_duplicate_email(client: TestClient):
    first_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicate_email_user1",
            "email": "same_email@example.com",
            "password": "StrongPassword123",
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicate_email_user2",
            "email": "same_email@example.com",
            "password": "StrongPassword123",
        },
    )

    assert second_response.status_code in (400, 409)


def test_invalid_credentials(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "invalid_login_user",
            "email": "invalid_login@example.com",
            "password": "StrongPassword123",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "invalid_login_user",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert "detail" in data


def test_invalid_jwt(client: TestClient):
    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": "Bearer invalid.jwt.token",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert "detail" in data