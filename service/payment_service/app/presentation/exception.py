import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    DatabaseError,
    InvalidOrderStatusError,
    InvalidPaymentStatusError,
    InvalidTokenError,
    OrderForbiddenError,
    OrderNotFoundError,
    PaymentAlreadyExistsError,
    PaymentForbiddenError,
    PaymentNotFoundError,
    TokenExpiredError,
)

logger = logging.getLogger(__name__)


async def _payment_not_found_handler(request: Request, exc: PaymentNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def _payment_forbidden_handler(request: Request, exc: PaymentForbiddenError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


async def _payment_already_exists_handler(
    request: Request, exc: PaymentAlreadyExistsError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def _invalid_payment_status_handler(
    request: Request, exc: InvalidPaymentStatusError
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


async def _order_not_found_handler(request: Request, exc: OrderNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def _order_forbidden_handler(request: Request, exc: OrderForbiddenError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


async def _invalid_order_status_handler(
    request: Request, exc: InvalidOrderStatusError
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
    app.add_exception_handler(PaymentNotFoundError, _payment_not_found_handler)
    app.add_exception_handler(PaymentForbiddenError, _payment_forbidden_handler)
    app.add_exception_handler(PaymentAlreadyExistsError, _payment_already_exists_handler)
    app.add_exception_handler(InvalidPaymentStatusError, _invalid_payment_status_handler)
    app.add_exception_handler(OrderNotFoundError, _order_not_found_handler)
    app.add_exception_handler(OrderForbiddenError, _order_forbidden_handler)
    app.add_exception_handler(InvalidOrderStatusError, _invalid_order_status_handler)
    app.add_exception_handler(InvalidTokenError, _invalid_token_handler)
    app.add_exception_handler(TokenExpiredError, _token_expired_handler)
    app.add_exception_handler(DatabaseError, _database_error_handler)
    app.add_exception_handler(Exception, _unexpected_error_handler)
