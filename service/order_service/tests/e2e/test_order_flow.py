import uuid
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.infrastructure.cart_client import CartData, CartItemData, CartServiceClient
from app.infrastructure.product_client import ProductData, ProductServiceClient
from app.presentation.deps import CurrentUser, get_current_user


def _make_cart(product_id: uuid.UUID) -> CartData:
    return CartData(
        id=uuid.uuid4(),
        items=[CartItemData(product_id=product_id, quantity=1, unit_price=Decimal("390000"))],
    )


def _make_product(product_id: uuid.UUID) -> ProductData:
    return ProductData(
        id=product_id, name="Gaming PC RTX 4060", price=Decimal("390000"), status="active"
    )


@pytest.mark.asyncio
async def test_full_order_flow(client, app):
    user_id = uuid.uuid4()
    product_id = uuid.uuid4()

    user = CurrentUser(
        id=user_id,
        permissions=frozenset(["orders.read.own", "orders.update.own", "orders.update.all"]),
    )
    app.dependency_overrides[get_current_user] = lambda: user

    mock_cart = AsyncMock(spec=CartServiceClient)
    mock_cart.get_cart.return_value = _make_cart(product_id)
    mock_cart.clear_cart.return_value = None
    app.dependency_overrides[CartServiceClient] = lambda: mock_cart

    mock_product = AsyncMock(spec=ProductServiceClient)
    mock_product.get_product.return_value = _make_product(product_id)
    app.dependency_overrides[ProductServiceClient] = lambda: mock_product

    try:
        response = await client.post(
            "/api/v1/orders",
            json={"delivery_address": "Astana, Mangilik El 55", "payment_method": "kaspi"},
        )
        assert response.status_code == 201
        order = response.json()
        assert order["status"] == "pending_payment"
        assert Decimal(order["total_amount"]) == Decimal("390000")
        assert len(order["items"]) == 1
        assert order["items"][0]["product_name"] == "Gaming PC RTX 4060"
        assert mock_cart.clear_cart.called

        order_id = order["id"]

        response = await client.get("/api/v1/orders")
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = await client.get(f"/api/v1/orders/{order_id}")
        assert response.status_code == 200

        response = await client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "paid"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "paid"

        response = await client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "cancelled"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(CartServiceClient, None)
        app.dependency_overrides.pop(ProductServiceClient, None)
