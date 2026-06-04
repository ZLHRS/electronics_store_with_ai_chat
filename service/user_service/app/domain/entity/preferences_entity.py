import uuid
from dataclasses import dataclass


@dataclass
class PreferencesEntity:
    user_id: uuid.UUID
    language: str
    currency: str
    notification_enabled: bool
    preferred_categories: list[str]
    min_budget: int | None
    max_budget: int | None


@dataclass
class UpdatePreferences:
    language: str | None
    currency: str | None
    notification_enabled: bool | None
    preferred_categories: list[str] | None
    min_budget: int | None
    max_budget: int | None
