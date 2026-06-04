import uuid

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from app.application.service.view_history_service import ViewHistoryService
from app.presentation.deps import CurrentUser, get_current_user
from app.presentation.limiters import history_limiter
from app.presentation.schema.view_history_schema import ViewHistoryResponse

router = APIRouter(prefix="/users/me/view-history")


@router.get("", response_model=list[ViewHistoryResponse], dependencies=[Depends(history_limiter)])
@inject
async def get_view_history(
    service: FromDishka[ViewHistoryService],
    user: CurrentUser = Depends(get_current_user),
) -> list[ViewHistoryResponse]:
    results = await service.get_history(user.profile_id)
    return [ViewHistoryResponse(**r.__dict__) for r in results]


@router.post(
    "/{product_id}",
    response_model=ViewHistoryResponse,
    status_code=201,
    dependencies=[Depends(history_limiter)],
)
@inject
async def record_view(
    product_id: uuid.UUID,
    service: FromDishka[ViewHistoryService],
    user: CurrentUser = Depends(get_current_user),
) -> ViewHistoryResponse:
    result = await service.record_view(user.profile_id, product_id)
    return ViewHistoryResponse(**result.__dict__)
