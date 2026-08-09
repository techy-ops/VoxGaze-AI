import pytest


def test_user_registration_and_login_flow(client):
    """
    Test complete authentication lifecycle: registration, login, profile fetch (/auth/me),
    token refresh, and logout.
    """
    email = "phase2_user@voxgaze.ai"
    password = "SecurePassword123!"

    # 1. Register User
    reg_payload = {
        "email": email,
        "password": password,
        "display_name": "Phase2 User",
    }
    reg_response = client.post("/auth/register", json=reg_payload)
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert reg_data["status"] == "success"
    assert reg_data["email"] == email
    assert "user_id" in reg_data
    uid = reg_data["user_id"]

    # 2. Login User
    login_payload = {"email": email, "password": password}
    login_response = client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["status"] == "success"
    assert "access_token" in login_data
    assert "refresh_token" in login_data
    assert login_data["token_type"] == "Bearer"
    access_token = login_data["access_token"]
    refresh_token = login_data["refresh_token"]

    # 3. Access Protected /auth/me with Bearer JWT Header
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["status"] == "success"
    assert me_data["user_id"] == uid
    assert me_data["email"] == email
    assert me_data["display_name"] == "Phase2 User"
    assert me_data["profile_completed"] is True

    # 4. Refresh Token
    refresh_response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    assert refresh_data["status"] == "success"
    assert "access_token" in refresh_data

    # 5. Logout
    logout_response = client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert logout_response.status_code == 200
    assert logout_response.json()["status"] == "success"


def test_auth_me_unauthorized_without_token(client):
    """Test accessing GET /auth/me without Bearer token returns 401 Unauthorized or 403 Forbidden."""
    response = client.get("/auth/me")
    assert response.status_code in [401, 403]


def test_duplicate_registration_error(client):
    """Test registering an existing email returns 400 Bad Request."""
    email = "duplicate@voxgaze.ai"
    payload = {"email": email, "password": "SecurePassword123!", "display_name": "User 1"}
    
    res1 = client.post("/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_invalid_login_credentials(client):
    """Test login with wrong password returns 401 Unauthorized."""
    payload = {"email": "nonexistent@voxgaze.ai", "password": "WrongPassword"}
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 401


def test_forgot_password_and_verify_email(client):
    """Test POST /auth/forgot-password and POST /auth/verify-email endpoints."""
    fp_res = client.post("/auth/forgot-password", json={"email": "user@voxgaze.ai"})
    assert fp_res.status_code == 200
    assert fp_res.json()["status"] == "success"

    ve_res = client.post("/auth/verify-email", json={"email": "user@voxgaze.ai"})
    assert ve_res.status_code == 200
    assert ve_res.json()["status"] == "success"
