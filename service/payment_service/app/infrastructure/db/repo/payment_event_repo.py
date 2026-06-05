import json
import uuid

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entity.payment_entity import PaymentEventEntity
from app.domain.repo.payment_event_repo_protocol import (
    CreatePaymentEvent,
    PaymentEventRepository,
)
from app.exceptions import DatabaseError
from app.infrastructure.db.model.payment_event_model import PaymentEventModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.payment_mapper import payment_event_model_to_entity


class SQLAlchemyPaymentEventRepo(SQLAlchemyBaseRepo, PaymentEventRepository):
    async def create(self, data: CreatePaymentEvent) -> PaymentEventEntity:
        model = PaymentEventModel(
            payment_id=data.payment_id,
            provider=data.provider,
            event_type=data.event_type,
            payload=json.dumps(data.payload),
        )
        self.session.add(model)
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to create payment event") from e
        return payment_event_model_to_entity(model)

    async def get_by_payment_id(self, payment_id: uuid.UUID) -> list[PaymentEventEntity]:
        stmt = select(PaymentEventModel).where(PaymentEventModel.payment_id == payment_id)
        try:
            results = (await self.session.execute(stmt)).scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get payment events") from e
        return [payment_event_model_to_entity(r) for r in results]
