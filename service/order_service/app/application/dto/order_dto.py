import datetime
import uuid
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CreateOrderCommand:
    delivery_address: str
    payment_method: str


@dataclass(frozen=True)
class UpdateStatusCommand:
    status: str


@dataclass(frozen=True)
class OrderItemResult:
    id: uuid.UUID
    order_id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


@dataclass(frozen=True)
class OrderResult:
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    total_amount: Decimal
    delivery_address: str
    payment_method: str
    items: list[OrderItemResult]
    created_at: datetime.datetime
    updated_at: datetime.datetime
