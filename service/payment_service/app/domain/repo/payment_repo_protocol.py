import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from app.domain.entity.payment_entity import PaymentEntity


@dataclass
class CreatePayment:
    order_id: uuid.UUID
    user_id: uuid.UUID
    provider: str
    amount: Decimal
    currency: str
    provider_payment_id: str
    payment_url: str


class PaymentRepository(Protocol):
    async def get_by_id(self, payment_id: uuid.UUID) -> PaymentEntity | None: ...

    async def get_active_by_order_id(self, order_id: uuid.UUID) -> PaymentEntity | None: ...

    async def get_by_provider_payment_id(
        self, provider: str, provider_payment_id: str
    ) -> PaymentEntity | None: ...

    async def create(self, data: CreatePayment) -> PaymentEntity: ...

    async def update_status(
        self,
        payment_id: uuid.UUID,
        status: str,
        failure_reason: str | None = None,
    ) -> PaymentEntity: ...
