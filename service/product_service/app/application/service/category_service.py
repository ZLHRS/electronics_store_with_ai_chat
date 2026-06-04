import logging

from app.application.dto.product_dto import CategoryResult, CreateCategoryCommand
from app.domain.entity.category_entity import CreateCategory
from app.domain.repo.category_repo_protocol import CategoryRepository
from app.exceptions import SlugAlreadyExistsError
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


def _to_result(category) -> CategoryResult:
    return CategoryResult(
        id=category.id,
        name=category.name,
        slug=category.slug,
        parent_id=category.parent_id,
    )
