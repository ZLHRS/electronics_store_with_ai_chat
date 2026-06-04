from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.application.dto.auth_dto import (
    LoginCommand,
    LoginResult,
    LoginTokens,
    RegisterCommand,
    RegisterResult,
    SessionContext,
    UserResult,
)
from app.application.service.auth_service import AuthService
from app.config import AuthConfig
from app.domain.permissions import P
from app.presentation.deps import CurrentUser, get_current_user, get_session_context, require_permission
from app.presentation.limiters import login_limiter, refresh_limiter, register_limiter
from app.presentation.schema.user_schema import LoginRequest, RegisterRequest

router = APIRouter()


def _set_auth_cookies(response: Response, tokens: LoginTokens, config: AuthConfig) -> None:
    response.set_cookie(
        key=config.access_token_name,
        value=tokens.access_token,
        httponly=True,
        secure=config.cookie_secure,
        samesite=config.cookie_samesite,
        max_age=config.access_token_expire_minutes * 60,
    )
    response.set_cookie(
        key=config.refresh_token_name,
        value=tokens.refresh_token,
        httponly=True,
        secure=config.cookie_secure,
        samesite=config.cookie_samesite,
        max_age=config.refresh_token_expire_days * 24 * 60 * 60,
    )


def _delete_auth_cookies(response: Response, config: AuthConfig) -> None:
    response.delete_cookie(
        key=config.access_token_name,
        httponly=True,
        secure=config.cookie_secure,
        samesite=config.cookie_samesite,
    )
    response.delete_cookie(
        key=config.refresh_token_name,
        httponly=True,
        secure=config.cookie_secure,
        samesite=config.cookie_samesite,
    )


@router.post("/register", response_model=RegisterResult, dependencies=[Depends(register_limiter)])
@inject
async def register_user(data: RegisterRequest, service: FromDishka[AuthService]):
    return await service.register(RegisterCommand(email=data.email, password=data.password))


@router.post("/login", response_model=LoginResult, dependencies=[Depends(login_limiter)])
@inject
async def login_user(
    data: LoginRequest,
    response: Response,
    service: FromDishka[AuthService],
    auth_config: FromDishka[AuthConfig],
    context: SessionContext = Depends(get_session_context),
):
    tokens = await service.login(LoginCommand(email=data.email, password=data.password), context)
    _set_auth_cookies(response, tokens, auth_config)
    return LoginResult(access_token=tokens.access_token)


@router.post("/refresh", response_model=LoginResult, dependencies=[Depends(refresh_limiter)])
@inject
async def refresh_token(
    request: Request,
    response: Response,
    service: FromDishka[AuthService],
    auth_config: FromDishka[AuthConfig],
    context: SessionContext = Depends(get_session_context),
):
    token = request.cookies.get(auth_config.refresh_token_name)
    if token is None:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    tokens = await service.refresh(token, context)
    _set_auth_cookies(response, tokens, auth_config)
    return LoginResult(access_token=tokens.access_token)


@router.post("/logout")
@inject
async def logout(
    request: Request,
    response: Response,
    service: FromDishka[AuthService],
    auth_config: FromDishka[AuthConfig],
):
    token = request.cookies.get(auth_config.refresh_token_name)
    if token is not None:
        await service.logout(token)
    _delete_auth_cookies(response, auth_config)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResult)
@inject
async def get_me(
    service: FromDishka[AuthService],
    user: CurrentUser = Depends(get_current_user),
):
    return await service.get_me(user.id)


@router.post("/logout/all")
@inject
async def logout_all(
    response: Response,
    service: FromDishka[AuthService],
    auth_config: FromDishka[AuthConfig],
    user: CurrentUser = Depends(require_permission(P.ROLES_ASSIGN)),
):
    await service.logout_all(user.id)
    _delete_auth_cookies(response, auth_config)
    return {"message": "All sessions revoked"}
