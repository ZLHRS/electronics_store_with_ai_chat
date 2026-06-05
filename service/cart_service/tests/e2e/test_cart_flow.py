import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from app.infrastructure.product_client import ProductInfo, ProductServiceClient
from app.presentation.deps import CurrentUser, get_current_user


def _make_product(product_id: uuid.UUID) -> ProductInfo:
    return ProductInfo(
        id=product_id,
        name="Gaming PC",
        price=Decimal("350000"),
        status="active",
        image_url="https://example.com/img.jpg",
    )


@pytest.mark.asyncio
async def test_full_cart_flow(client, app):
    user_id = uuid.uuid4()
    product_id = uuid.uuid4()

    user = CurrentUser(id=user_id)
    app.dependency_overrides[get_current_user] = lambda: user

    mock_client = AsyncMock(spec=ProductServiceClient)
    mock_client.get_product.return_value = _make_product(product_id)
    app.dependency_overrides[ProductServiceClient] = lambda: mock_client

    try:
        response = await client.get("/api/v1/cart")
        assert response.status_code == 200
        assert response.json()["items"] == []

        response = await client.post(
            "/api/v1/cart/items",
            json={"product_id": str(product_id), "quantity": 2},
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
        assert data["items"][0]["product"]["name"] == "Gaming PC"
        assert Decimal(data["total"]) == Decimal("700000")

        response = await client.post(
            "/api/v1/cart/items",
            json={"product_id": str(product_id), "quantity": 1},
        )
        assert response.status_code == 201
        assert response.json()["items"][0]["quantity"] == 3

        response = await client.patch(
            f"/api/v1/cart/items/{product_id}",
            json={"quantity": 5},
        )
        assert response.status_code == 200
        assert response.json()["items"][0]["quantity"] == 5

        response = await client.delete(f"/api/v1/cart/items/{product_id}")
        assert response.status_code == 200
        assert response.json()["items"] == []

        await client.post(
            "/api/v1/cart/items",
            json={"product_id": str(product_id), "quantity": 1},
        )

        response = await client.delete("/api/v1/cart")
        assert response.status_code == 200
        assert response.json()["items"] == []
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(ProductServiceClient, None)
