import datetime
import uuid

from pydantic import BaseModel, Field


class UpdateProfileRequest(BaseModel):
    first_name: str | None = Field(default=None, max_length=128)
    last_name: str | None = Field(default=None, max_length=128)
    phone: str | None = Field(default=None, max_length=32)
    avatar_url: str | None = Field(default=None)
    city: str | None = Field(default=None, max_length=128)


class ProfileResponse(BaseModel):
    id: uuid.UUID
    auth_user_id: uuid.UUID
    first_name: str | None
    last_name: str | None
    phone: str | None
    avatar_url: str | None
    city: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
