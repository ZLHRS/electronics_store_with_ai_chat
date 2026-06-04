import datetime
import uuid
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class ImageItemCommand:
    image_url: str
    sort_order: int = 0


@dataclass(frozen=True)
class AttributeItemCommand:
    name: str
    value: str


@dataclass(frozen=True)
class CreateProductCommand:
    name: str
    price: Decimal
    slug: str | None = None
    description: str | None = None
    category_id: uuid.UUID | None = None
    brand_id: uuid.UUID | None = None
    status: str = "draft"
    images: list[ImageItemCommand] = field(default_factory=list)
    attributes: list[AttributeItemCommand] = field(default_factory=list)


@dataclass(frozen=True)
class UpdateProductCommand:
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    price: Decimal | None = None
    category_id: uuid.UUID | None = None
    brand_id: uuid.UUID | None = None
    status: str | None = None
    images: list[ImageItemCommand] | None = None
    attributes: list[AttributeItemCommand] | None = None


@dataclass(frozen=True)
class CreateCategoryCommand:
    name: str
    slug: str | None = None
    parent_id: uuid.UUID | None = None


@dataclass(frozen=True)
class CreateBrandCommand:
    name: str
    slug: str | None = None


@dataclass(frozen=True)
class ImageResult:
    id: uuid.UUID
    product_id: uuid.UUID
    image_url: str
    sort_order: int


@dataclass(frozen=True)
class AttributeResult:
    id: uuid.UUID
    product_id: uuid.UUID
    name: str
    value: str


@dataclass(frozen=True)
class ProductResult:
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
    images: list[ImageResult]
    attributes: list[AttributeResult]


@dataclass(frozen=True)
class ProductListResult:
    items: list[ProductResult]
    total: int
    page: int
    limit: int


@dataclass(frozen=True)
class CategoryResult:
    id: uuid.UUID
    name: str
    slug: str
    parent_id: uuid.UUID | None


@dataclass(frozen=True)
class BrandResult:
    id: uuid.UUID
    name: str
    slug: str
