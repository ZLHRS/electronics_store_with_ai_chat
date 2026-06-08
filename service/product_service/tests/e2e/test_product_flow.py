import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest


def _make_access_token(user_id: uuid.UUID, permissions: list[str]) -> str:
    from app.config import setup_config

    config = setup_config()
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(UTC) + timedelta(minutes=30),
        "type": "access",
    }
    return jwt.encode(
        payload,
        config.jwt.secret_key.get_secret_value(),
        algorithm=config.jwt.algorithm,
    )


@pytest.mark.asyncio
async def test_full_product_crud_flow(client, app):

    from app.presentation.deps import CurrentUser, get_current_user

    user_id = uuid.uuid4()
    user = CurrentUser(
        id=user_id, permissions=frozenset(["products.create", "products.update", "products.delete"])
    )
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        response = await client.post(
            "/api/v1/categories",
            json={"name": "Компьютеры", "slug": "computers"},
        )
        assert response.status_code == 201
        category_id = response.json()["id"]

        response = await client.post(
            "/api/v1/brands",
            json={"name": "ASUS", "slug": "asus"},
        )
        assert response.status_code == 201
        brand_id = response.json()["id"]

        response = await client.post(
            "/api/v1/products",
            json={
                "name": "ASUS Gaming PC",
                "price": "350000.00",
                "status": "active",
                "category_id": category_id,
                "brand_id": brand_id,
                "images": [{"image_url": "https://example.com/pc.jpg", "sort_order": 0}],
                "attributes": [
                    {"name": "CPU", "value": "Intel i5-12400F"},
                    {"name": "GPU", "value": "RTX 4060"},
                    {"name": "RAM", "value": "16 GB"},
                ],
            },
        )
        assert response.status_code == 201
        product = response.json()
        product_id = product["id"]
        assert product["slug"] == "asus-gaming-pc"
        assert len(product["attributes"]) == 3

        response = await client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 200

        response = await client.get("/api/v1/products?status=active&attribute_gpu=RTX+4060")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

        response = await client.get("/api/v1/products?search=gaming")
        assert response.status_code == 200
        assert data["total"] >= 1

        response = await client.patch(
            f"/api/v1/products/{product_id}",
            json={"status": "archived"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "archived"

        response = await client.delete(f"/api/v1/products/{product_id}")
        assert response.status_code == 204

        response = await client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.pop(get_current_user, None)
