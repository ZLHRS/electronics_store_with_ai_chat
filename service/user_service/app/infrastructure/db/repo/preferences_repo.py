import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entity.preferences_entity import PreferencesEntity, UpdatePreferences
from app.domain.repo.preferences_repo_protocol import PreferencesRepository
from app.exceptions import DatabaseError
from app.infrastructure.db.model.preferences_model import PreferencesModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.preferences_mapper import preferences_model_to_entity


class SQLAlchemyPreferencesRepo(SQLAlchemyBaseRepo, PreferencesRepository):
    async def get_by_user(self, user_id: uuid.UUID) -> PreferencesEntity | None:
        stmt = select(PreferencesModel).where(PreferencesModel.user_id == user_id)
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get preferences") from e
        return preferences_model_to_entity(result) if result else None

    async def get_or_create(self, user_id: uuid.UUID) -> PreferencesEntity:
        stmt = (
            insert(PreferencesModel)
            .values(user_id=user_id)
            .on_conflict_do_nothing(index_elements=["user_id"])
            .returning(PreferencesModel)
        )
        try:
            result = (await self.session.execute(stmt)).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get or create preferences") from e
        if result is not None:
            return preferences_model_to_entity(result)
        existing = await self.get_by_user(user_id)
        if existing is None:
            raise DatabaseError("Failed to fetch preferences after upsert")
        return existing

    async def update(self, user_id: uuid.UUID, data: UpdatePreferences) -> PreferencesEntity:
        await self.get_or_create(user_id)
        stmt = select(PreferencesModel).where(PreferencesModel.user_id == user_id)
        try:
            model = (await self.session.execute(stmt)).scalar_one()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to fetch preferences for update") from e
        if data.language is not None:
            model.language = data.language
        if data.currency is not None:
            model.currency = data.currency
        if data.notification_enabled is not None:
            model.notification_enabled = data.notification_enabled
        if data.preferred_categories is not None:
            model.preferred_categories = data.preferred_categories
        if data.min_budget is not None:
            model.min_budget = data.min_budget
        if data.max_budget is not None:
            model.max_budget = data.max_budget
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to update preferences") from e
        return preferences_model_to_entity(model)
