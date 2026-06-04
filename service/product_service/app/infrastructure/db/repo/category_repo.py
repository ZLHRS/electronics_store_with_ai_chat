import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.domain.entity.category_entity import CategoryEntity, CreateCategory
from app.domain.repo.category_repo_protocol import CategoryRepository
from app.exceptions import DatabaseError, DuplicateEntryError
from app.infrastructure.db.model.category_model import CategoryModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.category_mapper import category_model_to_entity


class SQLAlchemyCategoryRepo(SQLAlchemyBaseRepo, CategoryRepository):
    async def get_by_id(self, category_id: uuid.UUID) -> CategoryEntity | None:
        stmt = select(CategoryModel).where(CategoryModel.id == category_id)
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get category by id") from e
        return category_model_to_entity(result) if result else None

    async def get_by_slug(self, slug: str) -> CategoryEntity | None:
        stmt = select(CategoryModel).where(CategoryModel.slug == slug)
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get category by slug") from e
        return category_model_to_entity(result) if result else None

    async def list(self) -> list[CategoryEntity]:
        stmt = select(CategoryModel).order_by(CategoryModel.name)
        try:
            rows = (await self.session.execute(stmt)).scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to list categories") from e
        return [category_model_to_entity(r) for r in rows]

    async def create(self, data: CreateCategory) -> CategoryEntity:
        model = CategoryModel(name=data.name, slug=data.slug, parent_id=data.parent_id)
        self.session.add(model)
        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            raise DuplicateEntryError("Slug already exists")
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to create category") from e
        return category_model_to_entity(model)
