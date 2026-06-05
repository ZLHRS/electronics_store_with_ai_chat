import uuid
from contextvars import ContextVar

from fastapi import Request
from fastapi.responses import Response

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


async def request_id_middleware(request: Request, call_next) -> Response:
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    token = request_id_var.set(request_id)
    try:
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response
    finally:
        request_id_var.reset(token)
