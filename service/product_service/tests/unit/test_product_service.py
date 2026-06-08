import datetime
import uuid
from decimal import Decimal

import pytest

from app.application.dto.product_dto import (
    AttributeItemCommand,
    CreateProductCommand,
)
from app.application.service.product_service import ProductService
from app.domain.entity.product_entity import (
    CreateProduct,
    ProductEntity,
    ProductFilter,
    UpdateProduct,
)
from app.exceptions import ProductNotFoundError, SlugAlreadyExistsError


class FakeProductRepo:
    def __init__(self):
        self._store: dict[uuid.UUID, ProductEntity] = {}
        self._by_slug: dict[str, uuid.UUID] = {}

    async def get_by_id(self, product_id: uuid.UUID) -> ProductEntity | None:
        return self._store.get(product_id)

    async def get_by_slug(self, slug: str) -> ProductEntity | None:
        pid = self._by_slug.get(slug)
        return self._store.get(pid) if pid else None

    async def list(self, filter: ProductFilter) -> tuple[list[ProductEntity], int]:
        items = list(self._store.values())
        if filter.status:
            items = [p for p in items if p.status == filter.status]
        if filter.search:
            term = filter.search.lower()
            items = [p for p in items if term in p.name.lower()]
        return items[: filter.limit], len(items)

    async def create(self, data: CreateProduct) -> ProductEntity:
        now = datetime.datetime.now(datetime.UTC)
        product = ProductEntity(
            id=uuid.uuid4(),
            name=data.name,
            slug=data.slug,
            description=data.description,
            price=data.price,
            category_id=data.category_id,
            brand_id=data.brand_id,
            status=data.status,
            created_at=now,
            updated_at=now,
            images=[],
            attributes=[],
        )
        self._store[product.id] = product
        self._by_slug[product.slug] = product.id
        return product

    async def update(self, product_id: uuid.UUID, data: UpdateProduct) -> ProductEntity:
        p = self._store[product_id]
        updated = ProductEntity(
            id=p.id,
            name=data.name if data.name is not None else p.name,
            slug=data.slug if data.slug is not None else p.slug,
            description=data.description if data.description is not None else p.description,
            price=data.price if data.price is not None else p.price,
            category_id=data.category_id if data.category_id is not None else p.category_id,
            brand_id=data.brand_id if data.brand_id is not None else p.brand_id,
            status=data.status if data.status is not None else p.status,
            created_at=p.created_at,
            updated_at=datetime.datetime.now(datetime.UTC),
            images=p.images,
            attributes=p.attributes,
        )
        self._store[product_id] = updated
        return updated

    async def delete(self, product_id: uuid.UUID) -> None:
        product = self._store.pop(product_id, None)
        if product:
            self._by_slug.pop(product.slug, None)


@pytest.mark.asyncio
async def test_create_product_success():
    repo = FakeProductRepo()
    service = ProductService(repo)

    result = await service.create_product(
        CreateProductCommand(
            name="Gaming PC",
            price=Decimal("350000.00"),
            attributes=[
                AttributeItemCommand("CPU", "Intel i5-12400F"),
                AttributeItemCommand("GPU", "RTX 4060"),
                AttributeItemCommand("RAM", "16 GB"),
            ],
        )
    )

    assert result.name == "Gaming PC"
    assert result.slug == "gaming-pc"
    assert result.price == Decimal("350000.00")


@pytest.mark.asyncio
async def test_create_product_slug_conflict():
    repo = FakeProductRepo()
    service = ProductService(repo)

    await service.create_product(CreateProductCommand(name="Gaming PC", price=Decimal("350000")))

    with pytest.raises(SlugAlreadyExistsError):
        await service.create_product(
            CreateProductCommand(name="Gaming PC", price=Decimal("400000"))
        )


@pytest.mark.asyncio
async def test_get_product_not_found():
    repo = FakeProductRepo()
    service = ProductService(repo)

    with pytest.raises(ProductNotFoundError):
        await service.get_product(uuid.uuid4())


@pytest.mark.asyncio
async def test_delete_product_not_found():
    repo = FakeProductRepo()
    service = ProductService(repo)

    with pytest.raises(ProductNotFoundError):
        await service.delete_product(uuid.uuid4())


@pytest.mark.asyncio
async def test_list_products_with_search():
    repo = FakeProductRepo()
    service = ProductService(repo)

    await service.create_product(
        CreateProductCommand(name="Gaming PC", price=Decimal("350000"), status="active")
    )
    await service.create_product(
        CreateProductCommand(name="Office Laptop", price=Decimal("200000"), status="active")
    )

    result = await service.list_products(ProductFilter(search="gaming", status="active"))

    assert result.total == 1
    assert result.items[0].name == "Gaming PC"
