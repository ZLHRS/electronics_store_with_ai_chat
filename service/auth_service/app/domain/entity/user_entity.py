import datetime
import uuid
from dataclasses import dataclass


@dataclass
class RegisterApplication:
    email: str
    password: str


@dataclass
class UserEntity:
    id: uuid.UUID
    email: str
    password: str
    is_active: bool
    created_at: datetime.datetime
