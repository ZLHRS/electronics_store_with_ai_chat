import logging
import uuid

from app.application.dto.product_dto import (
    AttributeResult,
    CreateProductCommand,
    ImageResult,
    ProductListResult,
    ProductResult,
    UpdateProductCommand,
)
from app.domain.entity.product_entity import (
    CreateAttributeItem,
    CreateImageItem,
    CreateProduct,
    ProductFilter,
    UpdateProduct,
)
from app.domain.repo.product_repo_protocol import ProductRepository
from app.exceptions import ProductNotFoundError, SlugAlreadyExistsError
from app.infrastructure.slugify import slugify

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self._products = product_repository

    async def list_products(self, filter: ProductFilter) -> ProductListResult:
        items, total = await self._products.list(filter)
        return ProductListResult(
            items=[_to_result(p) for p in items],
            total=total,
            page=filter.page,
            limit=filter.limit,
        )

    async def get_product(self, product_id: uuid.UUID) -> ProductResult:
        product = await self._products.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError("Product not found")
        return _to_result(product)

    async def create_product(self, command: CreateProductCommand) -> ProductResult:
        slug = command.slug or slugify(command.name)
        if await self._products.get_by_slug(slug):
            raise SlugAlreadyExistsError(f"Slug '{slug}' already taken")
        product = await self._products.create(
            CreateProduct(
                name=command.name,
                slug=slug,
                description=command.description,
                price=command.price,
                category_id=command.category_id,
                brand_id=command.brand_id,
                status=command.status,
                images=[CreateImageItem(i.image_url, i.sort_order) for i in command.images],
                attributes=[CreateAttributeItem(a.name, a.value) for a in command.attributes],
            )
        )
        logger.info("Product created slug=%s", slug)
        return _to_result(product)

    async def update_product(
        self, product_id: uuid.UUID, command: UpdateProductCommand
    ) -> ProductResult:
        existing = await self._products.get_by_id(product_id)
        if existing is None:
            raise ProductNotFoundError("Product not found")
        if command.slug and command.slug != existing.slug:
            if await self._products.get_by_slug(command.slug):
                raise SlugAlreadyExistsError(f"Slug '{command.slug}' already taken")
        product = await self._products.update(
            product_id,
            UpdateProduct(
                name=command.name,
                slug=command.slug,
                description=command.description,
                price=command.price,
                category_id=command.category_id,
                brand_id=command.brand_id,
                status=command.status,
                images=(
                    [CreateImageItem(i.image_url, i.sort_order) for i in command.images]
                    if command.images is not None
                    else None
                ),
                attributes=(
                    [CreateAttributeItem(a.name, a.value) for a in command.attributes]
                    if command.attributes is not None
                    else None
                ),
            ),
        )
        logger.info("Product updated product_id=%s", product_id)
        return _to_result(product)

    async def delete_product(self, product_id: uuid.UUID) -> None:
        existing = await self._products.get_by_id(product_id)
        if existing is None:
            raise ProductNotFoundError("Product not found")
        await self._products.delete(product_id)
        logger.info("Product deleted product_id=%s", product_id)


def _to_result(product) -> ProductResult:
    return ProductResult(
        id=product.id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        price=product.price,
        category_id=product.category_id,
        brand_id=product.brand_id,
        status=product.status,
        created_at=product.created_at,
        updated_at=product.updated_at,
        images=[
            ImageResult(id=i.id, product_id=i.product_id, image_url=i.image_url, sort_order=i.sort_order)
            for i in product.images
        ],
        attributes=[
            AttributeResult(id=a.id, product_id=a.product_id, name=a.name, value=a.value)
            for a in product.attributes
        ],
    )
