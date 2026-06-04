import datetime
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateProfileCommand:
    first_name: str | None
    last_name: str | None
    phone: str | None
    avatar_url: str | None
    city: str | None


@dataclass(frozen=True)
class ProfileResult:
    id: uuid.UUID
    auth_user_id: uuid.UUID
    first_name: str | None
    last_name: str | None
    phone: str | None
    avatar_url: str | None
    city: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass(frozen=True)
class CreateAddressCommand:
    city: str
    street: str
    house: str
    apartment: str | None
    comment: str | None
    is_default: bool


@dataclass(frozen=True)
class UpdateAddressCommand:
    city: str
    street: str
    house: str
    apartment: str | None
    comment: str | None
    is_default: bool


@dataclass(frozen=True)
class AddressResult:
    id: uuid.UUID
    user_id: uuid.UUID
    city: str
    street: str
    house: str
    apartment: str | None
    comment: str | None
    is_default: bool


@dataclass(frozen=True)
class FavoriteResult:
    user_id: uuid.UUID
    product_id: uuid.UUID
    created_at: datetime.datetime


@dataclass(frozen=True)
class ViewHistoryResult:
    id: uuid.UUID
    user_id: uuid.UUID
    product_id: uuid.UUID
    viewed_at: datetime.datetime


@dataclass(frozen=True)
class UpdatePreferencesCommand:
    language: str | None
    currency: str | None
    notification_enabled: bool | None
    preferred_categories: list[str] | None
    min_budget: int | None
    max_budget: int | None


@dataclass(frozen=True)
class PreferencesResult:
    user_id: uuid.UUID
    language: str
    currency: str
    notification_enabled: bool
    preferred_categories: list[str]
    min_budget: int | None
    max_budget: int | None
