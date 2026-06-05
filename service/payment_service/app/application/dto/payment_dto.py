import datetime
import uuid
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CreatePaymentCommand:
    order_id: uuid.UUID
    provider: str
    currency: str = "KZT"


@dataclass(frozen=True)
class WebhookPayload:
    provider: str
    event_type: str
    raw: dict


@dataclass(frozen=True)
class PaymentResult:
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
