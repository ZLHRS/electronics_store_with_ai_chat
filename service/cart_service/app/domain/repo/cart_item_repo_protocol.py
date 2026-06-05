import uuid
from typing import Protocol

from app.domain.entity.cart_entity import CartItemEntity, CreateCartItem


class CartItemRepository(Protocol):
    async def get_by_cart(self, cart_id: uuid.UUID) -> list[CartItemEntity]: ...

    async def get_by_cart_and_product(
        self, cart_id: uuid.UUID, product_id: uuid.UUID
    ) -> CartItemEntity | None: ...

    async def create(self, data: CreateCartItem) -> CartItemEntity: ...

    async def update_quantity(self, item_id: uuid.UUID, quantity: int) -> CartItemEntity: ...

    async def delete(self, item_id: uuid.UUID) -> None: ...

    async def delete_by_cart(self, cart_id: uuid.UUID) -> None: ...
