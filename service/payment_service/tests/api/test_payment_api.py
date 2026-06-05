import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.entity.payment_entity import PaymentProvider, PaymentStatus


def _mock_current_user(user_id: uuid.UUID):
    from app.presentation.deps import CurrentUser, get_current_user

    user = CurrentUser(id=user_id)

    async def _override():
        return user

    return get_current_user, _override


@pytest.mark.asyncio
async def test_create_payment_unauthorized(client):
    response = await client.post(
        "/api/v1/payments",
        json={"order_id": str(uuid.uuid4()), "provider": PaymentProvider.KASPI},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_webhook_kaspi_accepted(client):
    with patch(
        "app.application.service.payment_service.PaymentService.handle_webhook",
        new_callable=AsyncMock,
    ):
        response = await client.post(
            "/api/v1/webhooks/kaspi",
            json={"txn_id": "abc123", "status": "payment.success"},
        )
    assert response.status_code == 200
    assert response.json()["result"] == 0


@pytest.mark.asyncio
async def test_webhook_stripe_accepted(client):
    with patch(
        "app.application.service.payment_service.PaymentService.handle_webhook",
        new_callable=AsyncMock,
    ):
        response = await client.post(
            "/api/v1/webhooks/stripe",
            json={"type": "payment_intent.succeeded", "data": {"object": {"id": "pi_xxx"}}},
        )
    assert response.status_code == 200
    assert response.json()["received"] is True


@pytest.mark.asyncio
async def test_webhook_freedompay_accepted(client):
    with patch(
        "app.application.service.payment_service.PaymentService.handle_webhook",
        new_callable=AsyncMock,
    ):
        response = await client.post(
            "/api/v1/webhooks/freedompay",
            json={"pg_payment_id": "fp-999", "pg_result": "1"},
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/v1/health_check")
    assert response.status_code in (200, 503)
