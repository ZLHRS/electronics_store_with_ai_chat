import json
from decimal import Decimal

from app.domain.entity.payment_entity import PaymentEntity, PaymentEventEntity
from app.infrastructure.db.model.payment_event_model import PaymentEventModel
from app.infrastructure.db.model.payment_model import PaymentModel


def payment_model_to_entity(model: PaymentModel) -> PaymentEntity:
    return PaymentEntity(
        id=model.id,
        order_id=model.order_id,
        user_id=model.user_id,
        provider=model.provider,
        amount=Decimal(str(model.amount)),
        currency=model.currency,
        status=model.status,
        provider_payment_id=model.provider_payment_id,
        payment_url=model.payment_url,
        failure_reason=model.failure_reason,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def payment_event_model_to_entity(model: PaymentEventModel) -> PaymentEventEntity:
    return PaymentEventEntity(
        id=model.id,
        payment_id=model.payment_id,
        provider=model.provider,
        event_type=model.event_type,
        payload=json.loads(model.payload) if isinstance(model.payload, str) else model.payload,
        created_at=model.created_at,
    )
