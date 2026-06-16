from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entity.chat_entity import MessageEntity
from app.domain.repo.chat_repo import MessageRepository
from app.exceptions import DatabaseError
from app.infrastructure.db.model.message_model import MessageModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.chat_mapper import message_model_to_entity


class SQLAlchemyMessageRepo(SQLAlchemyBaseRepo, MessageRepository):
    async def get_by_session_id(self, session_id: uuid.UUID, limit: int) -> list[MessageEntity]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.session_id == session_id)
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
        )
        try:
            results = (await self.session.execute(stmt)).scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get messages") from e
        return list(reversed([message_model_to_entity(r) for r in results]))

    async def create(self, session_id: uuid.UUID, role: str, content: str) -> MessageEntity:
        model = MessageModel(session_id=session_id, role=role, content=content)
        self.session.add(model)
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to create message") from e
        return message_model_to_entity(model)
