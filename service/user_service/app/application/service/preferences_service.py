import logging
import uuid

from app.application.dto.user_dto import PreferencesResult, UpdatePreferencesCommand
from app.domain.entity.preferences_entity import UpdatePreferences
from app.domain.repo.preferences_repo_protocol import PreferencesRepository

logger = logging.getLogger(__name__)


class PreferencesService:
    def __init__(self, preferences_repository: PreferencesRepository):
        self._preferences = preferences_repository

    async def get_preferences(self, user_id: uuid.UUID) -> PreferencesResult:
        prefs = await self._preferences.get_or_create(user_id)
        return _to_result(prefs)

    async def update_preferences(
        self, user_id: uuid.UUID, command: UpdatePreferencesCommand
    ) -> PreferencesResult:
        prefs = await self._preferences.update(
            user_id,
            UpdatePreferences(
                language=command.language,
                currency=command.currency,
                notification_enabled=command.notification_enabled,
                preferred_categories=command.preferred_categories,
                min_budget=command.min_budget,
                max_budget=command.max_budget,
            ),
        )
        logger.info("Preferences updated user_id=%s", user_id)
        return _to_result(prefs)


def _to_result(prefs) -> PreferencesResult:
    return PreferencesResult(
        user_id=prefs.user_id,
        language=prefs.language,
        currency=prefs.currency,
        notification_enabled=prefs.notification_enabled,
        preferred_categories=prefs.preferred_categories,
        min_budget=prefs.min_budget,
        max_budget=prefs.max_budget,
    )
