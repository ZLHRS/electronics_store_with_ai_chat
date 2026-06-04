import uuid


def unique_email() -> str:
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


async def test_register_success(client):
    response = await client.post(
        "/api/v1/register",
        json={"email": unique_email(), "password": "StrongPass1"},
    )
    assert response.status_code == 200
    assert "email" in response.json()


async def test_register_existing_email_returns_409(client):
    payload = {"email": unique_email(), "password": "StrongPass1"}
    await client.post("/api/v1/register", json=payload)
    response = await client.post("/api/v1/register", json=payload)
    assert response.status_code == 409


async def test_register_invalid_email_returns_422(client):
    response = await client.post(
        "/api/v1/register",
        json={"email": "not-an-email", "password": "StrongPass1"},
    )
    assert response.status_code == 422


async def test_register_short_password_returns_422(client):
    response = await client.post(
        "/api/v1/register",
        json={"email": unique_email(), "password": "short"},
    )
    assert response.status_code == 422


async def test_login_success_sets_cookies(client):
    email = unique_email()
    await client.post("/api/v1/register", json={"email": email, "password": "StrongPass1"})
    response = await client.post("/api/v1/login", json={"email": email, "password": "StrongPass1"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


async def test_login_wrong_password_returns_401(client):
    email = unique_email()
    await client.post("/api/v1/register", json={"email": email, "password": "StrongPass1"})
    response = await client.post("/api/v1/login", json={"email": email, "password": "wrong"})
    assert response.status_code == 401


async def test_login_unknown_email_returns_401(client):
    response = await client.post(
        "/api/v1/login",
        json={"email": unique_email(), "password": "StrongPass1"},
    )
    assert response.status_code == 401
