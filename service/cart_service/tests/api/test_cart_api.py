import pytest

from app.presentation.deps import CurrentUser, get_current_user


@pytest.mark.asyncio
async def test_get_cart_unauthorized(client):
    response = await client.get("/api/v1/cart")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_cart_returns_empty(client, app):
    import uuid

    user = CurrentUser(id=uuid.uuid4())
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        response = await client.get("/api/v1/cart")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == "0"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
