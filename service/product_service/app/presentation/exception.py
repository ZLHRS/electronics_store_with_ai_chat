import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    BrandNotFoundError,
    CategoryNotFoundError,
    DatabaseError,
    DuplicateEntryError,
    InvalidTokenError,
    ProductNotFoundError,
    SlugAlreadyExistsError,
    TokenExpiredError,
)

logger = logging.getLogger(__name__)


async def _not_found_handler(request: Request, exc: ProductNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def _category_not_found_handler(request: Request, exc: CategoryNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def _brand_not_found_handler(request: Request, exc: BrandNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def _slug_exists_handler(request: Request, exc: SlugAlreadyExistsError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def _duplicate_handler(request: Request, exc: DuplicateEntryError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


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
    app.add_exception_handler(ProductNotFoundError, _not_found_handler)
    app.add_exception_handler(CategoryNotFoundError, _category_not_found_handler)
    app.add_exception_handler(BrandNotFoundError, _brand_not_found_handler)
    app.add_exception_handler(SlugAlreadyExistsError, _slug_exists_handler)
    app.add_exception_handler(DuplicateEntryError, _duplicate_handler)
    app.add_exception_handler(InvalidTokenError, _invalid_token_handler)
    app.add_exception_handler(TokenExpiredError, _token_expired_handler)
    app.add_exception_handler(DatabaseError, _database_error_handler)
    app.add_exception_handler(Exception, _unexpected_error_handler)
