import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entity.order_entity import CreateOrder, OrderEntity
from app.domain.repo.order_repo_protocol import OrderRepository
from app.exceptions import DatabaseError
from app.infrastructure.db.model.order_item_model import OrderItemModel
from app.infrastructure.db.model.order_model import OrderModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.order_mapper import order_model_to_entity


class SQLAlchemyOrderRepo(SQLAlchemyBaseRepo, OrderRepository):
    async def get_by_id(self, order_id: uuid.UUID) -> OrderEntity | None:
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        try:
            model = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get order by id") from e
        if model is None:
            return None
        items = await self._load_items([order_id])
        return order_model_to_entity(model, items.get(order_id, []))

    async def get_by_user(self, user_id: uuid.UUID) -> list[OrderEntity]:
        stmt = (
            select(OrderModel)
            .where(OrderModel.user_id == user_id)
            .order_by(OrderModel.created_at.desc())
        )
        try:
            rows = (await self.session.execute(stmt)).scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get orders by user") from e
        if not rows:
            return []
        order_ids = [r.id for r in rows]
        items = await self._load_items(order_ids)
        return [order_model_to_entity(r, items.get(r.id, [])) for r in rows]

    async def create(self, data: CreateOrder) -> OrderEntity:
        model = OrderModel(
            user_id=data.user_id,
            status=data.status,
            total_amount=data.total_amount,
            delivery_address=data.delivery_address,
            payment_method=data.payment_method,
        )
        self.session.add(model)
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to create order") from e

        item_models = [
            OrderItemModel(
                order_id=model.id,
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
            )
            for item in data.items
        ]
        self.session.add_all(item_models)
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to create order items") from e

        return order_model_to_entity(model, item_models)

    async def update_status(self, order_id: uuid.UUID, status: str) -> OrderEntity:
        stmt = select(OrderModel).where(OrderModel.id == order_id)
        try:
            model = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to fetch order for update") from e
        if model is None:
            raise DatabaseError("Order not found")
        model.status = status
        model.updated_at = datetime.datetime.now(datetime.UTC)
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to update order status") from e
        items = await self._load_items([order_id])
        return order_model_to_entity(model, items.get(order_id, []))

    async def _load_items(
        self, order_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, list[OrderItemModel]]:
        if not order_ids:
            return {}
        stmt = select(OrderItemModel).where(OrderItemModel.order_id.in_(order_ids))
        try:
            rows = (await self.session.execute(stmt)).scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to load order items") from e
        result: dict[uuid.UUID, list[OrderItemModel]] = {}
        for row in rows:
            result.setdefault(row.order_id, []).append(row)
        return result
