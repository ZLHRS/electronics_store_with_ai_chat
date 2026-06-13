import datetime
import uuid
from dataclasses import dataclass


@dataclass
class CreateSessionCommand:
    user_id: uuid.UUID


@dataclass
class SendMessageCommand:
    user_id: uuid.UUID
    session_id: uuid.UUID
    content: str


@dataclass
class ChatSessionResult:
    id: uuid.UUID
    user_id: uuid.UUID
    title: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class MessageResult:
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    created_at: datetime.datetime
    product_ids: list[uuid.UUID] | None = None
