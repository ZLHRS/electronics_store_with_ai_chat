import uuid
from dataclasses import dataclass

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, HTTPException, Request

from app.application.dto.auth_dto import SessionContext
from app.config import AuthConfig
from app.infrastructure.cache.permission_cache import PermissionCache
from app.infrastructure.security import SecurityService


@dataclass(frozen=True)
class CurrentUser:
    id: uuid.UUID
    permissions: frozenset[str]

    def has_permission(self, perm: str) -> bool:
        return perm in self.permissions


@inject
async def get_current_user(
    request: Request,
    security: FromDishka[SecurityService],
    cache: FromDishka[PermissionCache],
    auth_config: FromDishka[AuthConfig],
) -> CurrentUser:
    token = request.cookies.get(auth_config.access_token_name)
    if token is None:
        raise HTTPException(status_code=401, detail="Missing access token")

    user_id = security.decode_access_token(token)
    permissions = await cache.get(user_id)
    if permissions is None:
        raise HTTPException(status_code=401, detail="Session expired, please login again")

    return CurrentUser(id=user_id, permissions=permissions)


def get_session_context(request: Request) -> SessionContext:
    return SessionContext(
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        device_id=request.headers.get("x-device-id"),
    )


def require_permission(code: str):
    async def dep(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not user.has_permission(code):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user

    return dep
