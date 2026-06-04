import datetime
import uuid

import pytest

from app.application.service.favorite_service import FavoriteService
from app.domain.entity.favorite_entity import FavoriteEntity
from app.exceptions import FavoriteAlreadyExistsError, FavoriteNotFoundError


class FakeFavoriteRepo:
    def __init__(self):
        self._store: dict[tuple, FavoriteEntity] = {}

    async def get_all_by_user(self, user_id: uuid.UUID) -> list[FavoriteEntity]:
        return [f for f in self._store.values() if f.user_id == user_id]

    async def exists(self, user_id: uuid.UUID, product_id: uuid.UUID) -> bool:
        return (user_id, product_id) in self._store

    async def add(self, user_id: uuid.UUID, product_id: uuid.UUID) -> FavoriteEntity:
        favorite = FavoriteEntity(
            user_id=user_id,
            product_id=product_id,
            created_at=datetime.datetime.now(datetime.UTC),
        )
        self._store[(user_id, product_id)] = favorite
        return favorite

    async def remove(self, user_id: uuid.UUID, product_id: uuid.UUID) -> None:
        self._store.pop((user_id, product_id), None)


@pytest.mark.asyncio
async def test_add_favorite_success():
    repo = FakeFavoriteRepo()
    service = FavoriteService(repo)
    user_id = uuid.uuid4()
    product_id = uuid.uuid4()

    result = await service.add_favorite(user_id, product_id)

    assert result.user_id == user_id
    assert result.product_id == product_id


@pytest.mark.asyncio
async def test_add_favorite_duplicate_raises():
    repo = FakeFavoriteRepo()
    service = FavoriteService(repo)
    user_id = uuid.uuid4()
    product_id = uuid.uuid4()

    await service.add_favorite(user_id, product_id)

    with pytest.raises(FavoriteAlreadyExistsError):
        await service.add_favorite(user_id, product_id)


@pytest.mark.asyncio
async def test_remove_favorite_not_found_raises():
    repo = FakeFavoriteRepo()
    service = FavoriteService(repo)

    with pytest.raises(FavoriteNotFoundError):
        await service.remove_favorite(uuid.uuid4(), uuid.uuid4())
