import datetime
import uuid
from dataclasses import dataclass, field
from decimal import Decimal


class OrderStatus:
    CREATED = "created"
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    CANCELLABLE = {CREATED, PENDING_PAYMENT}


@dataclass
class OrderItemEntity:
    id: uuid.UUID
    order_id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


@dataclass
class OrderEntity:
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    total_amount: Decimal
    delivery_address: str
    payment_method: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    items: list[OrderItemEntity] = field(default_factory=list)


@dataclass
class CreateOrderItem:
    product_id: uuid.UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


@dataclass
class CreateOrder:
    user_id: uuid.UUID
    status: str
    total_amount: Decimal
    delivery_address: str
    payment_method: str
    items: list[CreateOrderItem]
