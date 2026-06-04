import uuid
from typing import Protocol

from app.domain.entity.product_entity import (
    CreateProduct,
    ProductEntity,
    ProductFilter,
    UpdateProduct,
)


class ProductRepository(Protocol):
    async def get_by_id(self, product_id: uuid.UUID) -> ProductEntity | None: ...

    async def get_by_slug(self, slug: str) -> ProductEntity | None: ...

    async def list(self, filter: ProductFilter) -> tuple[list[ProductEntity], int]: ...

    async def create(self, data: CreateProduct) -> ProductEntity: ...

    async def update(self, product_id: uuid.UUID, data: UpdateProduct) -> ProductEntity: ...

    async def delete(self, product_id: uuid.UUID) -> None: ...
