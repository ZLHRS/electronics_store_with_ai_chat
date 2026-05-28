from fastapi import APIRouter, HTTPException, Request, Response
from dishka.integrations.fastapi import FromDishka, inject

from app.application.dto.auth_dto import LoginCommand, LoginResult, LoginTokens, RegisterCommand, RegisterResult, SessionContext
from app.application.service.auth_service import AuthService
from app.config import AuthConfig
from app.presentation.schema.user_schema import LoginRequest, RegisterRequest

router = APIRouter()


def _build_context(request: Request) -> SessionContext:
    return SessionContext(
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        device_id=request.headers.get("x-device-id"),
    )


def _set_auth_cookies(response: Response, tokens: LoginTokens, config: AuthConfig) -> None:
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=config.access_token_expire_minutes * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=config.refresh_token_expire_days * 24 * 60 * 60,
    )


@router.post("/register", response_model=RegisterResult)
@inject
async def register_user(data: RegisterRequest, service: FromDishka[AuthService]):
    try:
        return await service.register(RegisterCommand(email=data.email, password=data.password))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResult)
@inject
async def login_user(
    data: LoginRequest,
    request: Request,
    response: Response,
    service: FromDishka[AuthService],
    auth_config: FromDishka[AuthConfig],
):
    try:
        tokens = await service.login(LoginCommand(email=data.email, password=data.password), _build_context(request))
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    _set_auth_cookies(response, tokens, auth_config)
    return LoginResult(access_token=tokens.access_token)


@router.post("/refresh", response_model=LoginResult)
@inject
async def refresh_token(
    request: Request,
    response: Response,
    service: FromDishka[AuthService],
    auth_config: FromDishka[AuthConfig],
):
    token = request.cookies.get("refresh_token")
    if token is None:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    try:
        tokens = await service.refresh(token, _build_context(request))
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    _set_auth_cookies(response, tokens, auth_config)
    return LoginResult(access_token=tokens.access_token)


@router.post("/logout", status_code=204)
@inject
async def logout(
    request: Request,
    response: Response,
    service: FromDishka[AuthService],
):
    token = request.cookies.get("refresh_token")
    if token is not None:
        await service.logout(token)
    response.delete_cookie(key="access_token", httponly=True, secure=True, samesite="strict")
    response.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="strict")


@router.post("/logout/all", status_code=204)
@inject
async def logout_all(
    request: Request,
    response: Response,
    service: FromDishka[AuthService],
):
    token = request.cookies.get("access_token")
    if token is None:
        raise HTTPException(status_code=401, detail="Missing access token")
    try:
        await service.logout_all(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    response.delete_cookie(key="access_token", httponly=True, secure=True, samesite="strict")
    response.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="strict")
