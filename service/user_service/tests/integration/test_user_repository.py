import uuid

import pytest

from app.domain.entity.user_entity import CreateUserProfile, UpdateUserProfile
from app.infrastructure.db.repo.user_repo import SQLAlchemyUserProfileRepo


@pytest.mark.asyncio
async def test_create_and_get_profile(db_session):
    repo = SQLAlchemyUserProfileRepo(db_session)
    auth_user_id = uuid.uuid4()

    profile = await repo.create(CreateUserProfile(auth_user_id=auth_user_id))

    assert profile.auth_user_id == auth_user_id
    assert profile.first_name is None

    fetched = await repo.get_by_auth_user_id(auth_user_id)
    assert fetched is not None
    assert fetched.id == profile.id


@pytest.mark.asyncio
async def test_update_profile(db_session):
    repo = SQLAlchemyUserProfileRepo(db_session)
    auth_user_id = uuid.uuid4()

    profile = await repo.create(CreateUserProfile(auth_user_id=auth_user_id))
    updated = await repo.update(
        profile.id,
        UpdateUserProfile(
            first_name="Данияр",
            last_name=None,
            phone=None,
            avatar_url=None,
            city="Астана",
        ),
    )

    assert updated.first_name == "Данияр"
    assert updated.city == "Астана"


@pytest.mark.asyncio
async def test_get_by_id_returns_none_for_unknown(db_session):
    repo = SQLAlchemyUserProfileRepo(db_session)

    result = await repo.get_by_id(uuid.uuid4())

    assert result is None
