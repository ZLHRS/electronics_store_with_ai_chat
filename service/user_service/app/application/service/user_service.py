import logging
import uuid

from app.application.dto.user_dto import ProfileResult, UpdateProfileCommand
from app.domain.entity.user_entity import CreateUserProfile, UpdateUserProfile
from app.domain.repo.user_repo_protocol import UserProfileRepository

logger = logging.getLogger(__name__)


class UserProfileService:
    def __init__(self, user_repository: UserProfileRepository):
        self._users = user_repository

    async def get_or_create_profile(self, auth_user_id: uuid.UUID) -> ProfileResult:
        profile = await self._users.get_by_auth_user_id(auth_user_id)
        if profile is None:
            profile = await self._users.create(CreateUserProfile(auth_user_id=auth_user_id))
            logger.info("Profile created for auth_user_id=%s", auth_user_id)
        return ProfileResult(
            id=profile.id,
            auth_user_id=profile.auth_user_id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            phone=profile.phone,
            avatar_url=profile.avatar_url,
            city=profile.city,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    async def update_profile(
        self, profile_id: uuid.UUID, command: UpdateProfileCommand
    ) -> ProfileResult:
        profile = await self._users.update(
            profile_id,
            UpdateUserProfile(
                first_name=command.first_name,
                last_name=command.last_name,
                phone=command.phone,
                avatar_url=command.avatar_url,
                city=command.city,
            ),
        )
        logger.info("Profile updated profile_id=%s", profile_id)
        return ProfileResult(
            id=profile.id,
            auth_user_id=profile.auth_user_id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            phone=profile.phone,
            avatar_url=profile.avatar_url,
            city=profile.city,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
