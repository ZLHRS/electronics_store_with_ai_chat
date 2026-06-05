import datetime
import uuid
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class AddItemCommand:
    product_id: uuid.UUID
    quantity: int


@dataclass(frozen=True)
class UpdateItemCommand:
    quantity: int


@dataclass(frozen=True)
class ProductSnapshot:
    name: str | None
    image_url: str | None
    current_price: Decimal | None
    status: str | None


@dataclass(frozen=True)
class CartItemResult:
    id: uuid.UUID
    cart_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    created_at: datetime.datetime
    updated_at: datetime.datetime
    product: ProductSnapshot | None


@dataclass(frozen=True)
class CartResult:
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    items: list[CartItemResult]
    total: Decimal
    created_at: datetime.datetime
    updated_at: datetime.datetime
