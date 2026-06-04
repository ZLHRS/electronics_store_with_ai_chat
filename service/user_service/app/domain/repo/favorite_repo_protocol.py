import uuid
from typing import Protocol

from app.domain.entity.favorite_entity import FavoriteEntity


class FavoriteRepository(Protocol):
    async def get_all_by_user(self, user_id: uuid.UUID) -> list[FavoriteEntity]: ...

    async def exists(self, user_id: uuid.UUID, product_id: uuid.UUID) -> bool: ...

    async def add(self, user_id: uuid.UUID, product_id: uuid.UUID) -> FavoriteEntity: ...

    async def remove(self, user_id: uuid.UUID, product_id: uuid.UUID) -> None: ...
