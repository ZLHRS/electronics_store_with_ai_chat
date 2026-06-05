import datetime
import uuid
from dataclasses import dataclass
from decimal import Decimal


class PaymentStatus:
    CREATED = "created"
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentProvider:
    KASPI = "kaspi"
    STRIPE = "stripe"
    FREEDOMPAY = "freedompay"

    ALL = {KASPI, STRIPE, FREEDOMPAY}


@dataclass
class PaymentEntity:
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


@dataclass
class PaymentEventEntity:
    id: uuid.UUID
    payment_id: uuid.UUID
    provider: str
    event_type: str
    payload: dict
    created_at: datetime.datetime
