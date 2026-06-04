from app.domain.entity.preferences_entity import PreferencesEntity
from app.infrastructure.db.model.preferences_model import PreferencesModel


def preferences_model_to_entity(model: PreferencesModel) -> PreferencesEntity:
    return PreferencesEntity(
        user_id=model.user_id,
        language=model.language,
        currency=model.currency,
        notification_enabled=model.notification_enabled,
        preferred_categories=model.preferred_categories or [],
        min_budget=model.min_budget,
        max_budget=model.max_budget,
    )
