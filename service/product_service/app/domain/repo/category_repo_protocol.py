import uuid
from typing import Protocol

from app.domain.entity.category_entity import CategoryEntity, CreateCategory


class CategoryRepository(Protocol):
    async def get_by_id(self, category_id: uuid.UUID) -> CategoryEntity | None: ...

    async def get_by_slug(self, slug: str) -> CategoryEntity | None: ...

    async def list(self) -> list[CategoryEntity]: ...

    async def create(self, data: CreateCategory) -> CategoryEntity: ...
