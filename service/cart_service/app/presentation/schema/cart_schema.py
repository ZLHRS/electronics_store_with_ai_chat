import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class AddItemRequest(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(ge=1)


class UpdateItemRequest(BaseModel):
    quantity: int = Field(ge=1)


class ProductSnapshotResponse(BaseModel):
    name: str | None
    image_url: str | None
    current_price: Decimal | None
    status: str | None


class CartItemResponse(BaseModel):
    id: uuid.UUID
    cart_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    created_at: datetime.datetime
    updated_at: datetime.datetime
    product: ProductSnapshotResponse | None


class CartResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    items: list[CartItemResponse]
    total: Decimal
    created_at: datetime.datetime
    updated_at: datetime.datetime
