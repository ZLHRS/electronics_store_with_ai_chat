import uuid
from typing import Protocol

from app.domain.entity.user_entity import CreateUserProfile, UpdateUserProfile, UserProfileEntity


class UserProfileRepository(Protocol):
    async def get_by_id(self, profile_id: uuid.UUID) -> UserProfileEntity | None: ...

    async def get_by_auth_user_id(self, auth_user_id: uuid.UUID) -> UserProfileEntity | None: ...

    async def create(self, data: CreateUserProfile) -> UserProfileEntity: ...

    async def update(self, profile_id: uuid.UUID, data: UpdateUserProfile) -> UserProfileEntity: ...
