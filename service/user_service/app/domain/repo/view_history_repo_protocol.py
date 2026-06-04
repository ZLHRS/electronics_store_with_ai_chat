import uuid
from typing import Protocol

from app.domain.entity.view_history_entity import ViewHistoryEntity


class ViewHistoryRepository(Protocol):
    async def get_recent(self, user_id: uuid.UUID, limit: int) -> list[ViewHistoryEntity]: ...

    async def upsert(self, user_id: uuid.UUID, product_id: uuid.UUID) -> ViewHistoryEntity: ...
