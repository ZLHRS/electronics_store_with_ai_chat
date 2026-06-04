import uuid

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from app.application.service.favorite_service import FavoriteService
from app.presentation.deps import CurrentUser, get_current_user
from app.presentation.limiters import favorites_limiter
from app.presentation.schema.favorite_schema import FavoriteResponse

router = APIRouter(prefix="/users/me/favorites")


@router.get("", response_model=list[FavoriteResponse], dependencies=[Depends(favorites_limiter)])
@inject
async def get_favorites(
    service: FromDishka[FavoriteService],
    user: CurrentUser = Depends(get_current_user),
) -> list[FavoriteResponse]:
    results = await service.get_favorites(user.profile_id)
    return [FavoriteResponse(**r.__dict__) for r in results]


@router.post(
    "/{product_id}",
    response_model=FavoriteResponse,
    status_code=201,
    dependencies=[Depends(favorites_limiter)],
)
@inject
async def add_favorite(
    product_id: uuid.UUID,
    service: FromDishka[FavoriteService],
    user: CurrentUser = Depends(get_current_user),
) -> FavoriteResponse:
    result = await service.add_favorite(user.profile_id, product_id)
    return FavoriteResponse(**result.__dict__)


@router.delete("/{product_id}", status_code=204, dependencies=[Depends(favorites_limiter)])
@inject
async def remove_favorite(
    product_id: uuid.UUID,
    service: FromDishka[FavoriteService],
    user: CurrentUser = Depends(get_current_user),
) -> None:
    await service.remove_favorite(user.profile_id, product_id)
