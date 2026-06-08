import uuid
from unittest.mock import AsyncMock

import pytest

from app.application.dto.user_dto import ProfileResult
from app.application.service.user_service import UserProfileService
from app.presentation.deps import CurrentUser, get_current_user


def _make_profile(auth_user_id: uuid.UUID) -> ProfileResult:
    import datetime

    now = datetime.datetime.now(datetime.UTC)
    return ProfileResult(
        id=uuid.uuid4(),
        auth_user_id=auth_user_id,
        first_name=None,
        last_name=None,
        phone=None,
        avatar_url=None,
        city=None,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_get_profile_unauthorized(client):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile_authorized(client, app):
    auth_user_id = uuid.uuid4()
    profile = _make_profile(auth_user_id)
    current_user = CurrentUser(auth_user_id=auth_user_id, profile_id=profile.id)

    mock_service = AsyncMock(spec=UserProfileService)
    mock_service.get_or_create_profile.return_value = profile

    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[UserProfileService] = lambda: mock_service

    try:
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 200
        data = response.json()
        assert data["auth_user_id"] == str(auth_user_id)
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(UserProfileService, None)
