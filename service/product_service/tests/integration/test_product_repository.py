import uuid
from decimal import Decimal

import pytest

from app.domain.entity.product_entity import (
    CreateAttributeItem,
    CreateImageItem,
    CreateProduct,
    ProductFilter,
    ProductStatus,
    UpdateProduct,
)
from app.infrastructure.db.repo.product_repo import SQLAlchemyProductRepo


@pytest.mark.asyncio
async def test_create_and_get_product(db_session):
    repo = SQLAlchemyProductRepo(db_session)

    product = await repo.create(
        CreateProduct(
            name="Gaming PC",
            slug="gaming-pc",
            description="High-end gaming PC",
            price=Decimal("350000.00"),
            category_id=None,
            brand_id=None,
            status=ProductStatus.ACTIVE,
            images=[CreateImageItem("https://example.com/img.jpg", 0)],
            attributes=[
                CreateAttributeItem("CPU", "Intel i5-12400F"),
                CreateAttributeItem("GPU", "RTX 4060"),
            ],
        )
    )

    assert product.slug == "gaming-pc"
    assert len(product.images) == 1
    assert len(product.attributes) == 2

    fetched = await repo.get_by_id(product.id)
    assert fetched is not None
    assert fetched.name == "Gaming PC"
    assert len(fetched.attributes) == 2


@pytest.mark.asyncio
async def test_list_products_with_attribute_filter(db_session):
    repo = SQLAlchemyProductRepo(db_session)

    await repo.create(
        CreateProduct(
            name="PC с RTX 4060",
            slug=f"pc-rtx-{uuid.uuid4().hex[:6]}",
            description=None,
            price=Decimal("350000"),
            category_id=None,
            brand_id=None,
            status=ProductStatus.ACTIVE,
            images=[],
            attributes=[CreateAttributeItem("GPU", "RTX 4060")],
        )
    )
    await repo.create(
        CreateProduct(
            name="PC с RTX 3060",
            slug=f"pc-rtx-{uuid.uuid4().hex[:6]}",
            description=None,
            price=Decimal("250000"),
            category_id=None,
            brand_id=None,
            status=ProductStatus.ACTIVE,
            images=[],
            attributes=[CreateAttributeItem("GPU", "RTX 3060")],
        )
    )

    items, total = await repo.list(
        ProductFilter(attributes={"GPU": "RTX 4060"}, status=ProductStatus.ACTIVE)
    )

    assert all("RTX 4060" in [a.value for a in p.attributes] for p in items)


@pytest.mark.asyncio
async def test_update_replaces_attributes(db_session):
    repo = SQLAlchemyProductRepo(db_session)

    product = await repo.create(
        CreateProduct(
            name="Laptop",
            slug=f"laptop-{uuid.uuid4().hex[:6]}",
            description=None,
            price=Decimal("200000"),
            category_id=None,
            brand_id=None,
            status=ProductStatus.DRAFT,
            images=[],
            attributes=[CreateAttributeItem("RAM", "8 GB")],
        )
    )

    updated = await repo.update(
        product.id,
        UpdateProduct(
            name=None, slug=None, description=None, price=None,
            category_id=None, brand_id=None, status=ProductStatus.ACTIVE,
            images=None,
            attributes=[CreateAttributeItem("RAM", "16 GB")],
        ),
    )

    assert updated.status == ProductStatus.ACTIVE
    assert len(updated.attributes) == 1
    assert updated.attributes[0].value == "16 GB"
