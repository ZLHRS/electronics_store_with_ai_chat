from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from app.application.dto.user_dto import UpdateProfileCommand
from app.application.service.user_service import UserProfileService
from app.presentation.deps import CurrentUser, get_current_user
from app.presentation.limiters import profile_read_limiter, profile_write_limiter
from app.presentation.schema.user_schema import ProfileResponse, UpdateProfileRequest

router = APIRouter(prefix="/users")


@router.get("/me", response_model=ProfileResponse, dependencies=[Depends(profile_read_limiter)])
@inject
async def get_profile(
    service: FromDishka[UserProfileService],
    user: CurrentUser = Depends(get_current_user),
) -> ProfileResponse:
    result = await service.get_or_create_profile(user.auth_user_id)
    return ProfileResponse(**result.__dict__)


@router.patch("/me", response_model=ProfileResponse, dependencies=[Depends(profile_write_limiter)])
@inject
async def update_profile(
    data: UpdateProfileRequest,
    service: FromDishka[UserProfileService],
    user: CurrentUser = Depends(get_current_user),
) -> ProfileResponse:
    result = await service.update_profile(
        user.profile_id,
        UpdateProfileCommand(
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            avatar_url=data.avatar_url,
            city=data.city,
        ),
    )
    return ProfileResponse(**result.__dict__)
