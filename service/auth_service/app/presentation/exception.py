import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    AlreadyLoggedInError,
    DatabaseError,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    TokenReuseError,
    UserAlreadyExistsError,
)

logger = logging.getLogger(__name__)


async def _user_already_exists_handler(
    request: Request, exc: UserAlreadyExistsError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def _invalid_credentials_handler(
    request: Request, exc: InvalidCredentialsError
) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


async def _invalid_token_handler(request: Request, exc: InvalidTokenError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


async def _token_expired_handler(request: Request, exc: TokenExpiredError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


async def _token_reuse_handler(request: Request, exc: TokenReuseError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


async def _already_logged_in_handler(request: Request, exc: AlreadyLoggedInError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def _database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    logger.error("Database error on %s %s", request.method, request.url.path, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


async def _unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unexpected error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserAlreadyExistsError, _user_already_exists_handler)
    app.add_exception_handler(InvalidCredentialsError, _invalid_credentials_handler)
    app.add_exception_handler(InvalidTokenError, _invalid_token_handler)
    app.add_exception_handler(TokenExpiredError, _token_expired_handler)
    app.add_exception_handler(TokenReuseError, _token_reuse_handler)
    app.add_exception_handler(AlreadyLoggedInError, _already_logged_in_handler)
    app.add_exception_handler(DatabaseError, _database_error_handler)
    app.add_exception_handler(Exception, _unexpected_error_handler)
