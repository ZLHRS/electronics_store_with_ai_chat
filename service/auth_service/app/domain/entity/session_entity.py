import datetime
import uuid
from dataclasses import dataclass


@dataclass
class SessionEntity:
    id: uuid.UUID
    user_id: uuid.UUID
    refresh_token_hash: str
    device_id: str | None
    ip_address: str | None
    user_agent: str | None
    created_at: datetime.datetime
    expires_at: datetime.datetime
    last_used_at: datetime.datetime
    revoked: bool


@dataclass(frozen=True)
class CreateSession:
    user_id: uuid.UUID
    refresh_token_hash: str
    device_id: str | None
    ip_address: str | None
    user_agent: str | None
    expires_at: datetime.datetime
