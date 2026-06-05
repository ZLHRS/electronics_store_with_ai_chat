import uuid
from typing import Protocol

from app.domain.entity.cart_entity import CartEntity


class CartRepository(Protocol):
    async def get_active_by_user_id(self, user_id: uuid.UUID) -> CartEntity | None: ...

    async def get_or_create_active(self, user_id: uuid.UUID) -> CartEntity: ...

    async def delete_by_user_id(self, user_id: uuid.UUID) -> None: ...
