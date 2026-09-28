def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "full_name": "New User",
            "password": "secret12",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["role"] == "user"
    assert "hashed_password" not in data


def test_register_duplicate_email(client, user):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": user.email,
            "full_name": "Another",
            "password": "secret12",
        },
    )
    assert response.status_code == 409


def test_register_validation_error(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "bad", "full_name": "", "password": "123"},
    )
    assert response.status_code == 422


def test_login_success(client, user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == user.email


def test_login_wrong_password(client, user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "wrong"},
    )
    assert response.status_code == 401


def test_me(client, auth_header, user):
    response = client.get("/api/v1/auth/me", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["email"] == user.email


def test_me_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
