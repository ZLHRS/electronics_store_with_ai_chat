import uuid
from dataclasses import dataclass


@dataclass
class AddressEntity:
    id: uuid.UUID
    user_id: uuid.UUID
    city: str
    street: str
    house: str
    apartment: str | None
    comment: str | None
    is_default: bool


@dataclass
class CreateAddress:
    user_id: uuid.UUID
    city: str
    street: str
    house: str
    apartment: str | None
    comment: str | None
    is_default: bool


@dataclass
class UpdateAddress:
    city: str
    street: str
    house: str
    apartment: str | None
    comment: str | None
    is_default: bool
