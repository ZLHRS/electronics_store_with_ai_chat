import datetime
import uuid

import pytest

from app.application.dto.user_dto import UpdateProfileCommand
from app.application.service.user_service import UserProfileService
from app.domain.entity.user_entity import CreateUserProfile, UpdateUserProfile, UserProfileEntity


class FakeUserProfileRepo:
    def __init__(self):
        self._store: dict[uuid.UUID, UserProfileEntity] = {}
        self._by_auth: dict[uuid.UUID, uuid.UUID] = {}

    async def get_by_id(self, profile_id: uuid.UUID) -> UserProfileEntity | None:
        return self._store.get(profile_id)

    async def get_by_auth_user_id(self, auth_user_id: uuid.UUID) -> UserProfileEntity | None:
        profile_id = self._by_auth.get(auth_user_id)
        return self._store.get(profile_id) if profile_id else None

    async def create(self, data: CreateUserProfile) -> UserProfileEntity:
        now = datetime.datetime.now(datetime.UTC)
        profile = UserProfileEntity(
            id=uuid.uuid4(),
            auth_user_id=data.auth_user_id,
            first_name=None,
            last_name=None,
            phone=None,
            avatar_url=None,
            city=None,
            created_at=now,
            updated_at=now,
        )
        self._store[profile.id] = profile
        self._by_auth[data.auth_user_id] = profile.id
        return profile

    async def update(self, profile_id: uuid.UUID, data: UpdateUserProfile) -> UserProfileEntity:
        profile = self._store[profile_id]
        updated = UserProfileEntity(
            id=profile.id,
            auth_user_id=profile.auth_user_id,
            first_name=data.first_name if data.first_name is not None else profile.first_name,
            last_name=data.last_name if data.last_name is not None else profile.last_name,
            phone=data.phone if data.phone is not None else profile.phone,
            avatar_url=data.avatar_url if data.avatar_url is not None else profile.avatar_url,
            city=data.city if data.city is not None else profile.city,
            created_at=profile.created_at,
            updated_at=datetime.datetime.now(datetime.UTC),
        )
        self._store[profile_id] = updated
        return updated


@pytest.mark.asyncio
async def test_get_or_create_creates_profile_on_first_call():
    repo = FakeUserProfileRepo()
    service = UserProfileService(repo)
    auth_user_id = uuid.uuid4()

    result = await service.get_or_create_profile(auth_user_id)

    assert result.auth_user_id == auth_user_id
    assert result.first_name is None


@pytest.mark.asyncio
async def test_get_or_create_returns_existing_profile():
    repo = FakeUserProfileRepo()
    service = UserProfileService(repo)
    auth_user_id = uuid.uuid4()

    first = await service.get_or_create_profile(auth_user_id)
    second = await service.get_or_create_profile(auth_user_id)

    assert first.id == second.id


@pytest.mark.asyncio
async def test_update_profile_applies_changes():
    repo = FakeUserProfileRepo()
    service = UserProfileService(repo)
    auth_user_id = uuid.uuid4()

    profile = await service.get_or_create_profile(auth_user_id)
    updated = await service.update_profile(
        profile.id,
        UpdateProfileCommand(
            first_name="Алибек",
            last_name="Сатыбалды",
            phone="+77001234567",
            avatar_url=None,
            city="Алматы",
        ),
    )

    assert updated.first_name == "Алибек"
    assert updated.last_name == "Сатыбалды"
    assert updated.city == "Алматы"
