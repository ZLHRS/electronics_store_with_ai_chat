import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from app.domain.entity.payment_entity import PaymentProvider, PaymentStatus
from app.infrastructure.order_client import OrderInfo


def _make_order_info(user_id: uuid.UUID) -> OrderInfo:
    return OrderInfo(
        id=uuid.uuid4(),
        user_id=user_id,
        status="pending_payment",
        total=Decimal("15000"),
    )


@pytest.mark.asyncio
async def test_full_payment_flow_via_webhook(client, db_session):
    from app.infrastructure.db.repo.payment_repo import SQLAlchemyPaymentRepo
    from app.presentation.deps import CurrentUser, get_current_user

    user_id = uuid.uuid4()
    order = _make_order_info(user_id)

    user = CurrentUser(id=user_id)

    async def _override_user():
        return user

    client.app.dependency_overrides[get_current_user] = _override_user

    try:
        with (
            patch(
                "app.infrastructure.order_client.OrderServiceClient.get_order",
                new_callable=AsyncMock,
                return_value=order,
            ),
            patch(
                "app.infrastructure.order_client.OrderServiceClient.notify_payment_paid",
                new_callable=AsyncMock,
            ) as mock_notify,
        ):
            create_resp = await client.post(
                "/api/v1/payments",
                json={"order_id": str(order.id), "provider": PaymentProvider.KASPI},
            )
            assert create_resp.status_code == 201
            data = create_resp.json()
            assert data["status"] == PaymentStatus.CREATED
            assert data["payment_url"] is not None
            provider_payment_id = data["provider_payment_id"]

            webhook_resp = await client.post(
                "/api/v1/webhooks/kaspi",
                json={"txn_id": provider_payment_id, "status": "payment.success"},
            )
            assert webhook_resp.status_code == 200

            mock_notify.assert_called_once()

            payment_repo = SQLAlchemyPaymentRepo(db_session)
            payment_id = uuid.UUID(data["id"])
            payment = await payment_repo.get_by_id(payment_id)
            assert payment is not None
            assert payment.status == PaymentStatus.PAID
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)
