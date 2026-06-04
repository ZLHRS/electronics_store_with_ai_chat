import datetime
import uuid

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entity.favorite_entity import FavoriteEntity
from app.domain.repo.favorite_repo_protocol import FavoriteRepository
from app.exceptions import DatabaseError
from app.infrastructure.db.model.favorite_model import FavoriteModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.favorite_mapper import favorite_model_to_entity


class SQLAlchemyFavoriteRepo(SQLAlchemyBaseRepo, FavoriteRepository):
    async def get_all_by_user(self, user_id: uuid.UUID) -> list[FavoriteEntity]:
        stmt = (
            select(FavoriteModel)
            .where(FavoriteModel.user_id == user_id)
            .order_by(FavoriteModel.created_at.desc())
        )
        try:
            rows = (await self.session.execute(stmt)).scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get favorites") from e
        return [favorite_model_to_entity(r) for r in rows]

    async def exists(self, user_id: uuid.UUID, product_id: uuid.UUID) -> bool:
        stmt = select(FavoriteModel).where(
            FavoriteModel.user_id == user_id, FavoriteModel.product_id == product_id
        )
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to check favorite") from e
        return result is not None

    async def add(self, user_id: uuid.UUID, product_id: uuid.UUID) -> FavoriteEntity:
        model = FavoriteModel(
            user_id=user_id,
            product_id=product_id,
            created_at=datetime.datetime.now(datetime.UTC),
        )
        self.session.add(model)
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to add favorite") from e
        return favorite_model_to_entity(model)

    async def remove(self, user_id: uuid.UUID, product_id: uuid.UUID) -> None:
        stmt = delete(FavoriteModel).where(
            FavoriteModel.user_id == user_id, FavoriteModel.product_id == product_id
        )
        try:
            await self.session.execute(stmt)
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to remove favorite") from e
