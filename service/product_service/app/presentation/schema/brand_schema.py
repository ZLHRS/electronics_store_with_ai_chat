import uuid

from pydantic import BaseModel, Field


class CreateBrandRequest(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    slug: str | None = Field(default=None, max_length=256)


class UpdateBrandRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=256)
    slug: str | None = Field(default=None, max_length=256)


class BrandResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
