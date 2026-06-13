import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    DatabaseError,
    IndexingError,
    InvalidTokenError,
    SessionForbiddenError,
    SessionNotFoundError,
    TokenExpiredError,
)

logger = logging.getLogger(__name__)


async def _session_not_found(request: Request, exc: SessionNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def _session_forbidden(request: Request, exc: SessionForbiddenError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


async def _indexing_error(request: Request, exc: IndexingError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(exc)})


async def _invalid_token(request: Request, exc: InvalidTokenError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


async def _token_expired(request: Request, exc: TokenExpiredError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


async def _database_error(request: Request, exc: DatabaseError) -> JSONResponse:
    logger.error("Database error on %s %s", request.method, request.url.path, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


async def _unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unexpected error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(SessionNotFoundError, _session_not_found)
    app.add_exception_handler(SessionForbiddenError, _session_forbidden)
    app.add_exception_handler(IndexingError, _indexing_error)
    app.add_exception_handler(InvalidTokenError, _invalid_token)
    app.add_exception_handler(TokenExpiredError, _token_expired)
    app.add_exception_handler(DatabaseError, _database_error)
    app.add_exception_handler(Exception, _unexpected_error)
