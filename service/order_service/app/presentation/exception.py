import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    CartEmptyError,
    DatabaseError,
    InvalidTokenError,
    OrderAccessDeniedError,
    OrderCancelForbiddenError,
    OrderNotFoundError,
    ProductNotAvailableError,
    ProductNotFoundError,
    TokenExpiredError,
)

logger = logging.getLogger(__name__)


async def _order_not_found_handler(request: Request, exc: OrderNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def _order_access_denied_handler(
    request: Request, exc: OrderAccessDeniedError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


async def _order_cancel_forbidden_handler(
    request: Request, exc: OrderCancelForbiddenError
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


async def _cart_empty_handler(request: Request, exc: CartEmptyError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


async def _product_not_found_handler(request: Request, exc: ProductNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


async def _product_not_available_handler(
    request: Request, exc: ProductNotAvailableError
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


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
    app.add_exception_handler(OrderNotFoundError, _order_not_found_handler)
    app.add_exception_handler(OrderAccessDeniedError, _order_access_denied_handler)
    app.add_exception_handler(OrderCancelForbiddenError, _order_cancel_forbidden_handler)
    app.add_exception_handler(CartEmptyError, _cart_empty_handler)
    app.add_exception_handler(ProductNotFoundError, _product_not_found_handler)
    app.add_exception_handler(ProductNotAvailableError, _product_not_available_handler)
    app.add_exception_handler(InvalidTokenError, _invalid_token_handler)
    app.add_exception_handler(TokenExpiredError, _token_expired_handler)
    app.add_exception_handler(DatabaseError, _database_error_handler)
    app.add_exception_handler(Exception, _unexpected_error_handler)
