import uuid
from dataclasses import dataclass
from typing import Protocol

from app.domain.entity.payment_entity import PaymentEventEntity


@dataclass
class CreatePaymentEvent:
    payment_id: uuid.UUID
    provider: str
    event_type: str
    payload: dict


class PaymentEventRepository(Protocol):
    async def create(self, data: CreatePaymentEvent) -> PaymentEventEntity: ...

    async def get_by_payment_id(self, payment_id: uuid.UUID) -> list[PaymentEventEntity]: ...
