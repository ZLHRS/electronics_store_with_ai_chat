from __future__ import annotations

import datetime
import uuid

from sqlalchemy import delete, func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.domain.entity.product_entity import (
    CreateProduct,
    ProductEntity,
    ProductFilter,
    UpdateProduct,
)
from app.domain.repo.product_repo_protocol import ProductRepository
from app.exceptions import DatabaseError, DuplicateEntryError
from app.infrastructure.db.model.brand_model import BrandModel
from app.infrastructure.db.model.category_model import CategoryModel
from app.infrastructure.db.model.product_attribute_model import ProductAttributeModel
from app.infrastructure.db.model.product_image_model import ProductImageModel
from app.infrastructure.db.model.product_model import ProductModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.product_mapper import product_model_to_entity


class SQLAlchemyProductRepo(SQLAlchemyBaseRepo, ProductRepository):
    async def get_by_id(self, product_id: uuid.UUID) -> ProductEntity | None:
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        try:
            model = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get product by id") from e
        if model is None:
            return None
        images = await self._load_images([product_id])
        attributes = await self._load_attributes([product_id])
        return product_model_to_entity(model, images.get(product_id, []), attributes.get(product_id, []))

    async def get_by_slug(self, slug: str) -> ProductEntity | None:
        stmt = select(ProductModel).where(ProductModel.slug == slug)
        try:
            model = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get product by slug") from e
        if model is None:
            return None
        images = await self._load_images([model.id])
        attributes = await self._load_attributes([model.id])
        return product_model_to_entity(model, images.get(model.id, []), attributes.get(model.id, []))

    async def list(self, filter: ProductFilter) -> tuple[list[ProductEntity], int]:
        stmt = select(ProductModel)

        if filter.category_slug:
            stmt = stmt.join(CategoryModel, ProductModel.category_id == CategoryModel.id)
            stmt = stmt.where(CategoryModel.slug == filter.category_slug)

        if filter.brand_slug:
            stmt = stmt.join(BrandModel, ProductModel.brand_id == BrandModel.id)
            stmt = stmt.where(BrandModel.slug == filter.brand_slug)

        if filter.min_price is not None:
            stmt = stmt.where(ProductModel.price >= filter.min_price)

        if filter.max_price is not None:
            stmt = stmt.where(ProductModel.price <= filter.max_price)

        if filter.search:
            term = f"%{filter.search.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(ProductModel.name).like(term),
                    func.lower(ProductModel.description).like(term),
                )
            )

        if filter.status:
            stmt = stmt.where(ProductModel.status == filter.status)

        for attr_name, attr_value in filter.attributes.items():
            subq = (
                select(ProductAttributeModel.product_id)
                .where(
                    func.lower(ProductAttributeModel.name) == attr_name.lower(),
                    func.lower(ProductAttributeModel.value) == attr_value.lower(),
                )
                .scalar_subquery()
            )
            stmt = stmt.where(ProductModel.id.in_(subq))

        try:
            total = await self.session.scalar(
                select(func.count()).select_from(stmt.subquery())
            )
            offset = (filter.page - 1) * filter.limit
            rows = (
                await self.session.execute(
                    stmt.order_by(ProductModel.created_at.desc()).offset(offset).limit(filter.limit)
                )
            ).scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to list products") from e

        if not rows:
            return [], total or 0

        product_ids = [r.id for r in rows]
        images = await self._load_images(product_ids)
        attributes = await self._load_attributes(product_ids)

        return (
            [product_model_to_entity(r, images.get(r.id, []), attributes.get(r.id, [])) for r in rows],
            total or 0,
        )

    async def create(self, data: CreateProduct) -> ProductEntity:
        model = ProductModel(
            name=data.name,
            slug=data.slug,
            description=data.description,
            price=data.price,
            category_id=data.category_id,
            brand_id=data.brand_id,
            status=data.status,
        )
        self.session.add(model)
        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            raise DuplicateEntryError("Slug already exists")
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to create product") from e

        image_models = await self._replace_images(model.id, data.images)
        attr_models = await self._replace_attributes(model.id, data.attributes)

        return product_model_to_entity(model, image_models, attr_models)

    async def update(self, product_id: uuid.UUID, data: UpdateProduct) -> ProductEntity:
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        try:
            model = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to fetch product for update") from e
        if model is None:
            raise DatabaseError("Product not found")

        if data.name is not None:
            model.name = data.name
        if data.slug is not None:
            model.slug = data.slug
        if data.description is not None:
            model.description = data.description
        if data.price is not None:
            model.price = data.price
        if data.category_id is not None:
            model.category_id = data.category_id
        if data.brand_id is not None:
            model.brand_id = data.brand_id
        if data.status is not None:
            model.status = data.status
        model.updated_at = datetime.datetime.now(datetime.UTC)

        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            raise DuplicateEntryError("Slug already exists")
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to update product") from e

        if data.images is not None:
            image_models = await self._replace_images(product_id, data.images)
        else:
            image_models = (await self._load_images([product_id])).get(product_id, [])

        if data.attributes is not None:
            attr_models = await self._replace_attributes(product_id, data.attributes)
        else:
            attr_models = (await self._load_attributes([product_id])).get(product_id, [])

        return product_model_to_entity(model, image_models, attr_models)

    async def delete(self, product_id: uuid.UUID) -> None:
        stmt = select(ProductModel).where(ProductModel.id == product_id)
        try:
            model = (await self.session.execute(stmt)).scalar_one_or_none()
            if model:
                await self.session.delete(model)
                await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to delete product") from e

    async def _load_images(
        self, product_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, list[ProductImageModel]]:
        if not product_ids:
            return {}
        stmt = (
            select(ProductImageModel)
            .where(ProductImageModel.product_id.in_(product_ids))
            .order_by(ProductImageModel.sort_order)
        )
        try:
            rows = (await self.session.execute(stmt)).scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to load images") from e
        result: dict[uuid.UUID, list[ProductImageModel]] = {}
        for row in rows:
            result.setdefault(row.product_id, []).append(row)
        return result

    async def _load_attributes(
        self, product_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, list[ProductAttributeModel]]:
        if not product_ids:
            return {}
        stmt = select(ProductAttributeModel).where(
            ProductAttributeModel.product_id.in_(product_ids)
        )
        try:
            rows = (await self.session.execute(stmt)).scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to load attributes") from e
        result: dict[uuid.UUID, list[ProductAttributeModel]] = {}
        for row in rows:
            result.setdefault(row.product_id, []).append(row)
        return result

    async def _replace_images(self, product_id: uuid.UUID, images) -> list[ProductImageModel]:
        try:
            await self.session.execute(
                delete(ProductImageModel).where(ProductImageModel.product_id == product_id)
            )
            models = [
                ProductImageModel(product_id=product_id, image_url=i.image_url, sort_order=i.sort_order)
                for i in images
            ]
            self.session.add_all(models)
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to replace images") from e
        return models

    async def _replace_attributes(self, product_id: uuid.UUID, attributes) -> list[ProductAttributeModel]:
        try:
            await self.session.execute(
                delete(ProductAttributeModel).where(ProductAttributeModel.product_id == product_id)
            )
            models = [
                ProductAttributeModel(product_id=product_id, name=a.name, value=a.value)
                for a in attributes
            ]
            self.session.add_all(models)
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to replace attributes") from e
        return models
