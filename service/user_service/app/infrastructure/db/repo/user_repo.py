import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entity.user_entity import CreateUserProfile, UpdateUserProfile, UserProfileEntity
from app.domain.repo.user_repo_protocol import UserProfileRepository
from app.exceptions import DatabaseError
from app.infrastructure.db.model.user_profile_model import UserProfileModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.user_mapper import user_profile_model_to_entity


class SQLAlchemyUserProfileRepo(SQLAlchemyBaseRepo, UserProfileRepository):
    async def get_by_id(self, profile_id: uuid.UUID) -> UserProfileEntity | None:
        stmt = select(UserProfileModel).where(UserProfileModel.id == profile_id)
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get profile by id") from e
        return user_profile_model_to_entity(result) if result else None

    async def get_by_auth_user_id(self, auth_user_id: uuid.UUID) -> UserProfileEntity | None:
        stmt = select(UserProfileModel).where(UserProfileModel.auth_user_id == auth_user_id)
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get profile by auth_user_id") from e
        return user_profile_model_to_entity(result) if result else None

    async def create(self, data: CreateUserProfile) -> UserProfileEntity:
        model = UserProfileModel(auth_user_id=data.auth_user_id)
        self.session.add(model)
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to create profile") from e
        return user_profile_model_to_entity(model)

    async def update(self, profile_id: uuid.UUID, data: UpdateUserProfile) -> UserProfileEntity:
        stmt = select(UserProfileModel).where(UserProfileModel.id == profile_id)
        try:
            model = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to fetch profile for update") from e
        if model is None:
            raise DatabaseError("Profile not found")
        if data.first_name is not None:
            model.first_name = data.first_name
        if data.last_name is not None:
            model.last_name = data.last_name
        if data.phone is not None:
            model.phone = data.phone
        if data.avatar_url is not None:
            model.avatar_url = data.avatar_url
        if data.city is not None:
            model.city = data.city
        model.updated_at = datetime.datetime.now(datetime.UTC)
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to update profile") from e
        return user_profile_model_to_entity(model)
