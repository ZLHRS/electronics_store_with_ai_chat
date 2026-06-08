import uuid

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entity.cart_entity import CartEntity, CartStatus
from app.domain.repo.cart_repo_protocol import CartRepository
from app.exceptions import DatabaseError
from app.infrastructure.db.model.cart_model import CartModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.cart_mapper import cart_model_to_entity


class SQLAlchemyCartRepo(SQLAlchemyBaseRepo, CartRepository):
    async def get_active_by_user_id(self, user_id: uuid.UUID) -> CartEntity | None:
        stmt = select(CartModel).where(
            CartModel.user_id == user_id,
            CartModel.status == CartStatus.ACTIVE,
        )
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get active cart") from e
        return cart_model_to_entity(result) if result else None

    async def get_or_create_active(self, user_id: uuid.UUID) -> CartEntity:
        existing = await self.get_active_by_user_id(user_id)
        if existing:
            return existing
        model = CartModel(user_id=user_id, status=CartStatus.ACTIVE)
        self.session.add(model)
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to create cart") from e
        return cart_model_to_entity(model)

    async def delete_by_user_id(self, user_id: uuid.UUID) -> None:
        stmt = delete(CartModel).where(
            CartModel.user_id == user_id,
            CartModel.status == CartStatus.ACTIVE,
        )
        try:
            await self.session.execute(stmt)
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to delete cart") from e
