import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entity.view_history_entity import ViewHistoryEntity
from app.domain.repo.view_history_repo_protocol import ViewHistoryRepository
from app.exceptions import DatabaseError
from app.infrastructure.db.model.view_history_model import ViewHistoryModel
from app.infrastructure.db.repo.base import SQLAlchemyBaseRepo
from app.infrastructure.mapper.view_history_mapper import view_history_model_to_entity


class SQLAlchemyViewHistoryRepo(SQLAlchemyBaseRepo, ViewHistoryRepository):
    async def get_recent(self, user_id: uuid.UUID, limit: int) -> list[ViewHistoryEntity]:
        stmt = (
            select(ViewHistoryModel)
            .where(ViewHistoryModel.user_id == user_id)
            .order_by(ViewHistoryModel.viewed_at.desc())
            .limit(limit)
        )
        try:
            rows = (await self.session.execute(stmt)).scalars().all()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to get view history") from e
        return [view_history_model_to_entity(r) for r in rows]

    async def upsert(self, user_id: uuid.UUID, product_id: uuid.UUID) -> ViewHistoryEntity:
        now = datetime.datetime.now(datetime.UTC)
        stmt = (
            insert(ViewHistoryModel)
            .values(user_id=user_id, product_id=product_id, viewed_at=now)
            .on_conflict_do_update(
                index_elements=["user_id", "product_id"],
                set_={"viewed_at": now},
            )
            .returning(ViewHistoryModel)
        )
        try:
            result = (await self.session.execute(stmt)).scalar_one()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to upsert view history") from e
        return view_history_model_to_entity(result)
