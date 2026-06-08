import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, Field

VALID_STATUSES = {
    "created",
    "pending_payment",
    "paid",
    "processing",
    "shipped",
    "delivered",
    "cancelled",
}


class PaymentConfirmedRequest(BaseModel):
    payment_id: uuid.UUID


class CreateOrderRequest(BaseModel):
    delivery_address: str = Field(min_length=1)
    payment_method: str = Field(min_length=1, max_length=64)


class UpdateStatusRequest(BaseModel):
    status: str = Field(
        pattern="^(created|pending_payment|paid|processing|shipped|delivered|cancelled)$"
    )


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class OrderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    total_amount: Decimal
    delivery_address: str
    payment_method: str
    items: list[OrderItemResponse]
    created_at: datetime.datetime
    updated_at: datetime.datetime
