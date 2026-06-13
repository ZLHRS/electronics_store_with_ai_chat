import uuid

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.application.dto.chat_dto import ChatSessionResult, MessageResult, SendMessageCommand
from app.application.service.chat_service import ChatService
from app.application.service.rag_service import RAGService
from app.presentation.deps import CurrentUser, get_current_user

router = APIRouter(tags=["chat"])


class SendMessageBody(BaseModel):
    content: str


class ChatSessionResponse(BaseModel):
    id: uuid.UUID
    title: str | None
    created_at: str
    updated_at: str

    @classmethod
    def from_result(cls, r: ChatSessionResult) -> "ChatSessionResponse":
        return cls(
            id=r.id,
            title=r.title,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat(),
        )


class MessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    created_at: str

    @classmethod
    def from_result(cls, r: MessageResult) -> "MessageResponse":
        return cls(
            id=r.id,
            session_id=r.session_id,
            role=r.role,
            content=r.content,
            created_at=r.created_at.isoformat(),
        )


@router.post("/chat/sessions", response_model=ChatSessionResponse, status_code=201)
@inject
async def create_session(
    service: FromDishka[ChatService],
    user: CurrentUser = Depends(get_current_user),
) -> ChatSessionResponse:
    result = await service.create_session(user.id)
    return ChatSessionResponse.from_result(result)


@router.get("/chat/sessions", response_model=list[ChatSessionResponse])
@inject
async def list_sessions(
    service: FromDishka[ChatService],
    limit: int = 20,
    offset: int = 0,
    user: CurrentUser = Depends(get_current_user),
) -> list[ChatSessionResponse]:
    results = await service.list_sessions(user.id, limit, offset)
    return [ChatSessionResponse.from_result(r) for r in results]


@router.post(
    "/chat/sessions/{session_id}/messages",
    response_model=MessageResponse,
    status_code=201,
)
@inject
async def send_message(
    session_id: uuid.UUID,
    body: SendMessageBody,
    service: FromDishka[ChatService],
    user: CurrentUser = Depends(get_current_user),
) -> MessageResponse:
    cmd = SendMessageCommand(
        user_id=user.id,
        session_id=session_id,
        content=body.content,
    )
    result = await service.send_message(cmd)
    return MessageResponse.from_result(result)


@router.get(
    "/chat/sessions/{session_id}/messages",
    response_model=list[MessageResponse],
)
@inject
async def get_messages(
    session_id: uuid.UUID,
    service: FromDishka[ChatService],
    limit: int = 50,
    user: CurrentUser = Depends(get_current_user),
) -> list[MessageResponse]:
    results = await service.get_messages(session_id, user.id, limit)
    return [MessageResponse.from_result(r) for r in results]


@router.post("/chat/index", status_code=202)
@inject
async def index_products(
    rag_service: FromDishka[RAGService],
    user: CurrentUser = Depends(get_current_user),
) -> dict:
    count = await rag_service.index_all_products()
    return {"indexed": count}
