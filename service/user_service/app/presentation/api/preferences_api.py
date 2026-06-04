from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from app.application.dto.user_dto import UpdatePreferencesCommand
from app.application.service.preferences_service import PreferencesService
from app.presentation.deps import CurrentUser, get_current_user
from app.presentation.schema.preferences_schema import PreferencesResponse, UpdatePreferencesRequest

router = APIRouter(prefix="/users/me/preferences")


@router.get("", response_model=PreferencesResponse)
@inject
async def get_preferences(
    service: FromDishka[PreferencesService],
    user: CurrentUser = Depends(get_current_user),
) -> PreferencesResponse:
    result = await service.get_preferences(user.profile_id)
    return PreferencesResponse(**result.__dict__)


@router.patch("", response_model=PreferencesResponse)
@inject
async def update_preferences(
    data: UpdatePreferencesRequest,
    service: FromDishka[PreferencesService],
    user: CurrentUser = Depends(get_current_user),
) -> PreferencesResponse:
    result = await service.update_preferences(
        user.profile_id,
        UpdatePreferencesCommand(
            language=data.language,
            currency=data.currency,
            notification_enabled=data.notification_enabled,
            preferred_categories=data.preferred_categories,
            min_budget=data.min_budget,
            max_budget=data.max_budget,
        ),
    )
    return PreferencesResponse(**result.__dict__)
