import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.entity.user_entity import RegisterApplication, UserEntity
from app.domain.repo.user_repo_protocol import UserRepository
from app.infrastructure.db.model.user_model import UserModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.user_mapper import register_application_to_model, user_model_to_entity


class SQLAlchemyUserRepo(SQLAlchemyBaseRepo, UserRepository):

    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = (await self.session.execute(stmt)).scalar_one_or_none()
        if result is None:
            raise ValueError("User not found")
        return user_model_to_entity(result)

    async def get_by_email(self, email: str) -> UserEntity | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = (await self.session.execute(stmt)).scalar_one_or_none()
        return user_model_to_entity(result) if result else None

    async def register(self, application_data: RegisterApplication) -> UserEntity:
        model = register_application_to_model(application_data)
        self.session.add(model)
        try:
            await self.session.flush()
        except IntegrityError:
            raise ValueError("Email already registered")
        return user_model_to_entity(model)
