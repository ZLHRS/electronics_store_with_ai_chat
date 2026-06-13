import uuid
from dataclasses import dataclass

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import HTTPException, Request

from app.config import JWTConfig
from app.exceptions import InvalidTokenError, TokenExpiredError
from app.infrastructure.jwt_service import JWTService
from app.infrastructure.permission_cache import PermissionCache


@dataclass(frozen=True)
class CurrentUser:
    id: uuid.UUID


@inject
async def get_current_user(
    request: Request,
    jwt_service: FromDishka[JWTService],
    cache: FromDishka[PermissionCache],
    jwt_config: FromDishka[JWTConfig],
) -> CurrentUser:
    token = request.cookies.get(jwt_config.access_token_name)
    if token is None:
        raise HTTPException(status_code=401, detail="Missing access token")
    try:
        user_id = jwt_service.decode_access_token(token)
    except TokenExpiredError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    permissions = await cache.get(user_id)
    if permissions is None:
        raise HTTPException(status_code=401, detail="Session expired, please login again")
    return CurrentUser(id=user_id)
