from __future__ import annotations

import uuid

from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entity.chat_entity import ChatSessionEntity
from app.domain.repo.chat_repo import ChatSessionRepository
from app.exceptions import DatabaseError
from app.infrastructure.db.model.chat_session_model import ChatSessionModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.chat_mapper import session_model_to_entity


class SQLAlchemyChatSessionRepo(SQLAlchemyBaseRepo, ChatSessionRepository):
    async def get_by_id(self, session_id: uuid.UUID) -> ChatSessionEntity | None:
        stmt = select(ChatSessionModel).where(ChatSessionModel.id == session_id)
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get session") from e
        return session_model_to_entity(result) if result else None

    async def get_by_user_id(
        self, user_id: uuid.UUID, limit: int, offset: int
    ) -> list[ChatSessionEntity]:
        stmt = (
            select(ChatSessionModel)
            .where(ChatSessionModel.user_id == user_id)
            .order_by(ChatSessionModel.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        try:
            results = (await self.session.execute(stmt)).scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to list sessions") from e
        return [session_model_to_entity(r) for r in results]

    async def create(self, user_id: uuid.UUID) -> ChatSessionEntity:
        model = ChatSessionModel(user_id=user_id)
        self.session.add(model)
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to create session") from e
        return session_model_to_entity(model)

    async def update_title(self, session_id: uuid.UUID, title: str) -> ChatSessionEntity:
        stmt = (
            update(ChatSessionModel)
            .where(ChatSessionModel.id == session_id)
            .values(title=title)
            .returning(ChatSessionModel)
        )
        try:
            result = (await self.session.execute(stmt)).scalar_one()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to update session title") from e
        return session_model_to_entity(result)
