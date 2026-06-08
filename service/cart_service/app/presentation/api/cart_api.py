import uuid

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from app.application.dto.cart_dto import AddItemCommand, CartResult, UpdateItemCommand
from app.application.service.cart_service import CartService
from app.presentation.deps import CurrentUser, get_current_user
from app.presentation.limiters import cart_limiter
from app.presentation.schema.cart_schema import (
    AddItemRequest,
    CartItemResponse,
    CartResponse,
    ProductSnapshotResponse,
    UpdateItemRequest,
)

router = APIRouter(prefix="/cart", dependencies=[Depends(cart_limiter)])


@router.get("", response_model=CartResponse)
@inject
async def get_cart(
    service: FromDishka[CartService],
    user: CurrentUser = Depends(get_current_user),
) -> CartResponse:
    return _to_response(await service.get_cart(user.id))


@router.post("/items", response_model=CartResponse, status_code=201)
@inject
async def add_item(
    data: AddItemRequest,
    service: FromDishka[CartService],
    user: CurrentUser = Depends(get_current_user),
) -> CartResponse:
    return _to_response(
        await service.add_item(
            user.id, AddItemCommand(product_id=data.product_id, quantity=data.quantity)
        )
    )


@router.patch("/items/{product_id}", response_model=CartResponse)
@inject
async def update_item(
    product_id: uuid.UUID,
    data: UpdateItemRequest,
    service: FromDishka[CartService],
    user: CurrentUser = Depends(get_current_user),
) -> CartResponse:
    return _to_response(
        await service.update_item(user.id, product_id, UpdateItemCommand(quantity=data.quantity))
    )


@router.delete("/items/{product_id}", response_model=CartResponse)
@inject
async def remove_item(
    product_id: uuid.UUID,
    service: FromDishka[CartService],
    user: CurrentUser = Depends(get_current_user),
) -> CartResponse:
    return _to_response(await service.remove_item(user.id, product_id))


@router.delete("", response_model=CartResponse)
@inject
async def clear_cart(
    service: FromDishka[CartService],
    user: CurrentUser = Depends(get_current_user),
) -> CartResponse:
    return _to_response(await service.clear_cart(user.id))


def _to_response(result: CartResult) -> CartResponse:
    return CartResponse(
        id=result.id,
        user_id=result.user_id,
        status=result.status,
        total=result.total,
        created_at=result.created_at,
        updated_at=result.updated_at,
        items=[
            CartItemResponse(
                id=item.id,
                cart_id=item.cart_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=item.line_total,
                created_at=item.created_at,
                updated_at=item.updated_at,
                product=(
                    ProductSnapshotResponse(
                        name=item.product.name,
                        image_url=item.product.image_url,
                        current_price=item.product.current_price,
                        status=item.product.status,
                    )
                    if item.product
                    else None
                ),
            )
            for item in result.items
        ],
    )
