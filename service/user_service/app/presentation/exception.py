import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    AddressLimitExceededError,
    AddressNotFoundError,
    DatabaseError,
    FavoriteAlreadyExistsError,
    FavoriteNotFoundError,
    InvalidTokenError,
    TokenExpiredError,
    UserProfileNotFoundError,
)

logger = logging.getLogger(__name__)


async def _address_not_found_handler(request: Request, exc: AddressNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def _address_limit_handler(
    request: Request, exc: AddressLimitExceededError
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


async def _favorite_exists_handler(
    request: Request, exc: FavoriteAlreadyExistsError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def _favorite_not_found_handler(
    request: Request, exc: FavoriteNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def _profile_not_found_handler(
    request: Request, exc: UserProfileNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def _invalid_token_handler(request: Request, exc: InvalidTokenError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


async def _token_expired_handler(request: Request, exc: TokenExpiredError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


async def _database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    logger.error("Database error on %s %s", request.method, request.url.path, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


async def _unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unexpected error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AddressNotFoundError, _address_not_found_handler)
    app.add_exception_handler(AddressLimitExceededError, _address_limit_handler)
    app.add_exception_handler(FavoriteAlreadyExistsError, _favorite_exists_handler)
    app.add_exception_handler(FavoriteNotFoundError, _favorite_not_found_handler)
    app.add_exception_handler(UserProfileNotFoundError, _profile_not_found_handler)
    app.add_exception_handler(InvalidTokenError, _invalid_token_handler)
    app.add_exception_handler(TokenExpiredError, _token_expired_handler)
    app.add_exception_handler(DatabaseError, _database_error_handler)
    app.add_exception_handler(Exception, _unexpected_error_handler)
