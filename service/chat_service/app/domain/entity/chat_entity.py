import datetime
import uuid
from dataclasses import dataclass


@dataclass
class ChatSessionEntity:
    id: uuid.UUID
    user_id: uuid.UUID
    title: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class MessageEntity:
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    created_at: datetime.datetime
