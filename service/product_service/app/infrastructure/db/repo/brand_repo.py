import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.domain.entity.brand_entity import BrandEntity, CreateBrand
from app.domain.repo.brand_repo_protocol import BrandRepository
from app.exceptions import DatabaseError, DuplicateEntryError
from app.infrastructure.db.model.brand_model import BrandModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.brand_mapper import brand_model_to_entity


class SQLAlchemyBrandRepo(SQLAlchemyBaseRepo, BrandRepository):
    async def get_by_id(self, brand_id: uuid.UUID) -> BrandEntity | None:
        stmt = select(BrandModel).where(BrandModel.id == brand_id)
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get brand by id") from e
        return brand_model_to_entity(result) if result else None

    async def get_by_slug(self, slug: str) -> BrandEntity | None:
        stmt = select(BrandModel).where(BrandModel.slug == slug)
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get brand by slug") from e
        return brand_model_to_entity(result) if result else None

    async def list(self) -> list[BrandEntity]:
        stmt = select(BrandModel).order_by(BrandModel.name)
        try:
            rows = (await self.session.execute(stmt)).scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to list brands") from e
        return [brand_model_to_entity(r) for r in rows]

    async def create(self, data: CreateBrand) -> BrandEntity:
        model = BrandModel(name=data.name, slug=data.slug)
        self.session.add(model)
        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            raise DuplicateEntryError("Slug already exists")
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to create brand") from e
        return brand_model_to_entity(model)
