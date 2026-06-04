import uuid
from typing import Protocol

from app.domain.entity.user_entity import RegisterApplication, UserEntity


class UserRepository(Protocol):
    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None: ...

    async def get_by_email(self, email: str) -> UserEntity | None: ...

    async def register(self, application_data: RegisterApplication) -> UserEntity: ...
