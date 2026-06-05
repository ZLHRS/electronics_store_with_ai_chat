import datetime
import uuid

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entity.cart_entity import CartItemEntity, CreateCartItem
from app.domain.repo.cart_item_repo_protocol import CartItemRepository
from app.exceptions import DatabaseError
from app.infrastructure.db.model.cart_item_model import CartItemModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.cart_mapper import cart_item_model_to_entity


class SQLAlchemyCartItemRepo(SQLAlchemyBaseRepo, CartItemRepository):
    async def get_by_cart(self, cart_id: uuid.UUID) -> list[CartItemEntity]:
        stmt = (
            select(CartItemModel)
            .where(CartItemModel.cart_id == cart_id)
            .order_by(CartItemModel.created_at)
        )
        try:
            rows = (await self.session.execute(stmt)).scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get cart items") from e
        return [cart_item_model_to_entity(r) for r in rows]

    async def get_by_cart_and_product(
        self, cart_id: uuid.UUID, product_id: uuid.UUID
    ) -> CartItemEntity | None:
        stmt = select(CartItemModel).where(
            CartItemModel.cart_id == cart_id,
            CartItemModel.product_id == product_id,
        )
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get cart item") from e
        return cart_item_model_to_entity(result) if result else None

    async def create(self, data: CreateCartItem) -> CartItemEntity:
        model = CartItemModel(
            cart_id=data.cart_id,
            product_id=data.product_id,
            quantity=data.quantity,
            unit_price=data.unit_price,
        )
        self.session.add(model)
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to create cart item") from e
        return cart_item_model_to_entity(model)

    async def update_quantity(self, item_id: uuid.UUID, quantity: int) -> CartItemEntity:
        stmt = select(CartItemModel).where(CartItemModel.id == item_id)
        try:
            model = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to fetch cart item for update") from e
        if model is None:
            raise DatabaseError("Cart item not found")
        model.quantity = quantity
        model.updated_at = datetime.datetime.now(datetime.UTC)
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to update cart item") from e
        return cart_item_model_to_entity(model)

    async def delete(self, item_id: uuid.UUID) -> None:
        stmt = delete(CartItemModel).where(CartItemModel.id == item_id)
        try:
            await self.session.execute(stmt)
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to delete cart item") from e

    async def delete_by_cart(self, cart_id: uuid.UUID) -> None:
        stmt = delete(CartItemModel).where(CartItemModel.cart_id == cart_id)
        try:
            await self.session.execute(stmt)
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to clear cart items") from e
