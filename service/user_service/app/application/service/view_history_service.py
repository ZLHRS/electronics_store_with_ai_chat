import logging
import uuid

from app.application.dto.user_dto import ViewHistoryResult
from app.domain.repo.view_history_repo_protocol import ViewHistoryRepository

logger = logging.getLogger(__name__)

_DEFAULT_HISTORY_LIMIT = 50


class ViewHistoryService:
    def __init__(self, view_history_repository: ViewHistoryRepository):
        self._history = view_history_repository

    async def get_history(self, user_id: uuid.UUID) -> list[ViewHistoryResult]:
        entries = await self._history.get_recent(user_id, _DEFAULT_HISTORY_LIMIT)
        return [
            ViewHistoryResult(
                id=e.id,
                user_id=e.user_id,
                product_id=e.product_id,
                viewed_at=e.viewed_at,
            )
            for e in entries
        ]

    async def record_view(self, user_id: uuid.UUID, product_id: uuid.UUID) -> ViewHistoryResult:
        entry = await self._history.upsert(user_id, product_id)
        logger.info("View recorded user_id=%s product_id=%s", user_id, product_id)
        return ViewHistoryResult(
            id=entry.id,
            user_id=entry.user_id,
            product_id=entry.product_id,
            viewed_at=entry.viewed_at,
        )
