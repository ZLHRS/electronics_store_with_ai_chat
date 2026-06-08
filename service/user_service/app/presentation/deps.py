import uuid
from dataclasses import dataclass

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import HTTPException, Request

from app.application.service.user_service import UserProfileService
from app.config import JWTConfig
from app.exceptions import InvalidTokenError, TokenExpiredError
from app.infrastructure.jwt_service import JWTService


@dataclass(frozen=True)
class CurrentUser:
    auth_user_id: uuid.UUID
    profile_id: uuid.UUID


@inject
async def get_current_user(
    request: Request,
    jwt_service: FromDishka[JWTService],
    user_service: FromDishka[UserProfileService],
    jwt_config: FromDishka[JWTConfig],
) -> CurrentUser:
    token = request.cookies.get(jwt_config.access_token_name)
    if token is None:
        raise HTTPException(status_code=401, detail="Missing access token")
    try:
        auth_user_id = jwt_service.decode_access_token(token)
    except TokenExpiredError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    profile = await user_service.get_or_create_profile(auth_user_id)
    return CurrentUser(auth_user_id=auth_user_id, profile_id=profile.id)
