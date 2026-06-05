import uuid
from typing import Protocol

from app.domain.entity.order_entity import CreateOrder, OrderEntity


class OrderRepository(Protocol):
    async def get_by_id(self, order_id: uuid.UUID) -> OrderEntity | None: ...

    async def get_by_user(self, user_id: uuid.UUID) -> list[OrderEntity]: ...

    async def create(self, data: CreateOrder) -> OrderEntity: ...

    async def update_status(self, order_id: uuid.UUID, status: str) -> OrderEntity: ...
