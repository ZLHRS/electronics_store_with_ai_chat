import uuid
from dataclasses import dataclass


@dataclass
class CategoryEntity:
    id: uuid.UUID
    name: str
    slug: str
    parent_id: uuid.UUID | None


@dataclass
class CreateCategory:
    name: str
    slug: str
    parent_id: uuid.UUID | None
