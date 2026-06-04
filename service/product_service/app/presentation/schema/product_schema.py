import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class ImageItemRequest(BaseModel):
    image_url: str
    sort_order: int = 0


class AttributeItemRequest(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    value: str = Field(min_length=1, max_length=512)


class CreateProductRequest(BaseModel):
    name: str = Field(min_length=1, max_length=512)
    price: Decimal = Field(gt=0, decimal_places=2)
    slug: str | None = Field(default=None, max_length=512)
    description: str | None = None
    category_id: uuid.UUID | None = None
    brand_id: uuid.UUID | None = None
    status: str = Field(default="draft", pattern="^(draft|active|archived)$")
    images: list[ImageItemRequest] = Field(default_factory=list)
    attributes: list[AttributeItemRequest] = Field(default_factory=list)


class UpdateProductRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=512)
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    slug: str | None = Field(default=None, max_length=512)
    description: str | None = None
    category_id: uuid.UUID | None = None
    brand_id: uuid.UUID | None = None
    status: str | None = Field(default=None, pattern="^(draft|active|archived)$")
    images: list[ImageItemRequest] | None = None
    attributes: list[AttributeItemRequest] | None = None


class ImageResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    image_url: str
    sort_order: int


class AttributeResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    name: str
    value: str


class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    price: Decimal
    category_id: uuid.UUID | None
    brand_id: uuid.UUID | None
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    images: list[ImageResponse]
    attributes: list[AttributeResponse]


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    limit: int
