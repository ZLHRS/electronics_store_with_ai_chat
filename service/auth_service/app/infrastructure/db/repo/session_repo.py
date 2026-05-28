import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update

from app.domain.entity.session_entity import CreateSession, SessionEntity
from app.domain.repo.session_repo_protocol import SessionRepository
from app.infrastructure.db.model.user_session_model import UserSessionModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.session_mapper import session_model_to_entity


class SQLAlchemySessionRepo(SQLAlchemyBaseRepo, SessionRepository):

    async def create(self, data: CreateSession) -> SessionEntity:
        model = UserSessionModel(
            user_id=data.user_id,
            refresh_token_hash=data.refresh_token_hash,
            device_id=data.device_id,
            ip_address=data.ip_address,
            user_agent=data.user_agent,
            expires_at=data.expires_at,
        )
        self.session.add(model)
        await self.session.flush()
        return session_model_to_entity(model)

    async def get_by_token_hash(self, token_hash: str) -> SessionEntity | None:
        stmt = select(UserSessionModel).where(UserSessionModel.refresh_token_hash == token_hash)
        result = (await self.session.execute(stmt)).scalar_one_or_none()
        return session_model_to_entity(result) if result else None

    async def revoke(self, session_id: uuid.UUID) -> None:
        stmt = update(UserSessionModel).where(UserSessionModel.id == session_id).values(revoked=True)
        await self.session.execute(stmt)

    async def revoke_all_by_user_id(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(UserSessionModel)
            .where(UserSessionModel.user_id == user_id, UserSessionModel.revoked == False)
            .values(revoked=True)
        )
        await self.session.execute(stmt)

    async def update_last_used(self, session_id: uuid.UUID) -> None:
        stmt = (
            update(UserSessionModel)
            .where(UserSessionModel.id == session_id)
            .values(last_used_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmt)
