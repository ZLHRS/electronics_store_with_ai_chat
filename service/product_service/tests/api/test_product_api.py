import pytest

from app.presentation.deps import CurrentUser, get_current_user


@pytest.mark.asyncio
async def test_list_products_public(client):
    response = await client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_create_product_unauthorized(client):
    response = await client.post(
        "/api/v1/products",
        json={"name": "Test", "price": "100000"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_product_authorized(client, app):
    import uuid

    user = CurrentUser(
        id=uuid.uuid4(),
        permissions=frozenset(["products.create"]),
    )
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        response = await client.post(
            "/api/v1/products",
            json={
                "name": "Gaming PC",
                "price": "350000.00",
                "status": "active",
                "attributes": [
                    {"name": "CPU", "value": "Intel i5-12400F"},
                    {"name": "GPU", "value": "RTX 4060"},
                ],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Gaming PC"
        assert data["slug"] == "gaming-pc"
        assert len(data["attributes"]) == 2
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_list_categories_public(client):
    response = await client.get("/api/v1/categories")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_brands_public(client):
    response = await client.get("/api/v1/brands")
    assert response.status_code == 200
