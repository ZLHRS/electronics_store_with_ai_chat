import uuid

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Request

from app.application.dto.order_dto import CreateOrderCommand, OrderResult, UpdateStatusCommand
from app.application.service.order_service import OrderService
from app.config import JWTConfig
from app.domain.permissions import P
from app.presentation.deps import CurrentUser, get_current_user, require_permission
from app.presentation.limiters import orders_limiter
from app.presentation.schema.order_schema import (
    CreateOrderRequest,
    OrderItemResponse,
    OrderResponse,
    PaymentConfirmedRequest,
    UpdateStatusRequest,
)

router = APIRouter(prefix="/orders", dependencies=[Depends(orders_limiter)])


@router.post("", response_model=OrderResponse, status_code=201)
@inject
async def create_order(
    request: Request,
    data: CreateOrderRequest,
    service: FromDishka[OrderService],
    jwt_config: FromDishka[JWTConfig],
    user: CurrentUser = Depends(get_current_user),
) -> OrderResponse:
    token = request.cookies.get(jwt_config.access_token_name, "")
    result = await service.create_order(
        user.id,
        token,
        CreateOrderCommand(
            delivery_address=data.delivery_address,
            payment_method=data.payment_method,
        ),
    )
    return _to_response(result)


@router.get("", response_model=list[OrderResponse])
@inject
async def list_orders(
    service: FromDishka[OrderService],
    user: CurrentUser = Depends(get_current_user),
) -> list[OrderResponse]:
    results = await service.list_orders(user.id, user.permissions)
    return [_to_response(r) for r in results]


@router.get("/{order_id}", response_model=OrderResponse)
@inject
async def get_order(
    order_id: uuid.UUID,
    service: FromDishka[OrderService],
    user: CurrentUser = Depends(get_current_user),
) -> OrderResponse:
    result = await service.get_order(order_id, user.id, user.permissions)
    return _to_response(result)


@router.patch("/{order_id}/cancel", response_model=OrderResponse)
@inject
async def cancel_order(
    order_id: uuid.UUID,
    service: FromDishka[OrderService],
    user: CurrentUser = Depends(get_current_user),
) -> OrderResponse:
    result = await service.cancel_order(order_id, user.id)
    return _to_response(result)


@router.patch("/{order_id}/status", response_model=OrderResponse)
@inject
async def update_status(
    order_id: uuid.UUID,
    data: UpdateStatusRequest,
    service: FromDishka[OrderService],
    _: CurrentUser = Depends(require_permission(P.ORDERS_UPDATE_ALL)),
) -> OrderResponse:
    result = await service.update_status(order_id, UpdateStatusCommand(status=data.status))
    return _to_response(result)


@router.post("/{order_id}/payment-confirmed", response_model=OrderResponse)
@inject
async def payment_confirmed(
    order_id: uuid.UUID,
    data: PaymentConfirmedRequest,
    service: FromDishka[OrderService],
) -> OrderResponse:
    result = await service.update_status(order_id, UpdateStatusCommand(status="paid"))
    return _to_response(result)


@router.post("/{order_id}/payment-failed", response_model=OrderResponse)
@inject
async def payment_failed(
    order_id: uuid.UUID,
    service: FromDishka[OrderService],
) -> OrderResponse:
    result = await service.update_status(order_id, UpdateStatusCommand(status="cancelled"))
    return _to_response(result)


def _to_response(result: OrderResult) -> OrderResponse:
    return OrderResponse(
        id=result.id,
        user_id=result.user_id,
        status=result.status,
        total_amount=result.total_amount,
        delivery_address=result.delivery_address,
        payment_method=result.payment_method,
        created_at=result.created_at,
        updated_at=result.updated_at,
        items=[
            OrderItemResponse(
                id=i.id,
                order_id=i.order_id,
                product_id=i.product_id,
                product_name=i.product_name,
                quantity=i.quantity,
                unit_price=i.unit_price,
                total_price=i.total_price,
            )
            for i in result.items
        ],
    )
