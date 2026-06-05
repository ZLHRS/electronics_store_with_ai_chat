import pytest

from app.presentation.deps import CurrentUser, get_current_user


@pytest.mark.asyncio
async def test_list_orders_unauthorized(client):
    response = await client.get("/api/v1/orders")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_orders_empty(client, app):
    import uuid

    user = CurrentUser(id=uuid.uuid4(), permissions=frozenset(["orders.read.own"]))
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        response = await client.get("/api/v1/orders")
        assert response.status_code == 200
        assert response.json() == []
    finally:
        app.dependency_overrides.pop(get_current_user, None)
