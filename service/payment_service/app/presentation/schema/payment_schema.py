import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.entity.payment_entity import PaymentProvider


class CreatePaymentRequest(BaseModel):
    order_id: uuid.UUID
    provider: str = Field(default=PaymentProvider.KASPI)
    currency: str = Field(default="KZT", min_length=3, max_length=8)


class PaymentResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    user_id: uuid.UUID
    provider: str
    amount: Decimal
    currency: str
    status: str
    provider_payment_id: str | None
    payment_url: str | None
    failure_reason: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


class WebhookKaspiRequest(BaseModel):
    txn_id: str | None = None
    payment_id: str | None = None
    status: str | None = None
    amount: Decimal | None = None
    error_message: str | None = None


class WebhookStripeRequest(BaseModel):
    id: str | None = None
    type: str | None = None
    data: dict | None = None


class WebhookFreedomPayRequest(BaseModel):
    pg_payment_id: str | None = None
    pg_result: str | None = None
    pg_error_description: str | None = None
