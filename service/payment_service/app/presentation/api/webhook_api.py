from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.application.dto.payment_dto import WebhookPayload
from app.application.service.payment_service import PaymentService
from app.domain.entity.payment_entity import PaymentProvider

router = APIRouter(prefix="/webhooks")


@router.post("/kaspi")
@inject
async def kaspi_webhook(
    request: Request,
    service: FromDishka[PaymentService],
) -> JSONResponse:
    payload = await request.json()
    await service.handle_webhook(
        WebhookPayload(
            provider=PaymentProvider.KASPI,
            event_type=payload.get("status", "payment.unknown"),
            raw=payload,
        )
    )
    return JSONResponse(content={"result": 0})


@router.post("/stripe")
@inject
async def stripe_webhook(
    request: Request,
    service: FromDishka[PaymentService],
) -> JSONResponse:
    payload = await request.json()
    await service.handle_webhook(
        WebhookPayload(
            provider=PaymentProvider.STRIPE,
            event_type=payload.get("type", "unknown"),
            raw=payload,
        )
    )
    return JSONResponse(content={"received": True})


@router.post("/freedompay")
@inject
async def freedompay_webhook(
    request: Request,
    service: FromDishka[PaymentService],
) -> JSONResponse:
    payload = await request.json()
    pg_result = str(payload.get("pg_result", "0"))
    event_type = "payment.success" if pg_result == "1" else "payment.failed"
    await service.handle_webhook(
        WebhookPayload(
            provider=PaymentProvider.FREEDOMPAY,
            event_type=event_type,
            raw=payload,
        )
    )
    return JSONResponse(content={"pg_status": "ok"})
