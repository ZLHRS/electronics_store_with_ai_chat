import datetime
import uuid
from dataclasses import dataclass
from decimal import Decimal


class CartStatus:
    ACTIVE = "active"
    CHECKED_OUT = "checked_out"
    ABANDONED = "abandoned"


@dataclass
class CartEntity:
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class CartItemEntity:
    id: uuid.UUID
    cart_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit_price: Decimal
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class CreateCartItem:
    cart_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit_price: Decimal
