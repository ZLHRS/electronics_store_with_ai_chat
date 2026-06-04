import datetime
import uuid
from dataclasses import dataclass


@dataclass
class UserProfileEntity:
    id: uuid.UUID
    auth_user_id: uuid.UUID
    first_name: str | None
    last_name: str | None
    phone: str | None
    avatar_url: str | None
    city: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class CreateUserProfile:
    auth_user_id: uuid.UUID


@dataclass
class UpdateUserProfile:
    first_name: str | None
    last_name: str | None
    phone: str | None
    avatar_url: str | None
    city: str | None
