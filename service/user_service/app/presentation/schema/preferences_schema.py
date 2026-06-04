import uuid

from pydantic import BaseModel, Field


class UpdatePreferencesRequest(BaseModel):
    language: str | None = Field(default=None, max_length=8)
    currency: str | None = Field(default=None, max_length=8)
    notification_enabled: bool | None = None
    preferred_categories: list[str] | None = None
    min_budget: int | None = Field(default=None, ge=0)
    max_budget: int | None = Field(default=None, ge=0)


class PreferencesResponse(BaseModel):
    user_id: uuid.UUID
    language: str
    currency: str
    notification_enabled: bool
    preferred_categories: list[str]
    min_budget: int | None
    max_budget: int | None
