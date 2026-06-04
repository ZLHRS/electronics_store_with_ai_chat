import datetime
import uuid
from dataclasses import dataclass, field
from decimal import Decimal


class ProductStatus:
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass
class ProductImageEntity:
    id: uuid.UUID
    product_id: uuid.UUID
    image_url: str
    sort_order: int


@dataclass
class ProductAttributeEntity:
    id: uuid.UUID
    product_id: uuid.UUID
    name: str
    value: str


@dataclass
class ProductEntity:
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
    images: list[ProductImageEntity] = field(default_factory=list)
    attributes: list[ProductAttributeEntity] = field(default_factory=list)


@dataclass
class CreateImageItem:
    image_url: str
    sort_order: int = 0


@dataclass
class CreateAttributeItem:
    name: str
    value: str


@dataclass
class CreateProduct:
    name: str
    slug: str | None
    description: str | None
    price: Decimal
    category_id: uuid.UUID | None
    brand_id: uuid.UUID | None
    status: str
    images: list[CreateImageItem]
    attributes: list[CreateAttributeItem]


@dataclass
class UpdateProduct:
    name: str | None
    slug: str | None
    description: str | None
    price: Decimal | None
    category_id: uuid.UUID | None
    brand_id: uuid.UUID | None
    status: str | None
    images: list[CreateImageItem] | None
    attributes: list[CreateAttributeItem] | None


@dataclass(frozen=True)
class ProductFilter:
    category_slug: str | None = None
    brand_slug: str | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    search: str | None = None
    attributes: dict[str, str] = field(default_factory=dict)
    status: str | None = ProductStatus.ACTIVE
    page: int = 1
    limit: int = 20
