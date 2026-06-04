import uuid


async def test_full_auth_flow(client):
    email = f"e2e_{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongPass1"

    # register
    register = await client.post("/api/v1/register", json={"email": email, "password": password})
    assert register.status_code == 200

    # login — client jar now holds access_token + refresh_token
    login = await client.post("/api/v1/login", json={"email": email, "password": password})
    assert login.status_code == 200
    assert "refresh_token" in login.cookies

    # refresh — client sends cookies from jar automatically
    refresh = await client.post("/api/v1/refresh")
    assert refresh.status_code == 200
    assert "access_token" in refresh.json()

    # logout
    logout = await client.post("/api/v1/logout")
    assert logout.status_code == 200
    assert "message" in logout.json()

    # refresh after logout should fail
    retry = await client.post("/api/v1/refresh")
    assert retry.status_code == 401


async def test_token_reuse_revokes_all_sessions(client):
    email = f"reuse_{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongPass1"

    await client.post("/api/v1/register", json={"email": email, "password": password})
    login = await client.post("/api/v1/login", json={"email": email, "password": password})

    # Save original tokens before the first refresh updates the jar
    original_refresh = login.cookies["refresh_token"]
    original_access = login.cookies["access_token"]

    # first refresh — ok, jar updated with new tokens
    first_refresh = await client.post("/api/v1/refresh")
    assert first_refresh.status_code == 200
    new_refresh = first_refresh.cookies["refresh_token"]
    new_access = first_refresh.cookies["access_token"]

    # reuse the original token — triggers reuse detection, revokes all sessions
    client.cookies.set("refresh_token", original_refresh)
    client.cookies.set("access_token", original_access)
    reuse = await client.post("/api/v1/refresh")
    assert reuse.status_code == 401

    # new token from first refresh is also invalid now
    client.cookies.set("refresh_token", new_refresh)
    client.cookies.set("access_token", new_access)
    retry = await client.post("/api/v1/refresh")
    assert retry.status_code == 401
