import uuid

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from app.application.dto.payment_dto import CreatePaymentCommand, PaymentResult
from app.application.service.payment_service import PaymentService
from app.presentation.deps import CurrentUser, get_current_user
from app.presentation.limiters import payment_limiter
from app.presentation.schema.payment_schema import CreatePaymentRequest, PaymentResponse

router = APIRouter(prefix="/payments", dependencies=[Depends(payment_limiter)])


@router.post("", response_model=PaymentResponse, status_code=201)
@inject
async def create_payment(
    data: CreatePaymentRequest,
    service: FromDishka[PaymentService],
    user: CurrentUser = Depends(get_current_user),
) -> PaymentResponse:
    return _to_response(
        await service.create_payment(
            user.id,
            CreatePaymentCommand(
                order_id=data.order_id,
                provider=data.provider,
                currency=data.currency,
            ),
        )
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
@inject
async def get_payment(
    payment_id: uuid.UUID,
    service: FromDishka[PaymentService],
    user: CurrentUser = Depends(get_current_user),
) -> PaymentResponse:
    return _to_response(await service.get_payment(payment_id, user.id))


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
@inject
async def refund_payment(
    payment_id: uuid.UUID,
    service: FromDishka[PaymentService],
    user: CurrentUser = Depends(get_current_user),
) -> PaymentResponse:
    return _to_response(await service.refund_payment(payment_id, user.id))


def _to_response(result: PaymentResult) -> PaymentResponse:
    return PaymentResponse(
        id=result.id,
        order_id=result.order_id,
        user_id=result.user_id,
        provider=result.provider,
        amount=result.amount,
        currency=result.currency,
        status=result.status,
        provider_payment_id=result.provider_payment_id,
        payment_url=result.payment_url,
        failure_reason=result.failure_reason,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )
