import logging

from app.application.dto.product_dto import BrandResult, CreateBrandCommand
from app.domain.entity.brand_entity import CreateBrand
from app.domain.repo.brand_repo_protocol import BrandRepository
from app.exceptions import SlugAlreadyExistsError
from app.infrastructure.slugify import slugify

logger = logging.getLogger(__name__)


class BrandService:
    def __init__(self, brand_repository: BrandRepository):
        self._brands = brand_repository

    async def list_brands(self) -> list[BrandResult]:
        brands = await self._brands.list()
        return [_to_result(b) for b in brands]

    async def create_brand(self, command: CreateBrandCommand) -> BrandResult:
        slug = command.slug or slugify(command.name)
        if await self._brands.get_by_slug(slug):
            raise SlugAlreadyExistsError(f"Slug '{slug}' already taken")
        brand = await self._brands.create(CreateBrand(name=command.name, slug=slug))
        logger.info("Brand created slug=%s", slug)
        return _to_result(brand)


def _to_result(brand) -> BrandResult:
    return BrandResult(id=brand.id, name=brand.name, slug=brand.slug)
