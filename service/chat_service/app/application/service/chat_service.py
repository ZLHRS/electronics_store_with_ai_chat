from __future__ import annotations

import uuid

from app.application.dto.chat_dto import (
    ChatSessionResult,
    MessageResult,
    SendMessageCommand,
)
from app.application.service.rag_service import RAGService
from app.domain.entity.chat_entity import ChatSessionEntity, MessageEntity
from app.domain.repo.chat_repo import ChatSessionRepository, MessageRepository
from app.exceptions import SessionForbiddenError, SessionNotFoundError


def _to_session_result(entity: ChatSessionEntity) -> ChatSessionResult:
    return ChatSessionResult(
        id=entity.id,
        user_id=entity.user_id,
        title=entity.title,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def _to_message_result(entity: MessageEntity) -> MessageResult:
    return MessageResult(
        id=entity.id,
        session_id=entity.session_id,
        role=entity.role,
        content=entity.content,
        created_at=entity.created_at,
    )


class ChatService:
    def __init__(
        self,
        session_repo: ChatSessionRepository,
        message_repo: MessageRepository,
        rag_service: RAGService,
        llm_service,
    ):
        self._sessions = session_repo
        self._messages = message_repo
        self._rag = rag_service
        self._llm = llm_service

    async def create_session(self, user_id: uuid.UUID) -> ChatSessionResult:
        session = await self._sessions.create(user_id)
        return _to_session_result(session)

    async def list_sessions(
        self, user_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> list[ChatSessionResult]:
        sessions = await self._sessions.get_by_user_id(user_id, limit, offset)
        return [_to_session_result(s) for s in sessions]

    async def get_messages(
        self, session_id: uuid.UUID, user_id: uuid.UUID, limit: int = 50
    ) -> list[MessageResult]:
        session = await self._sessions.get_by_id(session_id)
        if session is None:
            raise SessionNotFoundError(f"Session {session_id} not found")
        if session.user_id != user_id:
            raise SessionForbiddenError("Access denied")
        messages = await self._messages.get_by_session_id(session_id, limit)
        return [_to_message_result(m) for m in messages]

    async def send_message(self, cmd: SendMessageCommand) -> MessageResult:
        session = await self._sessions.get_by_id(cmd.session_id)
        if session is None:
            raise SessionNotFoundError(f"Session {cmd.session_id} not found")
        if session.user_id != cmd.user_id:
            raise SessionForbiddenError("Access denied")

        context = await self._rag.search(cmd.content)
        history = await self._messages.get_by_session_id(cmd.session_id, limit=10)

        response_text = await self._llm.chat(
            history=history,
            context=context,
            user_message=cmd.content,
        )

        await self._messages.create(cmd.session_id, "user", cmd.content)
        assistant_msg = await self._messages.create(cmd.session_id, "assistant", response_text)

        if session.title is None and len(history) == 0:
            title = cmd.content[:60]
            await self._sessions.update_title(cmd.session_id, title)

        result = _to_message_result(assistant_msg)
        result.product_ids = [item.product_id for item in context]
        return result
