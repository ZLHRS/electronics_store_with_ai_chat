import logging
import uuid

from app.application.dto.product_dto import (
    CategoryResult,
    CreateCategoryCommand,
    UpdateCategoryCommand,
)
from app.domain.entity.category_entity import CreateCategory
from app.domain.repo.category_repo_protocol import CategoryRepository
from app.exceptions import CategoryNotFoundError, SlugAlreadyExistsError
from app.infrastructure.slugify import slugify

logger = logging.getLogger(__name__)


class CategoryService:
    def __init__(self, category_repository: CategoryRepository):
        self._categories = category_repository

    async def list_categories(self) -> list[CategoryResult]:
        categories = await self._categories.list()
        return [_to_result(c) for c in categories]

    async def create_category(self, command: CreateCategoryCommand) -> CategoryResult:
        slug = command.slug or slugify(command.name)
        if await self._categories.get_by_slug(slug):
            raise SlugAlreadyExistsError(f"Slug '{slug}' already taken")
        category = await self._categories.create(
            CreateCategory(name=command.name, slug=slug, parent_id=command.parent_id)
        )
        logger.info("Category created slug=%s", slug)
        return _to_result(category)

    async def update_category(
        self, category_id: uuid.UUID, command: UpdateCategoryCommand
    ) -> CategoryResult:
        if not await self._categories.get_by_id(category_id):
            raise CategoryNotFoundError(f"Category {category_id} not found")
        new_slug = command.slug or (slugify(command.name) if command.name else None)
        if new_slug and await self._categories.get_by_slug(new_slug):
            existing = await self._categories.get_by_slug(new_slug)
            if existing and existing.id != category_id:
                raise SlugAlreadyExistsError(f"Slug '{new_slug}' already taken")
        category = await self._categories.update(category_id, name=command.name, slug=new_slug)
        logger.info("Category updated id=%s", category_id)
        return _to_result(category)

    async def delete_category(self, category_id: uuid.UUID) -> None:
        if not await self._categories.get_by_id(category_id):
            raise CategoryNotFoundError(f"Category {category_id} not found")
        await self._categories.delete(category_id)
        logger.info("Category deleted id=%s", category_id)


def _to_result(category) -> CategoryResult:
    return CategoryResult(
        id=category.id,
        name=category.name,
        slug=category.slug,
        parent_id=category.parent_id,
    )
