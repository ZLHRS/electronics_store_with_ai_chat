import uuid
from dataclasses import dataclass


@dataclass
class BrandEntity:
    id: uuid.UUID
    name: str
    slug: str


@dataclass
class CreateBrand:
    name: str
    slug: str
