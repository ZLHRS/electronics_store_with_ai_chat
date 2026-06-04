import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest


def _make_access_token(user_id: uuid.UUID) -> str:
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
async def test_full_profile_flow(client):
    user_id = uuid.uuid4()
    token = _make_access_token(user_id)

    response = await client.get(
        "/api/v1/users/me",
        cookies={"access_token": token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["auth_user_id"] == str(user_id)
    assert data["first_name"] is None

    response = await client.patch(
        "/api/v1/users/me",
        json={"first_name": "Алибек", "city": "Алматы"},
        cookies={"access_token": token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Алибек"
    assert data["city"] == "Алматы"


@pytest.mark.asyncio
async def test_address_flow(client):
    user_id = uuid.uuid4()
    token = _make_access_token(user_id)

    await client.get("/api/v1/users/me", cookies={"access_token": token})

    response = await client.post(
        "/api/v1/users/me/addresses",
        json={
            "city": "Алматы",
            "street": "ул. Абая",
            "house": "10",
            "apartment": "5",
            "is_default": True,
        },
        cookies={"access_token": token},
    )
    assert response.status_code == 201
    address = response.json()
    assert address["is_default"] is True

    response = await client.get(
        "/api/v1/users/me/addresses",
        cookies={"access_token": token},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.delete(
        f"/api/v1/users/me/addresses/{address['id']}",
        cookies={"access_token": token},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_favorites_flow(client):
    user_id = uuid.uuid4()
    product_id = uuid.uuid4()
    token = _make_access_token(user_id)

    await client.get("/api/v1/users/me", cookies={"access_token": token})

    response = await client.post(
        f"/api/v1/users/me/favorites/{product_id}",
        cookies={"access_token": token},
    )
    assert response.status_code == 201

    response = await client.get(
        "/api/v1/users/me/favorites",
        cookies={"access_token": token},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.post(
        f"/api/v1/users/me/favorites/{product_id}",
        cookies={"access_token": token},
    )
    assert response.status_code == 409

    response = await client.delete(
        f"/api/v1/users/me/favorites/{product_id}",
        cookies={"access_token": token},
    )
    assert response.status_code == 204
