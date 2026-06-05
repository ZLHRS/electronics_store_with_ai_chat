import logging
import uuid
from dataclasses import dataclass
from decimal import Decimal

import httpx

logger = logging.getLogger(__name__)


@dataclass
class OrderInfo:
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    total: Decimal


class OrderServiceClient:
    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    async def get_order(self, order_id: uuid.UUID) -> OrderInfo | None:
        try:
            response = await self._client.get(f"/api/v1/orders/{order_id}")
        except httpx.RequestError as e:
            logger.warning("Order service unavailable: %s", e)
            return None
        if response.status_code == 404:
            return None
        if not response.is_success:
            logger.warning(
                "Order service returned %s for order_id=%s", response.status_code, order_id
            )
            return None
        data = response.json()
        return OrderInfo(
            id=uuid.UUID(data["id"]),
            user_id=uuid.UUID(data["user_id"]),
            status=data["status"],
            total=Decimal(str(data["total"])),
        )

    async def notify_payment_paid(self, order_id: uuid.UUID, payment_id: uuid.UUID) -> None:
        try:
            await self._client.post(
                f"/api/v1/orders/{order_id}/payment-confirmed",
                json={"payment_id": str(payment_id)},
            )
        except httpx.RequestError as e:
            logger.warning(
                "Failed to notify order_service of payment.paid order_id=%s: %s", order_id, e
            )

    async def notify_payment_failed(self, order_id: uuid.UUID) -> None:
        try:
            await self._client.post(f"/api/v1/orders/{order_id}/payment-failed")
        except httpx.RequestError as e:
            logger.warning(
                "Failed to notify order_service of payment.failed order_id=%s: %s", order_id, e
            )
