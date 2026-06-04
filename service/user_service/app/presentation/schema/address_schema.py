import uuid

from pydantic import BaseModel, Field


class CreateAddressRequest(BaseModel):
    city: str = Field(max_length=128)
    street: str = Field(max_length=256)
    house: str = Field(max_length=32)
    apartment: str | None = Field(default=None, max_length=32)
    comment: str | None = Field(default=None)
    is_default: bool = False


class UpdateAddressRequest(BaseModel):
    city: str = Field(max_length=128)
    street: str = Field(max_length=256)
    house: str = Field(max_length=32)
    apartment: str | None = Field(default=None, max_length=32)
    comment: str | None = Field(default=None)
    is_default: bool = False


class AddressResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    city: str
    street: str
    house: str
    apartment: str | None
    comment: str | None
    is_default: bool
