import logging
import uuid

from app.application.dto.user_dto import FavoriteResult
from app.domain.repo.favorite_repo_protocol import FavoriteRepository
from app.exceptions import FavoriteAlreadyExistsError, FavoriteNotFoundError

logger = logging.getLogger(__name__)


class FavoriteService:
    def __init__(self, favorite_repository: FavoriteRepository):
        self._favorites = favorite_repository

    async def get_favorites(self, user_id: uuid.UUID) -> list[FavoriteResult]:
        favorites = await self._favorites.get_all_by_user(user_id)
        return [
            FavoriteResult(
                user_id=f.user_id,
                product_id=f.product_id,
                created_at=f.created_at,
            )
            for f in favorites
        ]

    async def add_favorite(self, user_id: uuid.UUID, product_id: uuid.UUID) -> FavoriteResult:
        if await self._favorites.exists(user_id, product_id):
            raise FavoriteAlreadyExistsError("Product already in favorites")
        favorite = await self._favorites.add(user_id, product_id)
        logger.info("Favorite added user_id=%s product_id=%s", user_id, product_id)
        return FavoriteResult(
            user_id=favorite.user_id,
            product_id=favorite.product_id,
            created_at=favorite.created_at,
        )

    async def remove_favorite(self, user_id: uuid.UUID, product_id: uuid.UUID) -> None:
        if not await self._favorites.exists(user_id, product_id):
            raise FavoriteNotFoundError("Product not in favorites")
        await self._favorites.remove(user_id, product_id)
        logger.info("Favorite removed user_id=%s product_id=%s", user_id, product_id)
