from app.domain.entity.user_entity import UserProfileEntity
from app.infrastructure.db.model.user_profile_model import UserProfileModel


def user_profile_model_to_entity(model: UserProfileModel) -> UserProfileEntity:
    return UserProfileEntity(
        id=model.id,
        auth_user_id=model.auth_user_id,
        first_name=model.first_name,
        last_name=model.last_name,
        phone=model.phone,
        avatar_url=model.avatar_url,
        city=model.city,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
