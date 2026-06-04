import uuid
from typing import Protocol

from app.domain.entity.preferences_entity import PreferencesEntity, UpdatePreferences


class PreferencesRepository(Protocol):
    async def get_by_user(self, user_id: uuid.UUID) -> PreferencesEntity | None: ...

    async def get_or_create(self, user_id: uuid.UUID) -> PreferencesEntity: ...

    async def update(self, user_id: uuid.UUID, data: UpdatePreferences) -> PreferencesEntity: ...
