import uuid
from dataclasses import dataclass
from typing import Protocol

from app.domain.entity.chat_entity import ChatSessionEntity, MessageEntity


@dataclass
class ProductContext:
    product_id: uuid.UUID
    content: str
    similarity: float


class ChatSessionRepository(Protocol):
    async def get_by_id(self, session_id: uuid.UUID) -> ChatSessionEntity | None: ...
    async def get_by_user_id(
        self, user_id: uuid.UUID, limit: int, offset: int
    ) -> list[ChatSessionEntity]: ...
    async def create(self, user_id: uuid.UUID) -> ChatSessionEntity: ...
    async def update_title(self, session_id: uuid.UUID, title: str) -> ChatSessionEntity: ...


class MessageRepository(Protocol):
    async def get_by_session_id(
        self, session_id: uuid.UUID, limit: int
    ) -> list[MessageEntity]: ...
    async def create(
        self, session_id: uuid.UUID, role: str, content: str
    ) -> MessageEntity: ...


class EmbeddingRepository(Protocol):
    async def upsert(
        self, product_id: uuid.UUID, content: str, embedding: list[float]
    ) -> None: ...
    async def search(
        self, query_embedding: list[float], limit: int
    ) -> list[ProductContext]: ...
    async def clear(self) -> None: ...
