from app.domain.entity.user_entity import RegisterApplication, UserEntity
from app.infrastructure.db.model.user_model import UserModel


def user_model_to_entity(user_model: UserModel) -> UserEntity:
    return UserEntity(
        id=user_model.id,
        email=user_model.email,
        password=user_model.password,
        is_active=user_model.is_active,
        created_at=user_model.created_at,
    )


def register_application_to_model(application_model: RegisterApplication) -> UserModel:
    return UserModel(email=application_model.email, password=application_model.password)
