import logging

import uuid

from app.application.dto.product_dto import BrandResult, CreateBrandCommand, UpdateBrandCommand
from app.domain.entity.brand_entity import CreateBrand
from app.domain.repo.brand_repo_protocol import BrandRepository
from app.exceptions import BrandNotFoundError, SlugAlreadyExistsError
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

    async def update_brand(self, brand_id: uuid.UUID, command: UpdateBrandCommand) -> BrandResult:
        if not await self._brands.get_by_id(brand_id):
            raise BrandNotFoundError(f"Brand {brand_id} not found")
        new_slug = command.slug or (slugify(command.name) if command.name else None)
        if new_slug:
            existing = await self._brands.get_by_slug(new_slug)
            if existing and existing.id != brand_id:
                raise SlugAlreadyExistsError(f"Slug '{new_slug}' already taken")
        brand = await self._brands.update(brand_id, name=command.name, slug=new_slug)
        logger.info("Brand updated id=%s", brand_id)
        return _to_result(brand)

    async def delete_brand(self, brand_id: uuid.UUID) -> None:
        if not await self._brands.get_by_id(brand_id):
            raise BrandNotFoundError(f"Brand {brand_id} not found")
        await self._brands.delete(brand_id)
        logger.info("Brand deleted id=%s", brand_id)


def _to_result(brand) -> BrandResult:
    return BrandResult(id=brand.id, name=brand.name, slug=brand.slug)
